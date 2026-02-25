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
            # Extract leading integer from version strings like "46", "47.1", etc.
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

    # No version gate — always applies
    if min_ver is None and max_ver is None:
        return True

    # Version-gated but no shell versions known — skip
    if not shell_versions:
        return False

    # Parse version values as integers
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


def main():
    if len(sys.argv) < 3:
        print("Usage: apply-patterns.py RULES_YAML EXTENSION_DIR", file=sys.stderr)
        sys.exit(1)

    rules_file = sys.argv[1]
    ext_dir = os.path.realpath(sys.argv[2])

    if not os.path.isfile(rules_file):
        return

    rules = parse_rules(rules_file)
    shell_versions = _get_shell_versions(ext_dir)

    for rule in rules:
        rid = rule.get('id', '?')
        pattern = rule.get('pattern', '')
        scopes = rule.get('scope', ['*.js'])
        severity = rule.get('severity', 'advisory')
        message = rule.get('message', rid)

        # Version gating: skip rules that don't apply to declared shell versions
        if not _version_gate_applies(rule, shell_versions):
            print(f"SKIP|{rid}|Not applicable for declared shell-version(s)")
            continue

        if isinstance(scopes, str):
            scopes = [scopes]

        status = 'FAIL' if severity == 'blocking' else 'WARN'
        found = False

        try:
            compiled = re.compile(pattern)
        except re.error:
            print(f"SKIP|{rid}|Invalid regex: {pattern}")
            continue

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
                seen.add(filepath)
                try:
                    with open(filepath, encoding='utf-8', errors='replace') as f:
                        for lineno, line in enumerate(f, 1):
                            if compiled.search(line):
                                rel = os.path.relpath(filepath, ext_dir)
                                print(f"{status}|{rid}|{rel}:{lineno}: {message}")
                                found = True
                except OSError:
                    continue

        if not found:
            print(f"PASS|{rid}|No matches")


if __name__ == '__main__':
    main()
