#!/usr/bin/env python3
"""parse-lint-results.py — Parse ego-lint output into structured JSON.

Usage: parse-lint-results.py [OPTIONS]

Reads ego-lint --show all stdout from stdin, outputs JSON to stdout.
Expects the extension name, uuid, and metadata via CLI flags.

Options:
  --name NAME           Extension name
  --uuid UUID           Extension UUID
  --ego-approved        Extension is EGO-approved
  --exit-code N         ego-lint exit code
  --version HASH        ego-lint version (git short hash)
"""

import json
import re
import sys
from datetime import datetime, timezone


def parse_lint_output(lines):
    """Parse ego-lint verbose output lines into findings, metrics, and counts."""
    findings = []
    metrics = {}
    counts = {'pass': 0, 'fail': 0, 'warn': 0, 'skip': 0}
    provenance_score = None

    # Pattern for [STATUS] check-name  detail
    result_re = re.compile(
        r'^\[(?P<status>PASS|FAIL|WARN|SKIP)\]\s+'
        r'(?P<check>\S+)\s+'
        r'(?P<detail>.+)$'
    )

    # Pattern for [METRIC] key: value
    metric_re = re.compile(r'^\[METRIC\]\s+(?P<key>[\w-]+):\s+(?P<value>.+)$')

    # Fix suggestion pattern
    fix_re = re.compile(r'^\s+(?P<check>\S+):\s+(?P<fix>.+)$')

    in_fix_section = False
    fix_map = {}

    for line in lines:
        line = line.rstrip('\n')

        # Check for fix suggestions section
        if '--- FIX SUGGESTIONS ---' in line:
            in_fix_section = True
            continue
        if line.startswith('---') and in_fix_section:
            in_fix_section = False
            continue

        if in_fix_section:
            m = fix_re.match(line)
            if m:
                fix_map[m.group('check')] = m.group('fix')
            continue

        # Result lines
        m = result_re.match(line)
        if m:
            status = m.group('status')
            check = m.group('check')
            detail = m.group('detail').strip()
            counts[status.lower()] += 1

            # Extract provenance score
            if check == 'quality/code-provenance':
                score_m = re.search(r'provenance-score=(\d+)', detail)
                if score_m:
                    provenance_score = int(score_m.group(1))

            # Only record non-PASS findings for the findings list
            if status != 'PASS':
                finding_id = make_finding_id(check, detail)
                findings.append({
                    'id': finding_id,
                    'status': status,
                    'check': check,
                    'detail': detail,
                })
            continue

        # Metric lines
        m = metric_re.match(line)
        if m:
            key = m.group('key')
            value = m.group('value').strip()
            # Parse numeric values
            if key in ('js-files', 'total-lines', 'css-lines', 'schema-keys'):
                try:
                    metrics[key.replace('-', '_')] = int(value)
                except ValueError:
                    print(f"Warning: non-integer value for metric '{key}': {value}",
                          file=sys.stderr)
                    metrics[key.replace('-', '_')] = value
            elif key == 'largest-file':
                metrics['largest_file'] = value
            else:
                metrics[key.replace('-', '_')] = value

    # Attach fix suggestions to findings
    for finding in findings:
        if finding['check'] in fix_map:
            finding['fix'] = fix_map[finding['check']]

    counts['total'] = sum(counts.values())

    if lines and counts['total'] == 0:
        print("Warning: parsed 0 results from non-empty input. "
              "ego-lint output format may have changed.", file=sys.stderr)

    return findings, metrics, counts, provenance_score


def make_finding_id(check, detail):
    """Create a stable finding ID from check name and detail.

    Strips line numbers and file-specific info to create IDs that
    remain stable across runs when the same issue persists.
    """
    # Strip line numbers (file.js:123 -> file.js)
    stable_detail = re.sub(r':\d+', '', detail)
    # Strip "in N file(s): ..." suffix for pattern rules
    stable_detail = re.sub(r'\s+in\s+\d+\s+file\(s\):.*$', '', stable_detail)
    # Strip leading file list for multi-file findings (require path-like prefix
    # with . or / to avoid stripping non-file prefixes like "GLib: message")
    stable_detail = re.sub(r'^[\w./,\s]*[./][\w./,\s]*:\s+', '', stable_detail)
    # Normalize whitespace
    stable_detail = ' '.join(stable_detail.split())

    return f"{check}::{stable_detail}"


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default='unknown')
    parser.add_argument('--uuid', default='unknown')
    parser.add_argument('--ego-approved', action='store_true')
    parser.add_argument('--exit-code', type=int, default=0)
    parser.add_argument('--version', default='unknown')
    args = parser.parse_args()

    lines = sys.stdin.readlines()
    findings, metrics, counts, provenance_score = parse_lint_output(lines)

    result = {
        'name': args.name,
        'uuid': args.uuid,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'ego_lint_version': args.version,
        'ego_approved': args.ego_approved,
        'exit_code': args.exit_code,
        'counts': counts,
        'metrics': metrics,
        'provenance_score': provenance_score,
        'findings': findings,
    }

    json.dump(result, sys.stdout, indent=2)
    print()

    # Exit 2 (distinct from crash) when non-empty input produces 0 results,
    # so the runner can detect format mismatches
    if lines and counts['total'] == 0:
        sys.exit(2)


if __name__ == '__main__':
    main()
