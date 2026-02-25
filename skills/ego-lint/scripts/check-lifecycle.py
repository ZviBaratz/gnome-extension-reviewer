#!/usr/bin/env python3
"""check-lifecycle.py — Tier 2 lifecycle heuristics for GNOME extensions.

Usage: check-lifecycle.py EXTENSION_DIR

Checks:
  - R-LIFE-01: Signal connection/disconnection balance
  - R-LIFE-02: Untracked timeout sources
  - R-LIFE-03: Missing enable/disable methods
  - R-LIFE-04: connectObject migration advisory
  - R-LIFE-05: Async/await without _destroyed guard
  - R-LIFE-06: timeout_add/idle_add without SOURCE_REMOVE/SOURCE_CONTINUE
  - R-LIFE-07: DBus proxy creation without disconnect
  - R-LIFE-08: File monitor without cancel
  - R-LIFE-09: Keybinding add without remove
  - R-LIFE-10: InjectionManager without clear()
  - R-FILE-07: Missing export default class

Output: PIPE-delimited lines: STATUS|check-name|detail
"""

import os
import re
import sys


def result(status, check, detail):
    print(f"{status}|{check}|{detail}")


def find_js_files(ext_dir, exclude_prefs=False):
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


def read_file(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return f.read()


def strip_comments(content):
    """Remove single-line and block comments from JS content."""
    # Remove block comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Remove single-line comments
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    return content


def check_enable_disable(ext_dir):
    """R-LIFE-03: extension.js must define enable() and disable()."""
    ext_js = os.path.join(ext_dir, 'extension.js')
    if not os.path.isfile(ext_js):
        return  # file-structure check handles this

    content = strip_comments(read_file(ext_js))

    has_enable = bool(re.search(r'\benable\s*\(', content))
    has_disable = bool(re.search(r'\bdisable\s*\(', content))

    if not has_enable:
        result("FAIL", "lifecycle/enable-method", "extension.js missing enable() method")
    if not has_disable:
        result("FAIL", "lifecycle/disable-method", "extension.js missing disable() method")
    if has_enable and has_disable:
        result("PASS", "lifecycle/enable-disable", "enable() and disable() both defined")


def check_default_export(ext_dir):
    """R-FILE-07: extension.js should have export default class."""
    ext_js = os.path.join(ext_dir, 'extension.js')
    if not os.path.isfile(ext_js):
        return

    content = strip_comments(read_file(ext_js))
    if not re.search(r'\bexport\s+default\s+class\b', content):
        result("WARN", "lifecycle/default-export",
               "extension.js missing 'export default class' — required for GNOME 45+")
    else:
        result("PASS", "lifecycle/default-export", "extension.js has default export class")


def check_signal_balance(ext_dir):
    """R-LIFE-01: Signal connection/disconnection balance."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return

    pure_connects = 0
    pure_disconnects = 0
    connect_objects = 0

    for filepath in js_files:
        for line in read_file(filepath).splitlines():
            if re.search(r'\.connectObject\s*\(', line):
                connect_objects += 1
            elif re.search(r'\.connect\s*\(', line) and not re.search(r'\.disconnect', line):
                pure_connects += 1
            if re.search(r'\.disconnectObject\s*\(', line):
                pass  # auto-cleanup
            elif re.search(r'\.disconnect\s*\(', line) and not re.search(r'\.connect\s*\(', line):
                pure_disconnects += 1

    # connectObject calls auto-disconnect, so only manual connects need matching disconnects
    imbalance = pure_connects - pure_disconnects
    if imbalance > 2:
        result("WARN", "lifecycle/signal-balance",
               f"{pure_connects} manual .connect() calls but only {pure_disconnects} "
               f".disconnect() calls — verify all signals are disconnected in disable()")
    else:
        result("PASS", "lifecycle/signal-balance",
               f"Signal balance OK ({pure_connects} connects, {pure_disconnects} disconnects, "
               f"{connect_objects} connectObject)")


def check_untracked_timeouts(ext_dir):
    """R-LIFE-02: timeout_add/idle_add without stored return value."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return

    untracked = []
    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        for lineno, line in enumerate(read_file(filepath).splitlines(), 1):
            stripped = line.strip()
            # Skip comments
            if stripped.startswith('//') or stripped.startswith('*'):
                continue
            # Match timeout_add or idle_add calls
            if re.search(r'(timeout_add|idle_add)\s*\(', stripped):
                # Check if the return value is assigned
                if not re.search(r'(=|return)\s*.*(timeout_add|idle_add)', stripped):
                    untracked.append(f"{rel}:{lineno}")

    if untracked:
        for loc in untracked:
            result("WARN", "lifecycle/untracked-timeout",
                   f"{loc}: timeout_add/idle_add return value not stored — "
                   f"cannot be removed in disable()")
    else:
        result("PASS", "lifecycle/untracked-timeout",
               "All timeout/idle sources have stored IDs")


def check_connect_object_migration(ext_dir):
    """R-LIFE-04: Suggest connectObject when 3+ manual connect/disconnect pairs."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return

    manual_pairs = 0
    has_connect_object = False

    for filepath in js_files:
        content = read_file(filepath)
        if re.search(r'\.connectObject\s*\(', content):
            has_connect_object = True
        # Count lines that store a connect ID
        manual_pairs += len(re.findall(
            r'=\s*\w+\.connect\s*\(', content
        ))

    if manual_pairs >= 3 and not has_connect_object:
        result("WARN", "lifecycle/connectObject-migration",
               f"{manual_pairs} manual signal connections found — "
               f"consider using connectObject() for automatic cleanup")
    else:
        result("PASS", "lifecycle/connectObject-migration",
               "Signal connection pattern OK")


def check_async_destroyed_guard(ext_dir):
    """R-LIFE-05: Async functions with await should check _destroyed after resuming."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return

    has_async_await = False
    has_destroyed_flag = False

    for filepath in js_files:
        content = strip_comments(read_file(filepath))
        if re.search(r'\basync\b', content) and re.search(r'\bawait\b', content):
            has_async_await = True
        if re.search(r'\b_destroyed\b', content) or re.search(r'\b_isDestroyed\b', content):
            has_destroyed_flag = True

    if has_async_await and not has_destroyed_flag:
        result("WARN", "lifecycle/async-destroyed-guard",
               "async/await used without _destroyed or _isDestroyed guard — "
               "extension may act on stale state after disable()")
    elif has_async_await and has_destroyed_flag:
        result("PASS", "lifecycle/async-destroyed-guard",
               "async/await with _destroyed guard detected")
    # If no async/await, skip silently


def check_timeout_return_value(ext_dir):
    """R-LIFE-06: timeout_add/idle_add callbacks should return SOURCE_REMOVE or SOURCE_CONTINUE."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return

    missing = []
    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        lines = read_file(filepath).splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Skip comments
            if stripped.startswith('//') or stripped.startswith('*'):
                continue
            if re.search(r'(timeout_add|idle_add)\s*\(', stripped):
                # Look ahead up to 20 lines for SOURCE_REMOVE or SOURCE_CONTINUE
                lookahead = '\n'.join(lines[i:i + 20])
                if 'SOURCE_REMOVE' not in lookahead and 'SOURCE_CONTINUE' not in lookahead:
                    missing.append(f"{rel}:{i + 1}")
                    if len(missing) >= 3:
                        break
        if len(missing) >= 3:
            break

    if missing:
        locs = ', '.join(missing)
        result("WARN", "lifecycle/timeout-return-value",
               f"timeout_add/idle_add callback missing SOURCE_REMOVE/SOURCE_CONTINUE: {locs}")
    else:
        result("PASS", "lifecycle/timeout-return-value",
               "All timeout/idle callbacks return SOURCE_REMOVE or SOURCE_CONTINUE")


def check_keybinding_cleanup(ext_dir):
    """R-LIFE-09: addKeybinding must have matching removeKeybinding."""
    js_files = find_js_files(ext_dir)
    if not js_files:
        return

    add_count = 0
    remove_count = 0

    for filepath in js_files:
        content = strip_comments(read_file(filepath))
        add_count += len(re.findall(r'\.addKeybinding\s*\(', content))
        remove_count += len(re.findall(r'\.removeKeybinding\s*\(', content))

    if add_count > 0 and remove_count == 0:
        result("FAIL", "lifecycle/keybinding-cleanup",
               f"{add_count} addKeybinding() call(s) but no removeKeybinding() — "
               f"keybindings will leak after disable()")
    elif add_count > 0 and remove_count > 0:
        result("PASS", "lifecycle/keybinding-cleanup",
               f"Keybinding balance OK ({add_count} add, {remove_count} remove)")
    # If no keybindings, skip silently


def check_dbus_proxy_lifecycle(ext_dir):
    """R-LIFE-07: DBus proxy creation should have matching disconnect."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return

    has_proxy = False
    has_disconnect = False

    for filepath in js_files:
        content = strip_comments(read_file(filepath))
        if (re.search(r'Gio\.DBusProxy\.new_for_bus', content) or
                re.search(r'new\s+Gio\.DBusProxy', content) or
                re.search(r'makeProxyWrapper', content)):
            has_proxy = True
        if re.search(r'disconnectObject', content) or re.search(r'\.disconnect\s*\(', content):
            has_disconnect = True

    if has_proxy and not has_disconnect:
        result("WARN", "lifecycle/dbus-proxy-cleanup",
               "DBus proxy created but no disconnect/disconnectObject found — "
               "signals may leak after disable()")
    elif has_proxy and has_disconnect:
        result("PASS", "lifecycle/dbus-proxy-cleanup",
               "DBus proxy with disconnect pattern detected")
    # If no proxy, skip silently


def check_file_monitor_lifecycle(ext_dir):
    """R-LIFE-08: File monitors should be cancelled in disable()."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return

    has_monitor = False
    has_cancel = False

    for filepath in js_files:
        content = strip_comments(read_file(filepath))
        if (re.search(r'\.monitor_file\s*\(', content) or
                re.search(r'\.monitor_directory\s*\(', content) or
                re.search(r'\.monitor_children\s*\(', content)):
            has_monitor = True
        if re.search(r'\.cancel\s*\(', content):
            has_cancel = True

    if has_monitor and not has_cancel:
        result("WARN", "lifecycle/file-monitor-cleanup",
               "File monitor created but no .cancel() found — "
               "monitor will continue after disable()")
    elif has_monitor and has_cancel:
        result("PASS", "lifecycle/file-monitor-cleanup",
               "File monitor with cancel pattern detected")
    # If no monitors, skip silently


def check_injection_manager(ext_dir):
    """R-LIFE-10: InjectionManager must be cleared in disable()."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return

    has_injection = False
    has_clear = False

    for filepath in js_files:
        content = strip_comments(read_file(filepath))
        if re.search(r'new\s+InjectionManager\s*\(', content):
            has_injection = True
        if re.search(r'\.clear\s*\(', content):
            has_clear = True

    if has_injection and not has_clear:
        result("FAIL", "lifecycle/injection-cleanup",
               "new InjectionManager() found but no .clear() call — "
               "injections will persist after disable()")
    elif has_injection and has_clear:
        result("PASS", "lifecycle/injection-cleanup",
               "InjectionManager with .clear() cleanup detected")


def main():
    if len(sys.argv) < 2:
        result("FAIL", "lifecycle/args", "No extension directory provided")
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])

    check_enable_disable(ext_dir)
    check_default_export(ext_dir)
    check_signal_balance(ext_dir)
    check_untracked_timeouts(ext_dir)
    check_connect_object_migration(ext_dir)
    check_async_destroyed_guard(ext_dir)
    check_timeout_return_value(ext_dir)
    check_keybinding_cleanup(ext_dir)
    check_dbus_proxy_lifecycle(ext_dir)
    check_file_monitor_lifecycle(ext_dir)
    check_injection_manager(ext_dir)


if __name__ == '__main__':
    main()
