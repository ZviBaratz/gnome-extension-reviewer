---
name: ego-submit
description: >-
  Complete pre-submission validation for EGO (extensions.gnome.org). Runs
  automated lint, performs manual code review, validates packaging, and
  produces a submission readiness report. Use as the final check before
  uploading to extensions.gnome.org.
---

# ego-submit

Complete pre-submission pipeline for extensions.gnome.org.

This skill orchestrates the full validation sequence before EGO submission,
combining automated checks with manual review in a structured pipeline.

## Parallelization Strategy

For extensions with 10+ JS files, run phases in parallel using 3 agents:

- **Agent 1:** ego-lint + package validation (Phase 1, Phase 3)
- **Agent 2:** ego-review lifecycle + signal + security (ego-review Phases 2-4)
- **Agent 3:** ego-review quality + AI patterns + metadata (ego-review Phases 5-5a, Phase 4)

When running in parallel, Agents 2-3 skip Phase 0 (ego-lint baseline) since
Agent 1 handles it. The deduplication happens at report compilation time, not
during individual agent work.

This reduces wall-clock time from ~10 minutes (sequential) to ~4 minutes. For
smaller extensions (<10 JS files), sequential execution is fine.

### Parallel Execution Protocol

When running in parallel mode:

- **Agent 1**: ego-lint + Phase 3 package validation. Reports lint summary
  (PASS/FAIL/WARN/SKIP counts) and package status.
- **Agent 2**: ego-review Phases 2-4 (lifecycle, signals, security). Skips
  Phase 0 since Agent 1 handles the ego-lint baseline.
- **Agent 3**: ego-review Phases 5-5a (quality, AI patterns) + Phase 4 metadata
  + disclosure matrix + reviewer notes draft.

**No early stopping**: All agents complete regardless of findings. If Agent 1
reports FAILs, the final readiness report verdict is NEEDS FIXES with FAIL
items listed first as blocking action items.

**Deduplication**: The orchestrator merges results from all agents. When ego-lint
and ego-review flag the same issue (e.g., both catch a missing signal
disconnect), prefer ego-lint's categorization (it has the rule ID).

**STOP condition**: Applied by the orchestrator after all agents complete, not
by individual agents during their work.

## Pipeline Phases

### Pre-flight: Review Simulation (skip if running full pipeline)

`gnome-extension-reviewer:ego-simulate` provides a quick (<1 min) reviewer's-eye-view
with a pass/fail score. Use it for iterative development during active coding;
skip it when running the full submission pipeline since Phases 1-5 provide
strictly more coverage.

- If the simulation score is **10+**: strongly recommend fixing blocking issues
  before proceeding with the full pipeline
- If the simulation score is **5-9**: note the concerns but proceed
- If the simulation score is **0-4**: proceed normally

The simulation is advisory — it does not block the pipeline.

### Phase 1: Automated Lint

Invoke `gnome-extension-reviewer:ego-lint` against the extension directory.

- Run all automated checks
- **Sequential mode**: If any FAIL results: **STOP** — fix failures before
  proceeding to Phase 2
- **Parallel mode**: All agents complete regardless. If FAILs are found, the
  final readiness report verdict is NEEDS FIXES with FAIL items listed first
  as blocking action items
- Report all WARN results for the developer to review

### Phase 2: Manual Code Review

Invoke `gnome-extension-reviewer:ego-review` against the extension directory.

- Perform the 5-phase review (discovery, lifecycle, signals, security, quality)
- If any BLOCKING issues found: **STOP** — fix before proceeding
- Report all ADVISORY issues

### Phase 3: Package Validation

ego-lint's `check-package.sh` already covers forbidden files, required files,
nested structure, and compiled schemas. Phase 3 only needs to cover:

1. Check if a distribution zip exists
2. If no, advise the developer to create one:
   - List what should be included (extension.js, metadata.json, schemas/, stylesheet.css, LICENSE, locale/)
   - List what should NOT be included (node_modules/, .git/, CLAUDE.md, .claude/, *.pot, tests/, docs/)
3. Verify extension-specific inclusions (e.g., `resources/`, `locale/`, helper scripts)
4. Check zip file size (warn if > 5MB)
5. Scan for secrets or dev artifacts not caught by `check-package.sh`

### Phase 4: Submission Metadata

Review the metadata and suggest improvements:

1. **Description quality**: Is it clear what the extension does? Are permissions disclosed?
2. **Screenshots**: Does the extension have screenshots ready? (not checked automatically)
3. **Shell versions**: Are the listed versions actually tested?
4. **Reviewer notes**: Draft notes for the EGO reviewer using
   [reviewer-notes-template.md](references/reviewer-notes-template.md), especially for:
   - pkexec/polkit usage
   - Private API usage
   - Network access
   - Clipboard access
5. **Disclosure cross-reference**: Compare what the code actually does against what the description declares:
   - Does code use `pkexec`/`Subprocess`? → Must be disclosed
   - Does code access clipboard (`St.Clipboard`)? → Must be disclosed
   - Does code make network requests (`Soup.Session`)? → Must be disclosed
   - Does code read/write files outside GSettings? → Must be disclosed

### Phase 5: Readiness Report

Generate a final report using
[readiness-report-template.md](references/readiness-report-template.md).

## Reference

For detailed submission guidance, see [submission-checklist.md](references/submission-checklist.md).
