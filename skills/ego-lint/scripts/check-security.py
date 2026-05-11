#!/usr/bin/env python3
"""check-security.py — UUID-aware extension interference checks.

Usage: check-security.py EXTENSION_DIR

Supplements the pattern-based R-SEC-09 rule with UUID-aware analysis:

  R-SEC-09b: lookupByUUID() called with a UUID other than the extension's own.
             Self-lookup (for openPreferences(), etc.) is a legitimate pattern
             and is explicitly exempted.

Output: pipe-delimited lines: STATUS|check-name|detail
"""

import json
import os
import re
import sys


def result(status, check, detail):
    print(f"{status}|{check}|{detail}")


def _get_extension_uuid(ext_dir):
    """Read uuid from metadata.json. Returns None if not found."""
    for candidate in (
        os.path.join(ext_dir, 'metadata.json'),
        os.path.join(ext_dir, 'src', 'metadata.json'),
        os.path.join(ext_dir, 'resources', 'metadata.json'),
    ):
        if os.path.isfile(candidate):
            try:
                with open(candidate, encoding='utf-8') as f:
                    meta = json.load(f)
                return meta.get('uuid')
            except (json.JSONDecodeError, OSError):
                pass
    return None


def _iter_js_files(ext_dir):
    skip_dirs = {'node_modules', '.git', '__pycache__', 'examples'}
    for root, dirs, filenames in os.walk(ext_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in filenames:
            if name.endswith('.js'):
                yield os.path.join(root, name)


# Matches lookupByUUID('some-uuid@domain') or lookupByUUID("some-uuid@domain")
_LOOKUP_STATIC_RE = re.compile(
    r'\blookupByUUID\s*\(\s*([\'"])([^\'"]+)\1\s*\)'
)
# Matches lookupByUUID with a non-literal argument (variable or expression)
_LOOKUP_DYNAMIC_RE = re.compile(
    r'\blookupByUUID\s*\('
)


def check_lookup_by_uuid(ext_dir, own_uuid):
    """Check for lookupByUUID calls targeting other extensions.

    Flags:
    - R-SEC-09b (advisory): lookupByUUID with a UUID that is not the extension's own
    - Skips: lookupByUUID with the extension's own UUID (self-lookup, e.g. openPreferences)
    - R-SEC-09b (advisory, dynamic): lookupByUUID with a dynamic argument (can't verify UUID)
    """
    found_any = False
    for filepath in _iter_js_files(ext_dir):
        rel = os.path.relpath(filepath, ext_dir)
        try:
            with open(filepath, encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except OSError:
            continue

        # Strip single-line comments for analysis but preserve line numbers
        for lineno, raw_line in enumerate(lines, 1):
            # Skip lines that are purely comments
            stripped = raw_line.lstrip()
            if stripped.startswith('//'):
                continue

            # Check inline suppression
            if 'ego-lint-ignore' in raw_line:
                m = re.search(r'ego-lint-ignore(?:-next-line)?(?::\s*(\S+))?', raw_line)
                if m:
                    specified = m.group(1)
                    if not specified or specified in ('R-SEC-09', 'R-SEC-09b'):
                        continue

            # Check previous line for next-line suppression
            if lineno >= 2 and 'ego-lint-ignore' in lines[lineno - 2]:
                m = re.search(
                    r'ego-lint-ignore(?:-next-line)?(?::\s*(\S+))?',
                    lines[lineno - 2]
                )
                if m:
                    specified = m.group(1)
                    if not specified or specified in ('R-SEC-09', 'R-SEC-09b'):
                        continue

            static_match = _LOOKUP_STATIC_RE.search(raw_line)
            if static_match:
                called_uuid = static_match.group(2)
                if own_uuid and called_uuid == own_uuid:
                    # Self-lookup — legitimate pattern (openPreferences, status check)
                    continue
                detail = (
                    f"{rel}:{lineno}: lookupByUUID('{called_uuid}') — "
                    "accessing another extension is discouraged; document the justification"
                )
                result('WARN', 'R-SEC-09b', detail)
                found_any = True
                continue

            # Dynamic argument — can't determine UUID at analysis time
            if _LOOKUP_DYNAMIC_RE.search(raw_line):
                detail = (
                    f"{rel}:{lineno}: lookupByUUID() with dynamic argument — "
                    "extension system interference is discouraged; document the justification"
                )
                result('WARN', 'R-SEC-09b', detail)
                found_any = True

    if not found_any:
        result('PASS', 'R-SEC-09b', 'No cross-extension lookupByUUID calls found')


def main():
    if len(sys.argv) < 2:
        print("Usage: check-security.py EXTENSION_DIR", file=sys.stderr)
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])
    if not os.path.isdir(ext_dir):
        print(f"ERROR: Not a directory: {ext_dir}", file=sys.stderr)
        sys.exit(1)

    own_uuid = _get_extension_uuid(ext_dir)
    check_lookup_by_uuid(ext_dir, own_uuid)


if __name__ == '__main__':
    main()
