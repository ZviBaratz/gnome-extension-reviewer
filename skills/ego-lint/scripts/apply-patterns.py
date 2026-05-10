#!/usr/bin/env python3
"""apply-patterns.py — Apply Tier 1 pattern rules from YAML to extension files.

Usage: apply-patterns.py RULES_YAML EXTENSION_DIR

Reads rules from a simple YAML file, greps matching files for each pattern,
outputs pipe-delimited results: STATUS|rule-id|detail

Requires only Python stdlib (no PyYAML dependency).
"""

import glob
import json
import os
import re
import sys
from collections import deque


def parse_rules(path):
    """Parse the constrained YAML subset used by patterns.yaml."""
    rules = []
    current = None
    with open(path) as f:
        for raw_line in f:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            if stripped.startswith('- '):
                if current is not None:
                    rules.append(current)
                current = {}
                rest = stripped[2:].strip()
                if rest and ':' in rest:
                    k, v = rest.split(':', 1)
                    current[k.strip()] = _parse_value(v.strip())
            elif current is not None and ':' in stripped:
                k, v = stripped.split(':', 1)
                current[k.strip()] = _parse_value(v.strip())
    if current is not None:
        rules.append(current)
    return rules


def _parse_value(v):
    """Parse a YAML scalar or simple list."""
    # List: ["a", "b"]
    if v.startswith('[') and v.endswith(']'):
        inner = v[1:-1]
        if not inner.strip():
            return []
        items = inner.split(',')
        return [i.strip().strip('"').strip("'") for i in items]
    # Double-quoted string: process YAML escape sequences
    if v.startswith('"') and v.endswith('"'):
        return _unescape_yaml_double(v[1:-1])
    # Single-quoted string: no escape processing in YAML
    if v.startswith("'") and v.endswith("'"):
        return v[1:-1]
    return v


def _unescape_yaml_double(s):
    """Process YAML double-quote escape sequences (subset)."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt == '\\':
                result.append('\\')
            elif nxt == '"':
                result.append('"')
            elif nxt == 'n':
                result.append('\n')
            elif nxt == 't':
                result.append('\t')
            elif nxt == 'r':
                result.append('\r')
            else:
                # Unknown escape: keep backslash + char as-is
                result.append('\\')
                result.append(nxt)
            i += 2
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def _get_shell_versions(ext_dir):
    """Read shell-version from metadata.json and return as list of ints."""
    metadata_path = os.path.join(ext_dir, 'metadata.json')
    # src/ layout fallback
    if not os.path.isfile(metadata_path):
        src_path = os.path.join(ext_dir, 'src', 'metadata.json')
        if os.path.isfile(src_path):
            metadata_path = src_path
    # resources/ layout fallback (TypeScript compiled extensions via esbuild)
    if not os.path.isfile(metadata_path):
        res_path = os.path.join(ext_dir, 'resources', 'metadata.json')
        if os.path.isfile(res_path):
            metadata_path = res_path
    if not os.path.isfile(metadata_path):
        return []
    try:
        with open(metadata_path, encoding='utf-8') as f:
            meta = json.load(f)
        versions = meta.get('shell-version', [])
        if not isinstance(versions, list):
            return []
        result = []
        for v in versions:
            m = re.match(r'^(\d+)', str(v))
            if m:
                result.append(int(m.group(1)))
        return result
    except (json.JSONDecodeError, OSError):
        return []


def _version_gate_applies(rule, shell_versions):
    """Check if a version-gated rule should apply given the shell versions.

    A rule with min-version fires only if at least one declared shell-version
    is >= min-version. A rule with max-version fires only if at least one
    declared shell-version is <= max-version. If no shell versions are known,
    version-gated rules are skipped (fail-safe: don't flag if we can't confirm).
    """
    min_ver = rule.get('min-version')
    max_ver = rule.get('max-version')

    if min_ver is None and max_ver is None:
        return True

    if not shell_versions:
        return False

    try:
        if min_ver is not None:
            min_ver = int(min_ver)
            if not any(v >= min_ver for v in shell_versions):
                return False
        if max_ver is not None:
            max_ver = int(max_ver)
            if not any(v <= max_ver for v in shell_versions):
                return False
    except (ValueError, TypeError):
        return False

    return True



def _is_suppressed(line, prev_line, rule_id):
    """Check if a line is suppressed via ego-lint-ignore comment.

    Supports:
      // ego-lint-ignore: R-XXX-NN  (same line or previous line, specific rule)
      // ego-lint-ignore             (same line or previous line, blanket)
      // ego-lint-ignore-next-line: R-XXX-NN  (previous line only)
      // ego-lint-ignore-next-line             (previous line, blanket)
    """
    # Check current line for inline suppression
    if 'ego-lint-ignore' in line:
        m = re.search(r'ego-lint-ignore(?:-next-line)?(?::\s*(\S+))?', line)
        if m:
            specified = m.group(1)
            if not specified or specified == rule_id:
                return True

    # Check previous line for next-line suppression
    if prev_line and 'ego-lint-ignore' in prev_line:
        m = re.search(r'ego-lint-ignore(?:-next-line)?(?::\s*(\S+))?', prev_line)
        if m:
            specified = m.group(1)
            if not specified or specified == rule_id:
                return True

    return False


def validate_rules(rules_file):
    """Validate patterns.yaml for common errors. Returns exit code."""
    if not os.path.isfile(rules_file):
        print(f"ERROR: File not found: {rules_file}", file=sys.stderr)
        return 1

    rules = parse_rules(rules_file)
    errors = 0
    seen_ids = {}
    required_fields = ('id', 'pattern', 'scope', 'severity', 'message')
    valid_severities = ('blocking', 'advisory')

    for i, rule in enumerate(rules):
        rid = rule.get('id', f'(rule #{i+1})')

        # Check required fields
        for field in required_fields:
            if field not in rule:
                print(f"ERROR: {rid}: missing required field '{field}'")
                errors += 1

        # Check duplicate IDs
        if 'id' in rule:
            if rule['id'] in seen_ids:
                print(f"ERROR: {rid}: duplicate ID (first seen at rule #{seen_ids[rule['id']]+1})")
                errors += 1
            seen_ids[rule['id']] = i

        # Check severity values
        severity = rule.get('severity', '')
        if severity and severity not in valid_severities:
            print(f"ERROR: {rid}: invalid severity '{severity}' (must be 'blocking' or 'advisory')")
            errors += 1

        # Check regex compilation
        pattern = rule.get('pattern', '')
        if pattern:
            try:
                re.compile(pattern)
            except re.error as e:
                print(f"ERROR: {rid}: invalid regex: {e}")
                errors += 1

        # Check guard-window validity
        gw = rule.get('guard-window', '')
        if gw:
            try:
                gw_int = int(gw)
                if gw_int < 1:
                    print(f"ERROR: {rid}: guard-window must be >= 1, got {gw}")
                    errors += 1
            except (ValueError, TypeError):
                print(f"ERROR: {rid}: guard-window must be an integer, got '{gw}'")
                errors += 1

        # Check fix-min-version validity
        fix_min = rule.get('fix-min-version')
        if fix_min is not None:
            try:
                int(fix_min)
            except (ValueError, TypeError):
                print(f"ERROR: {rid}: fix-min-version must be an integer, got '{fix_min}'")
                errors += 1

    if errors:
        print(f"\n{errors} error(s) found in {len(rules)} rules")
        return 1
    else:
        print(f"OK: {len(rules)} rules validated")
        return 0


# Patterns that signal a file is vendored/third-party code (checked in first 30 lines).
# Each pattern is matched against comment lines (lines starting with // or * or /*)
_VENDORED_SIGNALS = re.compile(
    r'(@license\b'
    r'|@generated\b'
    r'|@auto-generated\b'
    r'|Credits:\s*https?://'
    r'|Adapted from\s+https?://'
    r'|[Ww]as downloaded from\s+https?://'
    r'|[Dd]ownloaded from\s+https?://'
    r')',
    re.IGNORECASE,
)
_COMMENT_LINE = re.compile(r'^\s*(//|/?\*)')


def _is_vendored_file(filepath, scan_lines=30):
    """Return True if the file appears to be vendored/third-party code.

    Reads the first *scan_lines* lines and looks for common attribution
    patterns that indicate the file was copied from an external source:
    @license, @generated, Credits:, Adapted from.  Only matches inside
    comment lines to avoid false positives in code strings.
    """
    try:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                if i >= scan_lines:
                    break
                if _COMMENT_LINE.match(line) and _VENDORED_SIGNALS.search(line):
                    return True
    except OSError:
        pass
    return False


def _discover_vendored_files(ext_dir):
    """Scan all JS files in ext_dir and return a set of relative paths that
    appear to be vendored third-party code."""
    vendored = set()
    skip_dirs = ('node_modules', '.git', '__pycache__', 'examples')
    for filepath in glob.glob(os.path.join(ext_dir, '**', '*.js'), recursive=True):
        if not os.path.isfile(filepath):
            continue
        rel = os.path.relpath(filepath, ext_dir)
        if any(part in skip_dirs for part in rel.split(os.sep)):
            continue
        if _is_vendored_file(filepath):
            vendored.add(rel.replace(os.sep, '/'))
    return vendored


def _discover_dev_tool_dirs(ext_dir):
    """Return a set of top-level directory names that are dev-tooling infrastructure.

    These directories exist in source repos but are never shipped in an EGO package —
    they contain Vagrant VM scripts, Gulp build tasks, and similar dev-only code.
    Detection is trigger-file-based to avoid excluding legitimate extension subdirs
    that happen to share common names (e.g. an extension with a real conf/ subdir).
    """
    dev_dirs = set()

    # Vagrantfile at root → Vagrant-based dev setup; companion dirs are dev tooling
    if os.path.isfile(os.path.join(ext_dir, 'Vagrantfile')):
        for d in ('gulp', 'conf', 'vagrant'):
            if os.path.isdir(os.path.join(ext_dir, d)):
                dev_dirs.add(d)

    # gulpfile.js / Gulpfile.js at root → gulp/ is a dev-task directory
    for gulpfile in ('gulpfile.js', 'Gulpfile.js', 'gulpfile.mjs', 'Gulpfile.mjs'):
        if os.path.isfile(os.path.join(ext_dir, gulpfile)):
            if os.path.isdir(os.path.join(ext_dir, 'gulp')):
                dev_dirs.add('gulp')
            break

    # Gruntfile.js at root → grunt/ is a dev-task directory
    for gruntfile in ('Gruntfile.js', 'Gruntfile'):
        if os.path.isfile(os.path.join(ext_dir, gruntfile)):
            if os.path.isdir(os.path.join(ext_dir, 'grunt')):
                dev_dirs.add('grunt')
            break

    return dev_dirs


def _is_subprocess_entry(filepath, scan_lines=2):
    """Return True if the file is a standalone GJS subprocess (has #!/usr/bin/env gjs shebang)."""
    try:
        with open(filepath, encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                if i >= scan_lines:
                    break
                if line.startswith('#!') and 'gjs' in line:
                    return True
    except OSError:
        pass
    return False


def _discover_subprocess_dirs(ext_dir):
    """Return a set of top-level directory names that contain GJS subprocess entry points.

    Extensions like DING bundle a standalone GJS process (with a #!/usr/bin/env gjs
    shebang) in a subdirectory.  Those files intentionally use legacy CJS-style imports
    and must not be linted as GNOME Shell extension code.
    """
    subprocess_dirs = set()
    base_skip = ('node_modules', '.git', '__pycache__')
    for filepath in glob.glob(os.path.join(ext_dir, '**', '*.js'), recursive=True):
        if not os.path.isfile(filepath):
            continue
        rel = os.path.relpath(filepath, ext_dir)
        parts = rel.split(os.sep)
        if len(parts) < 2 or parts[0] in base_skip:
            continue
        if _is_subprocess_entry(filepath):
            subprocess_dirs.add(parts[0])
    return subprocess_dirs


def main():
    # Handle --validate mode
    if len(sys.argv) >= 3 and sys.argv[1] == '--validate':
        sys.exit(validate_rules(sys.argv[2]))

    if len(sys.argv) < 3:
        print("Usage: apply-patterns.py RULES_YAML EXTENSION_DIR", file=sys.stderr)
        print("       apply-patterns.py --validate RULES_YAML", file=sys.stderr)
        sys.exit(1)

    rules_file = sys.argv[1]
    ext_dir = os.path.realpath(sys.argv[2])

    if not os.path.isfile(rules_file):
        return

    rules = parse_rules(rules_file)
    shell_versions = _get_shell_versions(ext_dir)
    min_shell = min(shell_versions) if shell_versions else None
    is_compiled_ts = os.environ.get('EGO_LINT_COMPILED_TS') == '1'
    has_tsconfig = os.environ.get('EGO_LINT_HAS_TSCONFIG') == '1'
    has_spdx = os.environ.get('EGO_LINT_HAS_SPDX') == '1'

    # Pre-scan: identify subprocess directories, vendored files, and dev-tool dirs once
    subprocess_dirs = _discover_subprocess_dirs(ext_dir)
    if subprocess_dirs:
        dirs_list = ', '.join(sorted(subprocess_dirs))
        print(f"SKIP|subprocess-dir-exclusion|{len(subprocess_dirs)} top-level dir(s) contain "
              f"GJS subprocess entry points (#!/usr/bin/env gjs); excluded from pattern rules: {dirs_list}")

    vendored_files = _discover_vendored_files(ext_dir)
    if vendored_files:
        files_list = ', '.join(sorted(vendored_files))
        print(f"SKIP|vendored-file-exclusion|{len(vendored_files)} file(s) auto-detected as "
              f"vendored (third-party attribution header); excluded from pattern rules: {files_list}")

    dev_tool_dirs = _discover_dev_tool_dirs(ext_dir)
    if dev_tool_dirs:
        dirs_list = ', '.join(sorted(dev_tool_dirs))
        print(f"SKIP|dev-tooling-dir-exclusion|{len(dev_tool_dirs)} top-level dir(s) detected as "
              f"dev-tooling infrastructure (Vagrantfile/gulpfile trigger); excluded from pattern rules: {dirs_list}")

    for rule in rules:
        rid = rule.get('id', '?')
        pattern = rule.get('pattern', '')
        scopes = rule.get('scope', ['*.js'])
        severity = rule.get('severity', 'advisory')
        message = rule.get('message', rid)
        deduplicate = rule.get('deduplicate', '') == 'true'

        # Version gating: skip rules that don't apply to declared shell versions
        if not _version_gate_applies(rule, shell_versions):
            print(f"SKIP|{rid}|Not applicable for declared shell-version(s)")
            continue

        # Compiled TypeScript gating: skip rules that flag transpiler artifacts
        if is_compiled_ts and rule.get('skip-if-compiled', '') == 'true':
            print(f"SKIP|{rid}|Not applicable for compiled TypeScript")
            continue

        # TypeScript project gating: skip rules that produce noise on tsc-compiled output
        if has_tsconfig and rule.get('skip-if-tsconfig', '') == 'true':
            print(f"SKIP|{rid}|Not applicable for TypeScript project (tsconfig.json found)")
            continue

        # SPDX license header gating: skip rules that misfire on well-documented plain JS
        if has_spdx and rule.get('skip-if-spdx', '') == 'true':
            print(f"SKIP|{rid}|Not applicable for SPDX-licensed project (per-file SPDX headers found)")
            continue

        if isinstance(scopes, str):
            scopes = [scopes]

        status = 'FAIL' if severity == 'blocking' else 'WARN'

        # Version-compat downgrade: if extension targets GNOME versions where
        # this API was still valid, the deprecated code is backward-compat — WARN
        if (status == 'FAIL' and rule.get('compat-downgrade') == 'true'
                and min_shell is not None):
            rule_min = rule.get('min-version')
            if rule_min is not None and min_shell < int(rule_min):
                status = 'WARN'

        found = False
        dedup_files = set()  # For deduplicate mode
        exclude_dirs = set(rule.get('exclude-dirs', []))
        # exclude-files: list of glob patterns (relative to ext_dir) for per-rule exclusions
        exclude_files_patterns = rule.get('exclude-files', [])
        if isinstance(exclude_files_patterns, str):
            exclude_files_patterns = [exclude_files_patterns]
        # Expand exclude-files globs once per rule
        exclude_files_set = set()
        for efpat in exclude_files_patterns:
            for match in glob.glob(os.path.join(ext_dir, efpat), recursive=True):
                exclude_files_set.add(os.path.realpath(match))

        try:
            compiled = re.compile(pattern)
        except re.error:
            print(f"SKIP|{rid}|Invalid regex: {pattern}")
            continue

        guard = rule.get('guard-pattern', '')
        guard_re = re.compile(guard) if guard else None
        try:
            guard_window = max(1, int(rule.get('guard-window', '1')))
        except (ValueError, TypeError):
            guard_window = 1
        try:
            guard_window_fwd = max(0, int(rule.get('guard-window-forward', '0')))
        except (ValueError, TypeError):
            guard_window_fwd = 0

        for scope in scopes:
            # Expand glob relative to extension dir
            matches = glob.glob(os.path.join(ext_dir, '**', scope), recursive=True)
            # Also check files directly in ext_dir
            matches += glob.glob(os.path.join(ext_dir, scope))
            # Deduplicate and skip non-extension directories
            seen = set()
            skip_dirs = ('node_modules', '.git', '__pycache__', 'examples')
            for filepath in matches:
                if filepath in seen or not os.path.isfile(filepath):
                    continue
                # Skip files inside non-extension directories
                rel = os.path.relpath(filepath, ext_dir)
                if any(part in skip_dirs for part in rel.split(os.sep)):
                    continue
                # Skip files in auto-detected GJS subprocess directories
                rel_parts = rel.replace(os.sep, '/').split('/')
                if subprocess_dirs and rel_parts[0] in subprocess_dirs:
                    continue
                # Skip files in auto-detected dev-tooling directories (Vagrant/Gulp infra)
                if dev_tool_dirs and rel_parts[0] in dev_tool_dirs:
                    continue
                # Skip files in excluded directories (e.g., service daemons)
                if exclude_dirs:
                    if rel_parts[0] in exclude_dirs:
                        continue
                # Skip auto-detected vendored files
                rel_posix = rel.replace(os.sep, '/')
                if rel_posix in vendored_files:
                    continue
                # Skip per-rule excluded files
                if exclude_files_set and os.path.realpath(filepath) in exclude_files_set:
                    continue
                seen.add(filepath)
                try:
                    with open(filepath, encoding='utf-8', errors='replace') as f:
                        file_content = f.read()

                    # Check replacement-pattern: if both old and new patterns
                    # exist in the same file, it's backward-compatible — skip
                    replacement = rule.get('replacement-pattern', '')
                    if replacement and replacement in file_content:
                        continue

                    skip_comments = rule.get('skip-comments', '') == 'true'
                    in_block_comment = False
                    lines = file_content.splitlines(True)
                    line_buffer = deque(maxlen=guard_window)
                    for line_idx in range(len(lines)):
                        line = lines[line_idx]
                        lineno = line_idx + 1
                        # Track block comment state for skip-comments
                        if skip_comments:
                            if in_block_comment:
                                if '*/' in line:
                                    in_block_comment = False
                                    # Line may have code after */
                                    after_close = line[line.index('*/') + 2:]
                                    if '/*' in after_close:
                                        in_block_comment = True
                                line_buffer.append(line)
                                continue
                            if '/*' in line:
                                # Check if block comment closes on same line
                                bc_start = line.index('/*')
                                rest = line[bc_start + 2:]
                                if '*/' in rest:
                                    # Single-line block comment — check if match is inside
                                    bc_end = bc_start + 2 + rest.index('*/')
                                    m = compiled.search(line)
                                    if m and bc_start <= m.start() < bc_end:
                                        line_buffer.append(line)
                                        continue
                                else:
                                    # Multi-line block comment starts here
                                    m = compiled.search(line)
                                    if m and m.start() >= bc_start:
                                        in_block_comment = True
                                        line_buffer.append(line)
                                        continue
                                    in_block_comment = True
                        if compiled.search(line):
                            # Skip matches inside single-line comments
                            if skip_comments and '//' in line:
                                comment_pos = line.index('//')
                                m = compiled.search(line)
                                if m and m.start() >= comment_pos:
                                    line_buffer.append(line)
                                    continue
                            # Check for inline suppression (prev_line = last item in buffer)
                            prev_line = line_buffer[-1] if line_buffer else ''
                            if _is_suppressed(line, prev_line, rid):
                                line_buffer.append(line)
                                continue
                            # Check guard-pattern: backward lookback window
                            if guard_re and (guard_re.search(line) or
                                             any(guard_re.search(bl)
                                                 for bl in line_buffer)):
                                line_buffer.append(line)
                                continue
                            # Check guard-pattern: forward look window
                            if guard_re and guard_window_fwd > 0:
                                fwd_end = min(line_idx + guard_window_fwd + 1, len(lines))
                                if any(guard_re.search(lines[j])
                                       for j in range(line_idx + 1, fwd_end)):
                                    line_buffer.append(line)
                                    continue
                            rel = os.path.relpath(filepath, ext_dir)
                            if deduplicate:
                                dedup_files.add(rel)
                                found = True
                            else:
                                fix = rule.get('fix', '')
                                fix_min_ver = rule.get('fix-min-version')
                                if fix and fix_min_ver is not None and min_shell is not None:
                                    try:
                                        if min_shell < int(fix_min_ver):
                                            fix = ''
                                    except (ValueError, TypeError):
                                        pass
                                if fix:
                                    print(f"{status}|{rid}|{rel}:{lineno}: {message}|fix: {fix}")
                                else:
                                    print(f"{status}|{rid}|{rel}:{lineno}: {message}")
                                found = True
                        line_buffer.append(line)
                except OSError:
                    continue

        if deduplicate and dedup_files:
            files_list = ', '.join(sorted(dedup_files))
            fix = rule.get('fix', '')
            fix_min_ver = rule.get('fix-min-version')
            if fix and fix_min_ver is not None and min_shell is not None:
                try:
                    if min_shell < int(fix_min_ver):
                        fix = ''
                except (ValueError, TypeError):
                    pass
            summary = f"{message} in {len(dedup_files)} file(s): {files_list}"
            if fix:
                print(f"{status}|{rid}|{summary}|fix: {fix}")
            else:
                print(f"{status}|{rid}|{summary}")
        elif not found:
            print(f"PASS|{rid}|No matches")


if __name__ == '__main__':
    main()