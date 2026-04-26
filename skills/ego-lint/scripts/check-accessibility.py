#!/usr/bin/env python3
"""check-accessibility.py — Basic accessibility checks for GNOME extensions.

Usage: check-accessibility.py EXTENSION_DIR

Partial automation of accessibility checklist items A1, A2:
  A2: Icon-only St.Button without accessible_name
  A1: Custom St.Widget subclass without accessible_role

All findings are WARN severity — accessibility issues are advisory, not blocking.

Output: PIPE-delimited lines: STATUS|check-name|detail
"""

import os
import re
import sys


def result(status, check, detail):
    print(f"{status}|{check}|{detail}")


def find_js_files(ext_dir):
    """Find JS files excluding node_modules/.git."""
    skip_dirs = {'node_modules', '.git', '__pycache__', 'kwin'}
    files = []
    for root, dirs, filenames in os.walk(ext_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in filenames:
            if name.endswith('.js'):
                files.append(os.path.join(root, name))
    return files


def _preserve_newlines(match):
    """Replace block comment content with empty lines to preserve line numbers."""
    return '\n' * match.group(0).count('\n')


def strip_comments(content):
    """Remove single-line and block comments."""
    content = re.sub(r'/\*.*?\*/', _preserve_newlines, content, flags=re.DOTALL)
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    return content


def check_accessible_name(ext_dir, js_files):
    """A2: Icon-only St.Button without accessible_name.

    Detects new St.Button({...}) where the constructor args contain
    icon_name or child: (icon) but no accessible_name.
    """
    findings = []

    # Pattern: new St.Button({ ... }) spanning potentially multiple lines
    button_re = re.compile(
        r'new\s+St\.Button\s*\(\s*\{([^}]*)\}',
        re.DOTALL
    )

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = strip_comments(f.read())

        for m in button_re.finditer(content):
            args = m.group(1)
            # Check if it looks icon-only (has icon_name or style_class with icon)
            has_icon = bool(re.search(r'\bicon_name\b', args))
            has_child_icon = bool(re.search(r'\bchild\b.*St\.Icon', args, re.DOTALL))
            has_label = bool(re.search(r'\blabel\b', args))
            has_accessible = bool(re.search(r'\baccessible_name\b', args))

            if (has_icon or has_child_icon) and not has_label and not has_accessible:
                lineno = content[:m.start()].count('\n') + 1
                findings.append(f"{rel}:{lineno}")

    if findings:
        locs = ', '.join(findings[:5])
        result("WARN", "accessibility/accessible-name",
               f"{len(findings)} icon-only St.Button(s) without accessible_name: "
               f"{locs}")
    else:
        result("PASS", "accessibility/accessible-name",
               "All St.Button instances have labels or accessible_name")


def check_widget_role(ext_dir, js_files):
    """A1: Custom St.Widget subclass without accessible_role.

    Detects GObject.registerClass on St.Widget subclasses and checks if
    the class sets accessible_role in Properties or constructor.
    """
    findings = []

    # Pattern: class Foo extends St.Widget (or St.BoxLayout etc.)
    widget_class_re = re.compile(
        r'class\s+(\w+)\s+extends\s+St\.(\w+)',
    )

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = strip_comments(f.read())

        for m in widget_class_re.finditer(content):
            class_name = m.group(1)
            parent = m.group(2)

            # Only check St.Widget direct subclasses (St.BoxLayout, St.Bin etc.
            # already have default roles)
            if parent != 'Widget':
                continue

            # Check if accessible_role is set anywhere in this class
            # Look from the class declaration to the next class or end of file
            class_start = m.start()
            next_class = re.search(r'\nclass\s+\w+', content[class_start + 1:])
            class_end = class_start + 1 + next_class.start() if next_class else len(content)
            class_body = content[class_start:class_end]

            if 'accessible_role' not in class_body:
                lineno = content[:class_start].count('\n') + 1
                findings.append(f"{rel}:{lineno} ({class_name})")

    if findings:
        locs = ', '.join(findings[:5])
        result("WARN", "accessibility/widget-role",
               f"{len(findings)} custom St.Widget subclass(es) without "
               f"accessible_role: {locs}")
    else:
        result("PASS", "accessibility/widget-role",
               "All custom St.Widget subclasses have accessible_role "
               "or no custom widgets found")


def main():
    if len(sys.argv) < 2:
        result("FAIL", "accessibility/args", "No extension directory provided")
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])
    js_files = find_js_files(ext_dir)

    if not js_files:
        result("SKIP", "accessibility/no-js", "No JavaScript files found")
        return

    # Check for UI-related imports before running checks
    has_ui = False
    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = f.read()
        if re.search(r"gi://St|gi://Clutter|from\s+['\"].*ui/", content):
            has_ui = True
            break

    if not has_ui:
        result("SKIP", "accessibility/accessible-name",
               "No UI-related imports found")
        result("SKIP", "accessibility/widget-role",
               "No UI-related imports found")
        return

    check_accessible_name(ext_dir, js_files)
    check_widget_role(ext_dir, js_files)


if __name__ == '__main__':
    main()
