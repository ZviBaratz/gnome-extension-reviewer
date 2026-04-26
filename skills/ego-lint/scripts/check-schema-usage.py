#!/usr/bin/env python3
"""check-schema-usage.py — GSettings schema key usage validation.

Usage: check-schema-usage.py EXTENSION_DIR

Cross-references .gschema.xml key definitions against JS code usage.
Reports unused keys (WARN) and undefined keys referenced in code (FAIL).

Output: PIPE-delimited lines: STATUS|check-name|detail
"""

import os
import re
import sys
import xml.etree.ElementTree as ET


def result(status, check, detail):
    print(f"{status}|{check}|{detail}")


def find_schema_files(ext_dir):
    """Find .gschema.xml files."""
    files = []
    for root, dirs, filenames in os.walk(ext_dir):
        dirs[:] = [d for d in dirs if d not in {'node_modules', '.git'}]
        for name in filenames:
            if name.endswith('.gschema.xml'):
                files.append(os.path.join(root, name))
    return files


def find_js_files(ext_dir):
    """Find JS files."""
    skip_dirs = {'node_modules', '.git', '__pycache__', 'kwin'}
    files = []
    for root, dirs, filenames in os.walk(ext_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in filenames:
            if name.endswith('.js'):
                files.append(os.path.join(root, name))
    return files


def parse_schema_keys(schema_files):
    """Parse .gschema.xml for defined key names."""
    keys = set()
    for path in schema_files:
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            for key in root.iter('key'):
                name = key.get('name', '')
                if name:
                    keys.add(name)
        except ET.ParseError:
            pass
    return keys


_GSETTINGS_GETTERS = (
    r'get_(?:boolean|default_value|double|enum|flags|int64|int|mapped'
    r'|string|strv|uint64|uint|user_value|value)'
)
_GSETTINGS_SETTERS = (
    r'set_(?:boolean|double|enum|flags|int64|int|string|strv|uint64|uint|value)'
)


def find_key_references(js_files):
    """Scan JS files for GSettings key name references.

    Matches patterns like:
        get_int('key-name')
        get_string("key-name")
        get_boolean('key-name')
        get_strv('key-name')
        get_value('key-name')
        get_double('key-name')
        get_uint('key-name')
        set_int('key-name', ...)
        set_string('key-name', ...)
        set_boolean('key-name', ...)
        set_strv('key-name', ...)
        set_value('key-name', ...)
        set_double('key-name', ...)
        set_uint('key-name', ...)
        bind('key-name', ...)
        connect('changed::key-name', ...)

    Note: only GSettings methods are matched — GTK Builder get_object() and
    GObject set_property() are intentionally excluded.
    """
    keys = set()
    has_dynamic = False

    # Match known GSettings get_*/set_*/bind with string literal key.
    # Deliberately excludes non-GSettings methods like get_object() and
    # set_property() to avoid false positives on GTK Builder widget IDs.
    accessor_re = re.compile(
        rf'\.({_GSETTINGS_GETTERS}|{_GSETTINGS_SETTERS}|bind)'
        r'\s*\(\s*["\']([a-z][a-z0-9-]*)["\']'
    )
    # Match connect('changed::key-name', ...)
    changed_re = re.compile(
        r"\.connect\s*\(\s*['\"]changed::([a-z][a-z0-9-]*)['\"]"
    )
    # Detect dynamic GSettings key access (variable or template literal)
    dynamic_re = re.compile(
        rf'\.({_GSETTINGS_GETTERS}|{_GSETTINGS_SETTERS}|bind)\s*\(\s*(`[^`]*`|\w+\s*[+,)])'
    )

    for path in js_files:
        with open(path, encoding='utf-8', errors='replace') as f:
            content = f.read()

        for m in accessor_re.finditer(content):
            keys.add(m.group(2))
        for m in changed_re.finditer(content):
            keys.add(m.group(1))
        if dynamic_re.search(content):
            has_dynamic = True

    return keys, has_dynamic


def main():
    if len(sys.argv) < 2:
        result("FAIL", "schema-usage/args", "No extension directory provided")
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])

    schema_files = find_schema_files(ext_dir)
    if not schema_files:
        result("SKIP", "schema-usage/unused-key", "No .gschema.xml found")
        result("SKIP", "schema-usage/undefined-key", "No .gschema.xml found")
        return

    js_files = find_js_files(ext_dir)
    if not js_files:
        result("SKIP", "schema-usage/unused-key", "No JS files found")
        result("SKIP", "schema-usage/undefined-key", "No JS files found")
        return

    defined_keys = parse_schema_keys(schema_files)
    if not defined_keys:
        result("SKIP", "schema-usage/unused-key", "No keys defined in schema")
        result("SKIP", "schema-usage/undefined-key", "No keys defined in schema")
        return

    referenced_keys, has_dynamic = find_key_references(js_files)

    # If dynamic key access detected, skip — can't reliably determine usage
    if has_dynamic:
        result("SKIP", "schema-usage/unused-key",
               "Dynamic key access detected — cannot verify statically")
        result("SKIP", "schema-usage/undefined-key",
               "Dynamic key access detected — cannot verify statically")
        return

    # Check for unused keys (defined but not referenced)
    unused = defined_keys - referenced_keys
    if unused:
        result("WARN", "schema-usage/unused-key",
               f"{len(unused)} schema key(s) defined but not referenced in code: "
               f"{', '.join(sorted(unused))}")
    else:
        result("PASS", "schema-usage/all-keys-used",
               f"All {len(defined_keys)} schema key(s) referenced in code")

    # Check for undefined keys (referenced but not defined)
    undefined = referenced_keys - defined_keys
    if undefined:
        result("FAIL", "schema-usage/undefined-key",
               f"{len(undefined)} key(s) referenced in code but not defined in schema: "
               f"{', '.join(sorted(undefined))}")
    else:
        result("PASS", "schema-usage/undefined-key",
               "All referenced keys exist in schema")


if __name__ == '__main__':
    main()
