# Field Test Review Prompt

You are running an ego-review for the GNOME Shell extension **{{NAME}}**.

## Instructions

Run the ego-review skill (phases 1 through 5a) on the extension at `{{EXT_PATH}}`.

**Skip Phase 0** — ego-lint has already been run. Use the pre-computed lint results below as your automated baseline. Do NOT re-run ego-lint.

For Phase 2, run the resource graph builder:
```bash
python3 {{PLUGIN_DIR}}/skills/ego-lint/scripts/build-resource-graph.py {{EXT_PATH}}
```

## Pre-computed Lint Results (JSON)

```json
{{LINT_JSON}}
```

{{DIFF_JSON_SECTION}}

{{ANNOTATIONS_SECTION}}

## Output

Produce the standard ego-review report format (Sections 1-6) as defined in the ego-review skill. Include:
- Section 1: Blocking Issues (Must Fix)
- Section 2: Justification Required
- Section 3: Advisory Issues
- Section 4: Automated Check Summary (from the lint JSON above)
- Section 5: AI Pattern Analysis
- Section 6: Submission Readiness

Focus on issues that ego-lint **cannot** detect: semantic correctness, cross-file design problems, async safety nuances, and contextual judgment calls. Do not duplicate findings already present in the lint results.
