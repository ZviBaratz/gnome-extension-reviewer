#!/usr/bin/env python3
"""check-gobject.py — GObject pattern validation for GNOME extensions.

Usage: check-gobject.py EXTENSION_DIR

Checks:
  - Missing GTypeName in GObject.registerClass calls
  - Missing super._init() in GObject subclass constructors
  - Missing cr.$dispose() in drawing callbacks

Output: PIPE-delimited lines: STATUS|check-name|detail
"""

import os
import re
import sys


def result(status, check, detail):
    print(f"{status}|{check}|{detail}")


def find_js_files(ext_dir):
    """Find all JS files in extension directory, excluding node_modules."""
    skip_dirs = {'node_modules', '.git', '__pycache__'}
    files = []
    for root, dirs, filenames in os.walk(ext_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in filenames:
            if name.endswith('.js'):
                files.append(os.path.join(root, name))
    return files


def check_gtypename(ext_dir, js_files):
    """WARN when GObject.registerClass has no GTypeName."""
    missing = []
    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = f.read()

        for m in re.finditer(r'GObject\.registerClass\s*\(', content):
            lineno = content[:m.start()].count('\n') + 1
            # Look ahead for GTypeName in the next ~300 chars (metadata object)
            lookahead = content[m.start():m.start() + 300]
            if 'GTypeName' not in lookahead:
                missing.append(f"{rel}:{lineno}")

    if missing:
        for loc in missing[:5]:
            result("WARN", "gobject/missing-gtypename",
                   f"{loc}: GObject.registerClass without GTypeName — "
                   f"add GTypeName to avoid conflicts between extensions")
    else:
        result("PASS", "gobject/missing-gtypename",
               "All registerClass calls include GTypeName")


def check_super_init(ext_dir, js_files):
    """WARN when GObject subclass _init does not call super._init()."""
    missing = []
    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Find class ... extends ... { patterns inside registerClass
        for m in re.finditer(
            r'class\s+\w+\s+extends\s+[\w.]+\s*\{', content
        ):
            # Check if this class is inside registerClass
            preceding = content[max(0, m.start() - 80):m.start()]
            if 'registerClass' not in preceding:
                continue

            # Find _init method in this class
            class_body = content[m.end():]
            init_match = re.search(r'\b_init\s*\([^)]*\)\s*\{', class_body)
            if not init_match:
                continue

            # Extract init body (find matching brace)
            start = init_match.end()
            depth = 1
            pos = start
            while pos < len(class_body) and depth > 0:
                if class_body[pos] == '{':
                    depth += 1
                elif class_body[pos] == '}':
                    depth -= 1
                pos += 1
            init_body = class_body[start:pos - 1]

            if 'super._init' not in init_body and 'super(params)' not in init_body:
                lineno = content[:m.start()].count('\n') + \
                    class_body[:init_match.start()].count('\n') + 1
                missing.append(f"{rel}:{lineno}")

    if missing:
        for loc in missing[:5]:
            result("WARN", "gobject/missing-super-init",
                   f"{loc}: GObject subclass _init() missing super._init() call")
    else:
        result("PASS", "gobject/missing-super-init",
               "All GObject subclass _init() methods call super._init()")


def check_cairo_dispose(ext_dir, js_files):
    """WARN when drawing callbacks use get_context() without $dispose()."""
    missing = []
    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Find vfunc_repaint or set_draw_func callbacks
        for m in re.finditer(
            r'(vfunc_repaint|set_draw_func)\s*[\(\{]', content
        ):
            lineno = content[:m.start()].count('\n') + 1
            # Look ahead for the function body
            lookahead = content[m.start():m.start() + 500]
            if 'get_context' in lookahead and '$dispose' not in lookahead:
                missing.append(f"{rel}:{lineno}")

    if missing:
        for loc in missing:
            result("WARN", "gobject/cairo-dispose",
                   f"{loc}: Drawing callback uses get_context() without "
                   f"cr.$dispose() — will leak Cairo context")
    else:
        result("PASS", "gobject/cairo-dispose",
               "All drawing callbacks dispose Cairo context")


def main():
    if len(sys.argv) < 2:
        result("FAIL", "gobject/args", "No extension directory provided")
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])
    js_files = find_js_files(ext_dir)

    if not js_files:
        result("SKIP", "gobject/no-js", "No JavaScript files found")
        return

    check_gtypename(ext_dir, js_files)
    check_super_init(ext_dir, js_files)
    check_cairo_dispose(ext_dir, js_files)


if __name__ == '__main__':
    main()
