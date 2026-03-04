---
name: ego-field-test
description: Run automated field tests across all registered GNOME extensions, diff against baselines, classify findings, and produce regression reports.
---

# ego-field-test — Automated Field Test Pipeline

Run batch ego-lint across all field test extensions with baseline diffing, finding classification, and regression reporting.

## Modes

- **Default** (no args): Lint-only batch + classify + synthesize (fast, no API cost beyond this session)
- `--review`: Also run ego-review on extensions with changed results via `claude -p`
- `--review-all`: Run ego-review on ALL extensions regardless of changes
- `--update-baselines`: Save current lint results as new baselines after review

## Workflow

### Step 1: Run the Orchestrator

```bash
bash scripts/field-test-runner.sh --no-fetch
```

If extensions aren't cached yet:
```bash
bash scripts/field-test-runner.sh
```

This runs ego-lint on all extensions in `field-tests/manifest.yaml`, produces JSON results per extension, diffs against baselines, and appends to history.

### Step 2: Review Results

Read the summary:
```
field-tests/results/<latest-timestamp>/summary.json
```

For each extension, read:
- `field-tests/results/<latest-timestamp>/<name>.lint.json` — full results
- `field-tests/results/<latest-timestamp>/<name>.diff.json` — diff from baseline (if baseline exists)

### Step 3: Classify New Findings

For each extension with `unannotated_findings` in the diff:

1. Read the finding details from the lint JSON
2. Read the extension source code to determine if each finding is TP, FP, borderline, or expected
3. Update `field-tests/annotations/<name>.yaml` with the classification

Classification guide:
- **tp**: True positive — real issue that a reviewer would flag
- **fp**: False positive — ego-lint is wrong, should be fixed in the tool
- **borderline**: Arguable — reasonable people could disagree
- **expected**: Correct detection but expected for this extension type (e.g., shell overrides in V-Shell)

### Step 4: Selective ego-review (if `--review` or `--review-all`)

For each extension with changed results (or all, with `--review-all`):

Run ego-review via headless Claude:
```bash
claude -p "Run /ego-submit on <extension-path>. Focus on unannotated findings and issues ego-lint cannot detect. Known findings to skip: <annotation file contents>. Current lint results: <lint JSON>. Changes from baseline: <diff JSON>."
```

Save output to `field-tests/results/<timestamp>/<name>.review.md`.

### Step 5: Synthesize Regression Report

Produce `field-tests/reports/<date>-regression.md` with:

1. **Summary table**: Extension name × PASS/FAIL/WARN/SKIP with deltas from baseline
2. **Trend data**: From `field-tests/history.jsonl` — FP count on approved extensions over last N runs
3. **New unannotated findings** grouped by rule ID (cross-extension patterns)
4. **Resolved findings** (things that got fixed)
5. **High-priority FP candidates**: Rules that fire as FP on 2+ approved extensions
6. **Gaps**: Findings ego-review caught that ego-lint missed (only if `--review`)

### Step 6: Issue Creation (if FPs confirmed)

For new false positives on EGO-approved extensions that are confirmed FP (not borderline):

Create a GitHub issue:
- Label: `false-positive`
- Title: `False positive: R-XXXX-NN on <extension>`
- Body: Rule ID, file:line, why it's FP, which other extensions are affected, suggested fix

### Step 7: Update Baselines (if `--update-baselines`)

```bash
bash scripts/field-test-runner.sh --update-baselines --no-fetch
```

## File Layout

```
field-tests/
├── manifest.yaml           # Extension sources (committed)
├── cache/                  # Downloaded extensions (gitignored)
├── baselines/              # Golden JSON snapshots (committed)
├── annotations/            # Finding classifications (committed)
├── results/                # Timestamped run output (gitignored)
├── history.jsonl           # Trend data (committed)
└── reports/                # Regression reports (committed)

scripts/
├── field-test-runner.sh    # Bash orchestrator
├── parse-manifest.py       # Manifest YAML → JSON
├── parse-lint-results.py   # ego-lint output → JSON
└── diff-baselines.py       # Baseline comparison
```

## Annotation Format

```yaml
findings:
  - id: "R-SEC-22::dconf CLI spawn"
    classification: tp
    notes: "dconf import/export — legitimate but needs disclosure"

  - id: "init/shell-modification::constructor"
    classification: fp
    notes: "Constructor called from enable(). Fixed in PR #21"
    fixed_in: "#21"
```

## Iteration Cycle

1. Make a code change (guard pattern, threshold tweak, new rule)
2. Run `/ego-field-test` — see immediate impact across all extensions
3. Classify new unannotated findings
4. If FPs found, create issues and fix them
5. Run `/ego-field-test --update-baselines` to snapshot improved state
6. Repeat
