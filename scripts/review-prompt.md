Run /ego-review on the extension at {{EXT_PATH}}.

Your ENTIRE text output will be saved as the review report file. Do NOT summarize at the end — your full output IS the deliverable. Write the complete report inline as you go, with all six sections in full detail. Every word you output goes into the report.

## Phase 0 Override

Skip Phase 0 (ego-lint). It has already been run. Use these pre-computed results as your automated baseline — do NOT re-run ego-lint:

```json
{{LINT_JSON}}
```

{{DIFF_JSON_SECTION}}

{{ANNOTATIONS_SECTION}}

## Required Output

Write the FULL ego-review report with ALL sections below. Do NOT abbreviate or skip any section. If a section has no findings, write "None" under it — do not omit it.

Start your output with:
```
## EGO Review Report — {{NAME}}
```

Then include ALL of these sections:

### Section 1: Blocking Issues (Must Fix)
Each issue: file:line, description, why reviewers reject it, fix code.

### Section 2: Justification Required
Items acceptable IF properly documented.

### Section 3: Advisory Issues (May Cause Questions)
Each: file:line, description, reviewer perspective, suggestion.

### Section 4: Automated Check Summary
Build from the lint JSON above. Table: Category × Pass/Fail/Warn.

### Section 5: AI Pattern Analysis
Score, triggered items with file:line, assessment.

### Section 6: Submission Readiness
Verdict (LIKELY APPROVED / NEEDS REVISION / LIKELY REJECTED), action items checklist.

Focus on issues ego-lint CANNOT detect: semantic correctness, cross-file design, async safety, contextual judgment. Do not duplicate lint findings.
