#!/usr/bin/env python3
"""check-async.py — Async safety and cancellation checks for GNOME extensions.

Usage: check-async.py EXTENSION_DIR

Checks:
  - Gio async calls without Gio.Cancellable
  - disable() missing cancel()/abort() when extension uses async Gio

Output: PIPE-delimited lines: STATUS|check-name|detail
"""

import os
import re
import sys


def result(status, check, detail):
    print(f"{status}|{check}|{detail}")


def find_js_files(ext_dir, exclude_prefs=True):
    """Find JS files, optionally excluding prefs.js."""
    skip_dirs = {'node_modules', '.git', '__pycache__'}
    files = []
    for root, dirs, filenames in os.walk(ext_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in filenames:
            if name.endswith('.js'):
                if exclude_prefs and name == 'prefs.js':
                    continue
                files.append(os.path.join(root, name))
    return files


def strip_comments(content):
    """Remove single-line and block comments from JS content."""
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    return content


def check_cancellable_usage(ext_dir, js_files):
    """WARN when Gio async calls exist but Gio.Cancellable is not used."""
    has_gio_async = False
    has_cancellable = False
    async_locations = []

    gio_async_patterns = [
        r'load_contents_async\s*\(',
        r'send_and_read_async\s*\(',
        r'read_bytes_async\s*\(',
        r'write_bytes_async\s*\(',
        r'query_info_async\s*\(',
        r'enumerate_children_async\s*\(',
        r'replace_contents_async\s*\(',
    ]

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = f.read()

        clean = strip_comments(content)

        if 'Gio.Cancellable' in clean or 'new Gio.Cancellable' in clean:
            has_cancellable = True

        for pat in gio_async_patterns:
            for m in re.finditer(pat, clean):
                lineno = clean[:m.start()].count('\n') + 1
                has_gio_async = True
                async_locations.append(f"{rel}:{lineno}")

    if has_gio_async and not has_cancellable:
        locs = ', '.join(async_locations[:3])
        result("WARN", "async/no-cancellable",
               f"Gio async calls at {locs} without Gio.Cancellable — "
               f"async operations should be cancellable via disable()")
    elif has_gio_async:
        result("PASS", "async/cancellable-used",
               "Gio.Cancellable used with async operations")


def check_async_inline_cancellable(ext_dir, js_files):
    """GAP-020: Flag individual _async() calls without cancellable on the same line.

    Suppressed when the enclosing function has a cancellable-like parameter
    (isCancelled, cancellable) — caller manages cancellation.
    """
    cancellable_param_re = re.compile(
        r'(?:async\s+)?\w+\s*\(([^)]*)\)\s*\{')
    cancellable_names = {'iscancelled', 'cancellable', 'cancel'}
    missing = []

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = f.read()
            lines = content.splitlines(True)

        # If file uses _destroyed pattern, it has an alternative async safety
        # mechanism — suppress missing-cancellable warnings for this file
        if '_destroyed' in content:
            continue

        # Track whether current scope has a cancellable parameter
        has_cancellable_param = False
        scope_depth = 0
        scope_start_depth = -1

        for lineno, line in enumerate(lines, 1):
            stripped = line.lstrip()
            if stripped.startswith('//') or stripped.startswith('*'):
                continue

            # Detect function/method definitions with parameters
            func_match = cancellable_param_re.search(line)
            if func_match:
                params = func_match.group(1).lower()
                param_names = {p.strip().split('=')[0].strip()
                               for p in params.split(',')}
                if param_names & cancellable_names:
                    has_cancellable_param = True
                    scope_start_depth = scope_depth

            # Track brace depth
            scope_depth += line.count('{') - line.count('}')

            # Reset cancellable param flag when exiting the function scope
            if has_cancellable_param and scope_depth <= scope_start_depth:
                has_cancellable_param = False

            if '_async(' not in stripped:
                continue
            # Skip lines that already have cancellable
            if 'cancellable' in line.lower():
                continue
            # Skip if enclosing function has cancellable parameter
            if has_cancellable_param:
                continue
            missing.append(f"{rel}:{lineno}")

    if missing:
        locs = ', '.join(missing[:3])
        extra = f" (+{len(missing) - 3} more)" if len(missing) > 3 else ""
        result("WARN", "async/missing-cancellable",
               f"_async() calls without Gio.Cancellable at {locs}{extra} "
               f"— async operations may run after disable()")
    else:
        result("PASS", "async/missing-cancellable",
               "All _async() calls have cancellable argument")


def check_disable_cancellation(ext_dir, js_files):
    """WARN when extension uses async but disable() has no cancel/abort."""
    ext_js = os.path.join(ext_dir, 'extension.js')
    if not os.path.isfile(ext_js):
        return

    with open(ext_js, encoding='utf-8', errors='replace') as f:
        content = f.read()

    clean = strip_comments(content)

    # Check if extension uses async
    has_async = bool(re.search(r'\basync\b', clean)) and \
        bool(re.search(r'\bawait\b', clean))
    if not has_async:
        return

    # Check if disable() contains cancel/abort
    disable_match = re.search(r'\bdisable\s*\(\s*\)\s*\{', clean)
    if not disable_match:
        return

    # Extract disable body
    start = disable_match.end()
    depth = 1
    pos = start
    while pos < len(clean) and depth > 0:
        if clean[pos] == '{':
            depth += 1
        elif clean[pos] == '}':
            depth -= 1
        pos += 1
    disable_body = clean[start:pos - 1]

    has_cancel = bool(re.search(r'\.(cancel|abort)\s*\(', disable_body))
    has_destroyed = bool(re.search(r'_destroyed\s*=\s*true', disable_body))

    if not has_cancel and not has_destroyed:
        result("WARN", "async/disable-no-cancel",
               "Extension uses async but disable() has no .cancel(), "
               ".abort(), or _destroyed flag — async operations may outlive disable()")
    else:
        result("PASS", "async/disable-cancellation",
               "disable() handles async cancellation")


def main():
    if len(sys.argv) < 2:
        result("FAIL", "async/args", "No extension directory provided")
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])
    js_files = find_js_files(ext_dir)

    if not js_files:
        result("SKIP", "async/no-js", "No JavaScript files found")
        return

    check_cancellable_usage(ext_dir, js_files)
    check_async_inline_cancellable(ext_dir, js_files)
    check_disable_cancellation(ext_dir, js_files)


if __name__ == '__main__':
    main()
