#!/usr/bin/env python3
"""check-quality.py — Tier 2 heuristic AI slop detection for GNOME extensions.

Usage: check-quality.py EXTENSION_DIR

Performs structural analysis that goes beyond simple pattern matching:
  - Excessive try-catch density
  - Impossible state checks (isLocked without lock session-mode)
  - Over-engineered async coordination (_pendingDestroy + _initializing)
  - Module-level mutable state
  - Empty catch blocks

Output: PIPE-delimited lines: STATUS|check-name|detail
"""

import json
import os
import re
import sys


def result(status, check, detail):
    print(f"{status}|{check}|{detail}")


def find_js_files(ext_dir):
    """Find all JS files in extension directory."""
    files = []
    for root, _dirs, filenames in os.walk(ext_dir):
        for name in filenames:
            if name.endswith('.js'):
                files.append(os.path.join(root, name))
    return files


def get_session_modes(ext_dir):
    """Read session-modes from metadata.json."""
    meta_path = os.path.join(ext_dir, 'metadata.json')
    if not os.path.isfile(meta_path):
        return None
    try:
        with open(meta_path) as f:
            meta = json.load(f)
        return meta.get('session-modes')
    except (json.JSONDecodeError, OSError):
        return None


def check_try_catch_density(ext_dir, js_files):
    """R-QUAL-01: Flag excessive try-catch and destroy-wrapping."""
    total_try = 0
    total_funcs = 0
    destroy_wraps = []

    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        rel = os.path.relpath(filepath, ext_dir)
        func_count = 0
        try_count = 0

        for i, line in enumerate(lines):
            # Count function/method definitions
            if re.search(r'\b(function|async\s+function)\s+\w+\s*\(', line):
                func_count += 1
            elif re.search(r'\b(async\s+)?\w+\s*\([^)]*\)\s*\{', line):
                func_count += 1

            # Count try blocks
            if re.search(r'\btry\s*\{', line):
                try_count += 1

            # Detect try-catch wrapping a single .destroy() call
            if re.search(r'\btry\s*\{', line):
                # Look ahead for .destroy() followed by catch
                block = ''.join(lines[i:min(i + 5, len(lines))])
                if re.search(r'try\s*\{[^}]*\.destroy\(\)[^}]*\}\s*catch', block):
                    destroy_wraps.append(f"{rel}:{i + 1}")

        total_try += try_count
        total_funcs += max(func_count, 1)

    ratio = total_try / max(total_funcs, 1)
    if ratio > 0.5 and total_try >= 3:
        result("WARN", "quality/try-catch-density",
               f"{total_try} try-catch blocks across {total_funcs} functions "
               f"(ratio: {ratio:.1f}) — review for necessity")
    else:
        result("PASS", "quality/try-catch-density",
               f"Try-catch ratio acceptable ({total_try}/{total_funcs})")

    for loc in destroy_wraps:
        result("WARN", "quality/destroy-try-catch",
               f"{loc}: try-catch around .destroy() — usually unnecessary")


def check_impossible_state(ext_dir, js_files):
    """R-QUAL-02: Flag isLocked/unlock-dialog checks without matching session-modes."""
    session_modes = get_session_modes(ext_dir)
    # If session-modes absent or ["user"], extension doesn't run on lock screen
    has_lock = (isinstance(session_modes, list) and
                any(m in session_modes for m in ('unlock-dialog', 'gdm')))

    if has_lock:
        result("PASS", "quality/impossible-state",
               "Extension declares lock screen session-modes")
        return

    found = False
    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for lineno, line in enumerate(f, 1):
                if re.search(r'sessionMode\.isLocked', line):
                    result("WARN", "quality/impossible-state",
                           f"{rel}:{lineno}: checks isLocked but extension "
                           f"does not run in lock screen")
                    found = True
                elif re.search(r"currentMode\s*===?\s*['\"]unlock-dialog['\"]", line):
                    result("WARN", "quality/impossible-state",
                           f"{rel}:{lineno}: checks for unlock-dialog but "
                           f"extension does not declare this session-mode")
                    found = True

    if not found:
        result("PASS", "quality/impossible-state",
               "No impossible state checks found")


def check_pendulum_pattern(ext_dir, js_files):
    """R-QUAL-03: Flag _pendingDestroy + _initializing coordination."""
    has_pending = False
    has_initializing = False

    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = f.read()
        if '_pendingDestroy' in content:
            has_pending = True
        if '_initializing' in content:
            has_initializing = True

    if has_pending and has_initializing:
        result("WARN", "quality/pendulum-pattern",
               "Uses _pendingDestroy + _initializing coordination — "
               "consider simpler _destroyed flag pattern per GNOME conventions")
    else:
        result("PASS", "quality/pendulum-pattern",
               "No over-engineered async coordination detected")


def check_module_state(ext_dir, js_files):
    """R-QUAL-04: Flag module-level let/var declarations."""
    found = []

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        brace_depth = 0
        for i, line in enumerate(lines):
            # Track brace depth (rough — doesn't handle strings/comments)
            brace_depth += line.count('{') - line.count('}')

            # Module scope: brace_depth <= 0 (outside any block)
            if brace_depth <= 0 and re.match(r'\s*(let|var)\s+\w+', line):
                found.append(f"{rel}:{i + 1}")

    if found:
        locations = ', '.join(found[:5])
        result("WARN", "quality/module-state",
               f"Module-level mutable state at {locations} — "
               f"ensure reset in both enable() and disable()")
    else:
        result("PASS", "quality/module-state",
               "No module-level mutable state found")


def check_empty_catch(ext_dir, js_files):
    """R-QUAL-05: Flag empty catch blocks."""
    found = []

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Match catch blocks that are empty or contain only whitespace/comments
        for m in re.finditer(r'\bcatch\s*(?:\([^)]*\))?\s*\{([\s\S]*?)\}', content):
            body = m.group(1).strip()
            # Empty or only comments
            if not body or all(
                line.strip().startswith('//') or line.strip().startswith('*')
                or not line.strip()
                for line in body.split('\n')
            ):
                # Calculate line number
                line_num = content[:m.start()].count('\n') + 1
                found.append(f"{rel}:{line_num}")

    if found:
        for loc in found:
            result("WARN", "quality/empty-catch",
                   f"{loc}: empty catch block — at minimum log with console.debug()")
    else:
        result("PASS", "quality/empty-catch",
               "No empty catch blocks found")


def main():
    if len(sys.argv) < 2:
        result("FAIL", "quality/args", "No extension directory provided")
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])
    js_files = find_js_files(ext_dir)

    if not js_files:
        result("SKIP", "quality/no-js", "No JavaScript files found")
        return

    check_try_catch_density(ext_dir, js_files)
    check_impossible_state(ext_dir, js_files)
    check_pendulum_pattern(ext_dir, js_files)
    check_module_state(ext_dir, js_files)
    check_empty_catch(ext_dir, js_files)


if __name__ == '__main__':
    main()
