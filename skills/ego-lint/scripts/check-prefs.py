#!/usr/bin/env python3
"""check-prefs.py — Validate prefs.js for EGO compliance.

Usage: check-prefs.py EXTENSION_DIR

Checks:
  - Dual prefs pattern (getPreferencesWidget + fillPreferencesWindow)
  - Missing default export class
  - Resource path capitalization

Output: PIPE-delimited lines: STATUS|check-name|detail
"""

import os
import re
import sys


def result(status, check, detail):
    print(f"{status}|{check}|{detail}")


def strip_comments(content):
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    return content


def main():
    if len(sys.argv) < 2:
        result("FAIL", "prefs/args", "No extension directory provided")
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])
    prefs_path = os.path.join(ext_dir, 'prefs.js')

    if not os.path.isfile(prefs_path):
        result("SKIP", "prefs/exists", "No prefs.js found")
        return

    with open(prefs_path, encoding='utf-8', errors='replace') as f:
        raw_content = f.read()

    content = strip_comments(raw_content)

    # Dual prefs pattern check
    has_widget = bool(re.search(r'\bgetPreferencesWidget\b', content))
    has_fill = bool(re.search(r'\bfillPreferencesWindow\b', content))

    if has_widget and has_fill:
        result("FAIL", "prefs/dual-prefs-pattern",
               "prefs.js defines both getPreferencesWidget() and fillPreferencesWindow() — "
               "use only fillPreferencesWindow() for GNOME 45+")
    elif has_fill:
        result("PASS", "prefs/prefs-method", "prefs.js uses fillPreferencesWindow()")
    elif has_widget:
        result("PASS", "prefs/prefs-method", "prefs.js uses getPreferencesWidget()")
    else:
        result("WARN", "prefs/missing-prefs-method",
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


if __name__ == '__main__':
    main()
