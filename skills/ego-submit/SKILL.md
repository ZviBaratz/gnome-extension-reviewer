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

## Pipeline Phases

### Phase 1: Automated Lint

Invoke `gnome-extension-reviewer:ego-lint` against the extension directory.

- Run all automated checks
- If any FAIL results: **STOP** — fix failures before proceeding
- Report all WARN results for the developer to review

### Phase 2: Manual Code Review

Invoke `gnome-extension-reviewer:ego-review` against the extension directory.

- Perform the 5-phase review (discovery, lifecycle, signals, security, quality)
- If any BLOCKING issues found: **STOP** — fix before proceeding
- Report all ADVISORY issues

### Phase 3: Package Validation

1. Check if a distribution zip exists
2. If yes, validate contents via ego-lint's package check
3. If no, advise the developer to create one:
   - List what should be included (extension.js, metadata.json, schemas/, stylesheet.css, LICENSE, locale/)
   - List what should NOT be included (node_modules/, .git/, CLAUDE.md, .claude/, *.pot, tests/, docs/)
4. Check zip file size (warn if > 5MB)

### Phase 4: Submission Metadata

Review the metadata and suggest improvements:

1. **Description quality**: Is it clear what the extension does? Are permissions disclosed?
2. **Screenshots**: Does the extension have screenshots ready? (not checked automatically)
3. **Shell versions**: Are the listed versions actually tested?
4. **Reviewer notes**: Draft notes for the EGO reviewer, especially for:
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

Generate a final report:

```
## EGO Submission Readiness Report

### Status: READY TO SUBMIT | NEEDS FIXES

### Automated Checks
- X passed, Y failed, Z warnings

### Code Metrics
- Total JS files: N
- Total non-blank lines: N
- Largest file: filename (N lines)

### Code Review
- X blocking, Y advisory, Z info

### AI Pattern Analysis
- Items checked: N
- Items triggered: N
  - [triggered item descriptions]
- Assessment: PASS | ADVISORY | BLOCKING

### Package
- Valid | Not created | Issues found

### Reviewer Notes (include in EGO submission)
- [note 1]
- [note 2]

### Action Items
1. [action needed]
2. [action needed]
```

## Reference

For detailed submission guidance, see [submission-checklist.md](references/submission-checklist.md).
