#!/usr/bin/env python3
"""check-prefs.py — Validate prefs.js for EGO compliance.

Usage: check-prefs.py EXTENSION_DIR

Checks:
  - Dual prefs pattern (getPreferencesWidget + fillPreferencesWindow)
  - Missing default export class
  - Resource path capitalization
  - R-PREFS-05: GObject instances stored as class properties without cleanup

Output: PIPE-delimited lines: STATUS|check-name|detail
"""

import json
import os
import re
import sys


def result(status, check, detail):
    print(f"{status}|{check}|{detail}")


def _preserve_newlines(match):
    """Replace block comment content with empty lines to preserve line numbers."""
    return '\n' * match.group(0).count('\n')


def strip_comments(content):
    content = re.sub(r'/\*.*?\*/', _preserve_newlines, content, flags=re.DOTALL)
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    return content


def _resolve_local_parent_content(ext_dir, content):
    """If prefs.js extends a namespace from a local import, return that file's content.

    Handles: import * as UI from './ui.js' + export default class extends UI.Prefs
    Returns stripped content of the parent file, or None if not resolved.
    """
    m = re.search(r'export\s+default\s+class\b[^{]*\bextends\s+(\w+)\.', content)
    if not m:
        return None
    namespace = m.group(1)
    imp = re.search(
        rf"import\s+\*\s+as\s+{re.escape(namespace)}\s+from\s+['\"](\./[^'\"]+)['\"]",
        content,
    )
    if not imp:
        return None
    local_path = imp.group(1).lstrip('./')
    parent_js = os.path.join(ext_dir, local_path)
    if not os.path.isfile(parent_js):
        return None
    with open(parent_js, encoding='utf-8', errors='replace') as f:
        return strip_comments(f.read())


def main():
    if len(sys.argv) < 2:
        result("FAIL", "prefs/args", "No extension directory provided")
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])
    prefs_path = os.path.join(ext_dir, 'prefs.js')
    if not os.path.isfile(prefs_path):
        prefs_path = os.path.join(ext_dir, 'src', 'prefs.js')

    if not os.path.isfile(prefs_path):
        result("SKIP", "prefs/exists", "No prefs.js found")
        return

    with open(prefs_path, encoding='utf-8', errors='replace') as f:
        raw_content = f.read()

    content = strip_comments(raw_content)

    # Dual prefs pattern check
    has_widget = bool(re.search(r'\bgetPreferencesWidget\b', content))
    has_fill = bool(re.search(r'\bfillPreferencesWindow\b', content))

    # If neither method found in prefs.js, check a local parent class file.
    if not has_widget and not has_fill:
        parent_content = _resolve_local_parent_content(ext_dir, content)
        if parent_content:
            if re.search(r'\bfillPreferencesWindow\b', parent_content):
                has_fill = True
            elif re.search(r'\bgetPreferencesWidget\b', parent_content):
                has_widget = True

    if has_widget and has_fill:
        result("FAIL", "prefs/dual-prefs-pattern",
               "prefs.js defines both getPreferencesWidget() and fillPreferencesWindow() — "
               "use only fillPreferencesWindow() for GNOME 45+")
    elif has_fill:
        result("PASS", "prefs/prefs-method", "prefs.js uses fillPreferencesWindow()")
    elif has_widget:
        result("PASS", "prefs/prefs-method", "prefs.js uses getPreferencesWidget()")
    else:
        result("FAIL", "prefs/missing-prefs-method",
               "prefs.js does not define fillPreferencesWindow() or getPreferencesWidget()")

    # Default export check
    if not re.search(r'\bexport\s+default\s+class\b', content):
        result("WARN", "prefs/default-export",
               "prefs.js missing 'export default class' — required for GNOME 45+")
    else:
        result("PASS", "prefs/default-export", "prefs.js has default export class")

    # Check extends ExtensionPreferences
    if re.search(r'\bexport\s+default\s+class\b', content):
        if not re.search(r'\bextends\s+ExtensionPreferences\b', content):
            result("WARN", "prefs/extends-base",
                   "prefs.js default class does not extend ExtensionPreferences — "
                   "required for GNOME 45+")
        else:
            result("PASS", "prefs/extends-base",
                   "prefs.js extends ExtensionPreferences")

    # Resource path capitalization
    # prefs.js should use resource:///org/gnome/Shell/Extensions/js/ (capitalized)
    # NOT resource:///org/gnome/shell/ui/ (lowercase, for extension.js only)
    wrong_path_pattern = r"resource:///org/gnome/shell/ui/"
    if re.search(wrong_path_pattern, raw_content):
        result("FAIL", "prefs/resource-path",
               "prefs.js uses Shell UI resource path (resource:///org/gnome/shell/ui/) — "
               "Shell UI modules are not available in the preferences process")
    else:
        result("PASS", "prefs/resource-path", "Resource paths OK")

    # R-PREFS-05: GObject instances stored as class properties without cleanup
    check_prefs_memory_leak(ext_dir, content)


def check_prefs_memory_leak(ext_dir, content):
    """Check for GObject instances stored as class properties without cleanup."""
    gobject_storage = re.findall(
        r'this\._\w+\s*=\s*new\s+(?:Gtk|Adw|Gio|GLib|GObject)\.\w+',
        content
    )
    if not gobject_storage:
        result("PASS", "prefs/memory-leak", "No stored GObject instances in prefs.js")
        return

    cleanup_patterns = [
        r'\bdestroy\b',
        r'\bclose-request\b',
        r'\bdisconnectObject\b',
        r'\brun_dispose\b',
    ]
    has_cleanup = any(re.search(p, content) for p in cleanup_patterns)

    if has_cleanup:
        result("PASS", "prefs/memory-leak",
               "Stored GObject instances have cleanup indicators")
    else:
        instances = ', '.join(m.split('=')[0].strip() for m in gobject_storage)
        result("WARN", "prefs/memory-leak",
               f"GObject instances stored without cleanup: {instances} — "
               "add destroy/disconnectObject in close-request handler")


if __name__ == '__main__':
    main()
