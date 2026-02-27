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


def is_suppressed(line, check_name, prev_line=''):
    """Check if a line is suppressed via ego-lint-ignore comment.

    Supports same-line and previous-line suppression for Tier 2 checks.
    """
    for check_line in (line, prev_line):
        if check_line and 'ego-lint-ignore' in check_line:
            m = re.search(r'ego-lint-ignore(?:-next-line)?(?::\s*(\S+))?', check_line)
            if m:
                specified = m.group(1)
                if not specified or specified == check_name:
                    return True
    return False


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
    """R-QUAL-04: Flag module-level let/var declarations.

    Suppressed when the variable is reset to null elsewhere in the file
    (developer manages cleanup).
    """
    found = []

    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = f.read()
        lines = content.splitlines()

        brace_depth = 0
        for i, line in enumerate(lines):
            # Track brace depth (rough — doesn't handle strings/comments)
            brace_depth += line.count('{') - line.count('}')

            # Module scope: brace_depth <= 0 (outside any block)
            if brace_depth <= 0:
                m = re.match(r'\s*(let|var)\s+(\w+)', line)
                if m:
                    var_name = m.group(2)
                    # Check if var is reset to null elsewhere
                    reset_re = re.compile(rf'\b{re.escape(var_name)}\s*=\s*null\b')
                    if reset_re.search(content):
                        continue  # Variable is cleaned up
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
    """R-QUAL-05: Flag empty catch blocks.

    Suppressed when:
    - Catch body contains only comments (developer acknowledged the empty catch)
    - Try body before catch contains cleanup calls (.disconnect, .cancel, .destroy,
      .close) or dynamic import() — empty catch is intentional
    """
    cleanup_re = re.compile(
        r'\.(disconnect|cancel|destroy|close)\s*\(|import\s*\('
        r'|\.(get_value|set_value|get_string|set_string|get_int|set_int'
        r'|get_boolean|set_boolean|get_double|set_double)\s*\('
    )
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
                # Check if try-body contains cleanup calls
                # Look backwards from catch to find the try block
                before_catch = content[:m.start()]
                try_match = re.search(r'\btry\s*\{([\s\S]*)\}[\s\n]*$', before_catch)
                if try_match and cleanup_re.search(try_match.group(1)):
                    continue  # Intentional cleanup — suppress

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
            content = f.read()

        # Detect try/catch guarded mock triggers (graceful degradation)
        has_try_import_guard = bool(re.search(
            r'try\s*\{[^}]*import\s*\([^}]*\}\s*catch', content, re.DOTALL))

        lines = content.splitlines()
        for lineno, line in enumerate(lines, 1):
            if re.search(r'use_mock|mock_trigger|MOCK_MODE|\.mock\b', line,
                         re.IGNORECASE):
                # Skip if file uses try/catch import guard pattern
                if has_try_import_guard:
                    continue
                prev = lines[lineno - 2] if lineno >= 2 else ''
                if is_suppressed(line, 'quality/mock-in-production', prev):
                    continue
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
        'Adw.ActionRow', 'Adw.ExpanderRow', 'Adw.ComboRow',
        'Adw.SwitchRow', 'Adw.SpinRow', 'Adw.EntryRow',
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

            # Skip if the class has a destroy() method (lifecycle-aware)
            # Look for destroy() between this class and the next class (or EOF)
            class_start = None
            for cm in re.finditer(r'class\s+\w+', content):
                if cm.start() < m.start():
                    class_start = cm.start()
            if class_start is not None:
                next_class = re.search(r'\nclass\s+\w+', content[m.start():])
                class_end = m.start() + next_class.start() if next_class else len(content)
                class_body = content[class_start:class_end]
                if re.search(r'\bdestroy\s*\(\s*\)\s*\{', class_body):
                    continue  # Class manages its own lifecycle

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
    """R-QUAL-12: Flag individual files with excessive non-blank lines.

    prefs.js gets a higher threshold (2000) because GTK4/Adw preferences files
    are structurally larger — each page builds widget trees in code.
    """
    for filepath in js_files:
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            count = sum(1 for line in f if line.strip())
        threshold = 2000 if os.path.basename(filepath) == 'prefs.js' else 1500
        if count > threshold:
            result("WARN", "quality/file-complexity",
                   f"{rel}: {count} non-blank lines — consider splitting into modules")
            return

    result("PASS", "quality/file-complexity",
           "No individual files exceed complexity thresholds")


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
    """R-QUAL-17: Flag excessive total console.* calls.

    Threshold scales with codebase size: max(30, total_non_blank_lines // 100).
    """
    total = 0
    total_non_blank = 0
    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for line in f:
                stripped = line.lstrip()
                if stripped.startswith('//') or stripped.startswith('*'):
                    continue
                if stripped:
                    total_non_blank += 1
                # console.log excluded — already a hard FAIL in ego-lint.sh
                total += len(re.findall(
                    r'console\.(debug|warn|error|info)\(', line))

    threshold = max(30, total_non_blank // 70)
    if total > threshold:
        result("WARN", "quality/logging-volume",
               f"{total} total console.* calls (threshold: {threshold} for "
               f"{total_non_blank} lines) — excessive logging may cause "
               f"rejection; keep only essential error/warning messages")
    else:
        result("PASS", "quality/logging-volume",
               f"Total logging volume OK ({total} calls, threshold: {threshold})")


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

    if total > 5:
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
            prev_line = ''
            for lineno, line in enumerate(f, 1):
                stripped = line.lstrip()
                if stripped.startswith('//') or stripped.startswith('*'):
                    prev_line = line
                    continue
                if is_suppressed(line, 'quality/private-api', prev_line):
                    prev_line = line
                    continue
                for pat, desc in patterns:
                    if re.search(pat, line):
                        matches.append((rel, lineno, desc))
                prev_line = line

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
    """R-QUAL-16: Flag direct Gettext.dgettext() usage in entry points.

    Only checks extension.js and prefs.js where this.gettext() is available.
    Library modules correctly use GLib.dgettext() — no alternative exists there.
    """
    # Only check entry-point files where this.gettext() is available
    entry_points = {'extension.js', 'prefs.js'}
    locations = []

    for filepath in js_files:
        if os.path.basename(filepath) not in entry_points:
            continue
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
               f"hardcoded gettext domain creates maintenance burden if domain changes; "
               f"use this.gettext() from the Extension base class")
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


def check_network_disclosure(ext_dir, js_files):
    """R-SEC-19: Flag network code not mentioned in metadata description."""
    network_patterns = [
        r'Soup\.Session',
        r'Soup\.Message',
        r'Soup\.URI',
        r'GLib\.Uri',
    ]

    has_network = False
    for filepath in js_files:
        # Exclude prefs.js — network in prefs is less concerning
        if os.path.basename(filepath) == 'prefs.js':
            continue
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = f.read()
        for pat in network_patterns:
            if re.search(pat, content):
                has_network = True
                break
        if has_network:
            break

    if not has_network:
        result("PASS", "quality/network-disclosure",
               "No network API usage detected")
        return

    meta_path = os.path.join(ext_dir, 'metadata.json')
    if not os.path.isfile(meta_path):
        result("WARN", "quality/network-disclosure",
               "Network APIs used but metadata.json not found")
        return

    try:
        with open(meta_path) as f:
            meta = json.load(f)
    except (json.JSONDecodeError, OSError):
        result("WARN", "quality/network-disclosure",
               "Network APIs used but metadata.json could not be read")
        return

    description = meta.get('description', '').lower()
    disclosure_keywords = [
        'network', 'internet', 'http', 'api', 'server',
        'online', 'fetch', 'request', 'web', 'service',
    ]

    for keyword in disclosure_keywords:
        if keyword in description:
            result("PASS", "quality/network-disclosure",
                   f"Network API usage disclosed in metadata description (keyword: '{keyword}')")
            return

    result("WARN", "quality/network-disclosure",
           "Network APIs used (Soup/GLib.Uri) but metadata description does not "
           "mention network access — reviewers expect disclosure")


def check_repeated_settings(ext_dir, js_files):
    """R-QUAL-28: Flag multiple getSettings()/Gio.Settings instances across extension files."""
    settings_re = re.compile(r'(\.getSettings\s*\(|new\s+Gio\.Settings\s*\()')
    total = 0
    locations = []

    for filepath in js_files:
        # Exclude prefs.js — multiple getSettings there is normal
        if os.path.basename(filepath) == 'prefs.js':
            continue
        rel = os.path.relpath(filepath, ext_dir)
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for lineno, line in enumerate(f, 1):
                stripped = line.lstrip()
                if stripped.startswith('//') or stripped.startswith('*'):
                    continue
                if settings_re.search(line):
                    total += 1
                    locations.append(f"{rel}:{lineno}")

    if total > 2:
        locs = ', '.join(locations[:5])
        result("WARN", "quality/repeated-settings",
               f"{total} getSettings()/Gio.Settings instances across extension files ({locs}) "
               f"— store a single instance and pass via dependency injection")
    else:
        result("PASS", "quality/repeated-settings",
               f"Settings instances OK ({total} across extension files)")


def check_code_provenance(ext_dir, js_files):
    """R-QUAL-29: Count positive indicators of hand-written code (AI defense context).

    Counts indicators that suggest authentic developer authorship:
      - Domain-specific vocabulary (hardware, DBus service names, app-specific terms)
      - Non-trivial algorithms (bitwise ops, math beyond simple arithmetic)
      - Debugging/workaround comments referencing bugs or version quirks
      - Consistent naming style (all camelCase or all snake_case, not mixed)

    Output is informational — provides context for AI slop scoring.
    """
    domain_vocab = 0
    nontrivial_algo = 0
    debug_comments = 0
    total_non_blank = 0
    naming_styles = {'camel': 0, 'snake': 0}

    # Domain vocabulary patterns (suggest real-world knowledge)
    domain_re = re.compile(
        r'\b(dbus|polkit|upower|networkmanager|bluez|logind|systemd|'
        r'pipewire|pulseaudio|wayland|x11|xdg|freedesktop|'
        r'brightness|backlight|cpu|gpu|battery|thermal|'
        r'inhibit|suspend|hibernate|idle|screensaver)\b', re.IGNORECASE
    )

    # Non-trivial algorithm patterns
    algo_re = re.compile(
        r'(<<|>>|>>>|&\s*0x|\|\s*0x'
        r'|Math\.(floor|ceil|round|pow|sqrt|log|min|max)\b'
        r'|for\s*\(\s*let\s+\w+\s*=\s*\w+[^;]*;\s*\w+[^;]*;\s*\w+)'
    )

    # Debugging/workaround comments (suggest iteration, not one-shot generation)
    debug_comment_re = re.compile(
        r'//\s*(workaround|hack|fixme|bug\s*#?\d+|regression|quirk|compat|'
        r'upstream|backport|see\s+https?://|gnome\.org|gitlab)',
        re.IGNORECASE
    )

    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            total_non_blank += 1

            domain_vocab += len(domain_re.findall(stripped))

            if algo_re.search(stripped):
                nontrivial_algo += 1

            if debug_comment_re.search(stripped):
                debug_comments += 1

            # Naming style consistency (private methods)
            for m in re.finditer(r'this\.(_[a-z][a-zA-Z0-9]+)', stripped):
                name = m.group(1)
                if '_' in name[1:]:
                    naming_styles['snake'] += 1
                else:
                    naming_styles['camel'] += 1

    signals = []
    if domain_vocab >= 5:
        signals.append(f"domain-vocabulary({domain_vocab})")
    if nontrivial_algo >= 3:
        signals.append(f"nontrivial-algorithms({nontrivial_algo})")
    if debug_comments >= 2:
        signals.append(f"debug-comments({debug_comments})")

    total_names = naming_styles['camel'] + naming_styles['snake']
    if total_names >= 10:
        dominant = max(naming_styles.values())
        if dominant / total_names > 0.9:
            signals.append("consistent-naming-style")

    score = len(signals)
    file_count = len(js_files)

    detail_parts = [f"provenance-score={score}"]
    if signals:
        detail_parts.append(f"signals=[{', '.join(signals)}]")
    detail_parts.append(f"files={file_count}")

    if score >= 3:
        result("PASS", "quality/code-provenance",
               f"Strong hand-written indicators: {'; '.join(detail_parts)}")
    elif score >= 1:
        result("PASS", "quality/code-provenance",
               f"Some hand-written indicators: {'; '.join(detail_parts)}")
    else:
        result("PASS", "quality/code-provenance",
               f"No strong provenance indicators: {'; '.join(detail_parts)}")


def check_excessive_null_checks(ext_dir, js_files):
    """R-QUAL-24: Flag excessive null/undefined checks instead of optional chaining."""
    total_checks = 0
    total_lines = 0

    null_patterns = [
        r'===?\s*null\b',
        r'!==?\s*null\b',
        r'===?\s*undefined\b',
        r"typeof\s+\w+\s*!==?\s*['\"]undefined['\"]",
    ]

    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        total_lines += sum(1 for l in lines if l.strip())
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith('//') or stripped.startswith('*'):
                continue
            for pat in null_patterns:
                total_checks += len(re.findall(pat, line))

    if total_lines > 0 and total_checks >= 15:
        ratio = total_checks / total_lines
        if ratio > 0.02:
            result("WARN", "quality/excessive-null-checks",
                   f"{total_checks} null/undefined checks across {total_lines} lines "
                   f"(ratio: {ratio:.3f}) — prefer optional chaining (?.) or nullish coalescing (??)")
            return

    result("PASS", "quality/excessive-null-checks",
           f"Null/undefined check density acceptable ({total_checks} in {total_lines} lines)")


def check_obfuscated_names(ext_dir, js_files):
    """Detect obfuscator-style variable names (single-char + digit patterns)."""
    obfuscated_names = set()
    # _0x1a2b style hex vars are strong obfuscator signals
    hex_var_re = re.compile(r'\b_0x[0-9a-f]{2,}\b')
    # Short letter+digit combos in variable declarations (not unicode escapes)
    decl_re = re.compile(r'(?:const|let|var|function)\s+([a-z]\d+)\b')
    total_usages = 0

    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for line in f:
                stripped = line.lstrip()
                if stripped.startswith('//') or stripped.startswith('*'):
                    continue
                for m in hex_var_re.finditer(stripped):
                    obfuscated_names.add(m.group(0))
                    total_usages += 1
                for m in decl_re.finditer(stripped):
                    obfuscated_names.add(m.group(1))
                    total_usages += 1

    if len(obfuscated_names) >= 15 or total_usages >= 50:
        result("FAIL", "quality/obfuscated-names",
               f"Detected {len(obfuscated_names)} obfuscator-style variable names "
               f"({total_usages} usages) — code appears minified or obfuscated")
    else:
        result("PASS", "quality/obfuscated-names",
               f"No significant obfuscation detected ({len(obfuscated_names)} suspect names)")


def check_mixed_indentation(ext_dir, js_files):
    """Detect files with mixed tab and space indentation."""
    mixed_files = []

    for filepath in js_files:
        tab_lines = 0
        space_lines = 0
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for line in f:
                if line.startswith('\t') and not line.startswith('\t//'):
                    tab_lines += 1
                elif line.startswith('    '):
                    space_lines += 1

        total = tab_lines + space_lines
        if total > 10 and tab_lines > 0 and space_lines > 0:
            minority = min(tab_lines, space_lines)
            if minority / total > 0.10:
                rel = os.path.relpath(filepath, ext_dir)
                mixed_files.append(f"{rel}(tabs:{tab_lines},spaces:{space_lines})")

    if mixed_files:
        result("WARN", "quality/mixed-indentation",
               f"Mixed tab/space indentation in {len(mixed_files)} file(s): "
               f"{', '.join(mixed_files[:3])}")
    else:
        result("PASS", "quality/mixed-indentation", "Consistent indentation style")


def check_excessive_logging(ext_dir, js_files):
    """Advisory: flag excessive console.debug/log without settings guard."""
    debug_count = 0
    has_settings_guard = False
    debug_re = re.compile(r'\bconsole\.(debug|log)\s*\(')
    guard_re = re.compile(r'(\bsettings\b|_debug\b|\bDEBUG\b|\bverbose\b|\blogLevel\b)')

    for filepath in js_files:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for line in f:
                stripped = line.lstrip()
                if stripped.startswith('//') or stripped.startswith('*'):
                    continue
                if debug_re.search(stripped):
                    debug_count += 1
                if guard_re.search(stripped):
                    has_settings_guard = True

    if debug_count > 15 and not has_settings_guard:
        result("WARN", "quality/excessive-logging",
               f"{debug_count} console.debug/log calls without a settings guard — "
               "consider making debug output configurable")
    else:
        result("PASS", "quality/excessive-logging",
               f"Logging volume acceptable ({debug_count} debug/log calls)")


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
    check_run_dispose_comment(ext_dir, js_files)
    check_clipboard_disclosure(ext_dir, js_files)
    check_network_disclosure(ext_dir, js_files)
    check_excessive_null_checks(ext_dir, js_files)
    check_repeated_settings(ext_dir, js_files)
    check_obfuscated_names(ext_dir, js_files)
    check_mixed_indentation(ext_dir, js_files)
    check_excessive_logging(ext_dir, js_files)
    check_code_provenance(ext_dir, js_files)


if __name__ == '__main__':
    main()
