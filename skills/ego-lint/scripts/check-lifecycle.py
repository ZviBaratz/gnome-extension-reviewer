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
  - R-LIFE-10: InjectionManager without clear() + prototype override detection
  - R-LIFE-11: Lock screen signal safety
  - R-LIFE-12: Stored timeout/idle ID without Source.remove() in disable()
  - R-LIFE-13: Selective disable() detection (conditional return skips cleanup)
  - R-LIFE-14: unlock-dialog comment requirement
  - R-LIFE-15: Soup.Session without abort() in disable/destroy
  - R-LIFE-16: DBus export without unexport in disable/destroy
  - R-LIFE-17: Timeout ID reassignment without prior Source.remove()
  - R-LIFE-18: Subprocess without cancellation in disable/destroy
  - R-SEC-16: Clipboard + keybinding cross-reference
  - R-FILE-07: Missing export default class

Output: PIPE-delimited lines: STATUS|check-name|detail
"""

import json
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
    """R-LIFE-10: InjectionManager must be cleared in disable().
    Also detects direct prototype overrides (WS1-D enhancement)."""
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

    # WS1-D: Detect direct prototype overrides
    prototype_overrides = []
    for filepath in js_files:
        content = strip_comments(read_file(filepath))
        rel = os.path.relpath(filepath, ext_dir)
        # SomeClass.prototype.methodName = ...
        for m in re.finditer(r'(\w+\.prototype\.\w+)\s*=', content):
            prototype_overrides.append((rel, m.group(1)))
        # Object.assign(SomeClass.prototype, ...)
        for m in re.finditer(r'Object\.assign\s*\(\s*(\w+\.prototype)', content):
            prototype_overrides.append((rel, f"Object.assign({m.group(1)}, ...)"))

    if prototype_overrides:
        # Check if disable() restores prototypes
        ext_js = os.path.join(ext_dir, 'extension.js')
        disable_restores = False
        if os.path.isfile(ext_js):
            ext_content = strip_comments(read_file(ext_js))
            disable_match = re.search(r'\bdisable\s*\(\s*\)\s*\{', ext_content)
            if disable_match:
                start = disable_match.end()
                depth = 1
                pos = start
                while pos < len(ext_content) and depth > 0:
                    if ext_content[pos] == '{':
                        depth += 1
                    elif ext_content[pos] == '}':
                        depth -= 1
                    pos += 1
                disable_body = ext_content[start:pos]
                # Check for prototype restoration in disable
                if re.search(r'\w+\.prototype\.\w+\s*=', disable_body):
                    disable_restores = True

        if not disable_restores:
            for rel, override in prototype_overrides:
                result("WARN", "lifecycle/prototype-override",
                       f"{rel}: {override} — direct prototype modification "
                       f"should be restored in disable()")


def check_selective_disable(ext_dir):
    """R-LIFE-13: Detect conditional returns in disable() that skip cleanup."""
    ext_js = os.path.join(ext_dir, 'extension.js')
    if not os.path.isfile(ext_js):
        return

    content = strip_comments(read_file(ext_js))

    # Extract disable() body using brace depth
    disable_match = re.search(r'\bdisable\s*\(\s*\)\s*\{', content)
    if not disable_match:
        return

    start = disable_match.end()
    depth = 1
    pos = start
    while pos < len(content) and depth > 0:
        if content[pos] == '{':
            depth += 1
        elif content[pos] == '}':
            depth -= 1
        pos += 1
    disable_body = content[start:pos]

    # Look for early returns that skip cleanup: `if (...) return;`
    # But exclude legitimate null guards like `if (this._x) { this._x.destroy(); }`
    # and `if (!this._x) return;` (null guard for a single resource)
    early_return_patterns = re.finditer(
        r'if\s*\(([^)]+)\)\s*return\s*;', disable_body
    )

    for m in early_return_patterns:
        condition = m.group(1).strip()

        # Exclude null guards: `if (!this._x)` — these protect a single destroy
        if re.match(r'^!\s*this\._\w+$', condition):
            continue

        # Flag session mode / enabled state checks that skip all cleanup
        result("FAIL", "lifecycle/selective-disable",
               f"disable() has conditional return: 'if ({condition}) return;' — "
               f"disable() must always clean up all resources regardless of state")
        return  # Report once

    result("PASS", "lifecycle/selective-disable",
           "disable() does not conditionally skip cleanup")


def check_unlock_dialog_comment(ext_dir):
    """R-LIFE-14: unlock-dialog session mode should have explanatory comment in disable()."""
    metadata_path = os.path.join(ext_dir, 'metadata.json')
    if not os.path.isfile(metadata_path):
        return

    try:
        with open(metadata_path, encoding='utf-8') as f:
            metadata = json.load(f)
    except (json.JSONDecodeError, OSError):
        return

    session_modes = metadata.get('session-modes', [])
    if 'unlock-dialog' not in session_modes:
        return  # Not relevant

    ext_js = os.path.join(ext_dir, 'extension.js')
    if not os.path.isfile(ext_js):
        return

    # Read raw content (not stripped) to preserve comments
    raw_content = read_file(ext_js)

    # Extract disable() body from raw content
    disable_match = re.search(r'\bdisable\s*\(\s*\)\s*\{', raw_content)
    if not disable_match:
        return

    start = disable_match.end()
    depth = 1
    pos = start
    while pos < len(raw_content) and depth > 0:
        if raw_content[pos] == '{':
            depth += 1
        elif raw_content[pos] == '}':
            depth -= 1
        pos += 1
    disable_body = raw_content[start:pos]

    # Look for comments mentioning unlock/lock/session/mode
    comment_keywords = re.search(
        r'//.*\b(unlock|lock|session|mode)\b', disable_body, re.IGNORECASE
    )

    if not comment_keywords:
        result("WARN", "lifecycle/unlock-dialog-comment",
               "extension declares 'unlock-dialog' session mode but disable() has no "
               "comment explaining lock screen behavior — add a comment documenting "
               "which resources need special handling on the lock screen")
    else:
        result("PASS", "lifecycle/unlock-dialog-comment",
               "disable() has comment documenting lock screen behavior")


def check_clipboard_keybinding(ext_dir):
    """R-SEC-16: Clipboard access combined with keybinding registration is suspicious."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return

    for filepath in js_files:
        content = strip_comments(read_file(filepath))
        rel = os.path.relpath(filepath, ext_dir)

        has_clipboard = bool(re.search(r'St\.Clipboard', content))
        has_keybinding = bool(re.search(r'addKeybinding', content))

        if has_clipboard and has_keybinding:
            result("WARN", "lifecycle/clipboard-keybinding",
                   f"{rel}: St.Clipboard and addKeybinding() in same file — "
                   f"review whether keybinding-triggered clipboard access is intended "
                   f"and not a keylogger pattern")
            return  # Report once

    # No co-occurrence found, skip silently


def check_lockscreen_signals(ext_dir):
    """R-LIFE-11: Lock screen signal safety — keyboard signals with unlock-dialog mode."""
    metadata_path = os.path.join(ext_dir, 'metadata.json')
    if not os.path.isfile(metadata_path):
        return

    try:
        with open(metadata_path, encoding='utf-8') as f:
            metadata = json.load(f)
    except (json.JSONDecodeError, OSError):
        return

    session_modes = metadata.get('session-modes', [])
    if 'unlock-dialog' not in session_modes:
        return  # Not relevant if extension doesn't run on lock screen

    js_files = find_js_files(ext_dir, exclude_prefs=True)
    keyboard_signals = ['key-press-event', 'key-release-event', 'captured-event']

    for filepath in js_files:
        content = strip_comments(read_file(filepath))
        rel = os.path.relpath(filepath, ext_dir)

        has_keyboard_signal = False
        for sig in keyboard_signals:
            if sig in content:
                has_keyboard_signal = True
                break

        if has_keyboard_signal:
            # Check for session mode guard
            has_guard = bool(
                re.search(r'(currentMode|sessionMode|unlock-dialog|session-modes)', content)
            )
            if not has_guard:
                result("FAIL", "lifecycle/lockscreen-signals",
                       f"{rel}: keyboard signal connected but session-modes includes "
                       f"'unlock-dialog' — must disconnect or guard keyboard signals on lock screen")
            else:
                result("PASS", "lifecycle/lockscreen-signals",
                       f"{rel}: keyboard signal with session mode guard detected")
            return  # Only report once

    # Has unlock-dialog mode but no keyboard signals — that's fine


def check_timeout_removal_in_disable(ext_dir):
    """R-LIFE-12: Stored timeout IDs should have Source.remove() in disable()."""
    ext_js = os.path.join(ext_dir, 'extension.js')
    if not os.path.isfile(ext_js):
        return

    content = strip_comments(read_file(ext_js))

    # Find stored timeout IDs: this._foo = ...timeout_add... or this._foo = ...idle_add...
    stored_ids = set()
    for m in re.finditer(r'this\.(_\w+)\s*=\s*.*?(timeout_add|idle_add)', content):
        stored_ids.add(m.group(1))

    if not stored_ids:
        return  # No stored timeouts to check

    # Extract disable() body
    disable_match = re.search(r'\bdisable\s*\(\s*\)\s*\{', content)
    if not disable_match:
        return  # check_enable_disable handles missing disable()

    # Extract body using brace depth
    start = disable_match.end()
    depth = 1
    pos = start
    while pos < len(content) and depth > 0:
        if content[pos] == '{':
            depth += 1
        elif content[pos] == '}':
            depth -= 1
        pos += 1
    disable_body = content[start:pos]

    # Check if Source.remove is called in disable() for each stored ID
    has_remove = bool(re.search(r'(Source\.remove|source_remove)\s*\(', disable_body))

    missing = []
    for var_name in stored_ids:
        # Check if this specific ID is passed to Source.remove() or if there's a general remove
        var_removed = bool(re.search(
            rf'(Source\.remove|source_remove)\s*\(\s*this\.{re.escape(var_name)}',
            disable_body
        ))
        if not var_removed and not has_remove:
            missing.append(var_name)

    if missing:
        for var_name in sorted(missing):
            result("FAIL", "lifecycle/timeout-not-removed",
                   f"this.{var_name} stores timeout/idle source but no "
                   f"GLib.Source.remove() call found in disable()")
    else:
        result("PASS", "lifecycle/timeout-not-removed",
               "All stored timeout/idle IDs have Source.remove() in disable()")


def check_pkexec_user_writable(ext_dir):
    """R-SEC-18: pkexec target must not be user-writable."""
    js_files = find_js_files(ext_dir)
    if not js_files:
        return

    user_writable_prefixes = ['/home/', '/tmp/', './', '../']

    for filepath in js_files:
        content = strip_comments(read_file(filepath))
        rel = os.path.relpath(filepath, ext_dir)

        # Match pkexec in argv arrays: ['pkexec', '/path/to/script']
        for m in re.finditer(
            r"""pkexec['"]\s*,\s*['"]([^'"]+)['"]""", content
        ):
            target = m.group(1)
            for prefix in user_writable_prefixes:
                if target.startswith(prefix):
                    result("FAIL", "lifecycle/pkexec-user-writable",
                           f"{rel}: pkexec target '{target}' is user-writable — "
                           f"attacker can replace it with arbitrary code")
                    return

        # Match pkexec in command strings: 'pkexec /path/to/script'
        for m in re.finditer(
            r"""['"]pkexec\s+([^'"]+)['"]""", content
        ):
            target = m.group(1).split()[0]
            for prefix in user_writable_prefixes:
                if target.startswith(prefix):
                    result("FAIL", "lifecycle/pkexec-user-writable",
                           f"{rel}: pkexec target '{target}' is user-writable — "
                           f"attacker can replace it with arbitrary code")
                    return


def check_destroy_then_null(ext_dir):
    """GAP-004: destroy() calls should be followed by null assignment."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return

    violations = []
    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        lines = read_file(filepath).splitlines()

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('*'):
                continue
            # Match this._xxx.destroy() or this._xxx?.destroy()
            m = re.search(r'(this\._\w+)\??\.\bdestroy\s*\(', stripped)
            if not m:
                continue
            prop = m.group(1)  # e.g. this._widget
            # Look ahead 5 lines for null assignment
            lookahead = '\n'.join(lines[i:i + 6])
            null_pattern = re.escape(prop) + r'\s*=\s*null\b'
            if not re.search(null_pattern, lookahead):
                violations.append(f"{rel}:{i + 1}")
                if len(violations) >= 5:
                    break
        if len(violations) >= 5:
            break

    if violations:
        for loc in violations:
            result("WARN", "lifecycle/destroy-no-null",
                   f"{loc}: .destroy() without null assignment — "
                   f"set reference to null after destroy to prevent stale access")
    else:
        result("PASS", "lifecycle/destroy-no-null",
               "All destroy() calls followed by null assignment")


def check_dbus_export_lifecycle(ext_dir):
    """GAP-003: DBus exported interfaces must be unexported in disable()/destroy()."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return

    export_patterns = [
        (r'\.export\s*\(', '.unexport('),
        (r'\.export_action_group\s*\(', 'unexport_action_group('),
        (r'\.export_menu_model\s*\(', 'unexport_menu_model('),
    ]

    exports_found = []
    all_content = ''

    for filepath in js_files:
        content = strip_comments(read_file(filepath))
        all_content += content
        rel = os.path.relpath(filepath, ext_dir)
        for export_pat, _ in export_patterns:
            # Skip ESM 'export' keyword — only match method calls on objects
            for m in re.finditer(export_pat, content):
                # Check that it's a method call (preceded by identifier or closing paren/bracket)
                start = m.start()
                if start > 0 and content[start - 1] not in (' ', '\t', '\n', ';', '{'):
                    exports_found.append((rel, export_pat))
                    break

    if not exports_found:
        return  # No DBus exports found

    # Check for matching unexports anywhere in extension code
    has_unexport = False
    for _, unexport_method in export_patterns:
        if unexport_method.replace('(', '\\s*\\(').replace('.', '\\.') and \
                re.search(re.escape(unexport_method).replace(r'\(', r'\s*\('), all_content):
            has_unexport = True
            break

    if not has_unexport:
        for rel, _ in exports_found:
            result("FAIL", "lifecycle/dbus-export-leak",
                   f"{rel}: DBus interface exported but no .unexport() found — "
                   f"exported interfaces must be unexported in disable()")
            return  # Report once
    else:
        result("PASS", "lifecycle/dbus-export-leak",
               "DBus export/unexport lifecycle OK")


def check_timeout_reassignment(ext_dir):
    """GAP-010: Timeout ID reassignment without prior Source.remove() leaks GLib sources."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return

    violations = []
    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        content = strip_comments(read_file(filepath))
        lines = content.splitlines()

        for i, line in enumerate(lines):
            # Match: this._xxx = GLib.timeout_add( or this._xxx = GLib.idle_add(
            m = re.search(r'(this\._\w+)\s*=\s*.*?(timeout_add|idle_add)\s*\(', line)
            if not m:
                continue
            prop = m.group(1)
            # Check if this property is assigned timeout/idle elsewhere too (reassignment pattern)
            assign_count = len(re.findall(
                re.escape(prop) + r'\s*=\s*.*?(timeout_add|idle_add)\s*\(',
                content
            ))
            if assign_count < 2:
                continue  # Single assignment, not a reassignment pattern
            # Look back 5 lines for Source.remove(this._xxx)
            lookback = '\n'.join(lines[max(0, i - 5):i])
            remove_pat = r'(Source\.remove|source_remove)\s*\(\s*' + re.escape(prop)
            if not re.search(remove_pat, lookback):
                violations.append(f"{rel}:{i + 1}")
                break  # One per file

    if violations:
        for loc in violations:
            result("WARN", "lifecycle/timeout-reassignment",
                   f"{loc}: timeout/idle ID reassigned without prior "
                   f"GLib.Source.remove() — may leak GLib sources")
    else:
        result("PASS", "lifecycle/timeout-reassignment",
               "No timeout ID reassignment without removal detected")


def check_subprocess_cancellation(ext_dir):
    """GAP-012: Gio.Subprocess should have cancellation in disable()/destroy()."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return

    has_subprocess = False
    has_cancel = False

    for filepath in js_files:
        content = strip_comments(read_file(filepath))
        if (re.search(r'new\s+Gio\.Subprocess', content) or
                re.search(r'Gio\.Subprocess\.new', content) or
                re.search(r'Gio\.SubprocessLauncher', content)):
            has_subprocess = True
        if (re.search(r'\.force_exit\s*\(', content) or
                re.search(r'\.send_signal\s*\(', content) or
                re.search(r'cancellable.*\.cancel\s*\(', content, re.IGNORECASE)):
            has_cancel = True

    if has_subprocess and not has_cancel:
        result("WARN", "lifecycle/subprocess-no-cancel",
               "Gio.Subprocess created but no .force_exit(), .send_signal(), or "
               "cancellable.cancel() found — subprocess may outlive disable()")
    elif has_subprocess and has_cancel:
        result("PASS", "lifecycle/subprocess-no-cancel",
               "Subprocess with cancellation pattern detected")
    # If no subprocess, skip silently


def check_soup_session_abort(ext_dir):
    """R-LIFE-15: Soup.Session should be aborted in disable()/destroy()."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return

    has_session = False
    has_abort = False

    for filepath in js_files:
        content = strip_comments(read_file(filepath))
        if (re.search(r'new\s+Soup\.Session', content) or
                re.search(r'Soup\.Session\.new', content)):
            has_session = True
        if re.search(r'\.abort\s*\(', content):
            has_abort = True

    if has_session and not has_abort:
        result("WARN", "lifecycle/soup-session-abort",
               "Soup.Session created but no .abort() found — "
               "pending requests will continue after disable()")
    elif has_session and has_abort:
        result("PASS", "lifecycle/soup-session-abort",
               "Soup.Session with .abort() cleanup detected")
    # If no session, skip silently


def main():
    if len(sys.argv) < 2:
        result("FAIL", "lifecycle/args", "No extension directory provided")
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])

    check_enable_disable(ext_dir)
    check_default_export(ext_dir)
    check_signal_balance(ext_dir)
    check_untracked_timeouts(ext_dir)
    check_timeout_removal_in_disable(ext_dir)
    check_connect_object_migration(ext_dir)
    check_async_destroyed_guard(ext_dir)
    check_timeout_return_value(ext_dir)
    check_keybinding_cleanup(ext_dir)
    check_dbus_proxy_lifecycle(ext_dir)
    check_file_monitor_lifecycle(ext_dir)
    check_injection_manager(ext_dir)
    check_lockscreen_signals(ext_dir)
    check_selective_disable(ext_dir)
    check_unlock_dialog_comment(ext_dir)
    check_clipboard_keybinding(ext_dir)
    check_pkexec_user_writable(ext_dir)
    check_dbus_export_lifecycle(ext_dir)
    check_timeout_reassignment(ext_dir)
    check_subprocess_cancellation(ext_dir)
    check_soup_session_abort(ext_dir)
    check_destroy_then_null(ext_dir)


if __name__ == '__main__':
    main()
