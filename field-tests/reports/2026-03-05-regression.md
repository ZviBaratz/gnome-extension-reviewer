# Regression Report: ego-review Field Test

**Date**: 2026-03-05
**ego-lint version**: 203ab71 (`feat: add --budget flag, increase default to $4`)
**Review tool**: ego-review via headless Claude ($4 budget, parallel 3)
**Extensions tested**: 9 of 10 (hara-hachi-bu excluded — PASS, no review needed)

## 1. Summary Table

| Extension | Lint Exit | PASS | FAIL | WARN | SKIP | Review-only Blocking |
|---|---|---|---|---|---|---|
| hara-hachi-bu | 0 | 204 | 0 | 9 | 23 | — (not reviewed) |
| tiling-shell | 1 | 135 | 4 | 4 | 51 | 2 (settings leak, async guard) |
| v-shell | 0 | 185 | 0 | 91 | 17 | 1 (signal disconnect wrong object) |
| gsconnect | 1 | 167 | 12 | 144 | 17 | 3 (constructor effects, prototype restore, module state) |
| appindicator | 1 | 183 | 11 | 57 | 14 | 0 (all caught by lint) |
| clipboard-indicator | 1 | 192 | 2 | 24 | 17 | 0 (already annotated: stage actor + messageTray leak) |
| blur-my-shell | 1 | 187 | 4 | 42 | 17 | 0 (already annotated: .destroy parens, splice, timeouts) |
| dash-to-panel | 1 | 168 | 12 | 65 | 17 | 1 (async enable race) |
| media-controls | 1 | 183 | 6 | 28 | 17 | 2 (28 GSettings leaks, D-Bus signal leak) |
| just-perfection | 1 | 195 | 4 | 9 | 12 | 2 (settings leak, notification urgency) |
| **Totals** | — | 1799 | 55 | 473 | 191 | **11 review-only** |

## 2. Trend Data

Three consecutive runs on 2026-03-04 (version 0dbe7e8) showed **zero changes** across all 10 extensions — lint results are fully deterministic. The 2026-03-05 run (version 203ab71) also shows no count changes, confirming stability across the `--budget` flag commit.

## 3. Cross-Extension Patterns from ego-review

| Pattern | Extensions (count) | Automatable? |
|---|---|---|
| GSettings signal leak (bare .connect, no disconnect) | Media Controls (28), Just Perfection, Tiling Shell, Clipboard Indicator | YES — enhance check-lifecycle.py |
| Missing `_destroyed` guard after await | Tiling Shell, Dash to Panel, Clipboard Indicator | PARTIALLY — lint has heuristic, not per-await |
| Module-scope Shell state access | GSConnect, Dash to Panel, AppIndicator, Blur my Shell | PARTIALLY — lint catches most |
| Untracked timeout/idle source IDs | Blur my Shell, V-Shell (15), Media Controls, Dash to Panel, Clipboard Indicator | PARTIALLY — lint has `untracked-timeout` |
| Constructor side effects | GSConnect, Dash to Panel, AppIndicator | PARTIALLY — lint catches most |
| Prototype patches not fully restored | GSConnect, Media Controls | NO — semantic only |
| Signal disconnect on wrong object | V-Shell | NO — semantic only |
| global.stage actor leak | Clipboard Indicator | YES — check-lifecycle.py |
| Notification urgency abuse | Just Perfection | YES — simple pattern |
| `.destroy` without parentheses | Blur my Shell | YES — careful pattern needed |

## 4. Gap Analysis: New Rule Candidates

### Category A: Automatable (new lint rules)

#### R-LIFE-21: GSettings signal leak (highest priority)
- **Impact**: 4 extensions, 28+ leaked handlers on Media Controls alone
- **Tier**: 2 (enhance `check_settings_cleanup` in `check-lifecycle.py`)
- **Detection**: `settings.connect('changed::...')` where signal ID not stored AND no `disconnectObject` in disable
- **Current gap**: Only checks if settings object is nulled, not if individual signals are disconnected

#### R-LIFE-22: global.stage actor leak
- **Impact**: Clipboard Indicator (`_historyLabel` on global.stage, `_notifSource` in messageTray)
- **Tier**: 2 (`check-lifecycle.py`) — `global.stage.add_child` without `remove_child` in disable
- **Also covers**: `Main.layoutManager.addTopChrome`/`removeTopChrome`

#### R-QUAL-36: notification urgency abuse
- **Impact**: Just Perfection uses CRITICAL urgency for donation prompt
- **Tier**: 1 (`patterns.yaml`) — `\.urgency\s*=\s*.*Urgency\.CRITICAL`
- **Severity**: WARN

#### R-LIFE-23: .destroy without parentheses
- **Impact**: Blur my Shell (`actor.destroy` property access instead of call)
- **Tier**: 1 or 2 — `\.destroy\s*[;,\n]` (not followed by parens)
- **Risk**: High FP potential from callback refs like `.forEach(x => x.destroy)`

#### R-LIFE-24: MessageTray.Source leak
- **Impact**: Clipboard Indicator — `messageTray.add()` without source `.destroy()` in disable
- **Tier**: 2 (`check-lifecycle.py`)

### Category B: Semantic only (stays in ego-review Tier 3)

- **Signal disconnect on wrong object** (V-Shell) — needs connect/disconnect object identity tracking
- **Prototype patch save/restore completeness** (GSConnect, Media Controls) — needs understanding of which methods were saved
- **Constructor side effect reversibility** — needs API semantics knowledge
- **`splice()` argument type mismatch** (Blur my Shell) — needs type inference

## 5. False Positive Status on Approved Extensions

| FP Issue | Status | Extensions Affected |
|---|---|---|
| R-VER48-02 guard-window too small | Open gap — guard-window: 3 insufficient for Dash to Panel (PACKAGE_VERSION 5-10 lines before API) | Dash to Panel (2 FPs) |
| init/shell-modification non-extension.js | Fixed in PR #21 — constructor-only-in-extension.js | Tiling Shell (13), AppIndicator (3), Dash to Panel (4) |
| R-SLOP-01 provenance post-filter | Edge case — Dash to Panel WARNs appear despite provenance score 4 (bug) | Dash to Panel (5 FPs) |
| R-DEPR-06 in comments | Known — skip-comments would fix but Tweener rule is legitimate for actual imports | Dash to Panel (2 FPs) |

## 6. AI Provenance Assessment

All 10 extensions show **strong human authorship** indicators:
- 0/10 flagged for AI-generated code concerns
- Provenance scores: GSConnect (5), V-Shell (5), Dash to Panel (4), Media Controls (3), all others 3+
- R-SLOP pattern matches are either FPs (JSDoc, descriptive names) or low-impact advisories

## 7. Recommended Actions (prioritized)

1. **R-LIFE-21: GSettings signal leak detection** — highest impact, 4 extensions, fully automatable
2. **R-LIFE-22: global.stage/messageTray actor leak** — clear pattern, 1 extension but common anti-pattern
3. **R-QUAL-36: notification urgency abuse** — simple Tier 1 pattern rule
4. **R-LIFE-23: .destroy without parentheses** — needs careful pattern design to avoid FPs
5. **R-LIFE-24: MessageTray.Source leak** — lower priority, overlaps with R-LIFE-22

## 8. Methodology Notes

- ego-review ran as headless Claude sessions with $4 budget per extension
- 3 extensions ran in parallel batches
- Review reports saved as `.review.md` files (note: `dash-to-panel.review.md` missing — session wrote to stdout only)
- Review findings cross-referenced manually against ego-lint results to identify gaps
- Annotations use `review/` prefix to distinguish ego-review-only findings from ego-lint findings
