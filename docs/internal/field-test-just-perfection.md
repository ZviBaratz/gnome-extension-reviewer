# Field Test #10: Just Perfection

## Pre-flight

- **Extension**: Just Perfection (`just-perfection-desktop@just-perfection`)
- **Source**: https://github.com/jrahmatzadeh/just-perfection
- **GNOME versions**: 45, 46, 47, 48, 49, 50
- **File count**: 7 JS files, 2 CSS files; ~5,300 JS lines (Manager.js alone is 1,636 non-blank)
- **License**: GPL-3.0-only (in repo root, not in `src/`)
- **Why this extension**: Most popular GNOME extension; exercises connectObject/disconnectObject signal management (67 signals), prototype backup/restore via `#originals` map, `src/` directory layout, GNOME 50 support (widest version range), CSS-heavy (23.7%), private field usage (`#timeoutIds`, `#originals`, `#shellVersion`), 20 Shell.ui imports

## Step 1: ego-lint

```bash
./ego-lint --verbose /tmp/just-perfection/src
```

### Results (before fixes)

| Status | Count |
|--------|-------|
| PASS   | 202   |
| FAIL   | 3     |
| WARN   | 414   |
| SKIP   | 12    |
| Exit   | 1     |

### Classification of Each FAIL

| Rule | File:Line | TP/FP | Root Cause (if FP) |
|------|-----------|-------|-------------------|
| `license` | — | **FP** | LICENSE in repo root, not in `src/`; no parent-dir fallback for src/ layout |
| `R-VER48-07` | stylesheet.css:167 | TP | `.quick-menu-toggle` renamed to `.quick-toggle-has-menu` in GNOME 48 |
| `metadata/future-shell-version` | — | TP | GNOME 50 > CURRENT_STABLE (49) |

### Classification of Key WARNs

| Rule | Count | Classification | Notes |
|------|-------|---------------|-------|
| R-SLOP-01 (JSDoc @param) | 129 | **FP** | Provenance score=3 but threshold was >=4; PR #23 fixes threshold to >=3 |
| R-SLOP-02 (JSDoc @returns) | 271 | **FP** | Same root cause as R-SLOP-01 |
| `lifecycle/prototype-override` | 5 (3 unique) | TP + **bug** | Advisory is valid (prototypes restored via close() chain). Regex catches both override AND restore → duplicates |
| `metadata/uuid-matches-dir` | 1 | **FP** | Dir is `src`, not UUID; meaningless for src/ layout |
| `metadata/session-modes-consistency` | 1 | **FP** | `sessionMode.isLocked` used as guard — not lock screen functionality |
| `quality/impossible-state` | 1 | **FP** | Same isLocked guard pattern |
| `quality/comment-density` | 1 | **FP** | SupportNotifier.js has 40% comments from thorough hand-written JSDoc |
| `metadata/deprecated-version` | 1 | TP | `version` field ignored by EGO for GNOME 45+ |
| `quality/file-complexity` | 1 | TP | Manager.js 1,636 non-blank lines |
| `quality/private-api` | 1 | TP | statusArea access (legitimate for a UI tweaker) |
| `disclosure/private-api` | 1 | TP | Private API not disclosed in metadata description |

## Fixes Implemented

Split across 3 PRs per one-concern-per-PR convention:

### PR: fix/src-layout-license (closes #26)

| Rule/Check | Root Cause | Fix |
|------------|-----------|-----|
| `license` (FAIL) | No parent-dir fallback for src/ layout | `ego-lint.sh`: check parent dir when `basename == "src"` |
| `metadata/uuid-matches-dir` | Dir is `src` for src/ layout | `check-metadata.py`: skip when `dir_name == "src"` |

### PR: fix/islocked-guard (closes #27)

| Rule/Check | Root Cause | Fix |
|------------|-----------|-----|
| `session-modes-consistency` | `isLocked` is always a guard | `check-metadata.py`: narrow regex to `sessionMode.currentMode` only |
| `quality/impossible-state` | `isLocked` is always a guard | `check-quality.py`: remove `isLocked` from check, keep `currentMode` comparisons |
| `quality/comment-density` | 40% threshold too aggressive | `check-quality.py`: raise threshold from 40% to 50% |

### PR: fix/proto-override-dedup (closes #28)

| Rule/Check | Root Cause | Fix |
|------------|-----------|-----|
| `lifecycle/prototype-override` (dupes) | Regex matches override + restore | `check-lifecycle.py`: deduplicate by `(file, prototype)` key |

### Test Fixtures Added

| Fixture | What It Tests |
|---------|--------------|
| `src-license-fallback@test` | License found in parent dir for src/ layout; UUID-dir skip |
| `islocked-guard@test` | `sessionMode.isLocked` guard not flagged as impossible-state or session-modes inconsistency |
| `proto-override-dedup@test` | Each prototype warned only once despite override + restore pattern |

### Existing Fixture Updated

| Fixture | Change | Reason |
|---------|--------|--------|
| `ai-slop@test` | `sessionMode.isLocked` → `sessionMode.currentMode !== 'unlock-dialog'` | `isLocked` no longer triggers impossible-state (by design) |

## Results (after all fixes)

| Status | Before | After | Change |
|--------|--------|-------|--------|
| FAIL   | 3      | 2     | -1 (license FP fixed) |
| WARN   | 414    | 408   | -6 (5 FPs + 2 dupes fixed) |

**With PR #23 merged** (provenance threshold >=3): WARNs would drop to ~8, all true positives.

## Calibration Lessons Learned

1. **`sessionMode.isLocked` is always a guard**: Reading lock state to decide behavior is defensive coding, not lock screen functionality. Only `currentMode === 'unlock-dialog'` comparisons suggest active lock screen mode usage.

2. **`src/` layout needs holistic support**: License check and UUID-dir match didn't handle src/ layout. Multiple checks already had src/ fallbacks (CSS, prefs, metadata), but these two were missed.

3. **Prototype override + restore creates duplicates**: When an extension stores originals and restores them (Just Perfection's `#originals` map pattern), the same regex catches both the override and the restore. Deduplication by `(file, prototype_name)` is essential.

4. **Comment-density threshold interacts with provenance**: Well-documented hand-written code (provenance=3) naturally has higher comment density (40%+) from thorough JSDoc. The 40% threshold was too aggressive; 50% avoids FPs while still catching AI slop (typically 55-70%).

5. **Just Perfection validates PR #23**: Provenance score=3 with 400 JSDoc warnings confirms the threshold change from >=4 to >=3 is needed.
