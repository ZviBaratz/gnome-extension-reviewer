Run /ego-review on the extension at {{EXT_PATH}}.

After completing the review, you MUST write the full report to a file using the Write tool:

Write the report to: {{REVIEW_OUTPUT_PATH}}

The report MUST contain ALL six sections in full detail. Do NOT summarize. Do NOT abbreviate. If a section has no findings, write "None" under it — do not omit the section.

## Phase 0 Override

Skip Phase 0 (ego-lint). It has already been run. Use these pre-computed results as your automated baseline — do NOT re-run ego-lint:

```json
{{LINT_JSON}}
```

{{DIFF_JSON_SECTION}}

{{ANNOTATIONS_SECTION}}

## Required Report Format

The report file MUST start with:

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
