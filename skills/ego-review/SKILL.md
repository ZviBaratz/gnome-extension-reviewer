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

1. Read `extension.js` — verify enable/disable symmetry
2. Check constructor constraints (no resource allocation in constructor)
3. **Build a resource tracking table** as you read the code:

   | Resource | Created in (file:line) | Destroyed in (file:line) | Verified? |
   |----------|----------------------|------------------------|-----------|

4. **Signal inventory**: List every `.connect()` and `.connectObject()` call. For each, identify where the corresponding disconnect occurs. Flag any unmatched connections.
5. **Timeout inventory**: List every `timeout_add`/`idle_add` call. Verify each has a stored ID and a `GLib.Source.remove()` in the disable/destroy path.
6. **Async guard verification**: For every `await` in enable-path code, verify a `_destroyed` check follows the resume point.
7. Verify cleanup ordering (reverse order of creation)
8. Check for _destroyed flag pattern in async operations
9. Verify session mode handling if applicable

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
