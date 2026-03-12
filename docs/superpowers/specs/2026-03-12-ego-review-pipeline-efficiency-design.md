# ego-review Pipeline Efficiency — Design Spec

## Problem

ego-review sessions (both interactive `/ego-review` and headless field-test
reviews) spend significant time on work that ego-lint has already performed:

1. **Phase 2** tells the reviewer to re-run `build-resource-graph.py` even
   though ego-lint already ran it and reported resource-tracking findings.
2. **Phase 3** tells the reviewer to manually audit GSettings signal leaks and
   D-Bus connectSignal leaks, which ego-lint now catches deterministically
   (`lifecycle/gsettings-signal-leak`, `lifecycle/dbus-signal-leak`).
3. **Phase 5a** tells the reviewer to iterate all 46 AI checklist items, even
   though 24 are fully automated by ego-lint. Reading and cross-referencing
   those 24 items against lint JSON costs tokens without adding value.

Estimated saving: significant token and time reduction per ego-review session
(exact amount varies by extension size).

## Changes

### 1. Phase 2: Use lint resource-tracking findings (SKILL.md)

**Before:** Steps 3-7 instruct the reviewer to run `build-resource-graph.py`,
review the graph summary, classify each orphan, review ownership chains, and
build a resource tracking table.

**After:** Replace steps 3-7 with:

3. **Reference the resource-tracking findings from Phase 0 lint.** ego-lint
   already ran `build-resource-graph.py` and `check-resources.py`. Use the
   `resource-tracking/*` findings from the lint results as the starting point.
4. **For each resource-tracking FAIL/WARN from lint**: read the cited file:line
   to verify it's a true leak. Classify as: TRUE LEAK (blocking) | JUSTIFIED
   (note why) | FALSE POSITIVE (skip). For true leaks, include the fix in the
   report.
5. **For ownership chains**: if lint reports orphans, verify parent calls
   child's `destroy()` in its own `disable()`/`destroy()` and that destroy
   order is reverse of creation. If lint reports 0 orphans, do a brief
   spot-check of 1-2 ownership chains to verify graph accuracy, but do not
   perform a full ownership walk.
6. **Resource tracking table**: if the report needs a resource tracking table,
   build it from the lint JSON's `resource-tracking/*` findings rather than
   re-running `build-resource-graph.py --format=table`.

Keep steps 8-12 unchanged (async guards, cleanup ordering, _destroyed flag,
session mode handling) — these require semantic judgment.

### 2. Phase 3: Collapse to delta-only audit (SKILL.md)

**Before:** 4 steps including reviewing the resource graph, spot-checking 2-3
entries, listing resource types the graph misses (GSettings, custom cleanup,
D-Bus connectSignal), and conditionally doing a full manual grep.

**After:** Replace with:

1. **Abbreviate this phase** if Phase 2 found 0 orphans AND Phase 0 lint has
   no `resource-tracking/*` or `lifecycle/*` FAILs/WARNs. In this case, do a
   single spot-check: pick 1 resource entry from the graph and verify by
   reading the cited file:line that create/destroy are correctly paired.
2. **Otherwise**, for each resource-tracking or lifecycle FAIL/WARN from lint,
   verify by reading the cited code — focus on issues ego-lint cannot judge
   semantically (e.g., whether a cleanup pattern is architecturally correct).
3. **Check for resource types lint still misses**: custom cleanup methods
   (`_cleanup()`, `_teardown()`, `_clear()`) not recognized by the resource
   graph. GSettings signal leaks and D-Bus connectSignal leaks are now
   automated — do not re-check manually.
4. **Only do a full manual grep** if lint reported orphans AND you suspect the
   graph missed resources after the spot-checks above.

### 3. Phase 5a: Skip automated AI checklist items (SKILL.md)

**Before:** "For each checklist item" (all 46), branch on Automated status,
use lint result or search manually.

**After:** Replace step 1 with three sub-steps:

1. **Automated items (24 of 46):** Pull the count directly from Phase 0 lint.
   Items 1-2, 4-5, 8, 11-12, 14-15, 18-26, 28, 34, 36, 41-42, 44 are fully
   automated. Count how many triggered (any lint WARN/FAIL matching the check
   IDs listed in the checklist). Do NOT re-read the checklist descriptions or
   re-search the code for these items.

2. **Manual-only items (15 of 46):** Search extension source for items 3, 7,
   9, 13, 27, 31-32, 35, 37-40, 43, 45-46. These require semantic judgment
   that ego-lint cannot provide.

3. **Partial items (7 of 46):** Items 6, 10, 16-17, 29-30, 33. Use ego-lint's
   result as a starting point, then apply manual judgment for aspects ego-lint
   cannot cover (e.g., item 33: ego-lint counts comment density but cannot
   judge whether comments restate the obvious).

4. **Combine:** automated triggered count + manual triggered count + partial
   triggered count = total score. Apply thresholds and provenance adjustment
   as before.

### 4. Efficiency notes for headless sessions (review-prompt.md)

**Before:** The review prompt tells the headless reviewer to skip Phase 0 and
use lint JSON, but says nothing about the Phase 2/3/5a optimizations.

**After:** Add a section after the Phase 0 override:

```
## Efficiency Notes

- Phase 2: Do NOT re-run build-resource-graph.py — use resource-tracking
  findings from the lint JSON above. Spot-check 1-2 ownership chains even
  if lint reports 0 orphans.
- Phase 3: Abbreviate if lint shows 0 resource-tracking/lifecycle FAILs.
  Only manually check for custom cleanup methods lint cannot detect.
- Phase 5a: Do NOT iterate all 46 AI checklist items. Count the 24
  automated triggers from lint JSON, then manually check only the 22
  non-automated items (15 manual + 7 partial). Combine counts for the
  final score.
```

## Files Modified

| File | Change |
|------|--------|
| `skills/ego-review/SKILL.md` | Phase 2 steps 3-7, Phase 3 steps 1-4, Phase 5a step 1 |
| `scripts/review-prompt.md` | Add "Efficiency Notes" section |

## Files NOT Modified

- `skills/ego-review/references/ai-slop-checklist.md` — already has correct
  "Automated: Yes/No/Partial" annotations; no structural changes needed
- No scripts, no tests — this is a prompt-only change

## Success Criteria

- ego-review sessions should not re-run `build-resource-graph.py`
- ego-review sessions should not manually search for GSettings or D-Bus signal
  leaks (now automated by ego-lint)
- Phase 5a should only iterate ~22 items (15 manual + 7 partial) instead of 46
- Review report quality should not degrade — all 6 sections still produced
  with the same level of detail for findings that require manual judgment
- Ownership chain verification preserved via spot-checks even in 0-orphan case
