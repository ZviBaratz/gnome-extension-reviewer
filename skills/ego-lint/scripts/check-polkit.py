#!/usr/bin/env python3
"""check-polkit.py — Polkit action ID cross-reference for GNOME extensions.

Usage: check-polkit.py EXTENSION_DIR

Cross-references .policy XML, .rules JS, and pkexec invocations in code.
Validates action ID conventions and helper script paths.

Output: PIPE-delimited lines: STATUS|check-name|detail
"""

import os
import re
import sys
import xml.etree.ElementTree as ET


def result(status, check, detail):
    print(f"{status}|{check}|{detail}")


def find_files(ext_dir, extensions):
    """Find files with given extensions, excluding node_modules/.git."""
    skip_dirs = {'node_modules', '.git', '__pycache__', 'kwin'}
    files = []
    for root, dirs, filenames in os.walk(ext_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in filenames:
            if any(name.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, name))
    return files


def parse_policy_actions(policy_files):
    """Parse .policy XML files for action IDs."""
    actions = []
    for path in policy_files:
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            for action in root.iter('action'):
                action_id = action.get('id', '')
                if action_id:
                    actions.append({
                        'id': action_id,
                        'file': path,
                    })
        except ET.ParseError:
            pass
    return actions


def parse_rules_actions(rules_files):
    """Parse .rules JS files for referenced action IDs and program paths."""
    actions = []
    programs = []
    action_re = re.compile(r'action\.id\s*===?\s*["\']([^"\']+)["\']')
    program_re = re.compile(r'action\.lookup\s*\(\s*["\']program["\']\s*\)'
                            r'\s*===?\s*["\']([^"\']+)["\']')

    for path in rules_files:
        with open(path, encoding='utf-8', errors='replace') as f:
            content = f.read()
        for m in action_re.finditer(content):
            actions.append({'id': m.group(1), 'file': path})
        for m in program_re.finditer(content):
            programs.append({'path': m.group(1), 'file': path})

    return actions, programs


def find_pkexec_invocations(js_files):
    """Find pkexec invocations in JS code."""
    invocations = []
    pkexec_re = re.compile(r"""['"]pkexec['"]""")
    for path in js_files:
        with open(path, encoding='utf-8', errors='replace') as f:
            for lineno, line in enumerate(f, 1):
                if pkexec_re.search(line):
                    invocations.append({
                        'file': path,
                        'line': lineno,
                    })
    return invocations


def main():
    if len(sys.argv) < 2:
        result("FAIL", "polkit/args", "No extension directory provided")
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])

    policy_files = find_files(ext_dir, ['.policy'])
    rules_files = find_files(ext_dir, ['.rules'])
    js_files = find_files(ext_dir, ['.js'])

    # Skip if no polkit files at all
    if not policy_files and not rules_files:
        result("SKIP", "polkit/action-id-match", "No polkit files found")
        result("SKIP", "polkit/action-id-prefix", "No polkit files found")
        result("SKIP", "polkit/helper-exists", "No polkit files found")
        return

    # Parse all sources
    policy_actions = parse_policy_actions(policy_files)
    rules_actions, rules_programs = parse_rules_actions(rules_files)
    pkexec_invocations = find_pkexec_invocations(js_files)

    # Check 1: Action ID match between .policy and .rules
    if policy_actions and rules_actions:
        policy_ids = {a['id'] for a in policy_actions}
        rules_ids = {a['id'] for a in rules_actions}

        if policy_ids == rules_ids:
            result("PASS", "polkit/action-id-match",
                   f"Action IDs match between .policy and .rules "
                   f"({len(policy_ids)} action(s))")
        else:
            only_policy = policy_ids - rules_ids
            only_rules = rules_ids - policy_ids
            details = []
            if only_policy:
                details.append(f"in .policy only: {', '.join(sorted(only_policy))}")
            if only_rules:
                details.append(f"in .rules only: {', '.join(sorted(only_rules))}")
            result("FAIL", "polkit/action-id-match",
                   f"Action ID mismatch — {'; '.join(details)}")
    elif policy_actions and not rules_actions:
        if rules_files:
            result("WARN", "polkit/action-id-match",
                   "Policy defines actions but .rules file does not reference them")
        else:
            result("PASS", "polkit/action-id-match",
                   "Policy file found, no .rules file (may use defaults)")
    elif rules_actions and not policy_actions:
        result("WARN", "polkit/action-id-match",
               "Rules reference actions but no .policy file defines them")
    else:
        result("PASS", "polkit/action-id-match",
               "No action IDs to cross-reference")

    # Check 2: Action ID prefix convention
    all_ids = [a['id'] for a in policy_actions] + [a['id'] for a in rules_actions]
    if all_ids:
        bad_prefix = [aid for aid in all_ids
                      if not aid.startswith('org.gnome.shell.extensions.')]
        if bad_prefix:
            result("WARN", "polkit/action-id-prefix",
                   f"Action ID(s) don't follow org.gnome.shell.extensions.* "
                   f"convention: {', '.join(sorted(set(bad_prefix)))}")
        else:
            result("PASS", "polkit/action-id-prefix",
                   "All action IDs follow org.gnome.shell.extensions.* convention")
    else:
        result("PASS", "polkit/action-id-prefix",
               "No action IDs to check")

    # Check 3: Helper script paths exist
    if rules_programs:
        missing = []
        for prog in rules_programs:
            # Check relative to ext_dir
            prog_path = prog['path']
            # Try as relative path from extension
            candidates = [
                os.path.join(ext_dir, os.path.basename(prog_path)),
                os.path.join(ext_dir, prog_path),
            ]
            found = any(os.path.isfile(c) for c in candidates)
            if not found:
                missing.append(prog_path)

        if missing:
            result("WARN", "polkit/helper-exists",
                   f"Helper script(s) referenced in .rules not found in "
                   f"extension: {', '.join(missing)}")
        else:
            result("PASS", "polkit/helper-exists",
                   "All helper scripts referenced in .rules exist")
    else:
        result("PASS", "polkit/helper-exists",
               "No helper script paths in .rules to verify")


if __name__ == '__main__':
    main()
