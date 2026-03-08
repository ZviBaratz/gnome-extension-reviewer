# Regression Report: ego-lint + ego-review Field Test

**Date**: 2026-03-08
**ego-lint version**: 05523f9 (`fix(ego-lint): make R-LIFE-25 bare connectSignal always FAIL`)
**Review tool**: ego-review via headless Claude ($4 budget, parallel 3)
**Extensions tested**: 10 (all reviewed, **0 timed out** — vs 4/10 in 03-07)

## 1. Summary Table

| Extension | Lint Exit | PASS | FAIL | WARN | SKIP | Changed | Review Verdict |
|---|---|---|---|---|---|---|---|
| hara-hachi-bu | 0 | 208 | 0 | 9 | 23 | No | LIKELY APPROVED |
| tiling-shell | 1 | 139 | 3 | 5 | 51 | No | NEEDS REVISION |
| v-shell | 1 | 188 | 2 | 91 | 17 | Yes (+2F) | NEEDS REVISION |
| gsconnect | 1 | 172 | 11 | 134 | 17 | Yes (+1W-8R) | NEEDS REVISION |
| appindicator | 1 | 187 | 10 | 59 | 14 | Yes (+1F) | NEEDS REVISION |
| clipboard-indicator | 1 | 197 | 3 | 24 | 17 | Yes (+1F+1W-1R) | NEEDS REVISION |
| blur-my-shell | 1 | 193 | 4 | 40 | 17 | Yes (+1F+2W-5R) | NEEDS REVISION |
| dash-to-panel | 1 | 173 | 9 | 64 | 17 | Yes (+3W-5R) | NEEDS REVISION |
| media-controls | 1 | 188 | 4 | 28 | 17 | Yes (+2F-1R) | NEEDS REVISION |
| just-perfection | 1 | 204 | 1 | 13 | 12 | Yes (+1F+1W-1R) | NEEDS REVISION |
| **Totals** | — | **1849** | **47** | **467** | **202** | **8/10** | 10 ok, 0 timeout |

### Delta vs 2026-03-05 baseline AND 2026-03-07 run

| Metric | 03-05 | 03-07 | 03-08 | Delta (05→08) | Delta (07→08) |
|---|---|---|---|---|---|
| PASS | 1799 | 1834 | 1849 | +50 | +15 |
| FAIL | 55 | 56 | 47 | **-8** | **-9** |
| WARN | 473 | 476 | 467 | **-6** | **-9** |
| SKIP | 191 | 202 | 202 | +11 | 0 |
| Changed | — | 5/10 | 8/10 | — | — |
| New findings | — | 7 | 16 | — | — |
| Resolved | — | 2 | 21 | — | — |
| Reviews completed | — | 6/10 | **10/10** | — | — |
| New FPs | — | 1 | **0** | — | — |

The +15 PASS from 03-07 comes from new checks producing PASS results (R-LIFE-27, expanded gsettings-signal-leak, dbus-signal-leak improvements). The -9 FAIL/-9 WARN reflects FP elimination (R-SLOP-01, R-DEPR-06, R-VER48-02) and improved exemptions (service/ directory, init/shell-modification).

## 2. New Findings (16 total, all TP)

| Extension | Check | Severity | Detail | Cause |
|---|---|---|---|---|
| v-shell | css/shell-class-override | FAIL | `.osd-window` override | PR #57 CSS class list expansion |
| v-shell | lifecycle/gsettings-signal-leak | FAIL | 3 bare connects in optionsFactory/settings | PR #87 helper class detection |
| gsconnect | resource-tracking/ownership | WARN | Orphan count improved 19→13 | PR #88 service/ exemption |
| appindicator | lifecycle/gsettings-signal-leak | FAIL | 3 bare connects in prefs pages | PR #87 helper class detection |
| clipboard-indicator | lifecycle/stage-actor-leak | FAIL | `_historyLabel` not removed from stage | R-LIFE-22 (already caught in 03-07) |
| clipboard-indicator | lifecycle/messagetray-source-leak | WARN | `_notifSource` not destroyed | R-LIFE-24 (already caught in 03-07) |
| blur-my-shell | lifecycle/destroy-no-call | WARN | `.destroy` without `()` in coverflow_alt_tab.js | R-LIFE-23 (already caught in 03-07) |
| blur-my-shell | lifecycle/gsettings-signal-leak | FAIL | 1 bare connect in preferences | PR #87 helper class detection |
| blur-my-shell | resource-tracking/ownership | WARN | Orphan count improved 12→11 | PR #86 no-destroy-method FP reduction |
| dash-to-panel | lifecycle/module-scope-prototype | WARN | `TaskbarAppIcon.prototype.scaleAndFade` | R-LIFE-27 (PR #83) |
| dash-to-panel | lifecycle/module-scope-prototype | WARN | `TaskbarAppIcon.prototype.undoScaleAndFade` | R-LIFE-27 (PR #83) |
| dash-to-panel | lifecycle/module-scope-state | WARN | Module-scope `iconCacheMap` Map | R-LIFE-26 (already caught in 03-07) |
| media-controls | lifecycle/dbus-signal-leak | FAIL | 2 bare `proxy.connectSignal()` | PR #91 always-FAIL + narrow auto-cleanup |
| media-controls | lifecycle/gsettings-signal-leak | FAIL | 28 bare `settings.connect()` | PR #87 helper class detection |
| just-perfection | R-QUAL-36 | WARN | CRITICAL notification urgency | Pattern rule (already caught in 03-07) |
| just-perfection | lifecycle/gsettings-signal-leak | FAIL | 1 bare connect in SupportNotifier | PR #87 helper class detection |

**Zero false positives introduced** — all 16 new findings are confirmed true positives. 8 findings are from enhanced GSettings/D-Bus signal leak detection (PRs #64, #87, #91), 2 from module-scope prototype mutation (PR #83, R-LIFE-27), and 6 were first caught in 03-07 but appear as "new" vs the 03-05 baseline.

## 3. Resolved Findings (21 total)

| Extension | Check | Severity | Reason |
|---|---|---|---|
| gsconnect | lifecycle/prototype-override (×5) | WARN | service/ directory exempted (PR #88) |
| gsconnect | resource-tracking/destroy-not-called | WARN | service/ directory exempted (PR #88) |
| gsconnect | resource-tracking/no-destroy-method | WARN | service/ directory exempted (PR #88) |
| gsconnect | resource-tracking/ownership | WARN | Superseded by new count (19→13) |
| clipboard-indicator | R-LIFE-19 | WARN | Superseded by specific `lifecycle/stage-actor-leak` FAIL |
| blur-my-shell | init/shell-modification | FAIL | Exemption expanded for appfolders.js (PR #88) |
| blur-my-shell | quality/repeated-settings | WARN | Settings instances correctly consolidated |
| blur-my-shell | resource-tracking/no-destroy-method | WARN | settings.js cleanup pattern recognized (PR #86) |
| blur-my-shell | resource-tracking/ownership | WARN | Superseded by new count (12→11) |
| blur-my-shell | R-SLOP-38 | WARN | Identifier reclassified as domain-specific |
| dash-to-panel | R-VER46-05 | FAIL | Version-compat suppression (PR #84, replacement-pattern) |
| dash-to-panel | R-VER48-02 | FAIL | Version-compat suppression (PR #84, replacement-pattern) |
| dash-to-panel | lifecycle/prototype-override (×2) | WARN | Superseded by `lifecycle/module-scope-prototype` (R-LIFE-27) |
| dash-to-panel | R-SLOP-38 | WARN | Identifier reclassified as domain-specific |
| media-controls | R-VER49-02 | FAIL | Version-compat suppression (Clutter.ClickGesture fallback) |
| just-perfection | schema/exists | FAIL | src/schemas/ fallback added (PR #80) |

**Key theme**: 14 PRs (#64-#91) drove these improvements. PR #88 (service/ exemption) resolved 8 findings for GSConnect alone. PR #84 (replacement-pattern) resolved 3 version-compat FPs.

## 4. Gap Closure Assessment

| Gap | 03-07 Status | 03-08 Status | Fixed by | Assessment |
|---|---|---|---|---|
| **A: GSettings signal leak** | 1/4+ caught (1 FP) | **6/10 caught (5 TP + 1 FP)** | PR #87, #64 | **Substantially closed** |
| **B: D-Bus connectSignal** | 0 caught | **2 caught** | PR #91, #65 | **Partially closed** |
| **C: Prototype mutation** | 0 caught | **2 caught** | PR #83 (R-LIFE-27) | **Partially closed** |

### Gap A: GSettings signal leak (substantially closed)

In 03-07, only dash-to-panel was caught (and it was a false positive — array-based ID storage). Now ego-lint detects bare `settings.connect()` across helper classes and prefs:

| Extension | 03-07 | 03-08 | Detail |
|---|---|---|---|
| media-controls | Not caught | **28 FAIL** | Highest-impact leak in corpus |
| v-shell | Not caught | **3 FAIL** | optionsFactory + settings |
| appindicator | Not caught | **3 FAIL** | Prefs pages |
| blur-my-shell | Not caught | **1 FAIL** | Preferences |
| just-perfection | Not caught | **1 FAIL** | SupportNotifier |
| dash-to-panel | 1 FP | **FP fixed** | Array-based ID storage now recognized (PR #64) |

**Still missing**: tiling-shell (TypeScript compiled — source patterns invisible), clipboard-indicator (inferred from review but not confirmed).

### Gap B: D-Bus connectSignal (partially closed)

R-LIFE-25 now always emits FAIL for bare `connectSignal()` without stored ID (PR #91). Media-controls caught with 2 bare `proxy.connectSignal()` calls. Tiling-shell D-Bus leaks remain invisible (TypeScript compilation).

### Gap C: Module-scope prototype mutation (partially closed)

R-LIFE-27 detects direct `.prototype.methodName =` assignments at module scope. Caught 2 instances in dash-to-panel (`TaskbarAppIcon.prototype.scaleAndFade/undoScaleAndFade`). However, **indirect prototype mutation is not caught** — appindicator's `_promisifySignals(GObject.Object.prototype)` calls a function that internally does `proto.connect_once = ...`, which evades the regex-based check.

## 5. False Positive Status

| FP Issue | 03-07 Status | 03-08 Status | Fix |
|---|---|---|---|
| R-SLOP-01 (5 FPs, dash-to-panel) | Open | **Fixed (0 FPs)** | PR #85 provenance post-filter |
| R-DEPR-06 (2 FPs, dash-to-panel) | Open | **Fixed (0 FPs)** | skip-comments / version-compat |
| R-VER48-02 (1 FP, dash-to-panel) | Open | **Fixed (0 FPs)** | PR #84 replacement-pattern |
| gsettings-signal-leak (1 FP, dash-to-panel) | New FP | **Fixed (0 FPs)** | PR #64 array-based ID tracking |
| **New FPs introduced** | 1 | **0** | — |

All 4 known false positives from 03-07 are resolved. Zero new false positives introduced in 03-08. This is the first field test run with a clean FP slate.

## 6. Review Cross-Extension Patterns

### All 10 reviews completed (0 timeouts)

| Pattern | Extensions (count) | Lint Coverage | Change from 03-07 |
|---|---|---|---|
| GSettings signal leak | media-controls (28), v-shell (3), appindicator (3), blur-my-shell (1), just-perfection (1) | **GOOD: 5/7 TP** | Was 1/4+ (FP only) |
| D-Bus connectSignal leak | media-controls (2) | **PARTIAL: 1/2+** | Was 0 |
| Module-scope prototype mutation | dash-to-panel (2) | **PARTIAL: 1/2+** | Was 0 |
| Prototype overrides (inside functions) | all large extensions | **GOOD** | Stable |
| Private API access | all 10 extensions | **GOOD** | Stable |
| Module-scope mutable state | dash-to-panel (1) | **GOOD** | Was partial |
| Async without _destroyed guard | media-controls, tiling-shell, clipboard-indicator | **PARTIAL** | Stable |
| Constructor side effects | appindicator (6 blocking) | **POOR: semantic gap** | Stays Tier 3 |
| Global prototype mutation (indirect) | appindicator (GObject.Object.prototype) | **NONE: R-LIFE-27 gap** | New gap identified |

### Review verdicts

- **LIKELY APPROVED**: hara-hachi-bu (0 blocking)
- **NEEDS REVISION**: All other 9 extensions
- All 10 reviews completed within budget — 0 timeouts vs 4 in 03-07 (timeout raised from 600s to 900s)

## 7. Remaining Gaps

### Gap C.1: Indirect prototype mutation (new, medium priority)

AppIndicator's `promiseUtils.js` calls `_promisifySignals(GObject.Object.prototype)` at module scope, which internally assigns `proto.connect_once = function(...)`. R-LIFE-27's regex `([\w.]+\.prototype\.\w+)\s*=` only matches direct assignments, not function-call-based mutation. This is a known limitation of regex-based Tier 2 checks.

**Recommendation**: Enhance R-LIFE-27 to detect calls passing `.prototype` as argument to mutation functions, or add a special-case pattern.

### Gap D: TypeScript extension invisibility (fundamental)

Tiling-shell compiles TypeScript to a single JS bundle. Source-level patterns (GSettings leaks, D-Bus leaks) are invisible to ego-lint. Review found GSettings leak in `WindowBorderManager`. This is a fundamental limitation for TS extensions.

**Recommendation**: Consider detecting `esbuild`/`tsc` artifacts and adjusting expectations or suggesting source-level analysis.

### Gap E: Semantic-only gaps (stays Tier 3)

- Constructor side effects / lifecycle ordering (appindicator, just-perfection)
- Deceptive import aliases (appindicator: GdkPixbuf as Meta)
- Signal disconnect on wrong object (v-shell: dash.js)
- Prototype patch save/restore completeness (gsconnect, media-controls)
- Splice wrong argument type (blur-my-shell: window_list.js)

### Low priority

- R-SEC-03 HTTP in GPL headers: 2 WARNs on dash-to-panel (correct content, wrong protocol in boilerplate)

## 8. Unannotated Finding Counts

| Extension | Unannotated | Change from 03-07 |
|---|---|---|
| hara-hachi-bu | 32 | 0 |
| just-perfection | 26 | 0 |
| media-controls | 38 | +1 |
| tiling-shell | 59 | 0 |
| v-shell | 49 | +1 |
| blur-my-shell | 47 | -3 |
| appindicator | 52 | +1 |
| clipboard-indicator | 42 | 0 |
| dash-to-panel | 65 | -3 |
| gsconnect | 69 | -7 |
| **Total** | **479** | **-10** |

Total unannotated dropped from 489 to 479 due to resolved findings (especially GSConnect's service/ exemption removing 7 findings).

## 9. Timeout Analysis

**Zero timeouts** — all 10 reviews completed successfully within the $4 budget and 900s timeout (raised from 600s in 03-07).

| Extension | JS Lines | Report Lines | Verdict | Budget status |
|---|---|---|---|---|
| hara-hachi-bu | 1.4K | 303 | LIKELY APPROVED | Within budget |
| tiling-shell | 4.7K | 277 | NEEDS REVISION | Within budget |
| v-shell | 16.3K | 238 | NEEDS REVISION | Within budget |
| gsconnect | ~25K | 419 | NEEDS REVISION | Within budget |
| appindicator | 4.3K | 331 | NEEDS REVISION | Within budget |
| clipboard-indicator | 2.1K | 406 | NEEDS REVISION | Within budget |
| blur-my-shell | 7.8K | 248 | NEEDS REVISION | Within budget |
| dash-to-panel | 16.6K | 377 | NEEDS REVISION | Within budget |
| media-controls | 5.6K | 482 | NEEDS REVISION | Within budget |
| just-perfection | 3.2K | 338 | NEEDS REVISION | Within budget |

Previously timed-out extensions (v-shell, gsconnect, blur-my-shell, dash-to-panel) all completed this run. The 900s timeout and incremental Write strategy resolved the budget exhaustion issue.

## 10. Methodology

- Lint run: `bash scripts/field-test-runner.sh --no-fetch`
- Review run: `bash scripts/field-test-runner.sh --no-fetch --review`
- Budget: $4 per review session, timeout: 900s, parallel 3
- Extensions fetched from cache (previous clones)
- Baselines from 2026-03-05 run (version 0dbe7e8)
- 14 commits since 03-07 baseline (PRs #64-#91)
