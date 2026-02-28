# Real EGO Review Findings

**Date:** 2026-02-26
**Method:** Web search across GNOME Discourse, GNOME blogs, extensions.gnome.org review pages, gjs.guide, and developer community discussions. Focused on real reviewer comments, actual rejection reasons, and unwritten rules.
**Sources:** Listed per finding below.

---

## Summary Statistics

- **26 findings** extracted from real-world review comments and community discussions
- **8 unwritten rules** (not in official guidelines but consistently enforced)
- **6 reviewer preferences** (not required but speed up approval)
- **9 common rejections** (well-documented but with nuances not captured in guidelines)
- **3 developer advice patterns** (consistent guidance from reviewers to developers)

---

## Finding Index

| # | Title | Type | Frequency | Current Coverage |
|---|-------|------|-----------|-----------------|
| 1 | GNOME Trademark in UUID/Name/Schema ID | Unwritten Rule | Medium | None |
| 2 | Shell-Version Minor Versions Rejected for GNOME 40+ | Unwritten Rule | High | Partial (gap) |
| 3 | DBus Interface Must Be Unexported in disable() | Unwritten Rule | Medium | None |
| 4 | Null Out ALL References in disable() | Reviewer Preference | High | Tier 3 Only |
| 5 | Repeated getSettings() Calls Are Flagged | Reviewer Preference | Medium | None |
| 6 | Development Artifact Files (env.d.ts, jsconfig.json, .old) | Common Rejection | High | Partial (gap) |
| 7 | Generic/Overly-Simple Class Names in prefs.js | Reviewer Preference | Low | None |
| 8 | Version Checks Must Use Numeric Comparison | Unwritten Rule | Medium | None |
| 9 | Fork/Attribution Must Be in metadata.json Description | Common Rejection | Medium | Tier 3 Only |
| 10 | External Tool Dependencies Must Be Documented | Unwritten Rule | Medium | None |
| 11 | HTTP User-Agent Strings Are Scrutinized | Unwritten Rule | Low | None |
| 12 | Unused/Dead Code Functions Flagged | Reviewer Preference | Medium | Partial |
| 13 | Excessive Bash/Service Scripts Rejected | Common Rejection | Medium | Partial |
| 14 | Indicator/Widget Must Be Destroyed Then Nulled | Common Rejection | High | Partial |
| 15 | run_dispose() Is Not Permitted Without Justification | Common Rejection | Medium | Covered (R-QUAL-21) |
| 16 | Signals on Extension-Owned Objects: Gray Area | Developer Advice | Medium | Partial |
| 17 | AI-Generated: Try-Catch Around Known-Safe Calls | Common Rejection | High | Covered (R-SLOP-*) |
| 18 | AI-Generated: typeof super.destroy Check | Common Rejection | High | Partial |
| 19 | Reviewer Workload Causes Errors | Developer Advice | Low | N/A |
| 20 | Timeouts Must Be Removed Before Reassignment | Unwritten Rule | Medium | Partial |
| 21 | No Unnecessary Export Statements | Reviewer Preference | Low | None |
| 22 | Preferences Should Use Dependency Injection for Settings | Reviewer Preference | Medium | None |
| 23 | Review Scope: Security-First, Not Bug-Checking | Developer Advice | High | N/A |
| 24 | Compiled Schemas Rejected for GNOME 45+ Packages | Common Rejection | High | Covered (R-PKG-12) |
| 25 | Session-Modes Must Have Explicit Use Case | Common Rejection | Medium | Covered (R-META-09) |
| 26 | Deprecated Convenience.js Pattern | Unwritten Rule | Medium | Partial |

---

## Detailed Findings

### Finding 1: GNOME Trademark in UUID/Name/Schema ID

- **Source:** [Draw On Gnome review #62523](https://extensions.gnome.org/review/62523) — JustPerfection: "Don't use GNOME in uuid, name and schema id"
- **Type:** Unwritten Rule
- **Pattern:** Reviewer rejects extensions that include "GNOME" (any case) in their UUID, extension name, or GSettings schema ID. This is a trademark violation enforced during review, not just the `@gnome.org` namespace restriction that is officially documented.
- **Current coverage:** Partial — R-META-04 checks for `@gnome.org` in UUID namespace, but does NOT check for the word "GNOME" or "Gnome" appearing anywhere in the UUID, extension name, or schema ID.
- **Frequency:** Medium (affects any extension themed around GNOME functionality)
- **Actionability:** Add a check in `check-metadata.py` that warns if the UUID, `name`, or `settings-schema` fields contain "GNOME" (case-insensitive). Also add a check in `check-schema.sh` for the schema ID. This is a trademark rule that reviewers actively enforce.

### Finding 2: Shell-Version Minor Versions Rejected for GNOME 40+

- **Source:** [gnomehub review #30227](https://extensions.gnome.org/review/30227) — "Remove `41.alpha` and only use '41'. '41' means all minor versions of 41 is supported"; [Wechsel review #53836](https://extensions.gnome.org/review/53836) — "Please remove 45.1 and 45.5 from metadata.json. 45 would be enough."
- **Type:** Unwritten Rule
- **Pattern:** For GNOME 40+, reviewers require shell-version entries to be major-version-only (e.g., "45", not "45.1" or "45.5"). The current validator accepts `\d+(\.\d+)?` which would allow "45.1" to pass. For GNOME 3.x, minor versions like "3.38" are expected.
- **Current coverage:** Partial — `check-metadata.py` validates the format regex but does NOT flag minor version entries for GNOME 40+ (e.g., "45.1" passes validation).
- **Frequency:** High (very common mistake for new developers)
- **Actionability:** Add a check in `check-metadata.py`: for entries matching `\d+\.\d+` where the major version is >= 40, warn that only the major version should be used (unless the minor is "alpha" or "beta" which are valid for development releases).

### Finding 3: DBus Interface Must Be Unexported in disable()

- **Source:** [Wechsel review #53836](https://extensions.gnome.org/review/53836) — "When you export the dbus it should be unexported on disable"
- **Type:** Unwritten Rule
- **Pattern:** If an extension exports a DBus interface (via `Gio.DBusExportedObject.wrapJSObject` + `.export()`, or `connection.export_action_group()`, or `connection.export_menu_model()`), the reviewer requires the corresponding unexport call in `disable()`. Re-enabling without unexport causes "object already exported" errors.
- **Current coverage:** None — `check-lifecycle.py` checks for DBus proxy creation (R-LIFE-07) but NOT for DBus interface exports that need corresponding unexports. The resource graph tracks DBus proxies but not exported interfaces.
- **Frequency:** Medium (affects extensions that provide DBus APIs)
- **Actionability:** Add detection in `check-lifecycle.py` for `Gio.DBusExportedObject` + `.export(` patterns, and verify that `.unexport()` appears in disable(). Also add patterns for `export_action_group`/`export_menu_model` paired with their unexport counterparts.

### Finding 4: Null Out ALL References in disable()

- **Source:** [Recent Items review #54559](https://extensions.gnome.org/review/54559) — "null out in disable: this._settings = null;"; [Wechsel review #53836](https://extensions.gnome.org/review/53836) — "Also null out in disable: this.settings = null;"; [APCUPS Monitor review #68473](https://extensions.gnome.org/review/68473) — "Destroy the _label object, Set both _label and _settings to null"; [gjs.guide examples](https://gjs.guide/extensions/review-guidelines/review-guidelines.html) — `this._indicator = null; this._settings = null;`
- **Type:** Reviewer Preference (consistently enforced, essentially an unwritten MUST)
- **Pattern:** Reviewers consistently require that ALL member references are set to `null` after destruction or in disable(). This includes `_settings`, `_indicator`, `_label`, and any other stored references. The pattern is always: `this._thing?.destroy(); this._thing = null;` or just `this._thing = null;` for non-destroyable objects like settings.
- **Current coverage:** Tier 3 Only — lifecycle-checklist.md mentions nulling references but there is no automated check that verifies settings/objects are nulled in disable().
- **Frequency:** High (comes up in almost every review)
- **Actionability:** Add a heuristic check: if `this.getSettings()` or `new Gio.Settings` is found in enable(), verify that `= null` appears for the same property in disable(). Same for indicator/widget patterns. This would be a WARN-level check since it is hard to be certain about variable names.

### Finding 5: Repeated getSettings() Calls Are Flagged

- **Source:** [Wechsel review #53836](https://extensions.gnome.org/review/53836) — Lines 518/525 creating new GSettings instances instead of reusing `this.settings` from line 513; [Draw On Gnome review #62523](https://extensions.gnome.org/review/62523) — "Avoid repeated this.getSettings() calls; implement dependency injection"
- **Type:** Reviewer Preference
- **Pattern:** Reviewers flag code that calls `this.getSettings()` or `new Gio.Settings()` multiple times when a single instance should be stored and reused. This is both a performance concern and a cleanup concern (multiple settings instances all need to be individually tracked and nulled).
- **Current coverage:** None — no check for repeated settings instantiation.
- **Frequency:** Medium (common in extensions with multiple modules)
- **Actionability:** Add a WARN-level check: count occurrences of `getSettings()` and `new Gio.Settings` across the extension. If total > 2 in extension.js files (excluding prefs.js), warn about redundant settings instances. Could also use the resource graph to detect this.

### Finding 6: Development Artifact Files Not in Forbidden List

- **Source:** [Recent Items review #54559](https://extensions.gnome.org/review/54559) — "Please remove: env.d.ts, jsconfig.json"; [gnomehub review #30227](https://extensions.gnome.org/review/30227) — "Remove extension.js.old per review guidelines"; [Draw On Gnome review #62523](https://extensions.gnome.org/review/62523) — "Remove po folder per EGO review guidelines"
- **Type:** Common Rejection
- **Pattern:** Reviewers consistently flag TypeScript development artifacts (`env.d.ts`, `jsconfig.json`, `tsconfig.json`) and backup files (`*.old`, `*.bak`, `*.orig`). While our package check catches `tsconfig.json`, `package.json`, and `.po`/`.pot` files, it misses `env.d.ts`, `jsconfig.json`, and `*.old`/`*.bak`/`*.orig` patterns.
- **Current coverage:** Partial — `check-package.sh` has an extensive forbidden file list but misses several files reviewers actually flag: `env.d.ts`, `jsconfig.json`, `*.old`, `*.bak`, `*.orig`, `*.swp`, `*.swo`.
- **Frequency:** High (very common for TypeScript-based extensions)
- **Actionability:** Add to `check-package.sh` forbidden patterns: `env.d.ts`, `jsconfig.json`, `*.old`, `*.bak`, `*.orig`, `*.swp`, `*.swo`. These are all explicitly flagged in real reviews.

### Finding 7: Generic/Overly-Simple Class Names in prefs.js

- **Source:** [Recent Items review #54559](https://extensions.gnome.org/review/54559) — Reviewer objected to "overly generic class name exported from prefs.js" and requested a more descriptive identifier
- **Type:** Reviewer Preference
- **Pattern:** Reviewer flags generic exported class names like `Preferences` or `Prefs` in prefs.js, preferring descriptive names like `MyExtensionPreferences` that clearly identify the extension.
- **Current coverage:** None
- **Frequency:** Low (cosmetic preference, not a hard reject)
- **Actionability:** Low priority. Could add an advisory-level check for `export default class Prefs` or `export default class Preferences` without a more specific name, but this is borderline nitpick territory. Better suited as a Tier 3 checklist item in code-quality-checklist.md.

### Finding 8: Version Checks Must Use Numeric Comparison

- **Source:** [Draw On Gnome review #62523](https://extensions.gnome.org/review/62523) — "Replace string-based version checks with float/int parsing" in multiple files across 9 locations
- **Type:** Unwritten Rule
- **Pattern:** Reviewers flag code that compares GNOME Shell version strings using string comparison operators. The correct approach is to parse `Config.PACKAGE_VERSION` into numeric values using `parseInt()` or similar, then compare numerically. String comparison of version numbers ("46" > "5" but "46" < "9" lexicographically) is buggy.
- **Current coverage:** None — no check for string-based version comparison.
- **Frequency:** Medium (common in extensions that target multiple GNOME versions)
- **Actionability:** Add a pattern rule detecting version comparison anti-patterns. Look for patterns like `Config.PACKAGE_VERSION === '46'` or `Config.PACKAGE_VERSION >= '46'` or `Config.PACKAGE_VERSION.startsWith('4')`. WARN level with fix suggestion to use numeric parsing.

### Finding 9: Fork/Attribution Must Be in metadata.json Description

- **Source:** [Draw On Gnome review #62523](https://extensions.gnome.org/review/62523) — "Mention fork status in metadata.json description"; [Reply to extension upload review](https://discourse.gnome.org/t/reply-to-extension-upload-review/17622) — Reviewer asked for fork mention in metadata (though this turned out to be a reviewer error); [gjs.guide](https://gjs.guide/extensions/review-guidelines/review-guidelines.html) — example showing "It is a fork of MonochromeButton" in description
- **Type:** Common Rejection
- **Pattern:** When an extension is a fork of another extension, the reviewer requires that the original extension be mentioned in the metadata.json `description` field. The official guidelines include an example showing the expected format: "It is a fork of [OriginalExtension]." This is separate from the code attribution requirement (which requires attribution in distributed source files).
- **Current coverage:** Tier 3 Only — licensing-checklist.md covers fork naming and attribution but no automated detection.
- **Frequency:** Medium (affects all forked extensions)
- **Actionability:** Difficult to automate fork detection. Could add a heuristic: if extension code has significant similarity to known popular extensions, or if the git history shows a fork, flag for manual review. Practically, this is best left as a Tier 3 checklist enhancement. Add explicit mention of metadata.json description requirement to licensing-checklist.md.

### Finding 10: External Tool Dependencies Must Be Documented in Description

- **Source:** [Wechsel review #53836](https://extensions.gnome.org/review/53836) — "Clarify in description that the extension requires the wechsel CLI tool as a dependency"
- **Type:** Unwritten Rule
- **Pattern:** If an extension spawns external commands (via `Gio.Subprocess`, `GLib.spawn_*`), the reviewer requires that the external tool dependency be clearly documented in the metadata.json `description` field. Users need to know what to install.
- **Current coverage:** None — we detect subprocess usage (R-SEC-14, R-SEC-15) but do not check whether the description mentions the required external tools.
- **Frequency:** Medium (affects extensions that shell out to external tools)
- **Actionability:** Add a cross-reference check: if subprocess patterns are detected AND the spawned command is identifiable (literal string arguments), verify the command name appears in the metadata description. This is complex but high-value. A simpler approach: if any subprocess call is detected, add an advisory noting that external dependencies should be documented in the description.

### Finding 11: HTTP User-Agent Strings Are Scrutinized

- **Source:** [gnomehub review #30227](https://extensions.gnome.org/review/30227) — "Why do you send `Stackoverflow/1.0` in line 345 and 364?" (reviewer questioned misleading User-Agent header)
- **Type:** Unwritten Rule
- **Pattern:** Reviewers examine HTTP request headers. A misleading or deceptive User-Agent string (like `Stackoverflow/1.0`) raises red flags about the extension's intent. Extensions making HTTP requests should use an honest User-Agent that identifies the extension.
- **Current coverage:** None — no check for HTTP User-Agent strings.
- **Frequency:** Low (only affects extensions making HTTP requests)
- **Actionability:** Low priority. Could add an advisory-level pattern rule detecting common fake User-Agent patterns, but this is edge-case. Better suited as a Tier 3 checklist item in security-checklist.md.

### Finding 12: Unused/Dead Code Functions Flagged

- **Source:** [gnomehub review #30227](https://extensions.gnome.org/review/30227) — "Why `_getWeatherUri()` is unused but implemented?" and "`Extension._refresh_monitor()` not getting used. Why?"
- **Type:** Reviewer Preference
- **Pattern:** Reviewers flag functions that are defined but never called. This is a code quality concern — unused code increases review burden and suggests the developer doesn't fully understand their own codebase (or copied code they don't need).
- **Current coverage:** Partial — R-QUAL-10 (code volume) and R-QUAL-12 (file complexity) detect excessive code but not specifically unused functions.
- **Frequency:** Medium (common in AI-generated or copied code)
- **Actionability:** Difficult to implement fully (requires call graph analysis). However, a simpler heuristic could detect functions in extension.js that are defined with `_methodName()` syntax but whose name never appears as `this._methodName` anywhere in the file. WARN level. Could also be flagged by ESLint integration.

### Finding 13: Excessive Bash/Service Scripts Rejected

- **Source:** [GNOME Speech2Text review #67335](https://extensions.gnome.org/review/67335) — "The service bash script here is really getting too much for an extension"
- **Type:** Common Rejection
- **Pattern:** Extensions that include complex bash scripts or service orchestration are rejected for exceeding the appropriate scope of an extension. The reviewer's expectation is that extensions are primarily JavaScript, with shell scripts only for minimal privileged operations via pkexec.
- **Current coverage:** Partial — `ego-lint.sh` `non-gjs-scripts` check detects non-GJS scripts and issues FAIL/WARN, but does not assess script complexity or length.
- **Frequency:** Medium (affects extensions wrapping external services)
- **Actionability:** Enhance the non-GJS scripts check to measure script complexity: if included bash/python scripts exceed a reasonable line count (e.g., 50 lines), escalate from WARN to FAIL with a message about scope. Also add total non-JS code line count as a quality metric.

### Finding 14: Indicator/Widget Must Be Destroyed Then Nulled (Two-Step Pattern)

- **Source:** [APCUPS Monitor review #68473](https://extensions.gnome.org/review/68473) — "Destroy the _label object, Set both _label and _settings to null"; [gnomehub review #30227](https://extensions.gnome.org/review/30227) — "In disable(), before line 406, you should use this.indicator.destroy()"; [gjs.guide](https://gjs.guide/extensions/review-guidelines/review-guidelines.html) — `this._indicator?.destroy(); this._indicator = null;`
- **Type:** Common Rejection
- **Pattern:** The reviewer requires a strict two-step cleanup pattern for widgets: (1) `.destroy()` the widget, then (2) set the reference to `null`. Missing either step is flagged. This applies to any St.Widget, PanelMenu.Button, or other GObject that was created in enable().
- **Current coverage:** Partial — lifecycle-checklist.md and check-lifecycle.py check for signal balance and resource cleanup, but do not specifically verify the destroy-then-null pattern for widgets.
- **Frequency:** High (flagged in nearly every review of extensions with UI elements)
- **Actionability:** Add a check in check-lifecycle.py: if `new PanelMenu.Button` or `new St.` widget creation is found in enable(), verify that both `.destroy()` and `= null` appear in disable() for the same property name. This is the single most commonly flagged pattern in reviews.

### Finding 15: run_dispose() Is Not Permitted Without Justification

- **Source:** [Gio.Settings.run_dispose() discussion](https://discourse.gnome.org/t/gio-settings-run-dispose-in-extensions/17361) — Andy Holmes: "it is not okay to call GObject.Object.run_dispose() in extensions" unless there is "a good reason"
- **Type:** Common Rejection
- **Pattern:** `run_dispose()` is explicitly discouraged. Reviewers reject it as a lazy substitute for proper signal disconnection. Even though gnome-shell-extensions itself uses it, that is not considered a valid reference. Extensions must manually disconnect signals.
- **Current coverage:** Covered — R-QUAL-21 detects `run_dispose()` and warns if no explanatory comment is present.
- **Frequency:** Medium
- **Actionability:** Already covered. No action needed.

### Finding 16: Signals on Extension-Owned Objects: Gray Area

- **Source:** [Is disconnecting from signals always required?](https://discourse.gnome.org/t/is-disconnecting-from-signals-always-required/14862) — Andy Holmes: if a GObject created by the extension is properly garbage collected, "all signal handlers will be disconnected when it's disposed"
- **Type:** Developer Advice
- **Pattern:** Signal disconnection is technically not required for objects the extension owns and destroys, because GC will clean up the handlers. However, reviewers still prefer explicit disconnection for clarity. When signal disconnection status is ambiguous, reviewers may request clarification rather than reject outright.
- **Current coverage:** Partial — R-LIFE-01 (signal-balance) uses a heuristic with +2 tolerance.
- **Frequency:** Medium
- **Actionability:** Document this nuance in lifecycle-checklist.md: signals on extension-owned objects that are destroyed in disable() do not strictly need explicit disconnection, but explicit disconnection is preferred for reviewer clarity. Adjust the signal-balance heuristic description to note this gray area.

### Finding 17: AI-Generated: Try-Catch Around Known-Safe Calls

- **Source:** [AI and GNOME Shell Extensions blog post](https://blogs.gnome.org/jrahmatzadeh/2025/12/06/ai-and-gnome-shell-extensions/) — Example showing unnecessary try-catch around `super.destroy()`
- **Type:** Common Rejection
- **Pattern:** AI-generated code wraps well-defined API calls in try-catch blocks with `console.warn` in the catch. The specific example is `try { if (typeof super.destroy === 'function') { super.destroy(); } } catch (e) { console.warn(...); }` when `super.destroy()` alone is sufficient.
- **Current coverage:** Covered — R-SLOP-01 through R-SLOP-29 and check-quality.py catch try-catch density and defensive coding patterns.
- **Frequency:** High (most common AI slop pattern identified by reviewers)
- **Actionability:** Already well-covered. Consider adding a specific pattern rule for `typeof super.destroy === 'function'` or `typeof super.METHOD === 'function'` as a high-confidence AI slop signal.

### Finding 18: AI-Generated: typeof super.method Check

- **Source:** [AI and GNOME Shell Extensions blog post](https://blogs.gnome.org/jrahmatzadeh/2025/12/06/ai-and-gnome-shell-extensions/) — `typeof super.destroy === 'function'` example
- **Type:** Common Rejection
- **Pattern:** Checking `typeof super.METHOD === 'function'` before calling a parent method is a strong AI slop signal. In GJS/GObject, parent class methods are always well-defined and guaranteed to exist. This defensive check reveals the code was generated by an AI that doesn't understand the GObject type system.
- **Current coverage:** Partial — No specific pattern rule for `typeof super.` checks. Covered indirectly by try-catch density heuristics but a direct check would be higher confidence.
- **Frequency:** High (very common AI pattern)
- **Actionability:** Add a new pattern rule (e.g., R-SLOP-30) in `patterns.yaml`: detect `typeof super\.\w+ === 'function'` or `typeof super\.\w+ !== 'undefined'`. This is a high-confidence AI slop indicator with near-zero false positive rate in hand-written GJS code.

### Finding 19: Reviewer Workload Causes Errors

- **Source:** [Reply to extension upload review](https://discourse.gnome.org/t/reply-to-extension-upload-review/17622) — Reviewer confused "generated from" with "forked from" while reviewing 30+ extensions; JustPerfection reviews 15,000+ lines per day
- **Type:** Developer Advice
- **Pattern:** Reviewers make mistakes due to volume. The primary reviewer (JustPerfection/Javad Rahmatzadeh) reviews 30+ extensions and 15,000+ lines some days, spending ~6 hours on reviews. This means: (1) extensions should be as clean and obvious as possible to avoid misunderstandings, and (2) developers should push back politely if a review comment seems incorrect.
- **Current coverage:** N/A (meta-insight about the process)
- **Frequency:** Low (contextual)
- **Actionability:** Add guidance to ego-submit SKILL.md: "Make your extension as easy to review as possible — reviewers process 30+ extensions per day. Clean code, clear comments, and minimal file count reduce review friction."

### Finding 20: Timeouts Must Be Removed Before Reassignment

- **Source:** [Draw On Gnome review #62523](https://extensions.gnome.org/review/62523) — "Remove timeouts before destruction and reassignment (line 910, area.js)"
- **Type:** Unwritten Rule
- **Pattern:** When a timeout ID is stored in a member variable, the previous timeout must be removed via `GLib.Source.remove()` before the variable is reassigned to a new timeout. Otherwise the old timeout is orphaned (leaked). This applies to any code path where `this._timeoutId = GLib.timeout_add(...)` could be called more than once.
- **Current coverage:** Partial — R-LIFE-12 checks that `GLib.Source.remove()` appears in disable() for stored timeout IDs, but does NOT check for timeout reassignment without prior removal within enable() or other methods.
- **Frequency:** Medium (common in extensions with debounce/delay patterns)
- **Actionability:** Enhance check-lifecycle.py to detect patterns where `this._xxx = GLib.timeout_add(...)` or `this._xxx = GLib.idle_add(...)` appears in a method body without a preceding `GLib.Source.remove(this._xxx)` check. This catches the reassignment-without-cleanup anti-pattern.

### Finding 21: No Unnecessary Export Statements

- **Source:** [Wechsel review #53836](https://extensions.gnome.org/review/53836) — "Line 584's export statement is unnecessary"
- **Type:** Reviewer Preference
- **Pattern:** Reviewers flag export statements that serve no purpose — e.g., exporting a function or class that is never imported by another module, or using `export` on a helper function that is only used within the same file.
- **Current coverage:** None
- **Frequency:** Low (cosmetic preference)
- **Actionability:** Low priority. Could add an advisory detecting export statements on non-default-export items in extension.js (the main entry point typically only needs `export default`). Better suited as a Tier 3 checklist item.

### Finding 22: Preferences Should Use Dependency Injection for Settings

- **Source:** [Draw On Gnome review #62523](https://extensions.gnome.org/review/62523) — "Avoid repeated this.getSettings() calls; implement dependency injection"
- **Type:** Reviewer Preference
- **Pattern:** Rather than having each component/widget in the preferences UI call `this.getSettings()` independently, the reviewer prefers passing a single settings instance from the top-level preferences class down to child components. This is essentially a dependency injection pattern.
- **Current coverage:** None
- **Frequency:** Medium (common in complex preference UIs with multiple pages)
- **Actionability:** Low priority for automation. Add to code-quality-checklist.md as a best practice recommendation: "Pass settings instance to child components rather than calling getSettings() in each component."

### Finding 23: Review Scope: Security-First, Not Bug-Checking

- **Source:** [Developing Gnome Shell extension is a giant waste of time](https://discourse.gnome.org/t/developing-gnome-shell-extension-is-a-giant-waste-of-time/6179) — Reviewer clarified focus on "grievous cleanup errors, obvious leaks, very laggy code, and most importantly potential security issues"
- **Type:** Developer Advice
- **Pattern:** The review process is NOT comprehensive QA. Reviewers focus on: (1) security issues, (2) serious lifecycle/cleanup violations, (3) obvious performance problems, (4) code quality (readable, not minified). They do NOT test functionality, catch all bugs, or verify features work correctly. This means extensions can pass review but still be buggy.
- **Current coverage:** N/A (meta-insight about review process)
- **Frequency:** High (fundamental to understanding the review process)
- **Actionability:** Align ego-review phase priorities to match: security and lifecycle issues should be blockers, while code quality and style issues should be warnings. ego-simulate should model this priority order.

### Finding 24: Compiled Schemas Rejected for GNOME 45+ Packages

- **Source:** [APCUPS Monitor review #68473](https://extensions.gnome.org/review/68473) — "Remove schemas/gschemas.compiled — Not needed for 45+ packages"
- **Type:** Common Rejection
- **Pattern:** GNOME Shell 45+ auto-compiles schemas at load time. Including `gschemas.compiled` in the zip is unnecessary and rejected.
- **Current coverage:** Covered — R-PKG-12 in check-package.sh FAIL for gschemas.compiled when targeting GNOME 45+.
- **Frequency:** High (very common for first-time submitters)
- **Actionability:** Already covered. No action needed.

### Finding 25: Session-Modes Must Have Explicit Use Case

- **Source:** [gnomehub review #30227](https://extensions.gnome.org/review/30227) — "What is the use case for session-modes? If you don't have any use case for that, remove session-modes key"
- **Type:** Common Rejection
- **Pattern:** Reviewer questions any use of `session-modes` and requires an explicit justification. Simply including it without a clear reason (especially `["user"]` which is the default) triggers rejection.
- **Current coverage:** Covered — R-META-09 FAILs on `session-modes: ["user"]` (redundant). R-LIFE-14 warns when `unlock-dialog` is declared without explanatory comment in disable().
- **Frequency:** Medium
- **Actionability:** Already covered. No action needed.

### Finding 26: Deprecated Convenience.js Pattern

- **Source:** [Tweaks & Extensions review #28508](https://extensions.gnome.org/review/28508) — "Replace custom convenience functions with built-in alternatives — use initTranslations() and getSettings() from ExtensionUtils, which means removing the convenience.js file"
- **Type:** Unwritten Rule
- **Pattern:** Extensions that include a `convenience.js` file with custom implementations of `initTranslations()` and `getSettings()` are flagged. These functions have been available in `ExtensionUtils` (and later in the `Extension` base class) since GNOME 3.32+. For GNOME 45+ (ESM), they are methods on the `Extension`/`ExtensionPreferences` base classes.
- **Current coverage:** Partial — R-DEPR-05 detects `ExtensionUtils` usage (which is itself deprecated for 45+), but does not flag the presence of a `convenience.js` file that reimplements standard functionality.
- **Frequency:** Medium (mainly legacy extensions that haven't been ported)
- **Actionability:** Add to `check-package.sh` forbidden patterns: `convenience.js`. For GNOME 45+, this file is never needed. For older versions, it is technically valid but the pattern of reimplementing standard functions is discouraged.

---

## Priority Matrix: Actionable Findings

### P0: High-value, easy to implement (pattern rules or simple checks)

| # | Finding | Implementation | Effort |
|---|---------|---------------|--------|
| 2 | Shell-version minor versions | Add check in check-metadata.py | Small |
| 6 | Missing dev artifacts in forbidden list | Add to check-package.sh | Tiny |
| 18 | typeof super.method AI slop | Add pattern rule R-SLOP-30 | Tiny |
| 26 | convenience.js detection | Add to check-package.sh | Tiny |

### P1: High-value, moderate implementation

| # | Finding | Implementation | Effort |
|---|---------|---------------|--------|
| 1 | GNOME trademark in UUID/name/schema | Add checks in check-metadata.py + check-schema.sh | Small |
| 3 | DBus export/unexport lifecycle | Enhance check-lifecycle.py | Medium |
| 14 | Destroy-then-null widget pattern | Add check in check-lifecycle.py | Medium |
| 20 | Timeout reassignment without cleanup | Enhance check-lifecycle.py | Medium |

### P2: Medium-value, moderate-to-high implementation

| # | Finding | Implementation | Effort |
|---|---------|---------------|--------|
| 4 | Null out all references | Heuristic in check-lifecycle.py | Medium |
| 5 | Repeated getSettings() calls | Heuristic across files | Medium |
| 8 | String-based version comparison | Pattern rule | Small |
| 10 | External dependency documentation | Cross-reference check | High |
| 13 | Script complexity assessment | Enhance non-GJS check | Medium |

### P3: Low-value or hard to automate (Tier 3 checklist only)

| # | Finding | Action |
|---|---------|--------|
| 7 | Generic class names | Add to code-quality-checklist.md |
| 9 | Fork mention in description | Enhance licensing-checklist.md |
| 11 | User-Agent scrutiny | Add to security-checklist.md |
| 12 | Unused function detection | Add to code-quality-checklist.md |
| 21 | Unnecessary export statements | Add to code-quality-checklist.md |
| 22 | Settings dependency injection | Add to code-quality-checklist.md |

---

## Cross-Reference: Existing Coverage Gaps Confirmed

These findings confirm gaps already identified in `gap-analysis.md`:

1. **Signal balance tolerance** (Finding 16): The +2 tolerance in R-LIFE-01 is appropriate given the gray area around extension-owned objects, but should be documented.
2. **Widget cleanup completeness** (Finding 14): The destroy-then-null pattern is the most common reviewer complaint, confirming the gap-analysis note about "no general widget created in enable() but not destroyed in disable() check."
3. **Settings nulling** (Finding 4): Confirms gap-analysis note "Checklist covers nulling references. No automated check for missing = null after destroy."

## New Gaps Not Previously Identified

These are entirely new gaps discovered through this research:

1. **GNOME trademark in UUID/name/schema** (Finding 1): Not in gap-analysis at all.
2. **Shell-version minor version format** (Finding 2): gap-analysis noted version validation but not this specific format issue.
3. **DBus interface export/unexport lifecycle** (Finding 3): gap-analysis covered DBus proxies but not exported interfaces.
4. **String-based version comparison** (Finding 8): Not in gap-analysis.
5. **External dependency documentation** (Finding 10): Not in gap-analysis.
6. **typeof super.method AI slop pattern** (Finding 18): Not in any existing AI slop rule.
7. **Timeout reassignment without cleanup** (Finding 20): gap-analysis covered disable() cleanup but not mid-lifecycle reassignment.
8. **convenience.js as deprecated artifact** (Finding 26): Not in gap-analysis.

---

## Sources

- [Reply to extension upload review - GNOME Discourse](https://discourse.gnome.org/t/reply-to-extension-upload-review/17622)
- [Gio.Settings.run_dispose() in extensions - GNOME Discourse](https://discourse.gnome.org/t/gio-settings-run-dispose-in-extensions/17361)
- [Developing Gnome Shell extension is a giant waste of time - GNOME Discourse](https://discourse.gnome.org/t/developing-gnome-shell-extension-is-a-giant-waste-of-time/6179)
- [Is disconnecting from signals always required? - GNOME Discourse](https://discourse.gnome.org/t/is-disconnecting-from-signals-always-required/14862)
- [In a gnome-extension, about disable function when only unlock-dialog session-modes is used - GNOME Discourse](https://discourse.gnome.org/t/in-a-gnome-extension-about-disable-function-when-only-unlock-dialog-session-modes-is-used/17028)
- [AI and GNOME Shell Extensions - Javad Rahmatzadeh blog](https://blogs.gnome.org/jrahmatzadeh/2025/12/06/ai-and-gnome-shell-extensions/)
- [GNOME Shell Extensions Review Guidelines - gjs.guide](https://gjs.guide/extensions/review-guidelines/review-guidelines.html)
- [GNOME Wiki Extension Review Archive](https://wiki.gnome.org/Projects/GnomeShell/Extensions/Review)
- [gnomehub review #30227](https://extensions.gnome.org/review/30227) — JustPerfection
- [Tweaks & Extensions review #28508](https://extensions.gnome.org/review/28508) — JustPerfection
- [Recent Items review #54559](https://extensions.gnome.org/review/54559) — JustPerfection
- [Wechsel review #53836](https://extensions.gnome.org/review/53836) — JustPerfection
- [Draw On Gnome review #62523](https://extensions.gnome.org/review/62523) — JustPerfection
- [APCUPS Monitor review #68473](https://extensions.gnome.org/review/68473) — JustPerfection
- [Forge review #63292](https://extensions.gnome.org/review/63292) — JustPerfection
- [Lock Guard review #67062](https://extensions.gnome.org/review/67062) — JustPerfection
- [GNOME Speech2Text review #67335](https://extensions.gnome.org/review/67335) — JustPerfection
- [GNOME Foundation Trademark Guidelines](https://foundation.gnome.org/legal-and-trademarks)
- [GNOME Bans AI-Generated Code - WebProNews](https://www.webpronews.com/gnome-bans-ai-generated-code-for-shell-extensions-amid-quality-issues/)
- [Problem with icons for version 44 - GNOME Discourse](https://discourse.gnome.org/t/problem-with-icons-when-updating-a-gnome-shell-extension-to-version-44/16226)
