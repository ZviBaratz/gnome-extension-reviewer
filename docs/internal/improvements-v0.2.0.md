# ego-lint v0.2.0 Improvement Suggestions

> Findings from a full EGO submission pipeline run (ego-lint → ego-review → ego-simulate → package validation) on [hara-hachi-bu](https://github.com/ZviBaratz/hara-hachi-bu) v1.0 (18 JS files, 7,662 non-blank lines), performed 2026-02-28.
>
> Previous round: [false-positive-analysis-v0.1.0.md](false-positive-analysis-v0.1.0.md) (all resolved).

## Results Summary

**Post-v0.1.0 fixes**: 191 passed, 0 failed, 6 warnings, 17 skipped.
**ego-simulate score**: 1 (advisory #22 for notification volume). Verdict: "Likely to pass with minor comments."

The 6 remaining warnings are all advisory-level. None would cause EGO rejection, but they reduce signal-to-noise for developers who want a clean lint pass.

| Warning | Nature | Actionable? |
|---------|--------|-------------|
| R-SEC-20 | pkexec scrutiny advisory | Correct — keep |
| R-PREFS-04b | GTK widget with no Adw equivalent | False positive |
| quality/module-state | Module-level state with non-null reset | False positive |
| quality/private-api | Private API with inline justification | Suppressible (already supported) |
| polkit-files | Informational — polkit files present | Correct — keep |
| async/missing-cancellable | Was 3 locations, fixed to 0 in extension | Already resolved |

---

## Improvement 1: `quality/module-state` only recognizes `= null` reset

**File**: `skills/ego-lint/scripts/check-quality.py:196-198`

**Current code**:
```python
# Check if var is reset to null elsewhere
reset_re = re.compile(rf'\b{re.escape(var_name)}\s*=\s*null\b')
if reset_re.search(content):
    continue  # Variable is cleaned up
```

**Problem**: The suppression heuristic only checks for `varName = null`. Variables reset to initial primitive values (`0`, `false`, `''`, `Promise.resolve()`) are not recognized as cleaned up.

In hara-hachi-bu's `lib/helper.js`:
```javascript
let _ctlQueue = Promise.resolve();  // reset in destroyExecCheck() to Promise.resolve()
let _queueDepth = 0;                // reset in destroyExecCheck() to 0
let _execDestroyed = false;          // reset in initExecCheck() to false
```

All three are properly managed with explicit `destroy`/`init` lifecycle functions, but none reset to `null`, so all three are flagged.

**Suggested fix**: Broaden the reset pattern to recognize any re-assignment of the variable:

```python
# Check if var is re-assigned elsewhere in the file (cleanup/reset pattern)
# Matches: varName = null, varName = 0, varName = false, varName = Promise.resolve(), etc.
reset_re = re.compile(rf'^\s+{re.escape(var_name)}\s*=\s*', re.MULTILINE)
# Need at least 2 assignments: the declaration + the reset
if len(reset_re.findall(content)) >= 1:
    continue  # Variable is managed (re-assigned elsewhere)
```

The key insight: if a module-level variable is re-assigned anywhere outside its declaration, the developer is actively managing its lifecycle. The `= null` check was overly narrow.

**Alternative (lighter touch)**: Expand the literal check to cover common reset values:

```python
reset_re = re.compile(
    rf'\b{re.escape(var_name)}\s*=\s*'
    r'(?:null|0|false|true|undefined|Promise\.resolve\(\)|(?:\'\'|""))\s*;'
)
```

**Impact**: Eliminates 1 false-positive WARN on this extension. Expected to help any extension with module-level command queues, caches, or state flags.

**Effort**: Low

---

## Improvement 2: R-PREFS-04b flags widgets with no Adwaita equivalent

**File**: `rules/patterns.yaml:368-375`

**Current pattern**:
```yaml
- id: R-PREFS-04b
  pattern: "\\bnew\\s+Gtk\\.(Grid|ScrolledWindow|Frame|ComboBoxText|RadioButton|Stack|Revealer|Expander|FlowBox|Overlay|Paned|ListBox)\\b"
  scope: ["prefs.js"]
  severity: advisory
  deduplicate: true
```

**Problem**: The fix message says "Adwaita replacement available for GNOME 45+", but several widgets in this list have **no direct Adwaita replacement** in common usage patterns:

| Widget | Claimed Adw Replacement | Reality |
|--------|------------------------|---------|
| `Gtk.ScrolledWindow` | `Adw.PreferencesPage` (auto-scrolls) | Only works at page level. Constrained-height scrolling inside a group (e.g., a 300px-tall list) has no Adw equivalent. |
| `Gtk.ListBox` | `Adw.PreferencesGroup` (for static lists) | `Adw.PreferencesGroup` doesn't support dynamic row management (add/remove/reorder). `Gtk.ListBox` with `boxed-list` CSS class is the [recommended pattern](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/latest/boxed-lists.html). |
| `Gtk.Grid` | `Adw rows` | Only for simple label+control pairs. Grid layouts (e.g., 7 day-of-week toggle buttons) have no Adw equivalent. |
| `Gtk.Stack` | `Adw.ViewStack` | `Adw.ViewStack` requires `Adw.ViewSwitcher` for navigation. `Gtk.Stack` without a switcher (e.g., for conditional content) has no Adw equivalent. |

**Suggested fix**: Split R-PREFS-04b into two rules:

```yaml
# Widgets with genuine Adw replacements
- id: R-PREFS-04b
  pattern: "\\bnew\\s+Gtk\\.(Frame|ComboBoxText|RadioButton|Revealer|Expander|FlowBox|Overlay|Paned)\\b"
  scope: ["prefs.js"]
  severity: advisory
  message: "GTK widget in prefs.js — Adwaita replacement available for GNOME 45+"
  category: prefs
  deduplicate: true
  fix: "Gtk.Frame → Adw.PreferencesGroup, Gtk.ComboBoxText → Adw.ComboRow, Gtk.RadioButton → Adw.ActionRow, Gtk.Revealer → Adw.ExpanderRow, Gtk.Expander → Adw.ExpanderRow, Gtk.FlowBox → Adw.PreferencesGroup"

# Widgets that are legitimate in Adw prefs (informational only)
- id: R-PREFS-04c
  pattern: "\\bnew\\s+Gtk\\.(Grid|ScrolledWindow|Stack|ListBox)\\b"
  scope: ["prefs.js"]
  severity: info
  message: "GTK layout widget in prefs.js — verify Adw equivalent isn't available for this specific use case"
  category: prefs
  deduplicate: true
  fix: "Gtk.ListBox with boxed-list CSS is valid for dynamic lists. Gtk.ScrolledWindow is valid for constrained-height content. Gtk.Grid/Stack may have Adw equivalents depending on usage."
```

Changing severity to `info` means these won't count toward `WARN_COUNT` while still being visible to developers who want to audit their widget choices.

**Impact**: Eliminates 1 false-positive WARN on this extension. High value for any extension with non-trivial prefs UI.

**Effort**: Low

---

## Improvement 3: `quality/gettext-pattern` flags lib modules where `GLib.dgettext` is correct

**File**: `skills/ego-lint/scripts/check-quality.py` (gettext pattern check)

**Problem**: The check flags `GLib.dgettext()` usage across all JS files, but `GLib.dgettext()` is the **correct** approach for library modules (`lib/*.js`) that can't access `this.gettext()` from the Extension base class. Only `extension.js` and `prefs.js` have access to the base class gettext.

In hara-hachi-bu:
- `extension.js` and `prefs.js`: Use `import {gettext as _}` from the base class (correct)
- `lib/scheduleUtils.js`, `lib/ruleEvaluator.js`: Use `GLib.dgettext()` (correct — no base class access)

**Suggested fix**: Scope the check to only flag `extension.js` and `prefs.js`:

```python
# Only flag gettext patterns in entry-point files where base class gettext is available
entry_files = [f for f in js_files if os.path.basename(f) in ('extension.js', 'prefs.js')]
```

Or alternatively, adjust the message to not suggest `this.gettext()` for lib modules:

```python
if any(os.path.basename(f) in ('extension.js', 'prefs.js') for f in flagged_files):
    result("WARN", ...)  # Entry points should use base class gettext
else:
    result("INFO", ...)  # Lib modules: GLib.dgettext() is acceptable
```

**Impact**: Reduces noise for extensions with shared utility modules.

**Effort**: Low

---

## Improvement 4: `quality/logging-volume` threshold doesn't scale with code size

**Currently**: The threshold is a fixed number of `console.*` calls (appears to be ~30 based on gap analysis observations).

**Problem**: A large extension (7,662 non-blank lines across 18 files) naturally has more logging than a 500-line extension. The hara-hachi-bu extension has ~1 log call per 84 lines — well within reasonable density — but exceeds the absolute count threshold.

**Suggested fix**: Scale the threshold by code volume:

```python
# Reasonable density: 1 console.* call per 100 non-blank lines, minimum 30
non_blank_lines = sum(1 for f in js_files for line in open(f) if line.strip())
threshold = max(30, non_blank_lines // 100)
```

**Impact**: Eliminates false positives for well-structured large extensions.

**Effort**: Low

---

## Improvement 5: `async/missing-cancellable` doesn't recognize callback-based cancellation

**Problem**: The check flags `_async()` calls with `null` cancellable, but doesn't recognize functions that implement their own cancellation via callback parameters:

```javascript
// This is flagged, but the function has its own cancellation mechanism
export async function getAcOnlineSysfs(sysfsPath, isCancelled = null) {
    // ...
    if (isCancelled && isCancelled()) return null;  // callback-based cancellation
    const online = await readFileAsync(onlinePath);  // flagged: null cancellable
}
```

The `isCancelled` callback parameter provides equivalent functionality to `Gio.Cancellable` for cooperative cancellation.

**Suggested fix**: Before flagging, check if the enclosing function has a parameter with a cancellation-related name:

```python
# Check if the function has a callback-based cancellation parameter
func_sig_re = re.compile(r'(?:async\s+)?function\s+\w+\s*\([^)]*\b(cancel|isCancelled|cancelled)\b')
# Or for arrow/method syntax:
method_sig_re = re.compile(r'\w+\s*\([^)]*\b(cancel|isCancelled|cancelled)\b[^)]*\)\s*{')
```

**Impact**: Eliminates false positives for functions with alternative cancellation mechanisms.

**Effort**: Medium (requires tracking function scope context)

---

## Improvement 6: ego-simulate taxonomy / ego-lint threshold inconsistency for notifications

**Observation**: The ego-simulate rejection taxonomy scores notification volume at weight 1 (advisory) for >3 `Main.notify` call sites, but ego-lint's `quality/notification-volume` check uses a threshold of 5 call sites. This means:

- An extension with 4 notification sites scores 1 in simulation but PASSes lint
- An extension with 6 notification sites scores 1 in simulation and WARNs in lint

The two tools should use consistent thresholds, or the taxonomy should explicitly reference the lint threshold.

**Suggested fix**: Align the ego-lint threshold to match the taxonomy (>3), or update the taxonomy comment to reference the lint's threshold value. Since both tools are in the same project, they should be consistent.

**Impact**: Low (cosmetic consistency). No false positives currently — just a documentation alignment issue.

**Effort**: Low

---

## Summary

| # | Check | Type | Impact | Effort | Priority | Status |
|---|-------|------|--------|--------|----------|--------|
| 1 | quality/module-state | False positive | 1 WARN eliminated | Low | High | **Done** — broadened reset regex |
| 2 | R-PREFS-04b | False positive | 1 WARN eliminated | Low | High | **Done** — split into R-PREFS-04b + R-PREFS-04c |
| 3 | quality/gettext-pattern | False positive | 1 WARN eliminated | Low | Medium | Already implemented (pre-v0.2.0) |
| 4 | quality/logging-volume | False positive | 1 WARN eliminated | Low | Medium | Already implemented (pre-v0.2.0) |
| 5 | async/missing-cancellable | False positive | Variable | Medium | Low | Already implemented (pre-v0.2.0) |
| 6 | Taxonomy alignment | Consistency | None (docs) | Low | Low | **Done** — added threshold comment |

**Estimated impact**: Implementing items 1-4 would reduce hara-hachi-bu's warning count from 6 to 2 (R-SEC-20 and polkit-files, both correct informational warnings). This would bring ego-lint's output into full alignment with ego-simulate's "likely to pass" verdict.

---

## Extension-Side Actions (Not Reviewer Changes)

These are things the **extension** can do to reduce warnings without changes to ego-lint:

1. **`quality/private-api`**: Add `// ego-lint-ignore: quality/private-api` comments on `_indicators` access lines. Suppression is already supported (added in v0.1.0).

2. **`async/missing-cancellable`**: Already resolved — added `cancellable` parameters to `readFileAsync`, `readFileIntAsync`, and `DeviceManager.getDevice()` (commit 83da11f).
