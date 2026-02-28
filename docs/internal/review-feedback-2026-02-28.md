> **Note**: hara-hachi-bu findings from this document are consolidated in [field-test-hara-hachi-bu.md](field-test-hara-hachi-bu.md) (F-012 through F-021).

# gnome-extension-reviewer: Review Feedback (2026-02-28)

## Source

Full ego-submit pipeline run on `hara-hachi-bu@ZviBaratz` (2026-02-28). Extension profile: 17 JS files, 8,800 lines, pkexec/polkit, D-Bus proxies, file monitors, GSettings, scheduled profiles, boost charge state machine, multi-battery support.

Result: READY (0 FAIL, 5 WARN, 193 PASS on ego-lint; 0 blocking on manual review; AI score 1/46).

---

## P0: Parallelization Strategy Missing from ego-submit

**Problem:** The ego-submit skill describes a sequential 5-phase pipeline, but the phases are largely independent. In practice, I had to manually design a 3-agent parallel approach:
- Agent 1: Lifecycle + signal audit (ego-review phases 2-3)
- Agent 2: Security + quality + AI patterns (ego-review phases 4-5a)
- Agent 3: Package + metadata validation (ego-submit phases 3-4)

This cut wall-clock time from ~10 minutes (sequential) to ~4 minutes (parallel).

**Fix:** Add a "Parallelization Strategy" section to `skills/ego-submit/SKILL.md` documenting which phases can run concurrently. Suggest the 3-agent split as the default approach for complex extensions (10+ files).

**Files:** `skills/ego-submit/SKILL.md`

---

## P0: Disclosure Matrix Not Automated

**Problem:** Cross-referencing code capabilities vs. metadata.json disclosures is done entirely by the manual reviewer agent. Each agent independently searches for clipboard, network, pkexec, and private API usage, then checks if metadata.json mentions them. This is deterministic and should be automated.

**Fix:** Add a `check-disclosures.py` script to ego-lint that:
1. Scans code for `St.Clipboard`, `Soup.Session`, `pkexec`, `_indicators` (and other private API patterns)
2. Reads metadata.json description
3. Cross-references: WARN if capability found in code but not disclosed
4. Handles the clipboard-network pairing check (already partially in check-quality.py)

**Files:** New `skills/ego-lint/scripts/check-disclosures.py`, update `skills/ego-lint/scripts/ego-lint.sh`

---

## P1: Code Metrics Not Automated

**Problem:** ego-submit requires code metrics (JS file count, total lines, largest file) for the readiness report, but ego-lint doesn't output them. Each review agent must compute them manually with `wc -l`.

**Fix:** Add a `--metrics` flag to `ego-lint.sh` that outputs:
```
[METRIC] js-files: 17
[METRIC] total-lines: 8782
[METRIC] largest-file: prefs.js (1973)
[METRIC] css-lines: 126
[METRIC] schema-keys: 24
```

Or always include metrics in verbose mode.

**Files:** `skills/ego-lint/scripts/ego-lint.sh`

---

## P1: Resource Graph Output Too Large

**Problem:** `build-resource-graph.py` outputs raw JSON (39KB for hara-hachi-bu). The ego-lint `check-resources.py` consumes it, but the ego-review skill also instructs reviewers to "run the resource graph builder" — producing output that's too large to meaningfully review.

**Fix:** Add a `--summary` flag to `build-resource-graph.py` that outputs a concise human-readable summary:
```
Resources: 39 connectObject, 15 timeouts, 3 file monitors, 5 D-Bus proxies
Orphans: 0
Balance: All resources have matching cleanup
Largest chain: extension.js → stateManager → parameterDetector (depth 3)
```

Keep the full JSON as default for `check-resources.py` consumption.

**Files:** `skills/ego-lint/scripts/build-resource-graph.py`

---

## P1: Reviewer Notes Template Missing

**Problem:** ego-submit tells the agent to "draft reviewer notes for EGO submission" but provides no template. Each run produces different structure and coverage. The agent had to infer what reviewers care about.

**Fix:** Add a `reviewer-notes-template.md` to `skills/ego-submit/references/` with sections:
1. pkexec/polkit justification (if applicable)
2. Private API justification (if applicable)
3. Network access disclosure (if applicable)
4. Clipboard usage disclosure (if applicable)
5. File system operations beyond GSettings (if applicable)
6. Session mode usage (if applicable)

Each section has fill-in-the-blank guidance.

**Files:** New `skills/ego-submit/references/reviewer-notes-template.md`, update `skills/ego-submit/SKILL.md`

---

## P1: Readiness Report Format Not Standardized

**Problem:** ego-submit says to produce a "readiness report" but doesn't define a format. Each run produces a different structure. The synthesizing agent has to design the report layout from scratch.

**Fix:** Add a `readiness-report-template.md` to `skills/ego-submit/references/` with the standard sections:
1. Verdict (READY / NOT READY)
2. Automated lint summary (table: PASS/FAIL/WARN/SKIP counts)
3. Code metrics
4. Code review findings (grouped by severity)
5. AI pattern analysis (score, triggered items)
6. Package validation
7. Disclosure matrix
8. Reviewer notes
9. Prioritized action items

**Files:** New `skills/ego-submit/references/readiness-report-template.md`, update `skills/ego-submit/SKILL.md`

---

## P2: AI Slop Overlap Between ego-lint and ego-review

**Problem:** `check-quality.py` in ego-lint covers some AI patterns (try-catch density, impossible state, empty catch, destroyed density, mock detection, constructor resources, code provenance). The ego-review `ai-slop-checklist.md` has 46 items. There's no mapping of which items are automated vs. manual-only.

The reviewer agent re-checks items already covered by ego-lint, wasting time.

**Fix:** Add a column to `ai-slop-checklist.md`:
```markdown
| # | Item | Automated by ego-lint? | Notes |
|---|------|------------------------|-------|
| 1 | Excessive try-catch | Yes (quality/try-catch-density) | |
| 2 | Empty catch blocks | Yes (quality/empty-catch) | |
| 5 | isLocked without session-mode | Yes (quality/impossible-state) | |
| 8 | TypeScript-style JSDoc | No | Manual only |
...
```

This lets the ego-review agent skip items already covered and focus on manual-only checks.

**Files:** `skills/ego-review/references/ai-slop-checklist.md`

---

## P2: Polkit Action ID Not Cross-Referenced

**Problem:** ego-lint checks that polkit files exist (`polkit-files` check) and that pkexec is used (`R-SEC-20`), but doesn't validate that:
1. The `.policy` file's action ID matches what the code invokes
2. The `.rules` file references the same action ID
3. The helper script path in the rules matches the actual script location

This was flagged as a "Help Wanted" item in the README.

**Fix:** Add cross-reference logic to `check-disclosures.py` (or a new `check-polkit.py`):
- Parse `.policy` XML for action IDs
- Parse `.rules` JS for referenced action IDs and program paths
- Grep code for pkexec invocations and compare

**Files:** New `skills/ego-lint/scripts/check-polkit.py` or extend `check-disclosures.py`

---

## P2: GSettings Schema Key Usage Not Validated

**Problem:** No check that:
1. Schema keys defined in `.gschema.xml` are actually used in code
2. Code references to `settings.get_*('key-name')` use keys that exist in the schema

Unused schema keys add bloat and confuse reviewers. Missing keys cause runtime crashes.

**Fix:** Add a `check-schema-usage.py` script:
- Parse `.gschema.xml` for defined keys
- Grep JS files for `get_int|get_string|get_boolean|get_strv|set_|bind\(` with key names
- Report: unused keys (WARN), referenced-but-undefined keys (FAIL)

**Files:** New `skills/ego-lint/scripts/check-schema-usage.py`, update `skills/ego-lint/scripts/ego-lint.sh`

---

## P2: Accessibility Checks Minimal

**Problem:** The accessibility checklist (A1-A7) is entirely manual and only 98 lines. Some items could be partially automated:
- A1: Search for `update_property` / `accessible-role` usage
- A2: Check that clickable custom widgets have accessible names
- A5: Verify contrast ratios in stylesheet.css (basic check)

**Fix:** Add a `check-accessibility.py` script with basic automated checks:
- Count custom St.Widget subclasses vs. `accessible-role` declarations
- Flag `St.Button`/`St.Icon` without accessible labels
- Check CSS for low-contrast patterns

**Files:** New `skills/ego-lint/scripts/check-accessibility.py`

---

## P3: ego-simulate Redundancy

**Problem:** When running the full ego-submit pipeline, ego-simulate (described as "optional pre-flight") adds no value — its 23-reason taxonomy is entirely subsumed by ego-lint + ego-review. The simulation's weighted scoring is less precise than the actual findings.

**Recommendation:** Don't remove ego-simulate (it's useful for quick triage), but document in ego-submit that it should be skipped when running the full pipeline. Currently the skill says "optional" but doesn't explain when to use it vs. not.

**Fix:** Update `skills/ego-submit/SKILL.md` phase 1 to say:
> **Pre-flight (skip if running full pipeline)**: ego-simulate provides a quick (<1 min) reviewer's-eye-view. Use it for iterative development; skip it when running the full submission pipeline since phases 2-5 provide strictly more coverage.

**Files:** `skills/ego-submit/SKILL.md`

---

## P3: Package Validation Duplication

**Problem:** ego-lint already has `check-package.sh` that validates zip contents (forbidden files, required files, compiled schemas). The ego-submit skill then describes a separate "Phase 3: Package Validation" that repeats many of the same checks (size, included/excluded files).

**Fix:** Clarify in ego-submit that Phase 3 only needs to cover checks NOT in ego-lint:
- Verify specific files relevant to this extension (e.g., `resources/`, `locale/`)
- Check zip size against EGO limits
- Everything else is covered by ego-lint's `check-package.sh`

**Files:** `skills/ego-submit/SKILL.md`

---

## Summary: Priority Matrix

| Priority | Item | Type | Effort |
|----------|------|------|--------|
| **P0** | Parallelization strategy in ego-submit | Skill doc | Small |
| **P0** | Automated disclosure matrix | New script | Medium |
| **P1** | Code metrics in ego-lint | Script enhancement | Small |
| **P1** | Resource graph summary mode | Script enhancement | Small |
| **P1** | Reviewer notes template | Reference doc | Small |
| **P1** | Readiness report template | Reference doc | Small |
| **P2** | AI slop automation mapping | Reference doc update | Small |
| **P2** | Polkit action ID cross-reference | New script | Medium |
| **P2** | GSettings key usage validation | New script | Medium |
| **P2** | Accessibility automation | New script | Medium |
| **P3** | ego-simulate skip guidance | Skill doc | Small |
| **P3** | Package validation dedup | Skill doc | Small |
