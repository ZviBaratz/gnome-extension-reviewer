Run /ego-review on the extension at {{EXT_PATH}}.

IMPORTANT: You MUST read the extension source files and produce the FULL ego-review report with ALL six sections. Do NOT summarize. Do NOT skip phases. Output the complete report in markdown.

## Phase 0 Override

Skip Phase 0 (ego-lint). It has already been run. Use these pre-computed results as your automated baseline — do NOT re-run ego-lint:

```json
{{LINT_JSON}}
```

{{DIFF_JSON_SECTION}}

{{ANNOTATIONS_SECTION}}

## Required Output Format

You MUST output ALL of these sections with full detail:

### Section 1: Blocking Issues (Must Fix)
List each blocking issue with file:line, description, why reviewers reject it, and fix code.

### Section 2: Justification Required
Items acceptable IF properly documented.

### Section 3: Advisory Issues (May Cause Questions)
Each with file:line, description, reviewer perspective, suggestion.

### Section 4: Automated Check Summary
Build from the lint JSON above. Table with Category × Pass/Fail/Warn.

### Section 5: AI Pattern Analysis
Score, triggered items with file:line, assessment.

### Section 6: Submission Readiness
Verdict (LIKELY APPROVED / NEEDS REVISION / LIKELY REJECTED), action items checklist.

Focus on issues ego-lint CANNOT detect: semantic correctness, cross-file design, async safety, contextual judgment. Do not duplicate lint findings.
