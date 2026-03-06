#!/usr/bin/env python3
"""check-css.py — CSS class scoping validation for GNOME extensions.

Usage: check-css.py EXTENSION_DIR

Checks:
  - Bare generic CSS class names without prefix/scope
  - !important usage

Output: PIPE-delimited lines: STATUS|check-name|detail
"""

import os
import re
import sys


def result(status, check, detail):
    print(f"{status}|{check}|{detail}")


# Known GNOME Shell theme classes that are OK to target
KNOWN_SHELL_CLASSES = {
    # Panel (_panel.scss)
    'panel', 'panel-button', 'system-status-icon',
    'panel-status-indicators-box', 'clock-display',
    # Popup menu (_popovers.scss + popupMenu.js)
    'popup-menu', 'popup-menu-item', 'popup-separator-menu-item',
    'popup-sub-menu', 'popup-menu-section',
    'popup-menu-content', 'popup-menu-arrow', 'popup-menu-boxpointer',
    'popup-menu-icon', 'popup-menu-ornament',
    'popup-inactive-menu-item', 'popup-ornamented-menu-item',
    'popup-status-menu-item', 'panel-menu', 'background-menu',
    # Quick settings (_quick-settings.scss)
    'quick-toggle', 'quick-settings', 'quick-settings-item',
    'quick-settings-grid', 'quick-menu-toggle', 'quick-toggle-menu',
    'quick-slider',
    # Notifications / messages (_notifications.scss, _message-list.scss)
    'message', 'message-list', 'notification', 'notification-banner',
    # Calendar / date (_calendar.scss)
    'calendar', 'events-button',
    # Overview / workspace (_overview.scss, _window-picker.scss)
    'overview', 'workspace', 'workspace-background',
    'workspace-thumbnails', 'window-picker', 'window-caption',
    'window-close',
    # Search (_search-entry.scss)
    'search-entry',
    # Dash / app grid (_dash.scss, _app-grid.scss)
    'app-well-icon', 'dash', 'show-apps',
    'dash-background', 'overview-icon', 'icon-grid', 'app-folder',
    # Dialogs (_dialogs.scss)
    'modal-dialog',
    # OSD / other (_osd.scss, _slider.scss)
    'osd-window', 'slider',
}


def strip_css_comments(content):
    """Remove CSS block comments."""
    return re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)


def find_stylesheet(ext_dir):
    """Find stylesheet.css in common locations (root or src/)."""
    for candidate in ['stylesheet.css', os.path.join('src', 'stylesheet.css')]:
        path = os.path.join(ext_dir, candidate)
        if os.path.isfile(path):
            return path
    return None


def check_unscoped_classes(ext_dir):
    """WARN on bare generic CSS class names without prefix."""
    css_path = find_stylesheet(ext_dir)
    if not css_path:
        result("SKIP", "css/scoping", "No stylesheet.css found")
        return

    with open(css_path, encoding='utf-8', errors='replace') as f:
        content = f.read()

    content = strip_css_comments(content)

    # Extract top-level class selectors (first class in a rule)
    classes = set()
    for m in re.finditer(r'^\s*\.([\w-]+)', content, re.MULTILINE):
        classes.add(m.group(1))

    unscoped = []
    for cls in sorted(classes):
        # "Scoped" means contains hyphen or underscore (namespace prefix)
        if '-' not in cls and '_' not in cls:
            # Skip known GNOME Shell theme classes
            if cls.lower() not in KNOWN_SHELL_CLASSES:
                unscoped.append(cls)

    if unscoped:
        names = ', '.join(f'.{c}' for c in unscoped[:5])
        result("WARN", "css/unscoped-class",
               f"Found {len(unscoped)} potentially unscoped CSS class(es): "
               f"{names} — add a namespace prefix to avoid conflicts")
    else:
        result("PASS", "css/scoping", "CSS classes appear properly scoped")


def check_important_usage(ext_dir):
    """WARN on !important usage in stylesheet."""
    css_path = find_stylesheet(ext_dir)
    if not css_path:
        return

    with open(css_path, encoding='utf-8', errors='replace') as f:
        content = f.read()

    content = strip_css_comments(content)
    count = len(re.findall(r'!important', content))

    if count > 0:
        result("WARN", "css/important",
               f"Found {count} !important usage(s) in stylesheet.css — "
               f"!important overrides Shell theme; prefer higher specificity")
    else:
        result("PASS", "css/important", "No !important usage")


def check_shell_class_override(ext_dir):
    """WARN when a KNOWN_SHELL_CLASSES member appears as a top-level selector."""
    css_path = find_stylesheet(ext_dir)
    if not css_path:
        result("SKIP", "css/shell-class-override", "No stylesheet.css found")
        return

    with open(css_path, encoding='utf-8', errors='replace') as f:
        content = f.read()

    content = strip_css_comments(content)

    overrides = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('}'):
            continue
        # A top-level match: the first class selector on the line is a known
        # shell class (no preceding class/id/element selector that would scope it).
        # e.g. ".panel-button { ..." — bare shell class override
        # but NOT ".my-extension .panel-button { ..." (descendant scoping)
        # and NOT ".panel-button.my-ext-class { ..." (compound scoping)
        m = re.match(r'^\.([\w-]+)(.*)', stripped)
        if m:
            cls = m.group(1)
            rest = m.group(2)
            if cls in KNOWN_SHELL_CLASSES:
                # Skip compound selectors where shell class is paired with
                # a non-shell class (e.g. .quick-menu-toggle.my-ext-toggle)
                compound = re.match(r'^\.([\w-]+)', rest)
                if compound and compound.group(1) not in KNOWN_SHELL_CLASSES:
                    continue
                overrides.append(cls)

    if overrides:
        seen = []
        for cls in overrides:
            if cls not in seen:
                seen.append(cls)
        for cls in seen:
            result("FAIL", "css/shell-class-override",
                   f".{cls}: overrides GNOME Shell theme class "
                   f"— use a scoped selector (.my-extension .{cls})")
    else:
        result("PASS", "css/shell-class-override",
               "No unscoped GNOME Shell theme class overrides")


def main():
    if len(sys.argv) < 2:
        result("FAIL", "css/args", "No extension directory provided")
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])
    check_unscoped_classes(ext_dir)
    check_important_usage(ext_dir)
    check_shell_class_override(ext_dir)


if __name__ == '__main__':
    main()
