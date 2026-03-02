# Field Test: V-Shell

**Date**: 2026-03-02
**Target**: [V-Shell](https://github.com/G-dH/vertical-workspaces) v108 (version-name 49.13)
**Extension**: `vertical-workspaces@G-dH.github.com` — GNOME 45-49, 28 JS files, 19201 lines, GPL-3.0

## Pre-flight

- **Extension**: V-Shell (`vertical-workspaces@G-dH.github.com`)
- **Source**: `~/.local/share/gnome-shell/extensions/vertical-workspaces@G-dH.github.com/`
- **GNOME versions**: 45, 46, 47, 48, 49
- **File count**: 28 JS files, 19201 lines
- **License**: GPL-3.0 (LICENSE file)
- **Session modes**: unlock-dialog, user
- **Why this extension**: Approved on EGO, broad GNOME version range (45-49), heavy Shell UI overrides (workspace, dash, app display, panel), prototype override pattern, constructor-resources pattern, large codebase (16k+ non-blank lines), lib/ modular structure

### Key Patterns
- Overrides GNOME Shell UI components via lib/ modules (workspace, dash, appDisplay, panel, overview, etc.)
- Prototype overrides (2 detected)
- Constructor-resources pattern (51 instances — `.connect()/.connectObject()` in constructors)
- Broad private API access (180+ locations)
- Session modes: unlock-dialog + user (requires careful lifecycle handling)
- R-SEC-09 (extension system interference, 6 hits)
- optionsFactory.js imports Adw/Gtk (shared between prefs and extension)

## Step 1: ego-lint

```bash
./ego-lint --verbose ~/.local/share/gnome-shell/extensions/vertical-workspaces@G-dH.github.com/
```

### Results

| Status | Count |
|--------|-------|
| PASS   | 177   |
| FAIL   | 23    |
| WARN   | 143   |
| SKIP   | 17    |
| **Total** | **360** |

Exit code: 1

### Classification of Each FAIL

| Rule | File:Line | TP/FP/Expected | Notes |
|------|-----------|----------------|-------|
| R-VER44-02 | lib/dash.js:1302 | FP (runtime-guarded) | `if (global.compositor) { ... } else { Meta.later_remove() }` — old API only reached on GNOME <48 |
| R-VER46-07 | lib/windowAttentionHandler.js:18 | FP (feature-flag) | `const shellVersion46 = !Clutter.Container` — used as boolean, not as API call |
| R-VER46-07 | lib/appDisplay.js:41 | FP (feature-flag) | Same pattern: `const shellVersion46 = !Clutter.Container` |
| R-VER48-02 (x2) | lib/workspaceAnimation.js:343-344 | FP (runtime-guarded) | `if (Meta.disable_unredirect_for_display) ... else global.compositor.disable_unredirect()` |
| R-VER49-02 (x13) | multiple files | FP (runtime-guarded) | All use `Clutter.ClickAction \|\| Clutter.ClickGesture` fallback or `if (Clutter.ClickAction)` guards |
| imports/no-gtk-in-extension (x2) | lib/optionsFactory.js:12,15 | FP (prefs-only module) | File only imported by `prefs.js:19`, never by extension.js |
| init/shell-modification (x3) | lib/overviewBackground.js:105, lib/appDisplay.js:64,79 | FP (called from enable) | Constructors called from `_initModules()` inside `enable()` flow |

**Revised assessment**: All 23 FAILs are false positives on manual inspection. The 18 version-compat FAILs are all guarded by runtime feature detection (`Clutter.ClickAction || Clutter.ClickGesture`, `!Clutter.Container` flag, `if (global.compositor)` branching). ego-lint's static analysis cannot trace conditional branches, so it flags the deprecated API reference regardless of the guard. The 2 import violations are in a prefs-only module (`optionsFactory.js` is only imported by `prefs.js`). The 3 init violations are in constructors only called from within `enable()`.

**Implication for ego-lint**: Multi-version extensions with runtime feature detection will always produce version-compat false positives under the current static analysis approach. Fixing this would require control-flow analysis or an allowlist mechanism for guarded patterns.

### Classification of Key WARNs (143 total)

| Rule | Count | Legitimate? | Notes |
|------|-------|-------------|-------|
| quality/constructor-resources | 51 | Yes | `.connect()/.connectObject()` in GObject constructors — V-Shell's widgets manage their own lifecycle |
| R-SLOP-11 | 23 | Yes | Single-use constants — defensive coding style, not AI slop |
| lifecycle/untracked-timeout | 15 | Yes | GLib timeouts without stored IDs |
| R-SLOP-38 | 8 | Yes | Long parameter names — descriptive naming |
| R-SEC-09 | 6 | Yes | Extension system interference — core to V-Shell's purpose |
| R-QUAL-31 | 5 | Yes | `_onDestroy` naming — non-standard but functional |
| lifecycle/destroy-no-null | 5 | Yes | Missing null-after-destroy |
| R-VER48-04 | 3 | WARN/advisory | `vertical: true` deprecated in 48 |
| lifecycle/prototype-override | 2 | Yes | Core pattern for V-Shell |
| accessibility/* | 2 | Yes | Missing accessible names/roles |
| quality/private-api | 1 (180+ locations) | Yes | Extensive private API — expected for Shell customizer |
| quality/code-volume | 1 | Yes | 16293 lines — large but expected |
| quality/file-complexity | 1 | Yes | prefs.js: 2233 lines |
| quality/debug-volume | 1 | Yes | 68 console.debug calls |

## Step 2: ego-review

Run via ego-submit parallel pipeline (3 agents):
- Agent 1: ego-lint + package validation
- Agent 2: lifecycle/signals/security (Phases 2-4)
- Agent 3: quality/AI patterns/metadata (Phases 5-5a + 4)

### Verdict

**LIKELY APPROVED** | **Risk: LOW** (2 risk points)

### Blocking Issues

| # | Issue | File:Line | Category |
|---|-------|-----------|----------|
| B1 | Signal disconnect on wrong object | lib/dash.js:189 | Lifecycle/signals |

**B1 detail**: `this._newWindowConId` connected on `global.display` (line 169) but disconnected on `global.windowManager` (line 189). The `window-created` signal on `global.display` is never disconnected when the Dash module is disabled. Fix: change `global.windowManager` to `global.display`.

### Justification Required

| # | Item | File:Line | Notes |
|---|------|-----------|-------|
| J1 | System keybinding modification | extension.js:606-687 | Writes to `org.gnome.desktop.wm.keybindings`, reversed on disable |
| J2 | System setting modification | lib/layout.js:95 | Writes `enable-hot-corners`, reversed on disable |
| J3 | Extension order manipulation | extension.js:107-109 | Modifies `_extensionOrder` private API for Dash-to-Dock compat |
| J4 | Clipboard write | lib/search.js:346-347 | `St.Clipboard.set_text()`, user-initiated, write-only |

### Advisory Issues

| # | Severity | File:Line | Description |
|---|----------|-----------|-------------|
| A1 | LOW | extension.js:297 | Untracked `GLib.idle_add()` in startup-only path |
| A2 | LOW | lib/windowPreview.js:374 | Signal ID stored on foreign MetaWindow object |
| A3 | LOW | lib/util.js:798 | Random GType name via `Math.random()` — known reload workaround |
| A4 | LOW | 15 locations | Untracked one-shot timer return values in override methods |
| A5 | LOW | 3 locations | Icon-only `St.Button` without `accessible_name` |
| A6 | INFO | lib/appDisplay.js:140 | Legacy `log()` call — should be `console.error()` |
| A7 | INFO | lib/overviewControls.js:281 | Typo: "hed" → "had" |

### Issues ego-lint Could Not Detect

1. **Signal disconnect on wrong object (B1)**: `dash.js:189` disconnects on `global.windowManager` instead of `global.display`. Requires semantic understanding that the signal ID was obtained from a different object. ego-lint's connect/disconnect balance heuristic flagged the imbalance (116 vs 43) but couldn't pinpoint which specific disconnect was wrong.

2. **Version-conditional code correctness**: ego-lint flagged all `Clutter.ClickAction` usage as FAIL, but manual review confirmed every instance uses `Clutter.ClickAction || Clutter.ClickGesture` runtime fallback. Static analysis cannot determine that the deprecated API is never reached on target GNOME versions.

3. **optionsFactory.js import scope**: ego-lint flagged GTK/Adw imports as FAIL because the file is in `lib/`, but cross-file import analysis shows it's only imported by `prefs.js`. Requires import-graph traversal.

4. **Constructor call context**: ego-lint flagged shell modifications in constructors, but the constructors are only called from `_initModules()` inside `enable()`. Requires call-graph analysis.

5. **Resource tracking table completeness**: Manual review of ~40 resources found all properly tracked with create/destroy symmetry. ego-lint's signal balance heuristic (116 connect vs 43 disconnect) couldn't account for `connectObject`/`disconnectObject` patterns and destroy-handler cleanup in overrides.

### Resource Summary

| Category | Count | Balanced | Notes |
|----------|-------|----------|-------|
| Signal connections | ~40+ | 39+ balanced, 1 unbalanced (B1) | Override signals cleaned via widget destroy handlers |
| Timer sources | ~15+ | All balanced | Tracked in `_timeouts` objects |
| GSettings connections | All | Balanced | `_connectionIds[]` array, bulk disconnect in `Options.destroy()` |
| File monitors | 0 | N/A | |
| D-Bus proxies | 0 | N/A | |

### AI Pattern Analysis

**Score**: 0/46 triggered | **Provenance**: 5/5 | **Assessment**: PASS

Evidence of genuine authorship: complex domain-specific algorithms (custom `UnalignedLayoutStrategy`, fuzzy search with scoring), version-conditional code via feature detection (not version strings), inline comments reflecting real debugging experience (e.g., "conky is sticky but should never get above other windows during ws animation"), battle-tested workarounds for Dash-to-Dock compatibility.

## Step 3: ego-simulate

### Score

| Taxonomy Reason | Weight | Evidence |
|-----------------|--------|----------|
| #13 Signal leak | 5 | lib/dash.js:189 — disconnect on wrong object |
| #20 Excessive code volume | 3 | ~15,500 non-blank lines > 8,000 threshold |
| **Total** | **8** | |

No ego-lint FAILs added to score (all 23 are false positives with runtime guards).

### Verdict

**Score: 8** — May pass, but expect revision requests

The signal leak is the only functional issue. The code volume concern is inherent to V-Shell's scope as a comprehensive shell customizer. A reviewer familiar with V-Shell would request the disconnect fix and comment on the legacy `log()` call, then approve.

### Calibration Check

V-Shell is approved on EGO. Expected: score < 10 (below rejection threshold).

**Result: PASS** — Score 8 is below the 10-point rejection threshold, consistent with an approved extension that has one genuine bug. The high WARN count (143) and FAIL count (23) did NOT inflate the simulate score because:
- All 23 ego-lint FAILs were correctly identified as false positives (runtime feature detection)
- ego-lint WARNs do not contribute to the simulate score per the scoring rules
- The signal leak found by manual review (not by ego-lint) was the only taxonomy trigger

**Cross-tool calibration**:
- ego-review risk: 2 (LOW) — finding-category weighted
- ego-simulate score: 8 — taxonomy-weighted (includes code volume penalty)
- Both agree: signal disconnect bug is the only blocking issue

## Fixes Implemented

No fixes were applied to the extension (read-only field test). Findings reported for upstream developer action.

### Recommended Fixes (priority order)

| # | Priority | Fix | Impact |
|---|----------|-----|--------|
| 1 | BLOCKING | `dash.js:189`: `global.windowManager` → `global.display` | Fixes signal leak, drops simulate score by 5 |
| 2 | Advisory | `appDisplay.js:140`: `log(...)` → `console.error(...)` | Removes reviewer comment |
| 3 | Advisory | `overviewControls.js:281`: "hed" → "had" | Typo fix |
| 4 | Package | Exclude `.claude/` directory from submission zip | Required for EGO packaging |

### False Positives to Address in ego-lint

| Rule | Root Cause | Suggested Fix |
|------|-----------|---------------|
| R-VER* (all version rules) | Static analysis cannot trace runtime feature guards like `Clutter.ClickAction \|\| Clutter.ClickGesture` | Consider: (1) allowlist pattern for `X \|\| Y` fallback, (2) `if (X)` guard detection, (3) `!X` feature-flag detection |
| imports/no-gtk-in-extension | File in `lib/` but only imported by `prefs.js` | Requires import-graph analysis; consider: single-hop import check (who imports this file?) |
| init/shell-modification | Constructors called from within `enable()` flow | Requires call-graph analysis; consider: mark as WARN instead of FAIL for constructor context |

## Regression Verification

_(Not applicable — read-only field test, no changes made to ego-lint)_

## Calibration Lessons Learned

1. **Multi-version extensions produce systemic version-compat false positives**: V-Shell's runtime feature detection pattern (`Clutter.ClickAction || Clutter.ClickGesture`, `!Clutter.Container` as boolean flag, `if (global.compositor)` branching) is invisible to static analysis. All 23 ego-lint FAILs were false positives. This is the single largest accuracy gap for extensions targeting 3+ GNOME versions.

2. **ego-lint's signal balance heuristic (connect vs disconnect count) is a poor proxy for correctness**: The 116:43 ratio looked alarming but manual review found only 1 real leak out of ~40 tracked connections. The imbalance is caused by `connectObject`/`disconnectObject` patterns and widget destroy-handler cleanup, which ego-lint counts differently from manual `connect`/`disconnect` pairs.

3. **The real bug (B1) was only detectable by semantic analysis**: The disconnect-on-wrong-object bug at `dash.js:189` cannot be caught by pattern matching — it requires understanding that a signal ID obtained from `global.display.connect()` must be disconnected on `global.display`, not `global.windowManager`. This validates ego-review's value: the manual cross-reference in Phase 3 (signal audit) is the only phase that could find this.

4. **Import segregation needs import-graph awareness**: `optionsFactory.js` lives in `lib/` but is exclusively imported by `prefs.js`. The current file-path heuristic (`lib/` = extension-side) produces false positives for shared-code architectures. A single-hop import check would resolve this.

5. **ego-simulate calibrates well against approved extensions**: Score 8 (below 10 rejection threshold) for an approved extension with one genuine bug is a reasonable result. The code-volume penalty (#20, weight 3) is appropriate — reviewers DO spend extra time on large extensions, even well-written ones.

6. **Parallel 3-agent pipeline effective for large extensions**: 28 JS files across 3 agents (lint+packaging / lifecycle+signals+security / quality+AI+metadata) completed in ~5 minutes wall-clock vs estimated ~10 minutes sequential. Agent isolation was clean — no deduplication conflicts.
