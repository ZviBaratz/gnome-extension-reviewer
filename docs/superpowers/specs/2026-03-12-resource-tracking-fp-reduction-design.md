# Resource Tracking FP Reduction — Design Spec

## Problem

blur-my-shell has 7 false positive findings across 3 resource-tracking checks,
all stemming from cleanup pattern recognition gaps:

1. **`resource-tracking/no-destroy-method`** (3 hits, effects_manager.js) —
   `destroy_all()` method falls through all cleanup detection: `has_destroy`
   matches exact `destroy()`, `has_private_destroy` matches `_destroy\w*`,
   `has_custom_cleanup` regex omits `destroy_\w+` variants.

2. **`resource-tracking/destroy-not-called`** (2 hits, paint_signals.js) —
   `parent_of` dict stores only the last parent (dict overwrite).
   paint_signals.js has 5 parents; the last one (dash_to_dock.js) has
   `DestroyedLine: None` because its cleanup is in `destroy_dash()` (not
   recognized). applications.js has `DestroyedLine: 433` but is overwritten.

3. **`quality/constructor-resources`** (2 hits, effects_dialog.js) —
   `src/preferences/` path not excluded because `rel_parts[0]` is `src`,
   not `preferences`.

## Changes

### 1. `destroy_\w+` cleanup method recognition (`build-resource-graph.py`)

**a) `has_custom_cleanup` regex** (line 369-372):

Add `destroy_\w+` as an alternative in the regex:

```python
has_custom_cleanup = bool(re.search(
    r'(?:^|\s)(?:destroy_\w+|disconnect_all|_?cleanup\w*|close|shutdown|dispose|release)'
    r'\s*\([^)]*\)\s*\{',
    content, re.MULTILINE
))
```

**b) Dynamic method extraction in `scan_file()`** (after line 373):

Extract `destroy_\w+` method names from the file content inside `scan_file()`:

```python
extra_destroy_methods = set(re.findall(
    r'(?:^|\s)(destroy_\w+)\s*\(', content, re.MULTILINE
))
```

Include in the returned dict (line 375+): `'extra_destroy_methods': extra_destroy_methods`

**c) Cleanup method scan lists** (lines 333-335 and 581-582):

Both loops iterate over a hardcoded tuple of method names. Extend with
`extra_destroy_methods` from the scan dict:

```python
base_methods = ('destroy', 'disable', '_destroy', 'onDestroy',
                'disconnect_all', 'cleanup', '_cleanup',
                'close', 'shutdown', 'dispose', 'release')
for method_name in base_methods + tuple(extra_destroy_methods):
```

For line 333-335, `extra_destroy_methods` is available locally in
`scan_file()`. For line 581-582 in `detect_orphans()`, access it via
`scan.get('extra_destroy_methods', set())`.

### 2. Multi-parent ownership (`build-resource-graph.py`)

**a) `parent_of` structure** (lines 492-499):

Change from `dict[str, str]` to `dict[str, set[str]]`:

```python
parent_of.setdefault(child, set()).add(rel)
```

**b) `parent_calls_destroy` check** (lines 527-534):

Iterate over all parents instead of one:

```python
for parent_rel in parent_of.get(rel, set()):
    if parent_rel in ownership:
        for ref, ref_info in ownership[parent_rel].items():
            if ref_info.get('source_file') == rel:
                if ref_info.get('destroyed_line') is not None:
                    parent_calls_destroy = True
                    break
    if parent_calls_destroy:
        break
```

**c) `parent_manages_as_child` check** (lines 538-546):

Same iteration over all parents — `parent_of.get(rel, set())` returns a set,
so both 2b and 2c must loop over it:

```python
for parent_rel in parent_of.get(rel, set()):
    if parent_rel in file_scans:
        parent_child_refs = file_scans[parent_rel].get('child_refs', set())
        if parent_rel in ownership:
            for ref, ref_info in ownership[parent_rel].items():
                if ref_info.get('source_file') == rel:
                    if ref in parent_child_refs:
                        parent_manages_as_child = True
                        break
    if parent_manages_as_child:
        break
```

### 3. `src/preferences/` path exclusion (`check-quality.py`)

**Lines 418-419** — change from checking only `rel_parts[0]` to any component:

```python
if any(part in non_lifecycle_dirs for part in rel_parts):
```

### 4. Test fixtures

- Fixture for `destroy_\w+` recognition: class with `destroy_all()` creating
  signals — should NOT emit `no-destroy-method`.
- Fixture for multi-parent ownership: child class instantiated by 2 parents,
  only one calls cleanup — should NOT emit `destroy-not-called`.
- Fixture for `src/preferences/` path: `.connect()` in constructor inside
  `src/preferences/` — should NOT emit `constructor-resources`.

## Files Modified

| File | Change |
|------|--------|
| `skills/ego-lint/scripts/build-resource-graph.py` | `destroy_\w+` regex + dynamic method extraction + multi-parent `parent_of` |
| `skills/ego-lint/scripts/check-quality.py` | `any(part in non_lifecycle_dirs ...)` |
| `tests/fixtures/` | 3 new test fixtures |
| `tests/run-tests.sh` | Assertions for new fixtures |

## Files NOT Modified

- `check-resources.py` — delegates to `build-resource-graph.py` for orphan
  detection; no changes needed.
- `rules/patterns.yaml` — no pattern rules involved.
- `skills/ego-lint/references/rules-reference.md` — no new rule IDs.

## Success Criteria

- blur-my-shell field test: 7 FP findings eliminated (3 no-destroy-method,
  2 destroy-not-called, 2 constructor-resources)
- All existing tests pass (748 assertions)
- No unintended baseline changes in other field test extensions
- New test fixtures cover all three fix paths
