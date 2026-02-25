#!/usr/bin/env python3
"""build-resource-graph.py — Cross-file resource graph builder for GNOME extensions.

Usage: build-resource-graph.py EXTENSION_DIR

Scans all JS files in a GNOME extension directory and builds a structured JSON
resource graph with ownership chains and orphan detection.

Resource types tracked: signal, timeout, widget, dbus, filemonitor, gsettings

Output: JSON to stdout
"""

import json
import os
import re
import sys


# ---------------------------------------------------------------------------
# Helpers (copied from check-lifecycle.py)
# ---------------------------------------------------------------------------

def find_js_files(ext_dir, exclude_prefs=False):
    """Find JS files, optionally excluding prefs.js."""
    skip_dirs = {'node_modules', '.git', '__pycache__'}
    files = []
    for root, dirs, filenames in os.walk(ext_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in filenames:
            if name.endswith('.js'):
                if exclude_prefs and name == 'prefs.js':
                    continue
                files.append(os.path.join(root, name))
    return files


def read_file(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return f.read()


def strip_comments(content):
    """Remove single-line and block comments from JS content."""
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    return content


# ---------------------------------------------------------------------------
# Resource detection patterns
# ---------------------------------------------------------------------------

CREATE_PATTERNS = {
    'signal': [
        re.compile(r'\.connect\s*\('),
        re.compile(r'\.connectObject\s*\('),
    ],
    'timeout': [
        re.compile(r'timeout_add\s*\('),
        re.compile(r'idle_add\s*\('),
        re.compile(r'timeout_add_seconds\s*\('),
    ],
    'widget': [
        re.compile(r'new\s+St\.\w+'),
        re.compile(r'new\s+Clutter\.\w+'),
        re.compile(r'new\s+PanelMenu\.\w+'),
    ],
    'dbus': [
        re.compile(r'Gio\.DBusProxy\.new_for_bus'),
        re.compile(r'new\s+Gio\.DBusProxy'),
        re.compile(r'makeProxyWrapper'),
    ],
    'filemonitor': [
        re.compile(r'\.monitor_file\s*\('),
        re.compile(r'\.monitor_directory\s*\('),
        re.compile(r'\.monitor_children\s*\('),
    ],
    'gsettings': [
        re.compile(r'\.getSettings\s*\('),
        re.compile(r'new\s+Gio\.Settings\s*\('),
    ],
}

DESTROY_PATTERNS = {
    'signal': [
        re.compile(r'\.disconnect\s*\('),
        re.compile(r'\.disconnectObject\s*\('),
    ],
    'timeout': [
        re.compile(r'Source\.remove\s*\('),
        re.compile(r'GLib\.Source\.remove\s*\('),
    ],
    'widget': [
        re.compile(r'\.destroy\s*\('),
    ],
    'dbus': [
        re.compile(r'\.disconnect\s*\('),
        re.compile(r'\.disconnectSignal\s*\('),
    ],
    'filemonitor': [
        re.compile(r'\.cancel\s*\('),
    ],
    'gsettings': [
        re.compile(r'\.disconnectObject\s*\('),
        re.compile(r'\.disconnect\s*\('),
    ],
}


# ---------------------------------------------------------------------------
# Import resolution
# ---------------------------------------------------------------------------

def parse_imports(content, file_path, ext_dir):
    """Parse ES module imports to map class names to source files.

    Returns dict: {class_name: resolved_relative_path}
    """
    imports = {}
    file_dir = os.path.dirname(file_path)

    # import {Foo, Bar} from './path.js'
    for m in re.finditer(
        r'import\s+\{([^}]+)\}\s+from\s+[\'"](\.[^"\']+)[\'"]', content
    ):
        names = [n.strip().split(' as ')[-1].strip() for n in m.group(1).split(',')]
        import_path = m.group(2)
        resolved = os.path.normpath(os.path.join(file_dir, import_path))
        rel = os.path.relpath(resolved, ext_dir)
        for name in names:
            if name:
                imports[name] = rel

    # import Foo from './path.js'  (default import)
    for m in re.finditer(
        r'import\s+(\w+)\s+from\s+[\'"](\.[^"\']+)[\'"]', content
    ):
        name = m.group(1)
        import_path = m.group(2)
        resolved = os.path.normpath(os.path.join(file_dir, import_path))
        rel = os.path.relpath(resolved, ext_dir)
        imports[name] = rel

    # import * as Foo from './path.js'
    for m in re.finditer(
        r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"](\.[^"\']+)[\'"]', content
    ):
        name = m.group(1)
        import_path = m.group(2)
        resolved = os.path.normpath(os.path.join(file_dir, import_path))
        rel = os.path.relpath(resolved, ext_dir)
        imports[name] = rel

    return imports


# ---------------------------------------------------------------------------
# Method extraction
# ---------------------------------------------------------------------------

def find_method_body(content, method_name):
    """Find the body of a method by name, handling brace nesting.

    Returns (start_line, end_line, body_text) or None.
    """
    # Match method_name() { ... } — handles class method syntax
    pattern = re.compile(
        r'(?:^|\s)' + re.escape(method_name) + r'\s*\([^)]*\)\s*\{',
        re.MULTILINE
    )
    m = pattern.search(content)
    if not m:
        return None

    # Find the opening brace
    brace_pos = content.index('{', m.start())
    depth = 1
    pos = brace_pos + 1
    while pos < len(content) and depth > 0:
        if content[pos] == '{':
            depth += 1
        elif content[pos] == '}':
            depth -= 1
        pos += 1

    body = content[brace_pos + 1:pos - 1]

    # Calculate line numbers
    start_line = content[:brace_pos].count('\n') + 1
    end_line = content[:pos].count('\n') + 1

    return start_line, end_line, body


# ---------------------------------------------------------------------------
# Reference extraction
# ---------------------------------------------------------------------------

def extract_stored_ref(line):
    """Extract the left-hand side reference from an assignment.

    e.g. 'this._handlerId = global.display.connect(...)' -> 'this._handlerId'
         'const monitor = file.monitor_file(...)' -> None (not a this._ ref)
    """
    # this._foo = ...
    m = re.match(r'\s*(this\._\w+)\s*=', line)
    if m:
        return m.group(1)
    # this.foo = ... (non-underscore)
    m = re.match(r'\s*(this\.\w+)\s*=', line)
    if m:
        return m.group(1)
    return None


def extract_destroy_ref(line):
    """Extract the reference being cleaned up.

    e.g. 'this._monitor.cancel()' -> 'this._monitor'
         'this._monitor?.cancel()' -> 'this._monitor'
         'global.display.disconnect(this._handlerId)' -> 'this._handlerId'
    """
    # this._foo.method() or this._foo?.method()
    m = re.search(r'(this[._]\w+(?:\._\w+)*)\??\.\w+\s*\(', line)
    if m:
        return m.group(1)
    # Something.method(this._ref)
    m = re.search(r'\w+\.\w+\s*\(\s*(this\._\w+)', line)
    if m:
        return m.group(1)
    return None


# ---------------------------------------------------------------------------
# Scan a single file
# ---------------------------------------------------------------------------

def scan_file(file_path, ext_dir):
    """Scan a JS file and return creates, destroys, instantiates, imports, and method info."""
    raw_content = read_file(file_path)
    content = strip_comments(raw_content)
    lines = content.splitlines()
    rel = os.path.relpath(file_path, ext_dir)

    creates = []
    destroys = []
    instantiates = []

    imports = parse_imports(raw_content, file_path, ext_dir)

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue

        # Detect resource creates
        for rtype, patterns in CREATE_PATTERNS.items():
            for pat in patterns:
                if pat.search(stripped):
                    creates.append({
                        'line': lineno,
                        'type': rtype,
                        'pattern': stripped[:120],
                        'stored_as': extract_stored_ref(stripped),
                    })
                    break  # one match per type per line

        # Detect resource destroys
        for rtype, patterns in DESTROY_PATTERNS.items():
            for pat in patterns:
                if pat.search(stripped):
                    destroys.append({
                        'line': lineno,
                        'type': rtype,
                        'pattern': stripped[:120],
                        'ref': extract_destroy_ref(stripped),
                    })
                    break

        # Detect instantiations: this._foo = new ClassName(...)
        inst_match = re.search(
            r'(this[._]\w+)\s*=\s*new\s+(\w+)\s*\(', stripped
        )
        if inst_match:
            ref = inst_match.group(1)
            cls = inst_match.group(2)
            instantiates.append({
                'line': lineno,
                'type': 'object',
                'class': cls,
                'stored_as': ref,
                'has_destroy_call': False,
                'destroy_line': None,
            })

    # Check if instantiated objects have .destroy() calls
    for inst in instantiates:
        ref = inst['stored_as']
        if not ref:
            continue
        # Look for ref.destroy() or ref?.destroy()
        destroy_pat = re.compile(
            re.escape(ref) + r'\??\.destroy\s*\('
        )
        for lineno, line in enumerate(lines, 1):
            if destroy_pat.search(line):
                inst['has_destroy_call'] = True
                inst['destroy_line'] = lineno
                break

    # Track widget refs that are added as children (auto-cleanup on parent destroy)
    child_refs = set()
    child_add_pat = re.compile(
        r'\.(?:add_child|insert_child_below|insert_child_above|'
        r'insert_child_at_index|set_child|add_actor)\s*\(\s*(this[._]\w+)'
    )
    for line in lines:
        m = child_add_pat.search(line.strip())
        if m:
            child_refs.add(m.group(1))

    # Detect if file has a destroy() or disable() method
    has_destroy = find_method_body(content, 'destroy') is not None
    has_disable = find_method_body(content, 'disable') is not None
    # Also detect _destroyPowerManager-style private destroy methods
    has_private_destroy = bool(re.search(
        r'(?:^|\s)_destroy\w*\s*\([^)]*\)\s*\{', content, re.MULTILINE
    ))

    return {
        'rel': rel,
        'creates': creates,
        'destroys': destroys,
        'instantiates': instantiates,
        'imports': imports,
        'has_destroy': has_destroy,
        'has_disable': has_disable,
        'has_private_destroy': has_private_destroy,
        'child_refs': child_refs,
        'content': content,
    }


# ---------------------------------------------------------------------------
# Ownership graph building
# ---------------------------------------------------------------------------

def build_ownership(file_scans, ext_dir):
    """Build ownership map: which file owns which objects.

    Returns:
        ownership: {file: {ref: {class, source_file, created_line, destroyed_line}}}
        import_map: {class_name: source_file} (global)
    """
    ownership = {}
    global_import_map = {}

    # Build global import map
    for scan in file_scans.values():
        for cls, source in scan['imports'].items():
            global_import_map[cls] = source

    # Build ownership from instantiations
    for rel, scan in file_scans.items():
        file_ownership = {}
        for inst in scan['instantiates']:
            ref = inst['stored_as']
            cls = inst['class']
            if not ref:
                continue
            source_file = global_import_map.get(cls)
            file_ownership[ref] = {
                'class': cls,
                'source_file': source_file,
                'created_line': inst['line'],
                'destroyed_line': inst['destroy_line'],
            }
        if file_ownership:
            ownership[rel] = file_ownership

    return ownership, global_import_map


def compute_ownership_depth(ownership, file_scans):
    """Compute max ownership chain depth.

    e.g., extension.js -> Manager -> Controller = depth 3
    """
    # Build parent-child edges
    children = {}  # file -> [child_files]
    for rel, refs in ownership.items():
        for ref_info in refs.values():
            child = ref_info.get('source_file')
            if child and child in file_scans:
                children.setdefault(rel, []).append(child)

    # BFS to find max depth
    # Find root files (files not owned by any other)
    owned_files = set()
    for rel, refs in ownership.items():
        for ref_info in refs.values():
            child = ref_info.get('source_file')
            if child:
                owned_files.add(child)

    roots = [f for f in file_scans if f not in owned_files]
    if not roots:
        roots = list(file_scans.keys())[:1]

    max_depth = 1
    for root in roots:
        visited = set()
        queue = [(root, 1)]
        while queue:
            node, depth = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            if depth > max_depth:
                max_depth = depth
            for child in children.get(node, []):
                if child not in visited:
                    queue.append((child, depth + 1))

    return max_depth


# ---------------------------------------------------------------------------
# Orphan detection
# ---------------------------------------------------------------------------

def detect_orphans(file_scans, ownership):
    """Detect orphaned resources in files that are owned by other files.

    An orphan is a resource created in a child module where:
    1. No matching cleanup exists in that module's destroy() method, OR
    2. The module has no destroy() method but creates resources, OR
    3. The module's destroy() is never called by its parent.

    Only flags resources in files that ARE owned by another file.
    """
    orphans = []

    # Determine which files are owned (instantiated by a parent)
    owned_files = set()
    parent_of = {}  # child_file -> parent_file
    for rel, refs in ownership.items():
        for ref, ref_info in refs.items():
            child = ref_info.get('source_file')
            if child and child in file_scans:
                owned_files.add(child)
                parent_of[child] = rel

    for rel, scan in file_scans.items():
        if rel not in owned_files:
            continue  # Only check owned files

        creates = scan['creates']
        destroys = scan['destroys']
        has_destroy = scan['has_destroy']
        has_disable = scan['has_disable']
        has_private_destroy = scan['has_private_destroy']
        has_cleanup_method = has_destroy or has_disable or has_private_destroy

        if not creates:
            continue

        # Gather all destroy refs and types
        destroy_refs = set()
        destroy_types = set()
        for d in destroys:
            if d.get('ref'):
                destroy_refs.add(d['ref'])
            destroy_types.add(d['type'])

        # Check if parent calls destroy on this object
        parent_rel = parent_of.get(rel)
        parent_calls_destroy = False
        if parent_rel and parent_rel in ownership:
            for ref, ref_info in ownership[parent_rel].items():
                if ref_info.get('source_file') == rel:
                    if ref_info.get('destroyed_line') is not None:
                        parent_calls_destroy = True
                        break

        # Case 1: Module creates resources but has no destroy/disable method
        if not has_cleanup_method:
            for c in creates:
                orphans.append({
                    'file': rel,
                    'line': c['line'],
                    'type': c['type'],
                    'pattern': c['pattern'],
                    'reason': f"no destroy()/disable() method in {rel}",
                })
            continue

        # Case 2: Module has destroy() but parent never calls it
        if not parent_calls_destroy:
            for c in creates:
                orphans.append({
                    'file': rel,
                    'line': c['line'],
                    'type': c['type'],
                    'pattern': c['pattern'],
                    'reason': f"parent does not call destroy() on {rel}",
                })
            continue

        # Refs that are added as widget children (auto-cleanup by parent widget)
        child_refs = scan.get('child_refs', set())

        # Also check if refs are set to null in cleanup methods — a form of
        # releasing references even when the resource auto-cleans itself
        nulled_refs = set()
        content = scan['content']
        for method_name in ('destroy', 'disable', '_destroy'):
            mb = find_method_body(content, method_name)
            if mb:
                _, _, body = mb
                for m in re.finditer(r'(this[._]\w+)\s*=\s*null', body):
                    nulled_refs.add(m.group(1))

        # Case 3: Module has destroy() which is called, but specific resources
        # are not cleaned up. Match by stored_as ref.
        for c in creates:
            stored = c.get('stored_as')
            if not stored:
                # Resource not stored — can't track, skip (no false positive)
                continue

            # Skip widgets added as children — auto-destroyed by parent widget
            if c['type'] == 'widget' and stored in child_refs:
                continue

            # Skip dbus makeProxyWrapper — creates a class, not an instance
            if c['type'] == 'dbus' and 'makeProxyWrapper' in c.get('pattern', ''):
                continue

            # Check if there's a matching destroy for this ref
            matched = False
            for d in destroys:
                d_ref = d.get('ref')
                if not d_ref:
                    continue
                # Direct match: this._foo used in both create and destroy
                if d_ref == stored:
                    matched = True
                    break
                # Stored ref is a sub-ref (e.g., stored this._handlerId,
                # destroy uses something.disconnect(this._handlerId))
                if stored in d.get('pattern', ''):
                    matched = True
                    break

            # Also count as matched if ref is nulled in cleanup method
            if not matched and stored in nulled_refs:
                matched = True

            if not matched:
                orphans.append({
                    'file': rel,
                    'line': c['line'],
                    'type': c['type'],
                    'pattern': c['pattern'],
                    'reason': f"{stored} created but not cleaned up in destroy()",
                })

    return orphans


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_resource_graph(ext_dir):
    """Build the complete resource graph for an extension directory."""
    js_files = find_js_files(ext_dir, exclude_prefs=True)
    if not js_files:
        return {
            'files': {},
            'ownership': {},
            'orphans': [],
            'summary': {
                'total_creates': 0,
                'total_destroys': 0,
                'orphan_count': 0,
                'files_scanned': 0,
                'ownership_depth': 0,
            },
        }

    # Scan all files
    file_scans = {}
    for fp in js_files:
        rel = os.path.relpath(fp, ext_dir)
        file_scans[rel] = scan_file(fp, ext_dir)

    # Build ownership
    ownership, _ = build_ownership(file_scans, ext_dir)

    # Compute ownership depth
    depth = compute_ownership_depth(ownership, file_scans)

    # Detect orphans
    orphans = detect_orphans(file_scans, ownership)

    # Build output
    files_output = {}
    total_creates = 0
    total_destroys = 0

    for rel, scan in file_scans.items():
        total_creates += len(scan['creates'])
        total_destroys += len(scan['destroys'])
        files_output[rel] = {
            'creates': scan['creates'],
            'destroys': scan['destroys'],
            'instantiates': scan['instantiates'],
        }

    return {
        'files': files_output,
        'ownership': ownership,
        'orphans': orphans,
        'summary': {
            'total_creates': total_creates,
            'total_destroys': total_destroys,
            'orphan_count': len(orphans),
            'files_scanned': len(file_scans),
            'ownership_depth': depth,
        },
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: build-resource-graph.py EXTENSION_DIR", file=sys.stderr)
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])
    if not os.path.isdir(ext_dir):
        print(f"Error: {ext_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    graph = build_resource_graph(ext_dir)
    print(json.dumps(graph, indent=2))


if __name__ == '__main__':
    main()
