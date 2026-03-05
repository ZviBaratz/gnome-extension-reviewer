#!/usr/bin/env python3
"""parse-manifest.py — Parse field test manifest YAML to JSON.

Usage: parse-manifest.py MANIFEST_PATH

Reads the constrained YAML manifest format and outputs a JSON array
of extension entries to stdout. No PyYAML dependency.
"""

import json
import os
import sys


def parse_manifest(path):
    """Parse the manifest YAML into a list of extension dicts."""
    extensions = []
    current = None
    source = None

    with open(path) as f:
        for line_num, raw_line in enumerate(f, 1):
            stripped = raw_line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            # Top-level key (extensions:)
            if stripped == 'extensions:':
                continue

            # Indentation level
            indent = len(raw_line) - len(raw_line.lstrip())

            # New extension entry (indent 2, starts with -)
            if stripped.startswith('- ') and indent == 2:
                if current is not None:
                    if source is not None:
                        current['source'] = source
                    extensions.append(current)
                current = {}
                source = None
                rest = stripped[2:].strip()
                if rest and ':' in rest:
                    k, v = rest.split(':', 1)
                    current[k.strip()] = _parse_value(v.strip())
                continue

            if current is None:
                print(f"Warning: {path}:{line_num}: ignoring line outside entry: {stripped}",
                      file=sys.stderr)
                continue

            # Source block (indent 6)
            if stripped == 'source:':
                source = {}
                continue

            if ':' in stripped:
                k, v = stripped.split(':', 1)
                k = k.strip()
                v = v.strip()

                if source is not None and indent >= 6:
                    source[k] = _parse_value(v)
                elif indent >= 4:
                    current[k] = _parse_value(v)
            else:
                print(f"Warning: {path}:{line_num}: unrecognized line: {stripped}",
                      file=sys.stderr)

    # Don't forget the last entry
    if current is not None:
        if source is not None:
            current['source'] = source
        extensions.append(current)

    return extensions


def _parse_value(v):
    """Parse a YAML scalar value."""
    if v == 'true':
        return True
    if v == 'false':
        return False
    if v.isdigit():
        return int(v)
    # Strip quotes
    if (v.startswith('"') and v.endswith('"')) or \
       (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    return v


def resolve_path(path_str):
    """Expand ~ in paths."""
    return os.path.expanduser(path_str)


def main():
    if len(sys.argv) < 2:
        print("Usage: parse-manifest.py MANIFEST_PATH", file=sys.stderr)
        sys.exit(1)

    manifest_path = sys.argv[1]
    if not os.path.isfile(manifest_path):
        print(f"Error: {manifest_path} not found", file=sys.stderr)
        sys.exit(1)

    extensions = parse_manifest(manifest_path)

    # Validate required fields
    for i, ext in enumerate(extensions):
        missing = {'name', 'uuid', 'source'} - set(ext.keys())
        if missing:
            print(f"Error: extension #{i+1} missing fields: {missing}", file=sys.stderr)
            sys.exit(1)
        src = ext.get('source', {})
        if 'type' not in src:
            print(f"Error: extension '{ext.get('name', '?')}' source missing 'type'", file=sys.stderr)
            sys.exit(1)

    # Resolve paths
    for ext in extensions:
        src = ext.get('source', {})
        if src.get('type') == 'local' and 'path' in src:
            src['path'] = resolve_path(src['path'])

    json.dump(extensions, sys.stdout, indent=2)
    print()


if __name__ == '__main__':
    main()
