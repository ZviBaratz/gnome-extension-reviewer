# Field Test: hara-hachi-bu (Living Document)

This is the consolidated findings registry for the project's calibration baseline extension. Unlike one-shot field tests (e.g., Clipboard Indicator), this document grows over time as new findings are discovered through EGO reviewer feedback, PRs, and tool changes.

## Extension Profile

| Field | Value |
|-------|-------|
| **Name** | hara-hachi-bu |
| **UUID** | `hara-hachi-bu@ZviBaratz` |
| **Source** | [GitHub](https://github.com/ZviBaratz/hara-hachi-bu) |
| **GNOME versions** | 46, 47, 48 |
| **Size** | 18 JS files, ~8,894 lines |
| **License** | GPL-3.0-or-later |
| **EGO status** | Submitted, in review (v1.0 was rejected) |
| **Why baseline** | Exercises pkexec/polkit, D-Bus proxies, file monitors, GSettings, scheduled profiles, boost charge state machine, multi-battery support. Covers nearly all lint categories. |

## Current Baseline

Latest ego-lint results (2026-03-03, post F-027 dedup fix):

| Status | Count |
|--------|-------|
| PASS | 205 |
| FAIL | 0 |
| WARN | 8 |
| SKIP | 23 |
| Exit | 0 |

**ego-simulate score**: 1 (advisory #22 for notification volume). Verdict: "Likely to pass with minor comments."

**ego-submit verdict**: READY TO SUBMIT (0 blocking issues, 0 risk points).

**Remaining WARNs** (all correct/expected):

| Warning | Nature |
|---------|--------|
| polkit-files | Informational — 2 polkit files present (expected) |
| R-SEC-20 | pkexec scrutiny advisory — correct, disclosed in metadata |
| R-PREFS-04c | GTK layout widget advisory — correct (ListBox, SpinButton in prefs) |
| R-SLOP-40 | Promise wrapper advisory — correct (D-Bus proxy constructor) |
| R-QUAL-33 | Gio._promisify() module-scope advisory — correct (standard GJS pattern) |
| R-VER48-04b | vertical property deprecated advisory — correct (deduplicated to 1 per file) |
| metadata/shell-version-current | GNOME 49 not in shell-version — intentional (untested) |
| quality/private-api | Private API with inline justification — disclosed in metadata |

**Resource graph**: 17 files scanned, depth 3, 0 orphans

**Code provenance score**: 3 (244 domain vocab, 59 algorithms, consistent camelCase naming)

**AI pattern analysis**: 1/46 triggered (pkexec usage — contextually justified). Verdict: PASS.

**Disclosure matrix**: All 6 capabilities (clipboard, network, pkexec, subprocess, private API, file I/O) checked — all properly disclosed or N/A. No gaps.

**Package**: 100.3 KB zip, 34 files. No forbidden files, no secrets, no dev artifacts. MockDevice.js correctly excluded.

---

## Findings Registry

Each finding has a stable ID (F-NNN) that never changes. New findings always get the next available number.

### False Positives Found and Fixed

| ID | Rule/Check | Status | Added |
|----|-----------|--------|-------|
| F-001 | R-SEC-07 | Fixed (2026-02-27) | 2026-02-27 |
| F-002 | Verdict threshold | Fixed (2026-02-27) | 2026-02-27 |
| F-003 | quality/gettext-pattern | Fixed (2026-02-27) | 2026-02-27 |
| F-004 | R-SEC-20 | Fixed (2026-02-27) | 2026-02-27 |
| F-005 | quality/private-api | Fixed (2026-02-27) | 2026-02-27 |
| F-006 | quality/module-state | Fixed (2026-02-28) | 2026-02-28 |
| F-007 | R-PREFS-04b | Fixed (2026-02-28) | 2026-02-28 |
| F-008 | quality/gettext-pattern | Fixed (2026-02-28) | 2026-02-28 |
| F-009 | quality/logging-volume | Fixed (2026-02-28) | 2026-02-28 |
| F-010 | async/missing-cancellable | Fixed (2026-02-28) | 2026-02-28 |
| F-011 | ego-simulate threshold | Fixed (2026-02-28) | 2026-02-28 |

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
| F-012 | Disclosure matrix | Fixed (2026-02-28) | 2026-02-28 |
| F-013 | Polkit action IDs | Fixed (2026-02-28) | 2026-02-28 |
| F-014 | Schema key usage | Fixed (2026-02-28) | 2026-02-28 |
| F-015 | Accessibility checks | Fixed (2026-02-28) | 2026-02-28 |

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
| F-016 | Parallelization strategy | Fixed (2026-03-01) | 2026-02-28 |
| F-017 | Code metrics | Fixed (2026-02-28) | 2026-02-28 |
| F-018 | Resource graph too large | Fixed (2026-03-01) | 2026-02-28 |
| F-019 | Reviewer notes template | Fixed (2026-03-01) | 2026-02-28 |
| F-020 | Readiness report format | Fixed (2026-03-01) | 2026-02-28 |
| F-021 | AI slop overlap | Fixed (2026-03-01) | 2026-02-28 |
| F-022 | Phase 3 rebuilds resource graph manually | Fixed (2026-03-03) | 2026-03-03 |
| F-023 | Phase 5a re-checks automated AI patterns | Fixed (2026-03-03) | 2026-03-03 |
| F-024 | check-disclosures.py missing 4 capabilities | Fixed (2026-03-03) | 2026-03-03 |
| F-025 | Resource graph markdown table output | Fixed (2026-03-03) | 2026-03-03 |
| F-026 | Parallel protocol prevents ego-lint reuse | Fixed (2026-03-03) | 2026-03-03 |
| F-027 | R-VER48-04b deduplicate regression | Fixed (2026-03-03) | 2026-03-03 |
| F-028 | Baseline suppression for known warnings | Deferred | 2026-03-03 |

**F-016: Parallelization strategy missing from ego-submit**
ego-submit describes sequential phases, but they're largely independent. A 3-agent parallel approach (lifecycle+signals, security+quality, package+metadata) cut wall-clock time from ~10 to ~4 minutes. **Fix**: Added "Parallel Execution Protocol" section to `skills/ego-submit/SKILL.md` with agent roles, no-early-stopping rule, and deduplication strategy.

**F-017: Code metrics not in ego-lint output**
ego-submit requires code metrics for readiness reports but ego-lint didn't output them. **Fix**: Added metrics to ego-lint verbose output.

**F-018: Resource graph output too large for manual review**
`build-resource-graph.py` outputs raw JSON (39KB for hara-hachi-bu). ego-review instructs reviewers to run it, producing output too large to meaningfully review. **Fix**: Added `--summary` flag producing human-readable output (files, resource counts, orphans, depth). Also added "Resource Graph Interpretation" guide to `lifecycle-checklist.md`.

**F-019: Reviewer notes template missing**
ego-submit says to "draft reviewer notes" but provides no template, producing inconsistent structure. **Fix**: Added `reviewer-notes-template.md` in `skills/ego-submit/references/`.

**F-020: Readiness report format not standardized**
ego-submit says to produce a "readiness report" but doesn't define format. **Fix**: Added `readiness-report-template.md` in `skills/ego-submit/references/`.

**F-021: AI slop overlap between ego-lint and ego-review**
`check-quality.py` covers some AI patterns, but the 46-item `ai-slop-checklist.md` doesn't indicate which items are automated. Reviewer agents re-check automated items. **Fix**: Added `**Automated:**` field to each checklist item with Yes/No/Partial and the ego-lint check name.

**F-022: Phase 3 rebuilds resource graph manually**
ego-review Phase 3 instructs agents to grep for signals, timeouts, file monitors, and D-Bus proxies — duplicating what `build-resource-graph.py` already computes in Phase 2. Agent 2 spent ~200s of 381s on this. **Fix**: Rewrite Phase 3 to verify the graph output rather than rebuild it. See [pipeline-review-2026-03-03.md](pipeline-review-2026-03-03.md).

**F-023: Phase 5a re-checks automated AI patterns**
Despite F-021 adding automation mapping to the AI slop checklist, Phase 5a instructions don't tell agents to skip automated items. Agent 3 searched for all 46 items. **Fix**: Update Phase 5a instructions to use ego-lint results for automated items.

**F-024: check-disclosures.py missing 4 capabilities**
F-012 added clipboard+network disclosure checking, but the 6-capability disclosure matrix (also pkexec, subprocess, private API, file I/O) is still partly manual. **Fix**: Extend check-disclosures.py to cover all 6. **Status**: Already fixed — check-disclosures.py covers all 6 capabilities (clipboard, network, pkexec, private-api, file-io, subprocess) at lines 35-99. The pipeline review observation was based on stale data from the F-012 description.

**F-025: Resource graph markdown table output**
Readiness report requires a per-resource tracking table. Agents manually format this from graph JSON. **Fix**: Add `--format=table` flag to output markdown directly.

**F-026: Parallel protocol prevents ego-lint reuse**
3-agent parallel protocol runs ego-lint concurrently with review agents, so Agents 2-3 can't use ego-lint results. **Fix**: Two-phase approach: run ego-lint first (~30s), then fan out 2 review agents with ego-lint output as context.

**F-027: R-VER48-04b deduplicate regression**
Rule fired twice for quickSettingsPanel.js (lines 100 and 909). Previous run showed single WARN coincidentally. **Fix**: Not a regression — rule never had `deduplicate: true`. Added the field to collapse per-file hits into a single advisory WARN.

**F-028: Baseline suppression for known warnings**
No mechanism to mark warnings as acknowledged. Every run produces the same 7-9 known WARNs, drowning new findings. **Deferred**: Existing inline `// ego-lint-ignore` suppression is sufficient. The known WARNs are correct warnings that flag real patterns reviewers will notice — suppressing them could mask regressions. Baseline feature would require changes to ego-lint.sh's output pipeline, JSON file management, and new CLI flags (medium effort, P2).

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

| Date | PASS | FAIL | WARN | SKIP | ego-simulate | Notes |
|------|------|------|------|------|-------------|-------|
| 2026-02-27 (pre-fix) | 177 | 0 | 14 | 17 | 0 | Misleading "LIKELY REJECTED" verdict |
| 2026-02-27 (post-fix) | 191 | 0 | 6 | 17 | 0 | F-001 through F-005 fixed |
| 2026-02-28 | 193 | 0 | 5 | 17 | 1 | F-006 through F-015 fixed; 4 new Tier 2 scripts |
| 2026-03-01 | 201 | 0 | 8 | 23 | — | 6 new pattern rules, +3 WARNs (R-SLOP-40, R-QUAL-33, R-PREFS-04c), +6 SKIP (VER49/50) |
| 2026-03-02 | 206 | 0 | 7 | 23 | 1 | Full ego-submit pipeline (3-agent parallel). ESLint WARN resolved. +5 PASS. ego-submit: READY TO SUBMIT |
| 2026-03-03 | 205 | 0 | 9 | 23 | — | Full ego-submit (3-agent parallel, fresh session). +2 WARNs (R-VER48-04b dedup regression). Pipeline efficiency review → F-022 through F-028 |
| 2026-03-03 (post-fix) | 205 | 0 | 8 | 23 | — | F-022/F-023/F-025/F-026/F-027 fixed, F-024 closed, F-028 deferred. R-VER48-04b deduplicated (9→8 WARNs). 2-phase parallel protocol |

---

## Regression Infrastructure

**Local regression runner**: `tests/run-regression.sh` runs ego-lint against the locally installed extension (`~/.local/share/gnome-shell/extensions/hara-hachi-bu@ZviBaratz`) and sources assertions from `tests/assertions/local-regression.sh` (gitignored — contains 87 assertions specific to the local installation).

**Regression fixture**: `tests/fixtures/regressions/regression-001-ai-slop@test/` — minimal fixture that triggered an AI slop false positive (R-SLOP scoring regression). Part of CI test suite.

---

## Related Documents

- [false-positive-analysis-2026-02-27.md](false-positive-analysis-2026-02-27.md) — Detailed root-cause analysis for F-001 through F-005
- [pipeline-improvements-2026-02-28.md](pipeline-improvements-2026-02-28.md) — Detailed analysis and code snippets for F-006 through F-011
- [review-feedback-2026-02-28.md](review-feedback-2026-02-28.md) — Full pipeline improvement proposals (F-012 through F-021)
- [field-test-clipboard-indicator.md](field-test-clipboard-indicator.md) — One-shot field test (different format)
- [pipeline-review-2026-03-03.md](pipeline-review-2026-03-03.md) — Pipeline efficiency review: agent redundancy, parallel protocol redesign (F-022 through F-028)
- [Gap analysis](../research/gap-analysis.md) — "Known False Positives and Noise Reduction" section
