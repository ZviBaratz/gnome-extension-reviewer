#!/usr/bin/env python3
"""check-init.py — Detect init-time Shell modifications in GNOME extensions.

Usage: check-init.py EXTENSION_DIR

Extensions must not modify Shell globals (Main.panel, Main.overview, etc.)
or create GObjects at module scope or in constructor(). All Shell modifications
must happen inside enable() and be reversed in disable().

Checks:
  - R-INIT-01: Shell global access at module scope or in constructor()

Output: PIPE-delimited lines: STATUS|check-name|detail
"""

import os
import re
import sys


def result(status, check, detail):
    print(f"{status}|{check}|{detail}")


def strip_comments(content):
    """Remove single-line and block comments from JS content."""
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    return content


def find_js_files(ext_dir):
    """Find all .js files excluding prefs.js."""
    skip_dirs = {'node_modules', '.git', '__pycache__'}
    files = []
    for root, dirs, filenames in os.walk(ext_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in filenames:
            if name.endswith('.js') and name != 'prefs.js':
                files.append(os.path.join(root, name))
    return files


def is_skip_line(line):
    """Check if a line should be skipped (imports, Gio._promisify, empty)."""
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith('import ') or stripped.startswith('import{'):
        return True
    if 'Gio._promisify' in stripped:
        return True
    # Export statements that just re-export (no side effects)
    if re.match(r'^export\s*\{', stripped):
        return True
    return False


# Shell globals that should only be accessed inside enable()/disable()
SHELL_GLOBALS = re.compile(
    r'\bMain\.(panel|overview|layoutManager|sessionMode|messageTray|wm|'
    r'extensionManager|notify)\b'
)

# GObject constructors that allocate resources — any GI namespace is forbidden at init
GOBJECT_CONSTRUCTORS = re.compile(
    r'\bnew\s+(St\.\w+|Clutter\.\w+|Gio\.\w+|GLib\.\w+|'
    r'GObject\.\w+|Meta\.\w+|Shell\.\w+|Pango\.\w+|'
    r'Soup\.\w+|Cogl\.\w+|Atk\.\w+|GdkPixbuf\.\w+)\b'
)


def extract_module_scope_lines(content_lines):
    """Extract lines that are at module scope (outside any class/function body).

    Returns a list of (original_lineno, line_text) tuples.
    Uses brace-depth tracking: depth 0 = module scope.
    """
    module_lines = []
    depth = 0
    for lineno, line in enumerate(content_lines, 1):
        if depth == 0:
            module_lines.append((lineno, line))
        # Track brace depth (simple heuristic — doesn't handle braces in strings,
        # but strip_comments has already removed comments)
        depth += line.count('{') - line.count('}')
        if depth < 0:
            depth = 0
    return module_lines


def extract_constructor_lines(content_lines):
    """Extract lines inside constructor() method bodies.

    Returns a list of (original_lineno, line_text) tuples.
    Skips constructors inside GObject.registerClass() class bodies, since those
    only run when explicitly instantiated (not at module init time).
    """
    constructor_lines = []
    in_constructor = False
    ctor_depth = 0
    in_register_class = False
    depth = 0

    for lineno, line in enumerate(content_lines, 1):
        # Enter registerClass scope
        if not in_register_class and re.search(
                r'GObject\.registerClass\s*\(', line):
            in_register_class = True

        # Track brace depth
        depth += line.count('{') - line.count('}')
        if depth < 0:
            depth = 0

        # Exit registerClass scope when all braces close
        if in_register_class and ')' in line and depth == 0:
            in_register_class = False
            continue

        # Detect constructor start (skip inside registerClass bodies)
        if not in_constructor and re.search(r'\bconstructor\s*\(', line):
            if in_register_class:
                continue
            in_constructor = True
            open_braces = line.count('{')
            close_braces = line.count('}')
            if open_braces > 0:
                ctor_depth = open_braces - close_braces
                if ctor_depth <= 0:
                    constructor_lines.append((lineno, line))
                    in_constructor = False
                else:
                    constructor_lines.append((lineno, line))
            else:
                ctor_depth = 0
            continue

        if in_constructor:
            constructor_lines.append((lineno, line))
            ctor_depth += line.count('{') - line.count('}')
            if ctor_depth <= 0:
                in_constructor = False

    return constructor_lines


def check_init_modifications(ext_dir):
    """R-INIT-01: Detect Shell modifications outside enable()/disable()."""
    js_files = find_js_files(ext_dir)
    if not js_files:
        result("PASS", "init/shell-modification",
               "No init-time Shell modifications detected")
        return

    violations = []

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            raw_content = f.read()

        cleaned = strip_comments(raw_content)
        lines = cleaned.splitlines()

        # Check module-scope lines
        module_lines = extract_module_scope_lines(lines)
        for lineno, line in module_lines:
            if is_skip_line(line):
                continue
            if SHELL_GLOBALS.search(line):
                violations.append(f"{rel}:{lineno}")
            elif GOBJECT_CONSTRUCTORS.search(line):
                violations.append(f"{rel}:{lineno}")

        # Check constructor() lines
        ctor_lines = extract_constructor_lines(lines)
        for lineno, line in ctor_lines:
            if is_skip_line(line):
                continue
            if SHELL_GLOBALS.search(line):
                violations.append(f"{rel}:{lineno}")
            elif GOBJECT_CONSTRUCTORS.search(line):
                violations.append(f"{rel}:{lineno}")

    if violations:
        for loc in violations:
            result("FAIL", "init/shell-modification",
                   f"{loc}: Shell modification outside enable()")
    else:
        result("PASS", "init/shell-modification",
               "No init-time Shell modifications detected")


def check_promisify_placement(ext_dir):
    """R-INIT-02: Detect Gio._promisify() inside enable() body."""
    js_files = find_js_files(ext_dir)
    if not js_files:
        result("PASS", "init/promisify-in-enable",
               "No Gio._promisify() placement issues")
        return

    violations = []

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            raw_content = f.read()

        cleaned = strip_comments(raw_content)
        lines = cleaned.splitlines()

        in_enable = False
        enable_depth = 0

        for lineno, line in enumerate(lines, 1):
            # Detect enable() method start
            if not in_enable and re.search(r'\benable\s*\(', line):
                in_enable = True
                enable_depth = 0
                # Count braces on the enable line itself
                enable_depth += line.count('{') - line.count('}')
                if enable_depth <= 0 and '{' in line:
                    # Single-line enable body
                    if 'Gio._promisify' in line:
                        violations.append(f"{rel}:{lineno}")
                    in_enable = False
                continue

            if in_enable:
                enable_depth += line.count('{') - line.count('}')
                if 'Gio._promisify' in line:
                    violations.append(f"{rel}:{lineno}")
                if enable_depth <= 0:
                    in_enable = False

    if violations:
        for loc in violations:
            result("WARN", "init/promisify-in-enable",
                   f"{loc}: Gio._promisify() inside enable() "
                   f"— should be at module scope")
    else:
        result("PASS", "init/promisify-in-enable",
               "No Gio._promisify() placement issues")


def main():
    if len(sys.argv) < 2:
        result("FAIL", "init/args", "No extension directory provided")
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])
    check_init_modifications(ext_dir)
    check_promisify_placement(ext_dir)


if __name__ == '__main__':
    main()
