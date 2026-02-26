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
    """Find all JS files in extension directory, excluding node_modules."""
    skip_dirs = {'node_modules', '.git', '__pycache__'}
    files = []
    for root, dirs, filenames in os.walk(ext_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
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
            elif (re.search(r'\b(async\s+)?\w+\s*\([^)]*\)\s*\{', line) and
                  not re.search(r'\b(if|else|for|while|switch|catch|do)\b', line)):
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


def check_destroyed_density(ext_dir, js_files):
    """R-QUAL-06: Flag excessive _destroyed/_pendingDestroy/_initializing checks."""
    patterns = ['_destroyed', '_pendingDestroy', '_initializing']
    total_occurrences = 0
    total_lines = 0
    file_counts = {}

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        non_blank = sum(1 for l in lines if l.strip())
        total_lines += non_blank
        count = 0
        for line in lines:
            for pat in patterns:
                count += line.count(pat)
        if count > 0:
            file_counts[rel] = count
        total_occurrences += count

    if total_occurrences >= 10 and total_lines > 0:
        ratio = total_occurrences / total_lines
        if ratio > 0.02:
            files_summary = ', '.join(
                f"{f}({c})" for f, c in sorted(
                    file_counts.items(), key=lambda x: -x[1]
                )[:3]
            )
            result("WARN", "quality/destroyed-density",
                   f"{total_occurrences} _destroyed/_pendingDestroy/_initializing "
                   f"checks across {len(file_counts)} files "
                   f"(ratio: {ratio:.3f}) — top: {files_summary}")
            return

    result("PASS", "quality/destroyed-density",
           f"Destroyed-flag density acceptable "
           f"({total_occurrences} in {total_lines} lines)")


def check_mock_in_production(ext_dir, js_files):
    """R-QUAL-07: Flag mock/test code shipped in production."""
    mock_files = []
    mock_triggers = []

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        basename = os.path.basename(filepath)

        # Check filename patterns (case-insensitive)
        lower = basename.lower()
        if (lower.startswith('mock') or lower.startswith('test') or
                lower.startswith('spec') or lower.endswith('.test.js') or
                lower.endswith('.spec.js')):
            mock_files.append(rel)

        # Check for runtime mock triggers
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for lineno, line in enumerate(f, 1):
                if re.search(r'use_mock|mock_trigger|MOCK_MODE|\.mock\b', line,
                             re.IGNORECASE):
                    mock_triggers.append(f"{rel}:{lineno}")

    found = False
    for mf in mock_files:
        result("WARN", "quality/mock-in-production",
               f"{mf}: mock/test file should not ship in production extension")
        found = True
    for mt in mock_triggers:
        result("WARN", "quality/mock-in-production",
               f"{mt}: runtime mock trigger detected — remove for production")
        found = True

    if not found:
        result("PASS", "quality/mock-in-production",
               "No mock/test code detected in production files")


def check_constructor_resources(ext_dir, js_files):
    """R-QUAL-08: Flag resource allocation inside constructors.

    Skip for GObject widget subclasses — their constructors run within the
    enable/disable lifecycle, so signal connections there are acceptable.
    """
    bad_patterns = [
        (r'this\.getSettings\s*\(', 'this.getSettings()'),
        (r'\.connect\s*\(', '.connect()'),
        (r'\.connectObject\s*\(', '.connectObject()'),
        (r'timeout_add', 'GLib.timeout_add()'),
        (r'new\s+Gio\.DBusProxy', 'new Gio.DBusProxy()'),
    ]

    # GObject widget base classes whose constructors are lifecycle-bounded
    widget_bases = {
        'St.Widget', 'St.BoxLayout', 'St.Button', 'St.Label', 'St.Bin',
        'St.Icon', 'St.Entry', 'St.ScrollView', 'St.Viewport',
        'Clutter.Actor', 'Clutter.LayoutManager',
        'GObject.Object',
        'QuickToggle', 'QuickMenuToggle', 'QuickSlider',
        'SystemIndicator',
        'PanelMenu.Button', 'PanelMenu.ButtonBox',
        'PopupMenu.PopupBaseMenuItem', 'PopupMenu.PopupMenuItem',
        'PopupMenu.PopupSwitchMenuItem', 'PopupMenu.PopupSubMenuMenuItem',
        'Adw.PreferencesPage', 'Adw.PreferencesGroup',
        'Gtk.Widget', 'Gtk.Box', 'Gtk.Button',
    }
    # Also match just the short names (e.g., "BoxLayout" from "St.BoxLayout")
    widget_short_names = {b.split('.')[-1] for b in widget_bases}

    found = False

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Find constructor/_init bodies (rough heuristic)
        for m in re.finditer(
            r'(?:constructor|_init)\s*\([^)]*\)\s*\{', content
        ):
            # Determine which class this constructor belongs to
            # by finding the nearest class declaration before this position
            is_widget = False
            last_base = None
            for cm in re.finditer(r'class\s+(\w+)\s+extends\s+([\w.]+)', content):
                if cm.start() < m.start():
                    last_base = cm.group(2)

            if last_base and (last_base in widget_bases or
                              last_base.split('.')[-1] in widget_short_names):
                is_widget = True

            if is_widget:
                continue  # Skip widget constructors

            # Extract the constructor body (find matching brace)
            start = m.end()
            depth = 1
            pos = start
            while pos < len(content) and depth > 0:
                if content[pos] == '{':
                    depth += 1
                elif content[pos] == '}':
                    depth -= 1
                pos += 1
            body = content[start:pos - 1]
            body_start_line = content[:m.start()].count('\n') + 1

            for pat, name in bad_patterns:
                for hit in re.finditer(pat, body):
                    hit_line = body_start_line + body[:hit.start()].count('\n') + 1
                    result("WARN", "quality/constructor-resources",
                           f"{rel}:{hit_line}: {name} in constructor — "
                           f"move to enable()")
                    found = True

    if not found:
        result("PASS", "quality/constructor-resources",
               "No resource allocation in constructors")


def check_code_volume(ext_dir, js_files):
    """R-QUAL-10: Flag large codebases that are harder to review."""
    total_lines = 0
    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for line in f:
                if line.strip():
                    total_lines += 1

    if total_lines > 8000:
        result("WARN", "quality/code-volume",
               f"{total_lines} non-blank JS lines — large codebase; "
               f"ensure all code is necessary and manually reviewed")
    else:
        result("PASS", "quality/code-volume",
               f"Code volume OK ({total_lines} non-blank lines)")


def check_file_complexity(ext_dir, js_files):
    """R-QUAL-12: Flag individual files with excessive non-blank lines."""
    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            count = sum(1 for line in f if line.strip())
        if count > 1000:
            result("WARN", "quality/file-complexity",
                   f"{rel}: {count} non-blank lines — consider splitting into modules")
            return

    result("PASS", "quality/file-complexity",
           "No individual files exceed 1000 non-blank lines")


def check_debug_volume(ext_dir, js_files):
    """R-QUAL-13: Flag excessive console.debug() calls."""
    total = 0
    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for line in f:
                stripped = line.lstrip()
                if stripped.startswith('//') or stripped.startswith('*'):
                    continue
                total += len(re.findall(r'console\.debug\(', line))

    if total > 15:
        result("WARN", "quality/debug-volume",
               f"{total} console.debug() calls — excessive for production; "
               f"remove or reduce debug logging before submission")
    else:
        result("PASS", "quality/debug-volume",
               f"Debug logging volume OK ({total} calls)")


def check_logging_volume(ext_dir, js_files):
    """R-QUAL-17: Flag excessive total console.* calls."""
    total = 0
    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for line in f:
                stripped = line.lstrip()
                if stripped.startswith('//') or stripped.startswith('*'):
                    continue
                # console.log excluded — already a hard FAIL in ego-lint.sh
                total += len(re.findall(
                    r'console\.(debug|warn|error|info)\(', line))

    if total > 30:
        result("WARN", "quality/logging-volume",
               f"{total} total console.* calls — excessive logging may cause "
               f"rejection; keep only essential error/warning messages")
    else:
        result("PASS", "quality/logging-volume",
               f"Total logging volume OK ({total} calls)")


def check_notification_volume(ext_dir, js_files):
    """R-QUAL-14: Flag excessive Main.notify() calls."""
    total = 0
    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for line in f:
                stripped = line.lstrip()
                if stripped.startswith('//') or stripped.startswith('*'):
                    continue
                total += len(re.findall(r'Main\.notify\s*\(', line))

    if total > 3:
        result("WARN", "quality/notification-volume",
               f"{total} Main.notify() call sites — reviewers consider excessive "
               f"notifications a rejection risk; keep 2-3 essential (errors, one-time setup)")
    else:
        result("PASS", "quality/notification-volume",
               f"Notification volume OK ({total} call sites)")


def check_private_api(ext_dir, js_files):
    """R-QUAL-15: Flag access to private underscore-prefixed GNOME Shell APIs."""
    patterns = [
        (r'Main\.panel[^;]*\._\w+', 'Main.panel private API access'),
        (r'statusArea[^;]*\._\w+', 'statusArea private API access'),
        (r'quickSettings[^;]*\._\w+', 'quickSettings private API access'),
        (r'Main\.overview[^;]*\._\w+', 'Main.overview private API access'),
        (r'Main\.layoutManager[^;]*\._\w+', 'Main.layoutManager private API access'),
        (r'Main\.wm[^;]*\._\w+', 'Main.wm private API access'),
    ]
    matches = []

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for lineno, line in enumerate(f, 1):
                stripped = line.lstrip()
                if stripped.startswith('//') or stripped.startswith('*'):
                    continue
                for pat, desc in patterns:
                    if re.search(pat, line):
                        matches.append((rel, lineno, desc))

    if matches:
        for rel, lineno, desc in matches[:5]:
            result("WARN", "quality/private-api",
                   f"{rel}:{lineno}: {desc} — requires reviewer justification "
                   f"and version pinning")
        remaining = len(matches) - 5
        if remaining > 0:
            result("WARN", "quality/private-api",
                   f"...and {remaining} more private API access(es)")
    else:
        result("PASS", "quality/private-api",
               "No private GNOME Shell API access detected")


def check_gettext_pattern(ext_dir, js_files):
    """R-QUAL-16: Flag direct Gettext.dgettext() usage."""
    locations = []

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for lineno, line in enumerate(f, 1):
                stripped = line.lstrip()
                if stripped.startswith('//') or stripped.startswith('*'):
                    continue
                if re.search(r'Gettext\.dgettext\s*\(', line):
                    locations.append(f"{rel}:{lineno}")

    if locations:
        locs = ', '.join(locations[:5])
        result("WARN", "quality/gettext-pattern",
               f"Uses Gettext.dgettext() directly ({locs}) — "
               f"prefer this.gettext() from Extension/ExtensionPreferences base class")
    else:
        result("PASS", "quality/gettext-pattern",
               "Gettext usage follows recommended pattern")


def check_comment_density(ext_dir, js_files):
    """R-QUAL-11: Flag excessive comment-to-code ratio."""
    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        if len(lines) < 50:
            continue

        # Skip license header (first 10 lines)
        check_lines = lines[10:]
        comment_lines = 0
        code_lines = 0
        in_block_comment = False

        for line in check_lines:
            stripped = line.strip()
            if not stripped:
                continue
            if in_block_comment:
                comment_lines += 1
                if '*/' in stripped:
                    in_block_comment = False
                continue
            if stripped.startswith('/*'):
                comment_lines += 1
                if '*/' not in stripped:
                    in_block_comment = True
                continue
            if stripped.startswith('//') or stripped.startswith('*'):
                comment_lines += 1
            else:
                code_lines += 1

        total = comment_lines + code_lines
        if total > 0 and comment_lines / total > 0.4:
            result("WARN", "quality/comment-density",
                   f"{rel}: {comment_lines}/{total} lines are comments "
                   f"({comment_lines * 100 // total}%) — may indicate AI-generated verbose comments")
            return  # one warning is enough

    result("PASS", "quality/comment-density", "Comment density acceptable")


def check_redundant_cleanup(ext_dir, js_files):
    """R-QUAL-18: Flag verbose destroy/cleanup vs idiomatic optional chaining."""
    verbose_count = 0
    idiomatic_count = 0

    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Verbose pattern: if (this._x) { this._x.destroy(); this._x = null; }
        verbose_count += len(re.findall(
            r'if\s*\(this\._\w+\)\s*\{[^}]*\.destroy\(\)', content))

        # Idiomatic pattern: this._x?.destroy()
        idiomatic_count += len(re.findall(r'\?\.\s*destroy\s*\(', content))

    total = verbose_count + idiomatic_count
    if total >= 4 and verbose_count / max(total, 1) > 0.6:
        result("WARN", "quality/redundant-cleanup",
               f"{verbose_count} verbose destroy guards vs {idiomatic_count} idiomatic "
               f"'?.destroy()' — prefer optional chaining for cleanup")
    else:
        result("PASS", "quality/redundant-cleanup",
               f"Cleanup pattern balance OK (verbose: {verbose_count}, idiomatic: {idiomatic_count})")


def check_comment_prompt_density(ext_dir, js_files):
    """R-QUAL-19: Flag imperative instructional comments (LLM prompt style)."""
    prompt_re = re.compile(
        r'//\s*(Important|Note|Remember|TODO|FIXME):\s*'
        r'(Make sure|Ensure|Always|Don\'t forget|Handle|Never|Check|Verify)',
        re.IGNORECASE
    )

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        count = 0
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for line in f:
                if prompt_re.search(line):
                    count += 1

        if count > 5:
            result("WARN", "quality/comment-prompt-density",
                   f"{rel}: {count} imperative instructional comments — "
                   f"reads like LLM prompts; explain 'why' not 'what to do'")
            return

    result("PASS", "quality/comment-prompt-density",
           "No excessive instructional comment patterns")


def check_run_dispose_comment(ext_dir, js_files):
    """R-QUAL-21: Flag run_dispose() calls without an explanatory comment."""
    found_without_comment = []

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if '.run_dispose()' not in line:
                continue
            # Check if the current line has an inline comment
            if '//' in line:
                continue
            # Check if the preceding line has a comment
            if i > 0 and lines[i - 1].lstrip().startswith('//'):
                continue
            found_without_comment.append(f"{rel}:{i + 1}")

    if found_without_comment:
        for loc in found_without_comment:
            result("WARN", "quality/run-dispose-no-comment",
                   f"{loc}: run_dispose() without explanatory comment "
                   f"— reviewers require justification")
    else:
        result("PASS", "quality/run-dispose-no-comment",
               "All run_dispose() calls have comments or none found")


def check_clipboard_disclosure(ext_dir, js_files):
    """R-QUAL-22: Flag clipboard usage not mentioned in metadata description."""
    uses_clipboard = False

    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for line in f:
                if 'St.Clipboard' in line:
                    uses_clipboard = True
                    break
        if uses_clipboard:
            break

    if not uses_clipboard:
        result("PASS", "quality/clipboard-disclosure",
               "No St.Clipboard usage detected")
        return

    meta_path = os.path.join(ext_dir, 'metadata.json')
    if not os.path.isfile(meta_path):
        result("WARN", "quality/clipboard-disclosure",
               "St.Clipboard used but metadata.json not found")
        return

    try:
        with open(meta_path) as f:
            meta = json.load(f)
    except (json.JSONDecodeError, OSError):
        result("WARN", "quality/clipboard-disclosure",
               "St.Clipboard used but metadata.json could not be read")
        return

    description = meta.get('description', '')
    if 'clipboard' in description.lower():
        result("PASS", "quality/clipboard-disclosure",
               "St.Clipboard usage disclosed in metadata description")
    else:
        result("WARN", "quality/clipboard-disclosure",
               "St.Clipboard used but metadata description does not "
               "mention clipboard access")


def check_error_message_verbosity(ext_dir, js_files):
    """R-QUAL-20: Flag overly verbose error message strings."""
    lengths = []

    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for line in f:
                stripped = line.lstrip()
                if stripped.startswith('//') or stripped.startswith('*'):
                    continue
                # Find console.error/warn string arguments
                for m in re.finditer(
                    r'console\.(error|warn)\s*\([\'"`]([^\'"`]*)[\'"`]', line
                ):
                    msg = m.group(2)
                    if len(msg) > 10:  # skip trivially short messages
                        lengths.append(len(msg))

    if len(lengths) >= 3:
        avg = sum(lengths) / len(lengths)
        if avg > 50:
            result("WARN", "quality/error-message-verbosity",
                   f"{len(lengths)} error/warn messages with avg length {avg:.0f} chars — "
                   f"prefer terse error strings")
            return

    result("PASS", "quality/error-message-verbosity",
           "Error message verbosity acceptable")


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
    check_destroyed_density(ext_dir, js_files)
    check_mock_in_production(ext_dir, js_files)
    check_constructor_resources(ext_dir, js_files)
    check_code_volume(ext_dir, js_files)
    check_comment_density(ext_dir, js_files)
    check_file_complexity(ext_dir, js_files)
    check_debug_volume(ext_dir, js_files)
    check_logging_volume(ext_dir, js_files)
    check_notification_volume(ext_dir, js_files)
    check_private_api(ext_dir, js_files)
    check_gettext_pattern(ext_dir, js_files)
    check_redundant_cleanup(ext_dir, js_files)
    check_comment_prompt_density(ext_dir, js_files)
    check_error_message_verbosity(ext_dir, js_files)
    check_run_dispose_comment(ext_dir, js_files)
    check_clipboard_disclosure(ext_dir, js_files)


if __name__ == '__main__':
    main()
