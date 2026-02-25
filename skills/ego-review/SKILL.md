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

## Reviewer Context

Understanding the real EGO review process helps calibrate review severity:

- **Primary reviewer** processes 15,000+ lines of code per day across many extensions
- **Review priority order**: Security → Stability (resource leaks) → Code readability → Lifecycle correctness → API correctness → Metadata → AI pattern detection
- **Lifecycle cleanup is the #1 rejection cause** — not security, not metadata
- **AI slop triggers deeper scrutiny**: When a reviewer spots one AI-generated pattern, they examine the entire extension more carefully. A clean extension with one `pkexec` usage gets more leeway than one with `typeof super.destroy === 'function'` guards everywhere
- **The domino effect**: Bad patterns in published extensions get copied. Reviewers are stricter on patterns they've seen spread (excessive try-catch, empty catches, TypeScript JSDoc)
- **Developer understanding matters**: When asked to explain code, developers who respond with more AI-generated text are immediately flagged. Extensions where the developer clearly understands the code get more benefit of the doubt

### Phase 0: Automated Baseline

1. Run ego-lint on the extension directory (invoke the ego-lint skill)
2. Capture all FAIL/WARN/PASS results
3. For each FAIL/WARN, note the check name — Phases 2-5 should NOT re-report
   issues already caught by ego-lint (avoid duplication)
4. Focus manual review on issues ego-lint CANNOT detect (semantic, cross-file,
   design-level)

### Phase 1: Discovery

1. Read `metadata.json` -- note UUID, shell-version, settings-schema, any session-modes
2. Glob all `.js` files -- identify extension.js, prefs.js, lib/ modules
3. Check for helper scripts, polkit rules, or other resources
4. Note the extension's purpose and complexity level

### Phase 1b: Licensing & Legal

Using [licensing-checklist.md](references/licensing-checklist.md):

1. Verify LICENSE/COPYING file exists and is GPL-compatible
2. Check for code that appears borrowed from other extensions (attribution needed)
3. Verify no copyrighted/trademarked content without permission
4. Check extension name, description, and UI text for CoC compliance

### Phase 2: Lifecycle Audit

Using [lifecycle-checklist.md](references/lifecycle-checklist.md):

1. Read `extension.js` — verify enable/disable symmetry
2. Check constructor constraints (no resource allocation in constructor)
3. **Run the resource graph builder** to get deterministic cross-file data:
   ```bash
   python3 <plugin-dir>/skills/ego-lint/scripts/build-resource-graph.py <extension-dir>
   ```
4. **Review the graph summary**: files scanned, total creates/destroys, orphan count,
   ownership depth. Present this to ground the review.
5. **For each orphan in the graph**:
   - Read the cited file:line to verify it's a true leak
   - Classify as: TRUE LEAK (blocking) | JUSTIFIED (note why) | FALSE POSITIVE (skip)
   - For true leaks, include the fix in the report
6. **For each ownership chain** (from the `ownership` JSON field):
   - Verify parent calls child's `destroy()` in its own `disable()`/`destroy()`
   - Verify destroy order is reverse of creation
   - Verify child's `destroy()` cleans up all its own resources
7. **Build the resource tracking table** from graph data:

   | Resource | File:Line (create) | File:Line (destroy) | Owner | Status |
   |----------|-------------------|--------------------|---------|----|

8. **If the graph reports 0 orphans and complete ownership chains**: abbreviate
   this phase — focus on async guards and cleanup ordering below
9. **Async guard verification**: For every `await` in enable-path code, verify
   a `_destroyed` check follows the resume point
10. Verify cleanup ordering (reverse order of creation)
11. Check for _destroyed flag pattern in async operations
12. Verify session mode handling if applicable

### Phase 3: Signal & Resource Audit

1. Grep for `connect(` / `connectObject(` — list all signal connections
2. Grep for `timeout_add` / `timeout_add_seconds` / `idle_add` — list all timer sources
3. Grep for `FileMonitor` / `monitor_file` — list all file monitors
4. Grep for D-Bus proxy creation (`Gio.DBusProxy`, `new_for_bus`)
5. Cross-reference: every creation must have a corresponding cleanup in destroy/disable

**D-Bus proxy lifecycle:**
- Disconnect all signal connections from the proxy
- Null the proxy reference
- Verify error handling for when the D-Bus service is unavailable

**File monitor lifecycle:**
- `monitor.cancel()` first
- Then disconnect any signal handlers
- Then null the reference

**GSettings connections:**
- Verify `disconnectObject(this)` or manual `disconnect(id)` for all settings connections
- Check that settings reference is nulled after disconnect

### Phase 4: Security Review

Using [security-checklist.md](references/security-checklist.md):

1. Check subprocess/command execution patterns
2. Verify pkexec usage and helper script input validation
3. Check clipboard operations and disclosure
4. Check for network access
5. Verify file path handling (no traversal)
6. Check for telemetry/analytics patterns (banned by EGO)
7. Check clipboard access and disclosure requirements
8. Check for extension system interference (ExtensionManager usage)

**Reviewer perspective notes:**
- When a reviewer sees `pkexec`, they immediately check the helper script for input validation
- When a reviewer sees network access, they check if it's disclosed in the description
- When a reviewer sees clipboard access, they check if the user initiated it

### Phase 5: Code Quality

Using [code-quality-checklist.md](references/code-quality-checklist.md):

1. Check for deprecated modules and APIs
2. Check for web API usage (setTimeout, fetch, etc.)
3. Look for AI code artifacts (imaginary APIs, hallucinated imports)
4. Check for excessive logging
5. Verify private API usage is documented
6. Check error handling patterns
7. **Hallucinated API cross-reference**: Verify that every API method called actually exists in the declared `shell-version` range. Common hallucinations: `Meta.Screen`, `St.Button.set_label()`, `GLib.source_remove()`, `Clutter.Actor.show_all()`
8. **GObject pattern verification**: Check that `registerClass` calls have `GTypeName`, that `destroy()` chains to `super.destroy()`, that GObject properties emit `notify`
9. **Prefs.js specific checks**: Verify `fillPreferencesWindow()` exists, GTK4/Adwaita patterns used correctly, no deprecated GTK3 patterns, no Shell imports
10. Check for `var` declarations (should use const/let)
11. Check import ordering (GI → resource → extension)
12. Check for `console.log()` (banned — only debug/warn/error allowed)

**Reviewer perspective notes:**
- When a reviewer sees `console.log()`, they think "developer forgot to clean up debug logging"
- When a reviewer sees module-level `let`, they think "will this persist across enable/disable cycles?"
- When a reviewer sees `try { super.destroy() } catch`, they think "AI-generated code"

### Phase 5a: AI Pattern Analysis

Using [ai-slop-checklist.md](references/ai-slop-checklist.md) (21-item checklist):

1. For each checklist item, search the extension source for the described pattern
2. Record whether it triggers, with file:line references
3. Note whether the pattern is justified by context
4. Apply the scoring model:
   - 1-2 triggered: ADVISORY — note them, extension may still pass
   - 3-5 triggered: BLOCKING — suggests insufficient code review
   - 6+ triggered: BLOCKING — likely unreviewed AI output
5. Include count, category breakdown, and assessment in the report
6. When score reaches BLOCKING, provide specific file:line citations for each triggered item so the developer has an actionable fix list

## Output Format

```
## EGO Review Report — [Extension Name] v[version]

### Verdict: [LIKELY APPROVED | NEEDS REVISION | LIKELY REJECTED]

**Rejection Risk**: [LOW | MEDIUM | HIGH | VERY HIGH]

---

### Section 1: Blocking Issues (Must Fix)

#### [B1] Issue title (category)
**File**: path/to/file.js:line
**What**: Description of the issue
**Why reviewers reject this**: Explanation with reviewer perspective
**Fix**:
```js
// BEFORE
old code

// AFTER
fixed code
```

---

### Section 2: Justification Required

Items that are acceptable IF properly documented:

#### [J1] pkexec usage
**File**: path/to/file.js:line
**Status**: Requires reviewer justification
**Template**: [Include pkexec justification template from security checklist]

---

### Section 3: Advisory Issues (May Cause Questions)

#### [A1] Issue title
**File**: path/to/file.js:line
**What**: Description
**Reviewer perspective**: What the reviewer thinks when they see this
**Suggestion**: How to fix

---

### Section 4: Automated Check Summary (from ego-lint)

| Category | Pass | Fail | Warn |
|----------|------|------|------|
| Metadata | N | N | N |
| Security | N | N | N |
| Lifecycle | N | N | N |
| Quality | N | N | N |

---

### Section 5: AI Pattern Analysis

**Score**: N/27 triggered — [ADVISORY | BLOCKING]
**Triggered items**: list with file:line
**Assessment**: interpretation

---

### Section 6: Submission Readiness

**Ready to submit?** [YES | NO] — N blocking issues remain

**Action items (priority order)**:
1. [ ] First thing to fix
2. [ ] Second thing to fix
```

## Rejection-Risk Scoring Model

Calculate based on findings:

| Finding | Risk Points |
|---------|-------------|
| Each BLOCKING lifecycle issue | +3 |
| Each BLOCKING security issue | +4 |
| Each BLOCKING API hallucination | +5 (indicates AI) |
| AI slop score >= 3 | +5 |
| AI slop score >= 6 | +10 |
| Each ADVISORY issue | +1 |
| Justified advisory (with docs) | +0 |

**Verdict thresholds:**
- 0-2 points: **LIKELY APPROVED** — minor or no issues
- 3-6 points: **NEEDS REVISION** — fixable, resubmit after changes
- 7-12 points: **LIKELY REJECTED** — significant issues
- 13+ points: **LIKELY REJECTED** — fundamental problems or AI-generated

## When to Use

- Before submitting to extensions.gnome.org
- After making significant changes to an extension
- When reviewing someone else's GNOME extension code
- As a learning tool for new extension developers
