# Field Test: Clipboard Indicator

**Date**: 2026-02-28 (updated 2026-03-02)
**Target**: [Clipboard Indicator](https://github.com/Tudmotu/gnome-shell-extension-clipboard-indicator) v? (latest main)
**Extension**: `clipboard-indicator@tudmotu.com` — GNOME 46-49, 6 JS files, MIT license

## ego-lint Results

### Before Fixes

| Status | Count |
|--------|-------|
| PASS   | 178   |
| FAIL   | 27    |
| WARN   | 23    |
| SKIP   | 8     |
| **Total** | **236** |

Exit code: 1

### After Fixes

| Status | Count |
|--------|-------|
| PASS   | 179   |
| FAIL   | 1     |
| WARN   | 24    |
| SKIP   | 12    |
| **Total** | **216** |

Exit code: 1 (one true positive remains)

## False Positives Found and Fixed

### 1. R-WEB-01/02/10/11: setTimeout/setInterval/clearTimeout/clearInterval (24 FAILs)

**Root cause**: GJS added native `setTimeout`, `setInterval`, `clearTimeout`, `clearInterval` as global polyfills in GNOME 45. These rules were unconditionally blocking, but they're only invalid for GNOME 44 and earlier.

**Fix**: Added `max-version: 44` to R-WEB-01, R-WEB-02, R-WEB-10, R-WEB-11 in `rules/patterns.yaml`. Rules are now SKIP for GNOME 45+ targets.

**Impact**: -24 false FAILs. Any GNOME 45+ extension using timer APIs was getting spurious blocking failures.

### 2. License file variant not recognized (1 FAIL)

**Root cause**: The license check in `ego-lint.sh` only looked for exactly `LICENSE` or `COPYING`. Clipboard Indicator uses `LICENSE.rst`.

**Fix**: Extended to check `LICENSE`, `COPYING`, `LICENSE.rst`, `LICENSE.md`, `LICENSE.txt`, `COPYING.rst`, `COPYING.md`, `COPYING.txt`.

**Impact**: -1 false FAIL. Extensions using non-plain-text license files were blocked.

### 3. uuid-matches-dir blocking on cloned repos (1 FAIL)

**Root cause**: `check-metadata.py` emitted FAIL when the directory name didn't match the UUID. When cloning a repo, the directory is typically the repo name (e.g., `clipboard-indicator`) not the UUID (`clipboard-indicator@tudmotu.com`).

**Fix**: Downgraded from FAIL to WARN with a message clarifying the match is required when installed.

**Impact**: -1 false FAIL. Every cloned extension review would hit this.

## True Positives (Validate Our Checks Work)

### Blocking (1)
- **css/shell-class-override**: `.popup-menu-item` in stylesheet.css overrides a Shell theme class without scoping. Genuine issue — reviewer would flag this.

### Advisory (24 WARNs — all legitimate)
- **css/important**: 1 `!important` usage — correct advisory
- **R-DEPR-09** (3): `var` declarations in extension.js — correct, should be `const`/`let`
- **R-SEC-06**: `run_dispose()` on virtual keyboard device in keyboard.js — correct advisory
- **R-PREFS-04c**: GTK layout widget in prefs.js — correct advisory
- **R-VER48-04b** (3): `vertical: true/false` property removed in GNOME 48 — correct advisory
- **metadata/uuid-matches-dir**: Directory name mismatch — now correctly WARN
- **quality/module-state**: 5 module-level `let` variables — correct, real issue for enable/disable lifecycle
- **quality/constructor-resources** (2): `.connect()` in prefs constructor — correct advisory
- **quality/private-api**: `Main.panel` private API access — correct advisory
- **quality/run-dispose-no-comment**: `run_dispose()` without justification comment — correct
- **lifecycle/signal-balance**: 17 connects vs 6 disconnects — genuine concern
- **lifecycle/async-destroyed-guard**: No `_destroyed` guard on async code — correct
- **lifecycle/clipboard-keybinding**: Clipboard + keybinding pattern detected — correct for security review
- **gobject/missing-gtypename**: `ConfirmDialog` missing `GTypeName` — correct
- **async/no-cancellable**: Gio async without `Gio.Cancellable` — correct
- **async/missing-cancellable**: `_async()` calls without cancellable — correct
- **async/disable-no-cancel**: No cancel/abort in disable() — correct
- **resource-tracking/no-destroy-method**: `registry.js` has no `destroy()` — correct
- **resource-tracking/ownership**: 1 orphan detected — correct

## Coverage Gaps Identified

1. **No check for screenshot.png in source tree**: This file should not be in the extension package (wastes space). Only `check-package.sh` checks zip contents, but source-level review doesn't flag large binary assets.

2. **No check for `.pot` file in source**: The `clipboard-indicator.pot` template file shouldn't be shipped in the extension package.

3. **Makefile not flagged**: Build files (Makefile, meson.build) are development artifacts that shouldn't ship in the extension zip. Not detected at source level.

These are all package-level concerns. The source-level linter correctly focuses on code quality and doesn't overlap with package validation.

## Calibration Assessment

- **Severity levels**: Correctly calibrated. Blocking findings are genuinely blocking (CSS override). Advisories are relevant but non-blocking.
- **Signal-to-noise**: After fixes, 1 FAIL + 24 WARN. A reviewer would find this actionable — not overwhelmed by noise.
- **Timer API false positives were the biggest calibration issue**: 24 out of 27 FAILs were false. This would have caused reviewers to dismiss the tool immediately.

## Regression Verification

| Target | Before | After |
|--------|--------|-------|
| Clipboard Indicator | 27 FAIL | 1 FAIL (TP) |
| hara-hachi-bu | 0 FAIL, 8 WARN | 0 FAIL, 6 WARN |
| Test suite | 378 pass (pre-session) | 416 pass (post-session, includes parallel work) |

## Changes Made

1. `rules/patterns.yaml`: Added `max-version: 44` to R-WEB-01, R-WEB-02, R-WEB-10, R-WEB-11
2. `skills/ego-lint/scripts/ego-lint.sh`: Extended license check to recognize `.rst`/`.md`/`.txt` variants
3. `skills/ego-lint/scripts/check-metadata.py`: Downgraded `uuid-matches-dir` from FAIL to WARN
4. `tests/fixtures/web-apis/metadata.json`: Changed shell-version to "44" (was "48") so R-WEB rules still fire
5. `tests/fixtures/ego-lint-ignore@test/`: Changed to use R-WEB-04/06 (non-version-gated rules)
6. New fixture: `tests/fixtures/timer-apis-g45@test/` — verifies timer APIs are SKIP for GNOME 45+
7. New fixture: `tests/fixtures/license-rst@test/` — verifies LICENSE.rst detection
8. `tests/run-tests.sh`: Updated assertions for version-gating, added 13 new assertions

## ego-review Results

**Verdict: NEEDS REVISION** | **Rejection Risk: MEDIUM-HIGH**

### Blocking Issues (3)
1. **`_historyLabel` on `global.stage` never removed** (extension.js:1056-1063) — actor leak on every enable/disable cycle
2. **`_notifSource` never destroyed in `disable()`** (extension.js:992-1004) — notification source persists
3. **CSS `.popup-menu-item` override** (stylesheet.css:15-17) — Shell theme class override

### Justification Required (4)
- 27 module-level `let` variables (extension.js:23-49)
- Private API: `Main.panel.statusArea.dateMenu._indicator._settings` (extension.js:1024)
- Dead code: `Shell.KeyBindingMode` check (extension.js:1189)
- `run_dispose()` without comment (keyboard.js:19)

### Advisory (11 items)
- No `_destroyed` guard on async, no `Gio.Cancellable` (9+ calls), signal imbalance (17 vs 6), gettext-domain mismatch, 3x var, `let that = this` pattern, missing GTypeName, prefs.js constructor connects, prefs.js settings leak, `_getMenuItems()` private API, `global.stage` orphan

### AI Pattern Analysis
- **Score: 3/46 — ADVISORY** (below BLOCKING threshold)
- Triggered: setTimeout/setInterval (legacy, not AI), var declarations, manual signal tracking
- **Code provenance: clearly human-written** — authentic comments, domain logic, 2014 copyright, years of Git history

### Review Process Assessment
- Phases 0-5a all produced relevant findings
- Resource graph builder correctly detected the `_historyLabel` orphan
- AI slop checklist correctly classified legacy patterns as non-AI
- No false positives in the manual review phases
- The review found 2 blocking issues (B1, B2) that ego-lint could not detect (semantic lifecycle analysis)

## ego-simulate Results

**Score: 10** — At the rejection threshold

| Source | Weight |
|--------|--------|
| Signal leak (Reason #13: `_historyLabel` on `global.stage`) | 5 |
| CSS shell-class-override (unmapped ego-lint FAIL) | 5 |
| **Total** | **10** |

### Calibration Assessment
- Score of 10 for an approved-on-EGO extension suggests slightly conservative scoring — acceptable
- Fixing just the `global.stage` leak would drop score to 5 (likely pass with comments)
- The 23-reason taxonomy correctly avoided false triggers (no AI slop, no deprecated modules, no console.log)
- ego-lint FAIL integration worked correctly (CSS override added weight 5)

### Reviewer Triage (simulated)
The reviewer's internal monologue correctly identified: mature codebase, human-written, main concern is the stage leak, CSS is scoped enough to be borderline. The setTimeout usage was correctly identified as acceptable for GNOME 45+.

---

## 2026-03-02 Update: Full ego-submit Pipeline Run

Ran the complete ego-submit pipeline (ego-lint → ego-review → package validation → metadata review → readiness report) from a clean clone at `/tmp/clipboard-indicator` against latest `master` (commit `13ba8b1`).

### ego-lint Results (Phase 1)

| Status | Count |
|--------|-------|
| PASS   | 52    |
| FAIL   | 2     |
| WARN   | 27    |
| SKIP   | 6     |
| **Total** | **87** |

Exit code: 1

**Note**: Check count dropped from 236 (previous runs) to 87. This is because
previous runs used `--verbose` with the full pattern rule expansion. This run
used the standard ego-lint invocation via the ego-submit pipeline.

#### FAIL Classification

| Rule | File:Line | TP/FP | Notes |
|------|-----------|-------|-------|
| css/shell-class-override | stylesheet.css:15 | TP | `.popup-menu-item` override — same as previous runs |
| R-DEPR-11 | extension.js:1190 | TP | `Shell.KeyBindingMode` dead code — added in 03-01 update |

Both FAILs are true positives. No new false positives.

### ego-review Results (Phase 2)

**Verdict: NEEDS REVISION** | **Rejection Risk: HIGH** (15 risk points)

#### Blocking Issues (3 from manual review + 2 from lint)

| # | Issue | File:Line | Category |
|---|-------|-----------|----------|
| B1 | `_historyLabel` on `global.stage` never removed in `destroy()` | extension.js:1061 | lifecycle |
| B2 | No `_destroyed` guard on async `_buildMenu().then()` chain | extension.js:133-137 | lifecycle |
| B3 | `Registry` has no `destroy()` or `Gio.Cancellable` — async ops outlive extension | registry.js | lifecycle |
| B4 | CSS `.popup-menu-item` Shell theme class override | stylesheet.css:15 | lint FAIL |
| B5 | `Shell.KeyBindingMode` deprecated reference | extension.js:1190 | lint FAIL |

#### Issues ego-lint Could Not Detect

1. **B2: Async guard on `_buildMenu().then()`** — requires understanding that
   `_init()` calls an async method whose `.then()` callback fires after
   `destroy()` on rapid enable/disable. This is semantic cross-method analysis.

2. **B3: Registry missing cleanup** — requires understanding that `Registry` is
   a non-GObject helper class with async file I/O but no lifecycle method. The
   resource graph builder flagged the orphan widget, but the missing cancellable
   pattern is a semantic analysis finding.

3. **`_notifSource` not explicitly destroyed** — `MessageTray.Source` cleanup
   is implicit through `super.destroy()` chain, but reviewers prefer explicit.

#### Resource Graph

```
Files scanned: 5
Resources: 1 gsettings, 18 signal, 30 widget
Total: 49 creates, 26 destroys
Orphans: 1 (registry.js:148 — St.Icon in getEntryAsImage)
Ownership depth: 2
```

The creates > destroys ratio (49 vs 26) is normal — most widget creates are
child widgets auto-destroyed by parent's `super.destroy()`.

#### AI Pattern Analysis

**Score**: 2/46 — **PASS** (threshold: 0-3 for <10 files)
**Provenance score**: 4 (Very strong)
**Triggered items**: `var` declarations (item 23), Promise wrapper (item 40)
**Assessment**: Clearly hand-written, organic code evolution

### Package Validation (Phase 3)

- No distribution zip exists — must be created
- Required files: All present (extension.js, metadata.json, schemas/, locale/)
- Files to exclude: Makefile, README.rst, clipboard-indicator.pot, screenshot.png
- Secrets scan: Clean

### Metadata Review (Phase 4)

- **Description**: Marketing copy ("most popular clipboard manager, 1M downloads")
  — should be rewritten as functional description with clipboard access disclosure
- **Shell versions**: 46, 47, 48, 49 — GNOME 49 is unreleased, should verify tested
- **Screenshots**: screenshot.png exists in repo

#### Disclosure Matrix

| Capability | Found in Code | Disclosed in Metadata | Status |
|------------|--------------|----------------------|--------|
| Clipboard | Yes (`St.Clipboard`) | Implicit | WARN |
| Network | No | N/A | OK |
| pkexec | No | N/A | OK |
| Subprocess | No | N/A | OK |
| Private API | Yes (`Main.panel.statusArea`) | No | WARN |
| File I/O | Yes (cache dir) | No | OK |

### Readiness Report Verdict (Phase 5)

**NEEDS FIXES** — 5 blocking issues, 11 advisory items

All blocking issues are straightforward 1-5 line fixes. The extension has strong
fundamentals (no security issues, no AI patterns, excellent i18n with 20+ locales).

### Pipeline Process Assessment

1. **Sequential execution was appropriate** — 6 JS files, completed in reasonable time
2. **ego-lint → ego-review deduplication worked** — ego-review focused on semantic
   findings not caught by lint (B2, B3, _notifSource)
3. **Resource graph builder** correctly detected the `_historyLabel` stage orphan
   and the `registry.js` ownership gap
4. **Phase 4 disclosure matrix** identified 2 undisclosed capabilities (clipboard,
   private API) that need reviewer notes
5. **Readiness report template** produced an actionable output with prioritized
   action items

### Calibration Observations

- ego-review risk score (15 points → LIKELY REJECTED) may be slightly high for
  an extension that is approved and popular on EGO. However, the lifecycle issues
  are real — the extension likely predates stricter modern review standards.
- The B2 finding (async _buildMenu guard) is the kind of issue that only
  manifests on rapid enable/disable or during GNOME Shell restart. It wouldn't
  be visible in normal usage but is technically correct.
- The ego-submit pipeline correctly aggregated findings without duplication across
  phases — each blocking issue appears exactly once in the final report.

---

## 2026-03-01 Update: Re-run After 17 New Checks

### Results Comparison

| | Previous (02-28) | Current (03-01 pre-fix) | Post-fix |
|---|---|---|---|
| Total checks | 216 | 233 | 236 |
| PASS | 179 | 188 | 190 |
| FAIL | 1 | 1 | 2 |
| WARN | 24 | 27 | 27 |
| SKIP | 12 | 17 | 17 |

The 17 new checks come from: accessibility, disclosures, polkit, schema-usage, and code metrics.

### False Positives Found and Fixed

1. **quality/constructor-resources on prefs.js** (2 WARNs): `.connect()` in prefs.js constructors flagged with "move to enable()" — but prefs.js has no enable()/disable(). GTK widget signals auto-cleanup with the window. **Fix**: Skip prefs.js in `check_constructor_resources`.

2. **disclosure/private-api on own widget** (1 WARN): `this.historySection._getMenuItems()` flagged as Shell private API access — but `historySection` is the extension's own PopupMenu widget. **Fix**: Scoped `_getMenuItems()` and `_getTopMenu()` patterns to require Shell global prefixes (`Main.panel`, `statusArea`, `quickSettings`).

### New Findings (Post-fix)

- **R-DEPR-11** (FAIL): `Shell.KeyBindingMode` — dead code, removed before GNOME 40
- **R-LIFE-19** (WARN): `global.stage.add_child()` without matching `remove_child()` in disable
- **R-QUAL-34** (WARN): `enumerate_children()` synchronous I/O blocking the Shell main loop
- **accessibility/accessible-name** (WARN): Widget missing accessible name — true positive
- **R-SLOP-40** (WARN): Promise wrapper pattern — existed but newly triggered

### Coverage Gap Closure

The new rules close 3 gaps identified by ego-review:
1. `global.stage.add_child` leak → R-LIFE-19 now detects this pattern
2. `Shell.KeyBindingMode` dead code → R-DEPR-11 now flags it as blocking
3. Synchronous file enumeration → R-QUAL-34 now advises async alternative
