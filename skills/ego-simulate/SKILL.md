---
name: ego-simulate
description: >-
  Simulate an EGO review submission — produces a readiness report based on
  published review criteria. Triages the extension in reviewer order, applies
  a 23-reason rejection taxonomy with weighted scoring, and generates a
  structured report with a pass/fail verdict. Use before EGO submission to
  assess review readiness.
---

# EGO Review Simulation

Simulate how an EGO (extensions.gnome.org) reviewer would evaluate this GNOME
Shell extension submission. Unlike ego-review (which is a thorough code review)
or ego-submit (which is a packaging pipeline), this skill focuses on
**assessing the extension against known review criteria and published rejection
patterns**.

## Prerequisites

The extension directory must be provided by the user (or use the current
working directory).

## Process

### Step 1: Run ego-lint

Run the automated linter first to establish a baseline:

```bash
bash skills/ego-lint/scripts/ego-lint.sh --verbose EXTENSION_DIR
```

Capture the results: FAIL count, WARN count, and specific findings with
file:line references. These feed directly into the scoring in Step 3.

### Step 2: Reviewer Triage

Read `references/reviewer-persona.md` before starting this step.

Adopt the reviewer persona and triage the extension in the order reviewers
actually follow. Do NOT reorganize by category — follow this exact sequence:

1. **metadata.json** — Check UUID, shell-version, required fields, session-modes.
   A bad UUID or missing shell-version stops the review immediately.
2. **Code volume** — Count files and total lines. Assess whether this is
   reviewable in reasonable time. >5000 lines triggers extra scrutiny.
3. **enable/disable symmetry** — Quick visual check that `disable()` undoes
   everything `enable()` creates. This is the #1 rejection cause.
4. **Signal management** — Search for `.connect(` and `.disconnect(` — counts
   should roughly balance. Check for `connectObject` usage (modern pattern).
5. **Timeout handling** — Search for `timeout_add` and `Source.remove` /
   `GLib.Source.remove`. Verify stored IDs and cleanup in disable.
6. **Import segregation** — Quick scan that `extension.js` doesn't import GTK
   and `prefs.js` doesn't import Shell modules.
7. **Deeper read** — Only if all above pass: check for AI slop signals,
   security issues, API correctness, code quality.

For each step, note what a reviewer would think. Use the reviewer's internal
monologue style: "I see X but Y is missing" or "This looks clean."

### Step 3: Score

Read `references/rejection-taxonomy.md` before scoring.

Apply the 23-reason rejection taxonomy. For each reason:
- Check whether the extension triggers it
- If triggered, record the weight and the specific evidence (file:line)
- Each reason contributes its weight ONCE regardless of occurrence count

Sum the weights to compute the total score.

Also read `references/approved-examples.md` to calibrate — note where the
extension follows or deviates from idiomatic patterns.

### Step 4: Report

Generate the simulation report in this exact format:

```markdown
## EGO Review Simulation Report

### Extension: [name] ([uuid])

### Triage Summary
[2-3 sentence overview of first impressions, written as the reviewer's internal
monologue. What did they notice first? What's their gut feeling?]

### Blocking Issues (score: N)
- **[Reason #] [Reason name]** (weight N): [Evidence with file:line reference]

### Reviewer Concerns (score: N)
- **[Reason #] [Reason name]** (weight N): [Evidence with file:line reference]

### Advisory Notes
- [Non-blocking observations that reviewers would mention in comments]

### Verdict
**Score: N** — [verdict text based on threshold]
- 0: Likely to pass without comments
- 1-4: Likely to pass with minor comments
- 5-9: May pass, but expect revision requests
- 10+: Will be rejected — address blocking issues first

### Suggested Fixes (priority order)
1. [Most impactful fix — the one that drops the score the most]
2. [Next fix]
...
```

## References

Read these reference documents before generating the report:
- `references/reviewer-persona.md` — How reviewers triage submissions
- `references/rejection-taxonomy.md` — 23 rejection reasons with weights
- `references/approved-examples.md` — Idiomatic patterns reviewers like

## Important

- Be honest and direct, like real reviewers. Do not soften rejection verdicts.
- The score must reflect what would actually happen on EGO.
- Include specific file:line references for every triggered rejection reason.
- AI slop signals are cumulative — 3+ signals at weight 8 push the score well
  past the rejection threshold. This matches real reviewer behavior since the
  Dec 2025 blog post.
- A single weight-10 hard blocker is independently sufficient for rejection,
  regardless of how clean the rest of the code is.
- When the verdict is rejection, lead with that. Don't bury it under praise.
