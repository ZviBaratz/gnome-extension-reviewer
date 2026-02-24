---
name: ego-review
description: >-
  Perform a manual code review of a GNOME Shell extension simulating what an
  EGO reviewer checks. Analyzes lifecycle correctness, signal disconnection,
  resource cleanup, async safety, security patterns, and code quality. Use
  before EGO submission, when reviewing GNOME extension code, or for
  pre-submission review.
---

# ego-review

Simulated EGO reviewer code review for GNOME Shell extensions.

This skill guides a thorough manual code review that covers everything an
extensions.gnome.org reviewer checks, plus common rejection patterns learned
from real submissions.

## Review Phases

### Phase 1: Discovery

1. Read `metadata.json` -- note UUID, shell-version, settings-schema, any session-modes
2. Glob all `.js` files -- identify extension.js, prefs.js, lib/ modules
3. Check for helper scripts, polkit rules, or other resources
4. Note the extension's purpose and complexity level

### Phase 2: Lifecycle Audit

Using [lifecycle-checklist.md](references/lifecycle-checklist.md):

1. Read `extension.js` -- verify enable/disable symmetry
2. Check constructor constraints (no resource allocation in constructor)
3. Verify all resources created in enable() are destroyed in disable()
4. Check for _destroyed flag pattern in async operations
5. Verify session mode handling if applicable
6. Check cleanup ordering (reverse of creation)

### Phase 3: Signal & Resource Audit

1. Grep for `connect(` / `connectObject(` -- list all signal connections
2. Grep for `timeout_add` / `timeout_add_seconds` -- list all timeouts
3. Grep for `FileMonitor` / `monitor_file` -- list all file monitors
4. Grep for D-Bus proxy creation
5. Cross-reference: every creation must have a corresponding cleanup in destroy/disable
6. Check for `disconnectObject(this)` pattern vs manual disconnect with stored IDs

### Phase 4: Security Review

Using [security-checklist.md](references/security-checklist.md):

1. Check subprocess/command execution patterns
2. Verify pkexec usage and helper script input validation
3. Check clipboard operations and disclosure
4. Check for network access
5. Verify file path handling (no traversal)

### Phase 5: Code Quality

Using [code-quality-checklist.md](references/code-quality-checklist.md):

1. Check for deprecated modules and APIs
2. Check for web API usage (setTimeout, fetch, etc.)
3. Look for AI code artifacts (imaginary APIs, hallucinated imports)
4. Check for excessive logging
5. Verify private API usage is documented
6. Check error handling patterns

### Phase 5a: AI Pattern Analysis

Using [ai-slop-checklist.md](references/ai-slop-checklist.md):

1. For each checklist item, search the extension source for the described pattern
2. Record whether it triggers, with file:line references
3. Note whether the pattern is justified by context
4. Apply the scoring model:
   - 1-2 triggered: ADVISORY — note them, extension may still pass
   - 3-5 triggered: BLOCKING — suggests insufficient code review
   - 6+ triggered: BLOCKING — likely unreviewed AI output
5. Include count, category breakdown, and assessment in the report

## Output Format

```
## EGO Review Report

### BLOCKING Issues
- [B1] description (file:line)

### ADVISORY Issues
- [A1] description (file:line)

### INFO
- [I1] observation (file:line)

### Summary
- X blocking issues (must fix before submission)
- Y advisory issues (may cause reviewer questions)
- Z informational observations
```

## When to Use

- Before submitting to extensions.gnome.org
- After making significant changes to an extension
- When reviewing someone else's GNOME extension code
- As a learning tool for new extension developers
