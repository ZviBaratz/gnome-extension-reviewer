# Field Test: hara-hachi-bu (Living Document)

This is the consolidated findings registry for the project's calibration baseline extension. Unlike one-shot field tests (e.g., Clipboard Indicator), this document grows over time as new findings are discovered through EGO reviewer feedback, PRs, and tool changes.

## Extension Profile

| Field | Value |
|-------|-------|
| **Name** | hara-hachi-bu |
| **UUID** | `hara-hachi-bu@ZviBaratz` |
| **Source** | [GitHub](https://github.com/ZviBaratz/hara-hachi-bu) |
| **GNOME versions** | 48 |
| **Size** | 17 JS files, ~8,800 lines |
| **License** | GPL-2.0-or-later |
| **EGO status** | Submitted, in review (v1.0 was rejected) |
| **Why baseline** | Exercises pkexec/polkit, D-Bus proxies, file monitors, GSettings, scheduled profiles, boost charge state machine, multi-battery support. Covers nearly all lint categories. |

## Current Baseline

Latest ego-lint results (2026-02-28, v0.2.0):

| Status | Count |
|--------|-------|
| PASS | 193 |
| FAIL | 0 |
| WARN | 5 |
| SKIP | 17 |
| Exit | 0 |

**ego-simulate score**: 1 (advisory #22 for notification volume). Verdict: "Likely to pass with minor comments."

**Remaining WARNs** (all correct/expected):

| Warning | Nature |
|---------|--------|
| R-SEC-20 | pkexec scrutiny advisory — correct |
| R-PREFS-04b | GTK widget advisory — correct after split |
| quality/private-api | Private API with inline justification — suppressible |
| polkit-files | Informational — polkit files present |
| async/missing-cancellable | Advisory — `_destroyed` pattern used as alternative |

**Resource graph**: 17 files, 72 creates, 108 destroys, 0 orphans, depth 3

**Code provenance score**: 3 (244 domain vocab, 59 algorithms, consistent camelCase naming)

---

## Findings Registry

Each finding has a stable ID (F-NNN) that never changes. New findings always get the next available number.

### False Positives Found and Fixed

| ID | Rule/Check | Status | Added |
|----|-----------|--------|-------|
| F-001 | R-SEC-07 | Fixed (v0.1.0) | 2026-02-27 |
| F-002 | Verdict threshold | Fixed (v0.1.0) | 2026-02-27 |
| F-003 | quality/gettext-pattern | Fixed (v0.1.0) | 2026-02-27 |
| F-004 | R-SEC-20 | Fixed (v0.1.0) | 2026-02-27 |
| F-005 | quality/private-api | Fixed (v0.1.0) | 2026-02-27 |
| F-006 | quality/module-state | Fixed (v0.2.0) | 2026-02-28 |
| F-007 | R-PREFS-04b | Fixed (v0.2.0) | 2026-02-28 |
| F-008 | quality/gettext-pattern | Fixed (v0.2.0) | 2026-02-28 |
| F-009 | quality/logging-volume | Fixed (v0.2.0) | 2026-02-28 |
| F-010 | async/missing-cancellable | Fixed (v0.2.0) | 2026-02-28 |
| F-011 | ego-simulate threshold | Fixed (v0.2.0) | 2026-02-28 |

**F-001: R-SEC-07 fires even when disclosure is present**
R-SEC-07 (pattern rule) fired WARN for any `St.Clipboard` match, while `quality/clipboard-disclosure` (heuristic) correctly PASSed when metadata.json disclosed clipboard usage. The two checks didn't cross-reference. **Fix**: Removed R-SEC-07 entirely — `quality/clipboard-disclosure` is a strict superset.

**F-002: Verdict "LIKELY REJECTED" threshold too aggressive**
A flat threshold of >5 warnings triggered "LIKELY REJECTED" regardless of warning nature. 14 warnings included informational items and per-file duplicates. ego-simulate scored 0 for the same extension. **Fix**: Changed to count unique check IDs instead of raw WARN lines.

**F-003: quality/gettext-pattern fix message inaccurate**
Message said "use `this.gettext()` from the Extension base class" but `this.gettext()` can't be used at module scope. The idiomatic pattern is `import {gettext as _}` from the base module. **Fix**: Updated message text.

**F-004: R-SEC-20 fires per-file not per-check**
Matched `\bpkexec\b` in all JS/shell files, catching string literals and comments. Only 1 of 5 matched files actually invoked pkexec. **Fix**: Scoped and deduplicated.

**F-005: quality/private-api inflates WARN count**
Each location emitted a separate WARN line (up to 6 for one check). One concern produced 6 warning lines, skewing `WARN_COUNT`. **Fix**: Consolidated to single WARN with all locations in detail text.

**F-006: quality/module-state only recognizes `= null` reset**
Variables reset to `0`, `false`, `Promise.resolve()` were not recognized as cleanup. hara-hachi-bu's `lib/helper.js` had 3 properly managed module-level variables flagged. **Fix**: Broadened reset regex to recognize any re-assignment.

**F-007: R-PREFS-04b flags widgets with no Adwaita equivalent**
`Gtk.ListBox` with `boxed-list` CSS, `Gtk.ScrolledWindow` for constrained height, etc. have no Adw replacement. **Fix**: Split into R-PREFS-04b (genuine replacements, advisory) and R-PREFS-04c (legitimate GTK layout widgets, info).

**F-008: quality/gettext-pattern flags lib modules incorrectly**
`GLib.dgettext()` is the correct approach for library modules that can't access the Extension base class. Only `extension.js` and `prefs.js` have base class gettext access. **Fix**: Scoped check to entry-point files only.

**F-009: quality/logging-volume threshold doesn't scale**
Fixed count threshold (~30) doesn't account for code size. hara-hachi-bu had ~1 log call per 84 lines — reasonable density but exceeded absolute count. **Fix**: Scale threshold by code volume (1 per 100 non-blank lines, minimum 30).

**F-010: async/missing-cancellable misses callback cancellation**
Check flagged `_async()` calls with null cancellable but didn't recognize functions with `isCancelled` callback parameters providing equivalent cancellation. **Fix**: Check enclosing function for cancellation-related parameters.

**F-011: ego-simulate/ego-lint notification threshold mismatch**
ego-simulate scored notification volume at >3 `Main.notify` sites, but ego-lint's threshold was 5. An extension with 4 sites scored in simulation but PASSed lint. **Fix**: Aligned thresholds and added cross-reference comment.

### Coverage Gaps Identified

| ID | Gap | Status | Added |
|----|-----|--------|-------|
| F-012 | Disclosure matrix | Fixed (v0.2.0) | 2026-02-28 |
| F-013 | Polkit action IDs | Fixed (v0.2.0) | 2026-02-28 |
| F-014 | Schema key usage | Fixed (v0.2.0) | 2026-02-28 |
| F-015 | Accessibility checks | Fixed (v0.2.0) | 2026-02-28 |

**F-012: Disclosure matrix not automated**
Cross-referencing code capabilities (clipboard, network, pkexec) vs. metadata.json disclosures was entirely manual. **Fix**: Added `check-disclosures.py` — scans for capabilities, reads metadata, cross-references.

**F-013: Polkit action ID not cross-referenced**
ego-lint checked polkit file existence and pkexec usage separately, but didn't validate that `.policy` action IDs match `.rules` references and code invocations. **Fix**: Added `check-polkit.py` with R-POLKIT-01/02/03.

**F-014: Schema key usage not validated**
No check that schema keys defined in `.gschema.xml` are used in code, or that code references keys that exist. **Fix**: Added `check-schema-usage.py` with R-SCHEMA-10/11.

**F-015: Accessibility checks minimal**
The A1-A7 checklist was entirely manual. Some items (accessible-role usage, accessible labels on buttons) can be partially automated. **Fix**: Added `check-accessibility.py` with R-A11Y-01/02.

### Pipeline Improvements Identified

| ID | Improvement | Status | Added |
|----|------------|--------|-------|
| F-016 | Parallelization strategy | Open | 2026-02-28 |
| F-017 | Code metrics | Fixed (v0.2.0) | 2026-02-28 |
| F-018 | Resource graph too large | Open | 2026-02-28 |
| F-019 | Reviewer notes template | Open | 2026-02-28 |
| F-020 | Readiness report format | Open | 2026-02-28 |
| F-021 | AI slop overlap | Open | 2026-02-28 |

**F-016: Parallelization strategy missing from ego-submit**
ego-submit describes sequential phases, but they're largely independent. A 3-agent parallel approach (lifecycle+signals, security+quality, package+metadata) cut wall-clock time from ~10 to ~4 minutes. **Status**: Open — needs parallelization strategy section in `skills/ego-submit/SKILL.md`.

**F-017: Code metrics not in ego-lint output**
ego-submit requires code metrics for readiness reports but ego-lint didn't output them. **Fix**: Added metrics to ego-lint verbose output.

**F-018: Resource graph output too large for manual review**
`build-resource-graph.py` outputs raw JSON (39KB for hara-hachi-bu). ego-review instructs reviewers to run it, producing output too large to meaningfully review. **Status**: Open — needs `--summary` flag for human-readable output.

**F-019: Reviewer notes template missing**
ego-submit says to "draft reviewer notes" but provides no template, producing inconsistent structure. **Status**: Open — needs `reviewer-notes-template.md` in `skills/ego-submit/references/`.

**F-020: Readiness report format not standardized**
ego-submit says to produce a "readiness report" but doesn't define format. **Status**: Open — needs `readiness-report-template.md` in `skills/ego-submit/references/`.

**F-021: AI slop overlap between ego-lint and ego-review**
`check-quality.py` covers some AI patterns, but the 46-item `ai-slop-checklist.md` doesn't indicate which items are automated. Reviewer agents re-check automated items. **Status**: Open — needs automation mapping column in checklist.

### EGO Reviewer Feedback

*No entries yet. This section will be populated when hara-hachi-bu completes EGO review.*

### Discoveries from PRs

*No entries yet. Link findings to GitHub issues/PRs as they arise.*

---

## How to Add a Finding

1. Assign the next available F-NNN number
2. Add a row to the appropriate category table
3. Add a 2-5 line detail paragraph below the table
4. Required fields: ID, Rule/Check or Gap, Status (`Fixed (vX.Y.Z)` / `Open` / `Deferred`), Added date
5. If the finding led to a code change, reference the commit or PR
6. Update the Current Baseline section if ego-lint results changed

---

## Pipeline Run History

| Date | Version | PASS | FAIL | WARN | SKIP | ego-simulate | Notes |
|------|---------|------|------|------|------|-------------|-------|
| 2026-02-27 | v0.1.0 (pre-fix) | 177 | 0 | 14 | 17 | 0 | Misleading "LIKELY REJECTED" verdict |
| 2026-02-27 | v0.1.0 (post-fix) | 191 | 0 | 6 | 17 | 0 | F-001 through F-005 fixed |
| 2026-02-28 | v0.2.0 | 193 | 0 | 5 | 17 | 1 | F-006 through F-015 fixed; 4 new Tier 2 scripts |

---

## Regression Infrastructure

**Local regression runner**: `tests/run-regression.sh` runs ego-lint against the locally installed extension (`~/.local/share/gnome-shell/extensions/hara-hachi-bu@ZviBaratz`) and sources assertions from `tests/assertions/local-regression.sh` (gitignored — contains 87 assertions specific to the local installation).

**Regression fixture**: `tests/fixtures/regressions/regression-001-ai-slop@test/` — minimal fixture that triggered an AI slop false positive (R-SLOP scoring regression). Part of CI test suite.

---

## Related Documents

- [false-positive-analysis-v0.1.0.md](false-positive-analysis-v0.1.0.md) — Detailed root-cause analysis for F-001 through F-005
- [improvements-v0.2.0.md](improvements-v0.2.0.md) — Detailed analysis and code snippets for F-006 through F-011
- [review-feedback-2026-02-28.md](review-feedback-2026-02-28.md) — Full pipeline improvement proposals (F-012 through F-021)
- [field-test-clipboard-indicator.md](field-test-clipboard-indicator.md) — One-shot field test (different format)
- [Gap analysis](../research/gap-analysis.md) — "Known False Positives and Noise Reduction" section
