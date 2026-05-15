# Field Test Template

Use this template when running the ego-submit pipeline against a real extension. Copy this file as `field-test-<extension-name>.md` and fill in each section.

> The baseline extension (hara-hachi-bu) uses a living-document variant with a findings registry. See `field-test-hara-hachi-bu.md`. Other field tests use this template and can be re-run as the tool improves.

## Pre-flight

- **Extension**: [name] ([UUID])
- **Source**: [GitHub URL or local path]
- **Test mode**: `EGO ZIP` | `source checkout`
  - **EGO ZIP**: Downloaded from extensions.gnome.org (packaged release). Canonical test — matches exactly what EGO reviewers see. Fewer files, cleaner metadata, no build artifacts. Use for calibration against reviewer expectations.
  - **Source checkout**: Cloned from the extension's Git repository. Exercises more surface area (templates, sub-dirs, build artifacts, locale files). Warning and check counts can be significantly higher — **do not compare raw numbers between the two modes**. Directory-name checks always produce FPs on source checkouts (see lesson #2 in README).
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
