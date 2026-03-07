# Regression Report: ego-lint + ego-review Field Test

**Date**: 2026-03-07
**ego-lint version**: ae650be (`fix(ego-field-test): indent multi-line expressions`)
**Review tool**: ego-review via headless Claude ($4 budget, parallel 3)
**Extensions tested**: 10 (all reviewed, 4 timed out)

## 1. Summary Table

| Extension | Lint Exit | PASS | FAIL | WARN | SKIP | Changed | Review Verdict |
|---|---|---|---|---|---|---|---|
| hara-hachi-bu | 0 | 207 | 0 | 9 | 23 | No | LIKELY APPROVED (0 blocking) |
| tiling-shell | 1 | 138 | 4 | 4 | 51 | No | NEEDS REVISION (1 blocking) |
| v-shell | 1 | 188 | 1 | 91 | 17 | Yes (+1F) | Timeout (partial: 105 lines) |
| gsconnect | 1 | 171 | 12 | 144 | 17 | No | Timeout (partial: 400 lines) |
| appindicator | 1 | 187 | 11 | 57 | 14 | No | NEEDS REVISION (6 blocking) |
| clipboard-indicator | 1 | 196 | 3 | 24 | 17 | Yes (+2F-1R) | NEEDS REVISION (5 blocking) |
| blur-my-shell | 1 | 190 | 4 | 43 | 17 | Yes (+1W) | Timeout (partial: 196 lines) |
| dash-to-panel | 1 | 171 | 11 | 66 | 17 | Yes (+1F+1W-1R) | Timeout (partial: 125 lines) |
| media-controls | 1 | 188 | 6 | 28 | 17 | No | NEEDS REVISION (3 blocking) |
| just-perfection | 1 | 198 | 4 | 10 | 12 | Yes (+1W) | NEEDS REVISION (2 blocking) |
| **Totals** | — | 1834 | 56 | 476 | 202 | 5 | 6 ok, 4 timeout |

### Delta vs 2026-03-05 baseline

| Metric | 03-05 | 03-07 | Delta |
|---|---|---|---|
| PASS | 1799 | 1834 | +35 |
| FAIL | 55 | 56 | +1 |
| WARN | 473 | 476 | +3 |
| SKIP | 191 | 202 | +11 |

The +35 PASS / +11 SKIP increase comes from new checks (R-LIFE-25, R-LIFE-26, stage-actor-leak, messagetray-source-leak, gsettings-signal-leak, destroy-no-call, R-QUAL-36, CSS class list expansion) adding results across all extensions.

## 2. New Findings (7 total, all TP)

| Extension | Check | Severity | Detail |
|---|---|---|---|
| v-shell | css/shell-class-override | FAIL | `.osd-window` override (PR #57 CSS class list expansion) |
| clipboard-indicator | lifecycle/stage-actor-leak | FAIL | `_historyLabel` not removed from `global.stage` |
| clipboard-indicator | lifecycle/messagetray-source-leak | WARN | `_notifSource` added but not destroyed in disable |
| dash-to-panel | lifecycle/gsettings-signal-leak | FAIL | Bare `settings.connect('changed::...')` in panelStyle |
| dash-to-panel | lifecycle/module-scope-state | WARN | Module-scope `Map` (`iconCacheMap`) not cleared (R-LIFE-26) |
| blur-my-shell | lifecycle/destroy-no-call | WARN | `.destroy` without `()` in coverflow_alt_tab.js |
| just-perfection | R-QUAL-36 | WARN | CRITICAL notification urgency for donation prompt |

**One false positive identified**: dash-to-panel's `lifecycle/gsettings-signal-leak` (panelStyle.js) — the review's own B9 analysis confirmed signal IDs ARE stored in `_dtpSettingsSignalIds` array and disconnected in `disable()`. The lint check can't trace through array-based ID storage patterns. The remaining 6 new findings are confirmed true positives.

## 3. Resolved Findings (2)

| Extension | Check | Reason |
|---|---|---|
| clipboard-indicator | R-LIFE-19 | Superseded by specific `lifecycle/stage-actor-leak` FAIL |
| dash-to-panel | R-VER48-02 | Guard-window fix resolved 1 of 2 FPs (1 FP may remain) |

## 4. Rule Candidate Completion

All 5 rule candidates from the 2026-03-05 regression report are now implemented:

| Candidate | Implementation | Field Hit |
|---|---|---|
| R-LIFE-21 (GSettings signal leak) | `lifecycle/gsettings-signal-leak` in check-lifecycle.py | dash-to-panel (1) |
| R-LIFE-22 (global.stage actor leak) | `lifecycle/stage-actor-leak` in check-lifecycle.py | clipboard-indicator (1) |
| R-LIFE-23 (.destroy without parens) | `lifecycle/destroy-no-call` in check-lifecycle.py | blur-my-shell (1) |
| R-LIFE-24 (MessageTray.Source leak) | `lifecycle/messagetray-source-leak` in check-lifecycle.py | clipboard-indicator (1) |
| R-QUAL-36 (notification urgency) | Pattern rule in patterns.yaml | just-perfection (1) |

Two additional rules added beyond the report candidates:

| Rule | Implementation | Field Hit |
|---|---|---|
| R-LIFE-25 (D-Bus connectSignal leak) | check-lifecycle.py | 0 lint hits (reviews find 2+ in media-controls) |
| R-LIFE-26 (module-scope mutable state) | check-lifecycle.py | dash-to-panel (1) |

## 5. Review Cross-Extension Patterns

### Completed reviews (6)

| Pattern | Extensions (count) | Lint Coverage |
|---|---|---|
| GSettings signal leak | media-controls (28), just-perfection, tiling-shell, clipboard-indicator | PARTIAL: lint caught 1/4+ |
| D-Bus connectSignal leak | media-controls (2), tiling-shell (inferred) | POOR: R-LIFE-25 caught 0 |
| Prototype overrides | media-controls, just-perfection, tiling-shell | GOOD: lint reports all |
| Private API access | all 6 extensions | GOOD: lint reports all |
| Module-scope mutable state | hara-hachi-bu, clipboard-indicator, appindicator, tiling-shell | PARTIAL: R-LIFE-26 caught 1 |
| Async without _destroyed guard | media-controls, tiling-shell, clipboard-indicator | PARTIAL: heuristic coverage |
| Constructor side effects | appindicator (6 blocking issues) | POOR: semantic gap |
| Global prototype mutation | appindicator | NONE: new gap |

### Timed-out reviews (4)

All 4 timed-out extensions (v-shell, gsconnect, blur-my-shell, dash-to-panel) produced partial reports (105-400 lines). These are the largest codebases. Budget exhaustion at $4 is the limiting factor.

## 6. Remaining Gaps (lint vs review)

### Gap A: GSettings signal leak detection (high priority)

`lifecycle/gsettings-signal-leak` caught **1 of 4+ affected extensions**. The current heuristic likely only catches the simplest case (bare `.connect` without stored ID). Extensions using `settings.connect()` with stored IDs but no `disconnect()` in disable are missed.

**Affected**: media-controls (28 handlers), tiling-shell (1), just-perfection (1), clipboard-indicator (inferred)
**Recommendation**: Enhance check to track stored signal IDs and verify disconnect in disable()

### Gap B: D-Bus connectSignal leak detection (high priority)

R-LIFE-25 produced 0 lint hits despite reviews finding D-Bus leaks in media-controls (2: NameOwnerChanged, PropertiesChanged+Seeked) and tiling-shell. The detection may need tuning.

**Recommendation**: Verify R-LIFE-25 pattern matching against media-controls and tiling-shell source

### Gap C: Global prototype mutation (medium priority)

AppIndicator adds methods to `GObject.Object.prototype` and `Signals.EventEmitter.prototype` at import time, never removed. Potentially detectable as `.prototype.` assignment at module scope without corresponding removal.

**Recommendation**: Consider Tier 2 check for `.prototype.methodName =` at module scope

### Gap D: Semantic-only gaps (stays Tier 3)

- Constructor side effects / lifecycle ordering (appindicator, just-perfection)
- Deceptive import aliases (appindicator: GdkPixbuf as Meta)
- Signal disconnect on wrong object (v-shell, from 03-05 report)
- Prototype patch save/restore completeness (gsconnect, media-controls)

## 7. False Positive Status

| FP Issue | Status | Extensions |
|---|---|---|
| R-VER48-02 guard-window | Partially fixed: 1 of 2 FPs resolved | dash-to-panel (1 remaining?) |
| R-SLOP-01 provenance post-filter | Open: WARNs despite provenance score 4 | dash-to-panel (5 FPs) |
| R-DEPR-06 in comments | Open: skip-comments not applied | dash-to-panel (2 FPs) |
| lifecycle/gsettings-signal-leak | **New FP**: can't trace array-based ID storage | dash-to-panel (1 FP) |

One new FP introduced (gsettings-signal-leak on dash-to-panel). Identified via the extension's own review report.

## 8. Unannotated Finding Counts

| Extension | Unannotated | Comment |
|---|---|---|
| hara-hachi-bu | 32 | Smallest; stable |
| just-perfection | 26 | Low; well-covered |
| media-controls | 37 | Moderate |
| tiling-shell | 47 | Moderate (TS compiled) |
| v-shell | 48 | Moderate |
| blur-my-shell | 50 | Growing; effects pipeline |
| appindicator | 51 | Legacy patterns |
| tiling-shell | 59 | Compiled TS |
| clipboard-indicator | 42 | Post-new-checks |
| dash-to-panel | 68 | Largest non-gsconnect |
| gsconnect | 76 | Largest (D-Bus daemon) |

Total unannotated: 489 findings across 10 extensions.

## 9. Timeout Analysis

4 of 10 reviews timed out (exit code 124 from `timeout 600`):

| Extension | JS Lines | Report Lines | Sections Completed | Assessment |
|---|---|---|---|---|
| gsconnect | ~25K | 400 | All (verdict + checklist) | False timeout: report complete, killed during wind-down |
| blur-my-shell | 7.8K | 196 | 1-3 (no lint/AI/readiness) | Needed ~200-300s more |
| dash-to-panel | 16.6K | 125 | 1 only (9 blocking items) | Deep analysis per finding |
| v-shell | 19.2K | 105 | 1-2 only | Large codebase, many findings |

**Root cause**: The 600s hard timeout was the bottleneck, not the $4 budget. Fixed by raising the default to 900s and adding `--timeout SECONDS` flag.

## 10. Methodology

- Lint run: `bash scripts/field-test-runner.sh --no-fetch`
- Review run: `bash scripts/field-test-runner.sh --no-fetch --review`
- Budget: $4 per review session, timeout: 600s, parallel 3
- Extensions fetched from cache (previous clones)
- Baselines from 2026-03-05 run (version 203ab71)
