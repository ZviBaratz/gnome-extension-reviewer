# AI Slop Detection Checklist

These patterns signal unreviewed AI-generated code in GNOME Shell extension
submissions. Individual patterns may be benign -- a single try-catch or a
JSDoc annotation is not a problem. But clusters of these patterns strongly
suggest the developer submitted AI output without understanding or reviewing
it. The scoring model at the bottom determines severity.

## Category 1: Error Handling

### 1. Excessive try-catch

Is the try-catch ratio unnaturally high? Are `.destroy()` calls individually
wrapped in try-catch?

- **Red flag:** More than 50% of functions contain try-catch, or individual
  `destroy()` calls are each wrapped in their own try-catch block
- **Acceptable:** Try-catch around known-fallible operations (file I/O, network
  requests, GSettings access, D-Bus calls)

```javascript
// RED FLAG: every destroy wrapped individually
disable() {
    try { this._indicator.destroy(); } catch (e) { console.error(e); }
    try { this._menu.destroy(); } catch (e) { console.error(e); }
    try { this._label.destroy(); } catch (e) { console.error(e); }
}

// ACCEPTABLE: single try-catch around fallible operation
async _loadConfig() {
    try {
        const [ok, contents] = this._file.load_contents(null);
        this._config = JSON.parse(new TextDecoder().decode(contents));
    } catch (e) {
        console.error('Failed to load config:', e.message);
    }
}
```

### 2. Empty catch blocks

Are errors silently swallowed?

- **Red flag:** `catch { }` or `catch (e) { }` with no logging or handling
- **Acceptable:** `catch (e) { console.debug(...) }` or intentionally ignoring
  expected errors with a comment explaining why

```javascript
// RED FLAG: silent swallow
try { this._proxy.ActiveProfile; } catch (e) { }

// ACCEPTABLE: intentional ignore with explanation
try {
    this._proxy.ActiveProfile;
} catch (e) {
    // Proxy may be unavailable during screen lock transition; safe to ignore
}
```

### 3. Over-defensive error handling

Are there try-catch blocks in places that cannot throw?

- **Red flag:** Wrapping property assignments, simple arithmetic, or array
  index access in try-catch
- **Acceptable:** Wrapping GLib/GObject method calls that may fail at runtime

```javascript
// RED FLAG: property assignment cannot throw
try {
    this._enabled = true;
    this._count = 0;
} catch (e) {
    console.error(`Failed to set initial state: ${e.message}`);
}

// ACCEPTABLE: GObject method may throw
try {
    this._settings.set_int('refresh-interval', value);
} catch (e) {
    console.error('Failed to save setting:', e.message);
}
```

## Category 2: State & Lifecycle

### 4. _pendingDestroy + _initializing coordination

Over-engineered async teardown with multiple coordinating state flags.

- **Red flag:** Both `_pendingDestroy` and `_initializing` flags used together,
  or elaborate state machines for initialization/destruction sequencing
- **Acceptable:** Simple `_destroyed` flag checked at async resume points
  (see the [lifecycle checklist](lifecycle-checklist.md#the-_destroyed-flag-pattern))

```javascript
// RED FLAG: over-engineered state machine
async enable() {
    this._initializing = true;
    this._pendingDestroy = false;
    const proxy = await createProxy();
    if (this._pendingDestroy) {
        this._initializing = false;
        this._finishDestroy();
        return;
    }
    this._proxy = proxy;
    this._initializing = false;
}

disable() {
    if (this._initializing) {
        this._pendingDestroy = true;
        return;
    }
    this._cleanup();
}

// ACCEPTABLE: simple _destroyed flag
async enable() {
    this._destroyed = false;
    const proxy = await createProxy();
    if (this._destroyed) return;
    this._proxy = proxy;
}

disable() {
    this._destroyed = true;
    this._proxy = null;
}
```

### 5. isLocked check without lock session-mode

Checking for impossible states. If the extension does not declare lock-screen
session modes, it is never active on the lock screen.

- **Red flag:** `Main.sessionMode.isLocked` or `unlock-dialog` checks in an
  extension whose `metadata.json` does not declare
  `"session-modes": ["user", "unlock-dialog"]`
- **Acceptable:** Extension declares `"session-modes": ["user", "unlock-dialog"]`
  and uses session mode checks to handle transitions

```javascript
// RED FLAG (if metadata.json has no session-modes or only "user"):
enable() {
    if (Main.sessionMode.isLocked)
        return;
    this._createUI();
}

// ACCEPTABLE (if metadata.json declares unlock-dialog):
enable() {
    if (Main.sessionMode.currentMode === 'unlock-dialog')
        this._createLockUI();
    else
        this._createFullUI();
}
```

### 6. Unnecessary null guards

Checking for null before operations that cannot produce null.

- **Red flag:** `if (this._indicator !== null) this._indicator.destroy()` when
  `_indicator` was unconditionally assigned two lines above
- **Acceptable:** Null guards when a field may or may not have been initialized,
  or when guarding against rapid enable/disable

```javascript
// RED FLAG: just assigned, cannot be null
enable() {
    this._indicator = new PanelMenu.Button(0.0, 'MyExt');
    if (this._indicator !== null)
        Main.panel.addToStatusArea('my-ext', this._indicator);
}

// ACCEPTABLE: may not have been created
disable() {
    if (this._indicator) {
        this._indicator.destroy();
        this._indicator = null;
    }
}
```

### 7. Session mode checks in disable()

Checking session mode during cleanup. `disable()` must always perform full
cleanup regardless of the current session mode.

- **Red flag:** `if (Main.sessionMode.currentMode === 'user')` inside `disable()`
- **Acceptable:** Session mode checks in `enable()` to decide what to initialize

```javascript
// RED FLAG: conditional cleanup
disable() {
    if (Main.sessionMode.currentMode === 'user') {
        this._indicator.destroy();
        this._indicator = null;
    }
}

// ACCEPTABLE: session mode check in enable
enable() {
    if (Main.sessionMode.currentMode === 'unlock-dialog') {
        this._createMinimalUI();
    } else {
        this._createFullUI();
    }
}
```

## Category 3: Code Style

### 8. TypeScript-style JSDoc

Systematic `@param {Type}` and `@returns {Type}` annotations throughout the
codebase.

- **Red flag:** Systematic JSDoc on every method, especially with complex types
  like `@param {Map<string, GObject.Object>}` or `@returns {Promise<boolean>}`
- **Acceptable:** Occasional simple comments, GObject property documentation

```javascript
// RED FLAG: systematic TypeScript-style JSDoc
/**
 * Initialize the extension indicator
 * @param {Meta.Display} display - The current display
 * @param {St.BoxLayout} container - The panel container
 * @returns {PanelMenu.Button} The created indicator
 */
_createIndicator(display, container) { ... }

// ACCEPTABLE: brief comment
// Create the panel indicator and add it to the status area
_createIndicator() { ... }
```

### 9. Verbose error messages

Over-descriptive template literals in catch blocks with constructor names and
method context baked in.

- **Red flag:** `console.error(\`Failed to initialize ${this.constructor.name}: ${error.message}\`)`
- **Acceptable:** `console.error(error)` or `logError(error, 'ExtensionName')`

```javascript
// RED FLAG: enterprise-style error messages
catch (error) {
    console.error(
        `[${this.constructor.name}] Failed to execute ` +
        `${methodName} in state ${this._state}: ${error.message}`
    );
}

// ACCEPTABLE: straightforward error logging
catch (e) {
    console.error('Failed to load config:', e.message);
}
```

### 10. Defensive programming idioms

Enterprise-style null checks and type guards that are unnecessary in GJS.

- **Red flag:** `typeof x === 'undefined' && x !== null` checks, redundant
  `instanceof` checks, `Object.freeze()` on configuration objects
- **Acceptable:** Checks at trust boundaries (preferences UI input, D-Bus
  signals from external services)

```javascript
// RED FLAG: unnecessary type guards
if (typeof this._settings !== 'undefined' && this._settings !== null
    && this._settings instanceof Gio.Settings) {
    this._settings.set_int('value', newValue);
}

// ACCEPTABLE: validating external input
_onDBusSignal(proxy, sender, params) {
    const [value] = params;
    if (typeof value !== 'number' || value < 0 || value > 100)
        return;
    this._updateLevel(value);
}
```

## Category 4: API Usage

### 11. Browser API usage

`setTimeout`, `setInterval`, `fetch`, `document.*`, `window.*`.

- **Red flag:** Any use of browser APIs
- **Note:** These are automatically caught by `ego-lint` pattern rules (see
  the [web API ban list](code-quality-checklist.md#web-api-ban-list))

### 12. Deprecated module imports

`Mainloop`, `ByteArray`, `Lang`, `ExtensionUtils`, `Tweener`.

- **Red flag:** Any use of deprecated modules in a GNOME 45+ extension
- **Note:** Partially caught by `ego-lint` (see
  [deprecated modules](code-quality-checklist.md#deprecated-modules-and-their-replacements))

### 13. Non-idiomatic GLib usage

Wrong approach to common tasks.

- **Red flag:** Manual signal tracking arrays instead of `connectObject`,
  raw `GLib.timeout_add` without storing the ID for cleanup, using
  `GLib.spawn_command_line_sync` when `Gio.Subprocess` is available
- **Acceptable:** `connectObject` for auto-cleanup, stored timeout IDs cleared
  in `disable()`, `Gio.Subprocess` with explicit argv

```javascript
// RED FLAG: manual signal tracking array
enable() {
    this._signals = [];
    this._signals.push(this._settings.connect('changed::key1', () => {}));
    this._signals.push(this._settings.connect('changed::key2', () => {}));
}
disable() {
    this._signals.forEach(id => this._settings.disconnect(id));
    this._signals = [];
}

// ACCEPTABLE: connectObject
enable() {
    this._settings.connectObject(
        'changed::key1', () => this._onKey1Changed(),
        'changed::key2', () => this._onKey2Changed(),
        this
    );
}
disable() {
    this._settings.disconnectObject(this);
    this._settings = null;
}
```

## Category 5: Metadata

### 14. Non-standard fields

`version-name`, `homepage`, `bug-report-url`, `author`, `license` in
`metadata.json`.

- **Red flag:** Multiple non-standard fields present (EGO ignores them and
  reviewers flag them as cargo-culted from AI templates)
- **Note:** Partially automated by `ego-lint` metadata checks

### 15. Deprecated version field

`"version": 1` in `metadata.json` for GNOME 45+ extensions.

- **Red flag:** `version` field present -- EGO auto-assigns version numbers;
  the field is deprecated
- **Note:** Automated by `ego-lint` metadata checks

### 16. UUID format

Missing `@` sign, generic names.

- **Red flag:** UUID without `@` (e.g., `"my-extension"`), or generic names
  like `"extension"`, `"my-gnome-extension"` with no personalization
- **Acceptable:** `"my-extension@username.github.io"` with a unique identifier
- **Note:** UUID format is automated by `ego-lint`; generic naming requires
  manual judgment

## Category 6: Undeclared/Hallucinated

### 17. References to non-existent APIs

Calling methods that do not exist in GNOME Shell.

- **Red flag:** `Main.panel.addToStatusArea` with wrong signature, importing
  modules that do not exist at the specified path, using methods with incorrect
  argument counts
- **Ask:** Does the import path actually exist? Does the method signature match
  the GNOME Shell version declared in `metadata.json`?

See also: [imaginary APIs](code-quality-checklist.md#imaginary-apis) and
[hallucinated imports](code-quality-checklist.md#hallucinated-imports) in the
code quality checklist.

### 18. Root/elevated operations

Using `pkexec` or polkit without justification.

- **Red flag:** `pkexec` calls, `Gio.Subprocess` running commands with `sudo`
  or `pkexec`, polkit actions without a clear hardware or system-level need
- **Acceptable:** Only when the extension genuinely requires root access
  (hardware control, system settings that have no D-Bus interface)

See also: [pkexec and privilege escalation](security-checklist.md#pkexec-and-privilege-escalation)
in the security checklist.

## Category 7: Additional AI Signals

### 19. typeof super.destroy guard

Checking if `super.destroy` is a function before calling it.

- **Red flag:** `if (typeof super.destroy === 'function') super.destroy()`
- **Acceptable:** Calling `super.destroy()` directly — it always exists on GObject classes

```javascript
// RED FLAG: unnecessary type check
destroy() {
    try {
        if (typeof super.destroy === 'function') {
            super.destroy();
        }
    } catch (e) {
        console.warn(`${e.message}`);
    }
}

// ACCEPTABLE: direct call
destroy() {
    super.destroy();
}
```

This is the canonical example from JustPerfection's AI policy blog post.

### 20. Redundant instanceof this

Checking `this instanceof ClassName` inside a method of that class.

- **Red flag:** `if (this instanceof MyExtension)` inside `MyExtension`'s methods
- **Acceptable:** `instanceof` checks on external objects or arguments

```javascript
// RED FLAG: always true
enable() {
    if (this instanceof MyExtension) {
        this._init();
    }
}

// ACCEPTABLE: checking external argument
_processWidget(widget) {
    if (widget instanceof St.Button)
        widget.connect('clicked', this._onClick.bind(this));
}
```

### 21. Excessive comment density

Comments explaining obvious code on nearly every line.

- **Red flag:** >40% of lines are comments (after first 10 lines), especially
  comments like `// Set the label` before `this.label = 'text'`
- **Acceptable:** Comments explaining non-obvious logic, API quirks, or
  workarounds for known bugs

### 22. console.log instead of console.debug

Using `console.log()` in production code.

- **Red flag:** `console.log()` anywhere in extension code
- **Acceptable:** `console.debug()`, `console.warn()`, `console.error()`
- **Note:** `console.log()` is explicitly banned by EGO reviewers. AI defaults
  to it from browser JavaScript habits.

### 23. var declarations

Using `var` instead of `const`/`let`.

- **Red flag:** `var` declarations in GNOME 45+ extension code
- **Acceptable:** `const` for immutable bindings, `let` for mutable ones
- **Note:** AI-generated code frequently uses `var` because training data
  includes older JavaScript.

### 24. Wrong resource path in prefs.js

Using the extension.js resource path in prefs.js.

- **Red flag:** `resource:///org/gnome/shell/` (lowercase) in prefs.js
- **Acceptable:** `resource:///org/gnome/Shell/Extensions/js/` (capitalized)
- **Note:** AI models don't know about the capitalization difference between
  extension.js and prefs.js resource paths.

### 25. Missing SOURCE_REMOVE return in timeout

Timeout callbacks without explicit return value.

- **Red flag:** `GLib.timeout_add(..., () => { doStuff(); })` with no return
- **Acceptable:** `GLib.timeout_add(..., () => { doStuff(); return GLib.SOURCE_REMOVE; })`
- **Note:** AI models browser `setTimeout` patterns where no return is needed.
  In GLib, missing return causes infinite repetition.

### 26. Both getPreferencesWidget and fillPreferencesWindow

Defining both prefs methods in prefs.js.

- **Red flag:** Both methods defined in the same prefs.js file
- **Acceptable:** Only `fillPreferencesWindow()` for GNOME 45+
- **Note:** AI hedges by implementing both methods, not understanding they're
  mutually exclusive.

### 27. Generic extension name in UUID

Using template-like names in the UUID.

- **Red flag:** UUID like `my-extension@user`, `gnome-tool@dev`, `extension@test`
- **Acceptable:** Descriptive, unique UUID like `hara-hachi-bu@ZviBaratz`
- **Note:** AI-generated scaffolds often use generic placeholder UUIDs.

### 28. Comments that read like instructions to an AI model

Imperative comments that tell the code what to do rather than explaining why.

- **Red flag:** `// Important: Make sure to always initialize settings before use`,
  `// Note: Ensure proper cleanup in disable method`,
  `// Remember: Always handle errors gracefully`
- **Acceptable:** Comments explaining non-obvious design decisions or API quirks

```javascript
// RED FLAG: instructing the code
// Important: Make sure to clean up all resources in disable
// Note: Ensure the proxy is disconnected before nulling
// TODO: Don't forget to handle the error case

// ACCEPTABLE: explaining a design choice
// UPower proxy may outlive the extension on fast enable/disable cycles;
// check _destroyed before using the cached result.
```

### 29. Inconsistent code style within the same file

Mixed naming conventions, formatting patterns, or idioms suggesting copy-paste
from multiple AI sessions.

- **Red flag:** Mix of `camelCase` and `snake_case` for the same kind of
  identifier, inconsistent brace placement, varying quote styles within one file
- **Acceptable:** Consistent style throughout, even if it differs from GNOME
  conventions (style is fixable; inconsistency signals lack of review)

### 30. Overly uniform structure (copy-paste with variations)

Structurally identical code blocks with only variable names changed.

- **Red flag:** 3+ near-identical blocks like `if (this._x) { this._x.destroy(); this._x = null; }` repeated for different fields without using optional chaining or a helper
- **Acceptable:** Using `this._x?.destroy()` or a cleanup helper function

```javascript
// RED FLAG: 5 identical blocks
disable() {
    if (this._a) { this._a.destroy(); this._a = null; }
    if (this._b) { this._b.destroy(); this._b = null; }
    if (this._c) { this._c.destroy(); this._c = null; }
    if (this._d) { this._d.destroy(); this._d = null; }
    if (this._e) { this._e.destroy(); this._e = null; }
}

// ACCEPTABLE: idiomatic cleanup
disable() {
    this._a?.destroy();
    this._b?.destroy();
    this._c?.destroy();
    this._d?.destroy();
    this._e?.destroy();
    this._a = this._b = this._c = this._d = this._e = null;
}
```

### 31. Error handling that adds no value

Catch-and-rethrow or catch-and-log-only patterns.

- **Red flag:** `catch (e) { console.error(e); throw e; }` — logs and rethrows,
  adding nothing. Or `catch (e) { console.error('Error occurred'); }` that
  swallows the original error and provides a less useful message.
- **Acceptable:** Catch that adds context (`console.error('ExtName: failed to init proxy', e)`)
  or handles the error (retry, fallback, graceful degradation)

```javascript
// RED FLAG: catch-log-rethrow
try {
    await this._proxy.initAsync();
} catch (e) {
    console.error(`Failed to initialize proxy: ${e.message}`);
    throw e;
}

// ACCEPTABLE: catch with recovery
try {
    await this._proxy.initAsync();
} catch (e) {
    console.warn('Proxy init failed, using defaults');
    this._useDefaults = true;
}
```

### 32. Methods that exist for "completeness" but are never called

Dead methods that appear to exist because the AI generated a "complete" class.

- **Red flag:** Methods like `toString()`, `toJSON()`, `valueOf()`, `equals()`,
  or `clone()` that are defined but never referenced anywhere in the extension
- **Acceptable:** GObject virtual methods (`vfunc_*`) or lifecycle methods
  that are called by the framework

### 33. Documentation describing what code obviously does

Comments that restate the code rather than explaining intent.

- **Red flag:** `// Set the label text` before `this.label.set_text('Hello')`,
  `// Create a new button` before `new St.Button()`
- **Acceptable:** Comments explaining *why* something is done a certain way,
  API quirks, or non-obvious side effects

```javascript
// RED FLAG: restating the obvious
// Create a new BoxLayout with vertical orientation
const box = new St.BoxLayout({vertical: true});
// Add the label to the box
box.add_child(this._label);

// ACCEPTABLE: explaining the 'why'
// BoxLayout must be vertical so the icon and label stack;
// horizontal layout clips the label on small panels.
const box = new St.BoxLayout({vertical: true});
box.add_child(this._label);
```

---

## Real-World AI Detection Intelligence

**Reviewer perspective (Javad Rahmatzadeh, December 2025):**

The reviewer reported spending "more than 6 hours a day reviewing over 15,000 lines of extension code" due to AI-generated submissions. The primary detection signals:

1. **Try-catch around guaranteed APIs** — wrapping `super.destroy()` in try-catch is the single biggest tell
2. **Inconsistent style** — mixing patterns suggests copy-paste from different AI generations
3. **Imaginary APIs** — calling methods that don't exist in GNOME Shell (AI hallucinations)
4. **Comments as prompts** — "// Create a button that does X" reads like an LLM instruction
5. **Verbose error messages** — error strings that read like documentation, not debugging output

> **Reviewer says:** "While it is not prohibited to use AI as a learning aid or a development tool (i.e. code completions), extension developers should be able to justify and explain the code they submit, within reason."

## Scoring Model

Count the number of triggered items out of the 33 above.

```
1-3 triggered:  ADVISORY  -- note them, extension may still pass
4-6 triggered:  BLOCKING  -- suggests insufficient code review
7+  triggered:  BLOCKING  -- likely unreviewed AI output
```

**Independently blocking items:** Regardless of total count, any hallucinated
API (items 11, 17) or impossible state check (item 5) is independently blocking
because it demonstrates the code was not tested against a real GNOME Shell
instance.

## Verdict Guide

- **ADVISORY (1-2 triggered):** Mention the patterns found and suggest fixes,
  but do not block the extension. These patterns occasionally appear in
  hand-written code.
- **BLOCKING (3-5 triggered):** Request fixes for the specific patterns. The
  developer should demonstrate they understand the code by explaining their
  design choices or refactoring the flagged patterns.
- **BLOCKING (6+ triggered):** Request a thorough rewrite. The code likely does
  not reflect the developer's understanding of the GNOME Shell extension
  lifecycle and APIs. Point the developer to the
  [GNOME Shell extension documentation](https://gjs.guide/extensions/) and
  suggest they build familiarity before resubmitting.
