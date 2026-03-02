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
| R-VER44-02 | lib/dash.js:1302 | TP | `Meta.later_remove()` removed in GNOME 44 — but V-Shell targets 45+, so this is dead code |
| R-VER46-07 | lib/windowAttentionHandler.js:18 | TP | `Clutter.Container` removed in 46 |
| R-VER46-07 | lib/appDisplay.js:41 | TP | `Clutter.Container` removed in 46 |
| R-VER48-02 (x2) | lib/workspaceAnimation.js:343-344 | TP | `Meta.disable_unredirect_for_display` → `global.compositor` |
| R-VER48-04 (x3) | multiple | Advisory shown as WARN | `vertical: true` → `orientation: Clutter.Orientation.VERTICAL` |
| R-VER49-02 (x13) | multiple files | TP | `Clutter.ClickAction` removed in 49 → `Clutter.ClickGesture` |
| imports/no-gtk-in-extension (x2) | lib/optionsFactory.js:12,15 | TP/Borderline | Adw/Gtk imported in lib/ file — shared prefs/extension code |
| init/shell-modification (x3) | lib/overviewBackground.js:105, lib/appDisplay.js:64,79 | TP | Shell modification at module scope |

All 23 FAILs are true positives or borderline. The version-compat FAILs (18 of 23) indicate V-Shell uses version-conditional code paths but declares wide GNOME support — reviewers would need to verify the compat logic. The import segregation violations (2) reflect shared code architecture.

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

_(To be completed in dedicated ego-submit session)_

### Verdict

**TBD**

### Blocking Issues

| # | Issue | File:Line | Category |
|---|-------|-----------|----------|
|   |       |           |          |

### Issues ego-lint Could Not Detect

_(To be completed)_

### AI Pattern Analysis

**Score**: TBD | **Assessment**: TBD

## Step 3: ego-simulate

_(To be completed in dedicated ego-submit session)_

### Score

| Taxonomy Reason | Weight | Evidence |
|-----------------|--------|----------|
|                 |        |          |
| **Total**       |        |          |

### Verdict

TBD

### Calibration Check

V-Shell is approved on EGO. Expected: score < 10 (below rejection threshold). The high WARN count (143) and FAIL count (23) may challenge this — key question is whether ego-simulate correctly weighs version-compat issues (which are usually handled by per-version submission) vs genuine lifecycle issues.

## Fixes Implemented

_(To be completed post-pipeline)_

## Regression Verification

_(To be completed post-pipeline)_

## Calibration Lessons Learned

_(To be completed post-pipeline)_
