#!/usr/bin/env python3
"""diff-baselines.py — Compare current ego-lint results against baseline.

Usage: diff-baselines.py CURRENT_JSON BASELINE_JSON [ANNOTATION_YAML]

Outputs a JSON diff to stdout with new findings, resolved findings,
count deltas, and unannotated findings (filtered by annotation file).
"""

import json
import os
import sys


def parse_annotations(path):
    """Parse annotation YAML into a dict of finding_id -> classification.

    Uses inline YAML parser (no PyYAML dependency).
    """
    annotations = {}
    if not path or not os.path.isfile(path):
        return annotations

    current_id = None
    with open(path) as f:
        for raw_line in f:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            if stripped.startswith('- '):
                rest = stripped[2:].strip()
                if rest.startswith('id:'):
                    val = rest[3:].strip().strip('"').strip("'")
                    current_id = val
                continue

            if ':' in stripped and current_id is not None:
                k, v = stripped.split(':', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k == 'id':
                    # New id without classification for previous — warn
                    if current_id not in annotations:
                        print(f"Warning: annotation '{current_id}' has no classification",
                              file=sys.stderr)
                    current_id = v
                elif k == 'classification':
                    annotations[current_id] = v
                    current_id = None

    # Check last entry
    if current_id is not None and current_id not in annotations:
        print(f"Warning: annotation '{current_id}' has no classification",
              file=sys.stderr)

    return annotations


def diff_results(current, baseline, annotations):
    """Compute diff between current and baseline results."""
    # Build finding sets by ID
    current_ids = {f['id'] for f in current.get('findings', [])}
    baseline_ids = {f['id'] for f in baseline.get('findings', [])}

    current_by_id = {f['id']: f for f in current.get('findings', [])}
    baseline_by_id = {f['id']: f for f in baseline.get('findings', [])}

    new_ids = current_ids - baseline_ids
    resolved_ids = baseline_ids - current_ids

    new_findings = [current_by_id[fid] for fid in sorted(new_ids)]
    resolved_findings = [baseline_by_id[fid] for fid in sorted(resolved_ids)]

    # Unannotated: in current results, not in annotations
    unannotated = [
        current_by_id[fid]
        for fid in sorted(current_ids)
        if fid not in annotations
    ]

    # Count deltas
    bc = baseline.get('counts', {})
    cc = current.get('counts', {})
    count_deltas = {}
    for key in ('pass', 'fail', 'warn', 'skip', 'total'):
        count_deltas[key] = cc.get(key, 0) - bc.get(key, 0)

    return {
        'name': current.get('name', 'unknown'),
        'baseline_version': baseline.get('ego_lint_version', 'unknown'),
        'current_version': current.get('ego_lint_version', 'unknown'),
        'baseline_timestamp': baseline.get('timestamp', ''),
        'current_timestamp': current.get('timestamp', ''),
        'count_deltas': count_deltas,
        'new_findings': new_findings,
        'resolved_findings': resolved_findings,
        'unannotated_findings': unannotated,
        'changed': bool(new_findings or resolved_findings),
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: diff-baselines.py CURRENT_JSON BASELINE_JSON [ANNOTATION_YAML]",
              file=sys.stderr)
        sys.exit(1)

    current_path = sys.argv[1]
    baseline_path = sys.argv[2]
    annotation_path = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        with open(current_path) as f:
            current = json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {current_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: malformed JSON in {current_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(baseline_path):
        # No baseline — everything is new
        result = {
            'name': current.get('name', 'unknown'),
            'baseline_version': None,
            'current_version': current.get('ego_lint_version', 'unknown'),
            'baseline_timestamp': None,
            'current_timestamp': current.get('timestamp', ''),
            'count_deltas': None,
            'new_findings': current.get('findings', []),
            'resolved_findings': [],
            'unannotated_findings': current.get('findings', []),
            'changed': True,
            'no_baseline': True,
        }
        json.dump(result, sys.stdout, indent=2)
        print()
        return

    try:
        with open(baseline_path) as f:
            baseline = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: malformed JSON in {baseline_path}: {e}", file=sys.stderr)
        sys.exit(1)

    annotations = parse_annotations(annotation_path)
    result = diff_results(current, baseline, annotations)

    json.dump(result, sys.stdout, indent=2)
    print()


if __name__ == '__main__':
    main()
