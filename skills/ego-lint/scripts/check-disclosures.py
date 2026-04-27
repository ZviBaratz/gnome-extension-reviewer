#!/usr/bin/env python3
"""check-disclosures.py — Automated disclosure matrix for GNOME extensions.

Usage: check-disclosures.py EXTENSION_DIR

Cross-references code capabilities against metadata.json description to detect
undisclosed functionality that EGO reviewers will flag.

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
    skip_dirs = {'node_modules', '.git', '__pycache__', 'kwin'}
    files = []
    for root, dirs, filenames in os.walk(ext_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in filenames:
            if name.endswith('.js'):
                files.append(os.path.join(root, name))
    return files


# Each capability: name, code patterns (regex), disclosure keywords, check name
CAPABILITY_CHECKS = [
    {
        'name': 'clipboard',
        'code_patterns': [r'St\.Clipboard'],
        'disclosure_keywords': ['clipboard'],
        'check': 'disclosure/clipboard',
        'exclude_prefs': False,
    },
    {
        'name': 'network',
        'code_patterns': [
            r'Soup\.Session', r'Soup\.Message', r'Soup\.URI', r'GLib\.Uri',
        ],
        'disclosure_keywords': [
            'network', 'internet', 'http', 'api', 'server',
            'online', 'fetch', 'request', 'web', 'service',
        ],
        'check': 'disclosure/network',
        'exclude_prefs': True,
    },
    {
        'name': 'pkexec',
        'code_patterns': [r'\bpkexec\b', r'\bpolkit\b'],
        'disclosure_keywords': [
            'pkexec', 'polkit', 'root', 'privileged', 'elevated', 'admin',
        ],
        'check': 'disclosure/pkexec',
        'exclude_prefs': True,
    },
    {
        'name': 'private-api',
        'code_patterns': [
            r'Main\.panel\._\w+', r'statusArea\._\w+', r'quickSettings\._\w+',
            r'(?:Main\.panel|statusArea|quickSettings)[\w.]*\._getMenuItems\(',
            r'(?:Main\.panel|statusArea|quickSettings)[\w.]*\._getTopMenu\(',
            r'\._delegate\b',
        ],
        'disclosure_keywords': ['private', 'internal', 'unstable'],
        'check': 'disclosure/private-api',
        'exclude_prefs': True,
    },
    {
        'name': 'file-io',
        'code_patterns': [
            r'Gio\.File\.new_for_path', r'\.load_contents\b',
            r'\.replace_contents\b', r'\.monitor_file\b',
        ],
        'disclosure_keywords': [
            'file', 'read', 'write', 'disk', 'filesystem', 'storage',
        ],
        'check': 'disclosure/file-io',
        'exclude_prefs': True,
    },
    {
        'name': 'subprocess',
        'code_patterns': [
            r'\bGio\.Subprocess\b', r'\bGLib\.spawn',
        ],
        'disclosure_keywords': [
            'command', 'subprocess', 'exec', 'run', 'process', 'shell',
        ],
        'check': 'disclosure/subprocess',
        'exclude_prefs': True,
    },
]


def check_capability(ext_dir, js_files, capability, description):
    """Check a single capability against code and metadata."""
    check_name = capability['check']
    cap_name = capability['name']
    exclude_prefs = capability['exclude_prefs']

    # Scan code for capability patterns
    has_capability = False
    for filepath in js_files:
        if exclude_prefs and os.path.basename(filepath) == 'prefs.js':
            continue
        with open(filepath, encoding='utf-8', errors='replace') as f:
            content = f.read()
        for pat in capability['code_patterns']:
            if re.search(pat, content):
                has_capability = True
                break
        if has_capability:
            break

    if not has_capability:
        result("PASS", check_name,
               f"No {cap_name} usage detected")
        return

    # Check if disclosed in metadata description
    desc_lower = description.lower()
    for keyword in capability['disclosure_keywords']:
        if keyword in desc_lower:
            result("PASS", check_name,
                   f"{cap_name} usage disclosed in metadata description "
                   f"(keyword: '{keyword}')")
            return

    result("WARN", check_name,
           f"{cap_name} capability detected in code but metadata description "
           f"does not disclose it — reviewers expect disclosure")


def main():
    if len(sys.argv) < 2:
        result("FAIL", "disclosure/args", "No extension directory provided")
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])
    js_files = find_js_files(ext_dir)

    if not js_files:
        result("SKIP", "disclosure/no-js", "No JavaScript files found")
        return

    # Read metadata description once
    meta_path = os.path.join(ext_dir, 'metadata.json')
    # src/ layout fallback
    if not os.path.isfile(meta_path):
        src_path = os.path.join(ext_dir, 'src', 'metadata.json')
        if os.path.isfile(src_path):
            meta_path = src_path
    description = ''
    if os.path.isfile(meta_path):
        try:
            with open(meta_path) as f:
                meta = json.load(f)
            description = meta.get('description', '')
        except (json.JSONDecodeError, OSError):
            pass

    for capability in CAPABILITY_CHECKS:
        check_capability(ext_dir, js_files, capability, description)


if __name__ == '__main__':
    main()
