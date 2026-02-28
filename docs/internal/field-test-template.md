# Field Test Template

Use this template when running the ego-submit pipeline against a real extension. Copy this file as `field-test-<extension-name>.md` and fill in each section.

## Pre-flight

- **Extension**: [name] ([UUID])
- **Source**: [GitHub URL or local path]
- **GNOME versions**: [shell-version from metadata.json]
- **File count**: [N JS files, total lines]
- **License**: [type and filename]
- **Why this extension**: [what rule categories it exercises]

## Step 1: ego-lint

```bash
./ego-lint --verbose /path/to/extension
```

### Results

| Status | Count |
|--------|-------|
| PASS   |       |
| FAIL   |       |
| WARN   |       |
| SKIP   |       |
| Exit   |       |

### Classification of Each FAIL

| Rule | File:Line | TP/FP/Expected | Root Cause (if FP) |
|------|-----------|----------------|-------------------|
|      |           |                |                   |

### Classification of Key WARNs

| Rule | File:Line | Legitimate? | Notes |
|------|-----------|-------------|-------|
|      |           |             |       |

## Step 2: ego-review

Run the full multi-phase review (phases 0-5a).

### Verdict

**[LIKELY APPROVED | NEEDS REVISION | LIKELY REJECTED]** | **Risk: [LOW | MEDIUM | HIGH]**

### Blocking Issues

| # | Issue | File:Line | Category |
|---|-------|-----------|----------|
|   |       |           |          |

### Issues ego-lint Could Not Detect

List findings that required semantic/cross-file analysis:

1. ...

### AI Pattern Analysis

**Score**: N/46 | **Assessment**: [ADVISORY | BLOCKING]

## Step 3: ego-simulate

### Score

| Taxonomy Reason | Weight | Evidence |
|-----------------|--------|----------|
|                 |        |          |
| **Total**       |        |          |

### Verdict

**Score: N** — [verdict text]

### Calibration Check

Is the extension approved on EGO? If yes, does the score match expectations?

## Fixes Implemented

### False Positives Fixed

| Rule/Check | Root Cause | Fix |
|------------|-----------|-----|
|            |           |     |

### New Rules Added

| Rule ID | What It Catches | Triggered By |
|---------|----------------|-------------|
|         |                |             |

### Test Fixtures Added

| Fixture | What It Tests |
|---------|--------------|
|         |              |

## Regression Verification

```bash
bash tests/run-tests.sh
./ego-lint --verbose /path/to/extension        # re-run
./ego-lint --verbose ~/.local/share/gnome-shell/extensions/hara-hachi-bu@ZviBaratz  # baseline
```

| Target | Before | After |
|--------|--------|-------|
| Extension under test |  |  |
| hara-hachi-bu baseline |  |  |
| Test suite |  |  |

## Calibration Lessons Learned

Add any new lessons to `docs/internal/README.md` cumulative list.

1. ...
