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

        if isinstance(scopes, str):
            scopes = [scopes]

        status = 'FAIL' if severity == 'blocking' else 'WARN'
        found = False
        dedup_files = set()  # For deduplicate mode
        exclude_dirs = set(rule.get('exclude-dirs', []))

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
            skip_dirs = ('node_modules', '.git', '__pycache__')
            for filepath in matches:
                if filepath in seen or not os.path.isfile(filepath):
                    continue
                # Skip files inside non-extension directories
                rel = os.path.relpath(filepath, ext_dir)
                if any(part in skip_dirs for part in rel.split(os.sep)):
                    continue
                # Skip files in excluded directories (e.g., service daemons)
                if exclude_dirs:
                    rel_parts = rel.replace(os.sep, '/').split('/')
                    if rel_parts[0] in exclude_dirs:
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
