#!/usr/bin/env python3
"""check-resources.py — Cross-file resource tracking check for GNOME extensions.

Usage: check-resources.py EXTENSION_DIR

Invokes build-resource-graph.py to build a cross-file resource ownership graph,
then emits pipe-delimited warnings for orphaned resources (created but never
cleaned up in the destroy chain).

Checks:
  - resource-tracking/orphan-signal: Signal with no disconnect in destroy chain
  - resource-tracking/orphan-timeout: Timeout with no Source.remove in destroy chain
  - resource-tracking/orphan-widget: Widget with no .destroy() in destroy chain
  - resource-tracking/orphan-filemonitor: File monitor with no .cancel() in destroy chain
  - resource-tracking/orphan-dbus: D-Bus proxy with no disconnect in destroy chain
  - resource-tracking/orphan-gsettings: GSettings with no disconnect in destroy chain
  - resource-tracking/no-destroy-method: Module has resources but no destroy()/disable()
  - resource-tracking/destroy-not-called: Module has destroy() but parent never calls it
  - resource-tracking/ownership: Summary of files scanned, depth, and orphan count

Output: PIPE-delimited lines: STATUS|check-name|detail
"""

import json
import os
import subprocess
import sys


def result(status, check, detail):
    print(f"{status}|{check}|{detail}")


# Map orphan resource types to check IDs
TYPE_TO_CHECK = {
    'signal': 'resource-tracking/orphan-signal',
    'timeout': 'resource-tracking/orphan-timeout',
    'widget': 'resource-tracking/orphan-widget',
    'filemonitor': 'resource-tracking/orphan-filemonitor',
    'dbus': 'resource-tracking/orphan-dbus',
    'gsettings': 'resource-tracking/orphan-gsettings',
}


def classify_orphan(orphan):
    """Determine which check ID to use based on the orphan's reason and type.

    Returns (check_id, detail_message).
    """
    reason = orphan.get('reason', '')
    rtype = orphan.get('type', '')
    file_path = orphan.get('file', '')
    line = orphan.get('line', '?')

    # Case 1: No destroy/disable method at all
    if 'no destroy()/disable() method' in reason:
        detail = f"{file_path}:{line} — {reason}"
        return 'resource-tracking/no-destroy-method', detail

    # Case 2: Parent doesn't call destroy
    if 'parent does not call destroy()' in reason:
        detail = f"{file_path}:{line} — {reason}"
        return 'resource-tracking/destroy-not-called', detail

    # Case 3: Specific resource type orphan
    check_id = TYPE_TO_CHECK.get(rtype, f'resource-tracking/orphan-{rtype}')
    detail = f"{file_path}:{line} — {reason}"
    return check_id, detail


def main():
    if len(sys.argv) < 2:
        print("Usage: check-resources.py EXTENSION_DIR", file=sys.stderr)
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])
    if not os.path.isdir(ext_dir):
        print(f"Error: {ext_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Locate build-resource-graph.py in the same directory as this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    graph_builder = os.path.join(script_dir, 'build-resource-graph.py')

    if not os.path.isfile(graph_builder):
        result('SKIP', 'resource-tracking/ownership',
               'build-resource-graph.py not found')
        return

    # Run the graph builder as a subprocess
    try:
        proc = subprocess.run(
            [sys.executable, graph_builder, ext_dir],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        result('SKIP', 'resource-tracking/ownership',
               'build-resource-graph.py timed out (30s)')
        return
    except OSError as e:
        result('SKIP', 'resource-tracking/ownership',
               f'failed to run build-resource-graph.py: {e}')
        return

    if proc.returncode != 0:
        stderr_msg = proc.stderr.strip().replace('\n', ' ')[:200]
        result('SKIP', 'resource-tracking/ownership',
               f'build-resource-graph.py failed: {stderr_msg}')
        return

    # Parse JSON output
    try:
        graph = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError) as e:
        result('SKIP', 'resource-tracking/ownership',
               f'failed to parse graph JSON: {e}')
        return

    orphans = graph.get('orphans', [])
    summary = graph.get('summary', {})
    files_scanned = summary.get('files_scanned', 0)
    depth = summary.get('ownership_depth', 0)
    orphan_count = summary.get('orphan_count', len(orphans))

    # Emit per-orphan warnings
    for orphan in orphans:
        check_id, detail = classify_orphan(orphan)
        result('WARN', check_id, detail)

    # Emit summary line
    if orphan_count == 0:
        result('PASS', 'resource-tracking/ownership',
               f'{files_scanned} files scanned, depth {depth}, 0 orphans')
    else:
        result('WARN', 'resource-tracking/ownership',
               f'{files_scanned} files scanned, depth {depth}, '
               f'{orphan_count} orphan{"s" if orphan_count != 1 else ""} detected')


if __name__ == '__main__':
    main()
