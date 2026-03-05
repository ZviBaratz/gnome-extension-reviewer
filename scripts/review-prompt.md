Run /ego-review on the extension at {{EXT_PATH}}.

IMPORTANT — Write incrementally to survive budget limits:
You MUST write to the report file after EACH section using the Write tool. Do NOT wait until the end. If you run out of budget mid-review, earlier sections will still be saved.

Write the report to: {{REVIEW_OUTPUT_PATH}}

First, write the header immediately:

```
## EGO Review Report — {{NAME}}
```

Then after completing each section, APPEND it to the file by re-writing the full file (header + all completed sections so far). This ensures no work is lost if the session is terminated.

The report MUST contain ALL six sections in full detail. Do NOT summarize. Do NOT abbreviate. If a section has no findings, write "None" under it — do not omit the section.

## Phase 0 Override

Skip Phase 0 (ego-lint). It has already been run. Use these pre-computed results as your automated baseline — do NOT re-run ego-lint:

```json
{{LINT_JSON}}
```

{{DIFF_JSON_SECTION}}

{{ANNOTATIONS_SECTION}}

## Required Report Sections (write after completing EACH one)

### Section 1: Blocking Issues (Must Fix)
Each issue: file:line, description, why reviewers reject it, fix code.
→ Write the file now (header + Section 1).

### Section 2: Justification Required
Items acceptable IF properly documented.
→ Write the file now (header + Sections 1-2).

### Section 3: Advisory Issues (May Cause Questions)
Each: file:line, description, reviewer perspective, suggestion.
→ Write the file now (header + Sections 1-3).

### Section 4: Automated Check Summary
Build from the lint JSON above. Table: Category × Pass/Fail/Warn.
→ Write the file now (header + Sections 1-4).

### Section 5: AI Pattern Analysis
Score, triggered items with file:line, assessment.
→ Write the file now (header + Sections 1-5).

### Section 6: Submission Readiness
Verdict (LIKELY APPROVED / NEEDS REVISION / LIKELY REJECTED), action items checklist.
→ Write the file now (header + all 6 sections — final version).

Focus on issues ego-lint CANNOT detect: semantic correctness, cross-file design, async safety, contextual judgment. Do not duplicate lint findings.
