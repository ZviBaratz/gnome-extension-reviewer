# Lifecycle Checklist

Resource management is the single most common cause of EGO rejections. Every
resource created during `enable()` must be destroyed during `disable()`.

## Resource Creation/Destruction Table

| Resource Type | Create in enable() | Destroy in disable() | Pattern |
|---|---|---|---|
| Widgets / UI elements | `new St.Widget()`, `new PopupMenu.PopupMenuItem()` | `widget.destroy()` then `= null` | Destroy removes from parent and frees |
| GObject signal connections | `obj.connect('signal', handler)` | `obj.disconnect(id)` then `id = null` | Store returned ID for later disconnect |

> **Reviewer says:** "Destroy and null out in disable: `this._label.destroy(); this._label = null; this._settings = null;`"
| GObject signal connections (auto) | `obj.connectObject('signal', handler, this)` | `obj.disconnectObject(this)` | Preferred pattern; auto-cleanup by owner |
| GLib timeouts | `GLib.timeout_add(prio, ms, cb)` | `GLib.Source.remove(id)` then `id = null` | Always remove before nulling |
| GLib timeout (seconds) | `GLib.timeout_add_seconds(prio, s, cb)` | `GLib.Source.remove(id)` then `id = null` | Same cleanup as timeout_add |
| File monitors | `file.monitor_file(flags, null)` | `monitor.cancel()` then disconnect signal | Cancel first, then disconnect, then null |
| D-Bus proxies | `new DBusProxy(...)` | Disconnect signals, then `= null` | Disconnect before nulling |
| GSettings connections | `settings.connect('changed::key', cb)` | `settings.disconnect(id)` then `= null` | Or use connectObject pattern |
| Main.panel modifications | `Main.panel.addToStatusArea()` | `indicator.destroy()` | destroy() removes from panel |
| Quick Settings menu | `Main.panel.statusArea.quickSettings.addExternalIndicator()` | `indicator.quickSettingsItems.forEach(i => i.destroy())` then `indicator.destroy()` | Destroy items first, then indicator |
| Keybindings | `Main.wm.addKeybinding()` | `Main.wm.removeKeybinding()` | Must use same key name |

## Constructor Constraints

The constructor (`constructor()` in ES6 classes, `_init()` in legacy GObject)
is called once when the extension object is instantiated. It must NOT allocate
resources that need cleanup.

**Allowed in constructor:**
- Setting default property values
- Defining constants
- Calling `super()`

**NOT allowed in constructor:**
- Signal connections
- Timeout creation
- File monitor creation
- D-Bus proxy initialization
- UI element creation
- Any operation that would need cleanup in destroy/disable

> **Reviewer says:** "Resources should be created in enable() and cleaned up in disable(), not in the constructor. The constructor runs once but enable/disable can be called multiple times."

**Why:** The constructor runs once, but `enable()`/`disable()` can be called
multiple times during the extension's lifetime (lock screen, suspend, extension
toggling). Resources allocated in the constructor would leak on each
enable/disable cycle.

```javascript
// WRONG: resource allocation in constructor
class MyExtension extends Extension {
    constructor(metadata) {
        super(metadata);
        this._settings = this.getSettings(); // Leaks on re-enable
        this._proxy = new SomeProxy();       // Leaks on re-enable
    }
}

// CORRECT: resources in enable(), cleanup in disable()
class MyExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._proxy = new SomeProxy();
    }

    disable() {
        this._proxy = null;
        this._settings = null;
    }
}
```

## The _destroyed Flag Pattern

Extensions with async operations (D-Bus calls, file I/O, subprocess execution)
must guard against callbacks firing after the extension is disabled. The
`_destroyed` flag pattern prevents use-after-destroy errors.

```javascript
class MyController {
    constructor() {
        super();
        this._destroyed = false;
    }

    async someAsyncMethod() {
        if (this._destroyed)
            return false;

        const result = await someOperation();

        // CRITICAL: check again after every await point
        if (this._destroyed)
            return false;

        this._updateState(result);
        return true;
    }

    somePromiseMethod() {
        somePromise().then(result => {
            if (!this._destroyed)
                this._handleResult(result);
        }).catch(e => {
            if (!this._destroyed)
                console.error('MyController', e);
        });
    }

    destroy() {
        this._destroyed = true; // FIRST line of destroy
        // ... cancel timeouts, disconnect signals, etc.
    }
}
```

**Key rules:**
- Set `_destroyed = true` as the FIRST line of `destroy()`
- Check `_destroyed` before every `await` resume point
- Check `_destroyed` in every `.then()` and `.catch()` callback
- Check `_destroyed` in timeout callbacks that might fire during cleanup

> **Reviewer says:** "Your extension has async operations but I don't see a `_destroyed` flag check after the await points. If the extension is disabled during the async call, the callback will act on torn-down state."

## Session Mode Handling

If `metadata.json` declares `session-modes` (e.g., `["user", "unlock-dialog"]`),
the extension must handle transitions between modes.

```javascript
enable() {
    // Called when entering a declared session mode
    this._createUI();
}

disable() {
    // Called when leaving a declared session mode
    this._destroyUI();
}
```

**Common pattern:** Destroy UI on lock screen, recreate on unlock. The
extension's `enable()` and `disable()` are called for each mode transition, so
they must be fully symmetric -- every `enable()` can be followed by `disable()`
at any time.

**Caution:** If `session-modes` is `["user"]` or omitted entirely, EGO
reviewers expect that the extension does NOT set this field. Setting
`session-modes: ["user"]` explicitly is flagged as unnecessary.

> **Reviewer says:** "You don't need `session-modes: ['user']` in your metadata — that's the default. Only set session-modes if you need `unlock-dialog` support."

## Cleanup Ordering

Resources must be destroyed in the **reverse order** of creation. This prevents
dangling references and use-after-free patterns.

```javascript
enable() {
    // 1. Settings
    this._settings = this.getSettings();
    // 2. Controller (uses settings)
    this._controller = new MyController(this._settings);
    // 3. UI (uses controller)
    this._panel = new MyPanel(this._controller);
}

disable() {
    // 3. UI first (depends on controller)
    this._panel.destroy();
    this._panel = null;
    // 2. Controller (depends on settings)
    this._controller.destroy();
    this._controller = null;
    // 1. Settings last (no dependencies)
    this._settings = null;
}
```

**Specific ordering rules:**
- Disconnect signals on an object BEFORE destroying that object
- Cancel file monitors BEFORE disconnecting their change signals
- Remove timeouts BEFORE nulling the objects they reference
- Destroy child widgets BEFORE destroying parent containers
- Disconnect D-Bus proxy signals BEFORE nulling the proxy

> **Reviewer says:** "Your disable() destroys objects in the wrong order. Resources must be destroyed in reverse order of creation — disconnect signals first, then destroy widgets, then null references."

## D-Bus Proxy Cleanup Sequence

D-Bus proxies manage signal connections to external services. Cleanup must
follow a specific order:

```javascript
// In enable() or init
this._proxy = new SomeDBusProxy(Gio.DBus.system, 'org.service.Name',
    '/org/service/path');
this._proxy.connectObject(
    'g-properties-changed', () => this._onPropsChanged(),
    this
);

// In disable()
this._proxy.disconnectObject(this);  // 1. Disconnect signals first
this._proxy = null;                   // 2. Then null the reference
```

> *EGO reviewer feedback: "Destroy and null out in disable: `this._label.destroy();
> this._label = null; this._settings = null;`"*

## File Monitor Cleanup Sequence

File monitors must be cancelled before signal disconnection:

```javascript
// In enable()
const file = Gio.File.new_for_path('/some/path');
this._monitor = file.monitor_file(Gio.FileMonitorFlags.NONE, null);
this._monitor.connectObject('changed', (m, f, o, type) => {
    this._onFileChanged(f, type);
}, this);

// In disable()
this._monitor.cancel();                 // 1. Cancel monitoring first
this._monitor.disconnectObject(this);   // 2. Then disconnect signals
this._monitor = null;                   // 3. Then null reference
```

## Soup.Session Cleanup

Extensions using `Soup.Session` for HTTP requests must abort the session in
`disable()` before nullifying:

```javascript
enable() {
    this._session = new Soup.Session();
}

disable() {
    this._session.abort();   // Cancel all pending requests
    this._session = null;
}
```

- Verify `session.abort()` is called in `disable()` before nullifying
- Pattern: `this._session.abort(); this._session = null;`
- Without `abort()`, in-flight requests continue after disable and callbacks
  fire on torn-down state

> **Reviewer says:** "Please abort the Soup.Session in disable" — GitHub Tray, HakaWaka (Feb 2026)

**Automatically checked by ego-lint (R-LIFE-15).**

## Preferences Window Cleanup

GObject instances stored as class properties in prefs classes prevent garbage
collection after the preferences window is closed. The prefs window is a GTK4
window — it gets destroyed when the user closes it, but `this._settings` and
other GObject references on the class instance keep objects alive.

```javascript
// WRONG: GObject instance stored on class, never cleaned up
export default class MyPrefs extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        this._settings = this.getSettings();  // Leaks after window close
        // ... build UI using this._settings
    }
}

// CORRECT: use local variable or connect close-request for cleanup
export default class MyPrefs extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const settings = this.getSettings();  // Local — GC'd with window
        // ... build UI using settings

        // Alternative: explicit cleanup
        window.connect('close-request', () => {
            this._settings = null;
        });
    }
}
```

- Anti-pattern: `this._settings = new Gio.Settings(...)` without cleanup handler
- Verify: `connect('close-request', ...)` or local variables instead of `this._settings`

**Automatically checked by ego-lint (R-PREFS-05).**

## Keybinding Cleanup

Every `addKeybinding` must have a matching `removeKeybinding` in disable():

```javascript
enable() {
    Main.wm.addKeybinding('my-shortcut', this.getSettings(),
        Meta.KeyBindingFlags.IGNORE_AUTOREPEAT,
        Shell.ActionMode.NORMAL,
        () => this._onShortcut());
}

disable() {
    Main.wm.removeKeybinding('my-shortcut');
}
```

## GSettings Change Handler Cleanup

GSettings `changed::` handlers are the most commonly leaked signal:

```javascript
// PREFERRED: connectObject
enable() {
    this._settings = this.getSettings();
    this._settings.connectObject(
        'changed::my-key', () => this._onKeyChanged(),
        this
    );
}
disable() {
    this._settings.disconnectObject(this);
    this._settings = null;
}

// ACCEPTABLE: manual tracking
enable() {
    this._settings = this.getSettings();
    this._settingsId = this._settings.connect('changed::my-key',
        () => this._onKeyChanged());
}
disable() {
    this._settings.disconnect(this._settingsId);
    this._settingsId = null;
    this._settings = null;
}
```

## Cairo Context Disposal

Drawing callbacks must dispose the Cairo context to prevent memory leaks:

```javascript
vfunc_repaint() {
    const cr = this.get_context();
    // ... draw operations ...
    cr.$dispose();  // Required: prevents Cairo context leak
}
```

## Gio.Cancellable for Async Operations

Long-running async operations should accept a `Gio.Cancellable` and cancel it
in disable():

```javascript
enable() {
    this._cancellable = new Gio.Cancellable();
    this._loadDataAsync();
}

async _loadDataAsync() {
    try {
        const [ok, contents] = await this._file.load_contents_async(
            this._cancellable);
        // process
    } catch (e) {
        if (!e.matches(Gio.IOErrorEnum, Gio.IOErrorEnum.CANCELLED))
            console.error('Load failed:', e.message);
    }
}

disable() {
    this._cancellable.cancel();
    this._cancellable = null;
}
```

## Common Lifecycle Mistakes

### Forgetting to null references

> **Reviewer says:** "After destroying an object, set the reference to null. Otherwise the variable still points to a destroyed object, which is a common source of use-after-free bugs."

```javascript
// WRONG: object destroyed but reference kept
disable() {
    this._indicator.destroy();
    // this._indicator still points to destroyed object
}

// CORRECT
disable() {
    this._indicator.destroy();
    this._indicator = null;
}
```

### Missing timeout cleanup

> **Reviewer says:** "I see a `timeout_add` in enable() but no matching `GLib.Source.remove()` in disable(). All timeouts must be removed when the extension is disabled, otherwise the callback fires on a destroyed extension."

```javascript
// WRONG: timeout fires after disable
enable() {
    this._timeoutId = GLib.timeout_add_seconds(0, 30, () => {
        this._refresh();
        return GLib.SOURCE_CONTINUE;
    });
}

disable() {
    // Forgot to remove timeout -- callback fires on destroyed extension
}

// CORRECT
disable() {
    if (this._timeoutId) {
        GLib.Source.remove(this._timeoutId);
        this._timeoutId = null;
    }
}
```

### Rapid enable/disable race condition
```javascript
// WRONG: async init doesn't guard against mid-flight disable
async enable() {
    this._proxy = await createProxy();    // What if disable() called here?
    this._proxy.connect('signal', ...);   // Proxy is null / extension destroyed
}

// CORRECT
async enable() {
    this._destroyed = false;
    const proxy = await createProxy();
    if (this._destroyed) return;          // Extension disabled during await
    this._proxy = proxy;
    this._proxy.connect('signal', ...);
}

disable() {
    this._destroyed = true;
    if (this._proxy) {
        this._proxy.disconnect(...);
        this._proxy = null;
    }
}
```

### connectObject vs manual connect

> **Reviewer says:** "Please use `connectObject()` instead of manual signal tracking. It's less error-prone and `disconnectObject(this)` cleans up everything at once."

```javascript
// ACCEPTABLE but error-prone: manual connect with stored ID
enable() {
    this._signalId = someObject.connect('notify::property', () => { ... });
}
disable() {
    if (this._signalId) {
        someObject.disconnect(this._signalId);
        this._signalId = null;
    }
}

// PREFERRED: connectObject with automatic cleanup
enable() {
    someObject.connectObject('notify::property', () => { ... }, this);
}
disable() {
    someObject.disconnectObject(this);
}
```

The `connectObject` pattern is strongly preferred because:
- No signal ID bookkeeping
- `disconnectObject(this)` cleans up ALL connections from this owner at once
- Harder to forget or misorder cleanup

## Real-World Anti-Patterns

These anti-patterns come from real EGO rejections. Each shows rejected code and
the approved alternative.

### Anti-Pattern: Individual Try-Catch Around Destroy Calls

**Rejected:**
```js
disable() {
    if (this._indicator) {
        try { this._indicator.destroy(); } catch (e) { console.error(e); }
    }
    if (this._label) {
        try { this._label.destroy(); } catch (e) { console.error(e); }
    }
    if (this._button) {
        try { this._button.destroy(); } catch (e) { console.error(e); }
    }
}
```

**Why rejected:** `.destroy()` on GNOME Shell widgets doesn't throw. Wrapping
each call in try-catch is defensive programming that signals the author doesn't
understand the API. If destroy fails, the extension has a fundamental problem
that catching won't help.

**Approved:**
```js
disable() {
    this._indicator?.destroy();
    this._indicator = null;
    // Or if _indicator was added to panel:
    // this._indicator is auto-destroyed when removed
}
```

### Anti-Pattern: Checking isLocked Without Lock Session-Mode

**Rejected:**
```js
// metadata.json has no session-modes (defaults to ["user"])
enable() {
    if (Main.sessionMode.isLocked)
        return;
    this._init();
}
```

**Why rejected:** Extensions without `session-modes: ["unlock-dialog"]` in
metadata.json never run during the lock screen. Checking `isLocked` is an
impossible state — it can never be true. This signals the code was AI-generated
without understanding GNOME Shell's session model.

**Approved:**
```js
// If extension doesn't need lock screen support:
enable() {
    this._init(); // No lock check needed — we only run in "user" mode
}

// If extension DOES need lock screen support:
// In metadata.json: "session-modes": ["user", "unlock-dialog"]
enable() {
    if (Main.sessionMode.currentMode === 'unlock-dialog') {
        // Initialize limited UI for lock screen
    } else {
        // Full initialization
    }
}
```

### Anti-Pattern: Over-Engineered Async Coordination

**Rejected:**
```js
enable() {
    this._initializing = false;
    this._pendingDestroy = false;
    this._initAsync();
}

async _initAsync() {
    if (this._initializing) return;
    this._initializing = true;
    try {
        await this._loadData();
        if (this._pendingDestroy) return;
        this._createUI();
    } finally {
        this._initializing = false;
        if (this._pendingDestroy) {
            this._pendingDestroy = false;
            this._cleanup();
        }
    }
}

disable() {
    if (this._initializing) {
        this._pendingDestroy = true;
        return;
    }
    this._cleanup();
}
```

**Why rejected:** This is an over-engineered solution to async enable/disable.
The `_pendingDestroy` + `_initializing` "pendulum" pattern adds complexity
without benefit. GNOME extensions have a simple lifecycle where `disable()` must
clean up synchronously.

**Approved:**
```js
enable() {
    this._destroyed = false;
    this._initAsync();
}

async _initAsync() {
    const data = await this._loadData();
    if (this._destroyed) return; // Check once after each await
    this._createUI(data);
}

disable() {
    this._destroyed = true;
    this._indicator?.destroy();
    this._indicator = null;
}
```

**Key insight:** The `_destroyed` flag is checked after each `await` point.
`disable()` cleans up immediately and synchronously. No "pending" coordination
needed.

## Signal Balance Verification

> **Reviewer says:** "Your extension creates signals in enable() but I don't see matching disconnects in disable(). All signals must be cleaned up when the extension is disabled."

When reviewing, build an explicit inventory:

1. **Grep for all connect calls**: `.connect(`, `.connectObject(`
2. **Grep for all disconnect calls**: `.disconnect(`, `.disconnectObject(`
3. **For each `connectObject` call**, verify a matching `disconnectObject(this)` exists in the disable/destroy path
4. **For each manual `.connect(` call**, verify:
   - The returned handler ID is stored
   - A matching `.disconnect(id)` exists in disable/destroy
   - The ID is nulled after disconnect

### Untracked Timeout Check

1. **Grep for `timeout_add` and `idle_add`**
2. **For each call**, verify the return value is assigned to a variable
3. **For each stored ID**, verify `GLib.Source.remove(id)` is called in disable/destroy

### connectObject Migration

If the extension uses 3+ manual connect/disconnect pairs, suggest migrating to
`connectObject()` for automatic cleanup:

```javascript
// Before: manual tracking
enable() {
    this._id = this._settings.connect('changed::key', () => {});
}
disable() {
    this._settings.disconnect(this._id);
    this._id = null;
}

// After: auto-cleanup
enable() {
    this._settings.connectObject('changed::key', () => {}, this);
}
disable() {
    this._settings.disconnectObject(this);
}
```

## Search Provider Lifecycle

| Phase | Action |
|-------|--------|
| enable() | `Main.overview.searchController.addProvider(this._provider)` |
| disable() | `Main.overview.searchController.removeProvider(this._provider)` then `this._provider = null` |

- Search provider MUST be registered in `enable()` and unregistered in `disable()`
- Provider class must implement `getResultMetas()`, `activateResult()`, and `getInitialResultSet()`

## Notification Source Lifecycle

| Phase | Action |
|-------|--------|
| enable() | `this._source = new MessageTray.Source(...)` then `Main.messageTray.add(this._source)` |
| disable() | `this._source.destroy()` then `this._source = null` |

- Custom notification sources MUST handle the `destroy` signal
- Sources are auto-removed from the message tray on destroy
- Connect to `this._source.connect('destroy', ...)` to handle user-initiated dismissal

## Async Cancellation Patterns

For operations that may outlive the enable/disable cycle:
- Use `Gio.Cancellable` for cancellable async operations
- Cancel the cancellable in `disable()`: `this._cancellable.cancel()`
- Alternatively, use the `_destroyed` flag pattern after each `await`

---

## Notification and Dialog Lifecycle

### MessageTray.Source

If an extension creates a `MessageTray.Source` for notifications:

| Pattern | Requirement |
|---|---|
| Creating the source | Connect to `destroy` signal for safe reuse |
| Reusing after destruction | Re-add to `Main.messageTray` after the source is destroyed |
| In disable() | Destroy the source if it exists |

```javascript
// Correct pattern
enable() {
    this._source = new MessageTray.Source({title: 'My Extension'});
    this._source.connect('destroy', () => { this._source = null; });
    Main.messageTray.add(this._source);
}

disable() {
    this._source?.destroy();
    this._source = null;
}
```

### Modal Dialogs

If an extension creates modal dialogs:

- Dialogs have lifecycle states: `OPENED`, `CLOSED`, `OPENING`, `CLOSING`, `FADED_OUT`
- Do not operate on dialogs in incompatible states
- When `destroyOnClose: false`, the extension is responsible for manual destruction in disable()

```javascript
// If dialog may outlive enable/disable
disable() {
    if (this._dialog) {
        this._dialog.close(global.get_current_time());
        this._dialog.destroy();
        this._dialog = null;
    }
}
```

---

## Selective Disable Detection

Extensions MUST NOT disable selectively. The `disable()` method must always
perform complete cleanup regardless of the current session mode, enabled state,
or any other condition.

**Automatically checked by ego-lint (R-LIFE-13).**

### Rejected pattern: conditional return in disable()

```javascript
// REJECTED: skips cleanup based on session mode
disable() {
    if (Main.sessionMode.currentMode === 'unlock-dialog')
        return;  // R-LIFE-13 flags this
    this._indicator.destroy();
    this._indicator = null;
}
```

### Approved pattern: unconditional cleanup

```javascript
// APPROVED: always cleans up
disable() {
    this._indicator?.destroy();
    this._indicator = null;
}
```

**Exception:** Null guards like `if (!this._x) return;` are NOT flagged — they
protect against double-destroy on rapid enable/disable cycles.

## Prototype Override Restoration

Direct prototype modifications (`SomeClass.prototype.method = ...`) must be
restored in `disable()`. The preferred approach is to use `InjectionManager`:

```javascript
import {InjectionManager} from 'resource:///org/gnome/shell/extensions/extension.js';

enable() {
    this._injectionManager = new InjectionManager();
    this._injectionManager.overrideMethod(
        PopupMenu.PopupMenuItem.prototype, 'activate',
        original => function() { /* custom behavior */ }
    );
}

disable() {
    this._injectionManager.clear();
    this._injectionManager = null;
}
```

**Automatically checked by ego-lint (enhanced R-LIFE-10).**

---

## Real Rejection Examples

> **"Search Light" (May 2024):** "improper resource cleanup in disable, logging methods, and creating object instances in global scope." — Rejected for three simultaneous lifecycle violations.

> **"Blur my Shell" (March 2024):** "creating object instances in global scope." — Even well-known, popular extensions get rejected for init-time violations.

> **"Open Bar" (February 2024):** Rejected for lifecycle violations including orphaned signal handlers and missing timeout cleanup in disable().

**Key lesson:** Lifecycle violations are the #1 rejection cause. Reviewers check every `enable()` resource has a matching `disable()` cleanup.

---

## Additional Lifecycle Requirements

### DBus Exported Interfaces

Extensions that export DBus interfaces (`Gio.DBusExportedObject.wrapJSObject` +
`.export()`, `connection.export_action_group()`, or `connection.export_menu_model()`)
must call the corresponding `.unexport()` / `unexport_action_group()` /
`unexport_menu_model()` in `disable()`. Exported interfaces that outlive `disable()`
remain on the bus and leak resources.

**Automatically checked by ego-lint (R-LIFE-16).**

### Timeout Removal Before Reassignment

When a timeout/idle ID is reassigned to a new timeout, the previous source must be
removed first via `GLib.Source.remove()`. Debounce patterns that directly overwrite
`this._timeoutId = GLib.timeout_add(...)` without first removing the old source
leak GLib sources.

```javascript
// WRONG: leaks the previous timeout
_onSettingsChanged() {
    this._debounceId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 300, () => {
        this._applySettings();
        return GLib.SOURCE_REMOVE;
    });
}

// CORRECT: remove before reassign
_onSettingsChanged() {
    if (this._debounceId)
        GLib.Source.remove(this._debounceId);
    this._debounceId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 300, () => {
        this._applySettings();
        return GLib.SOURCE_REMOVE;
    });
}
```

**Automatically checked by ego-lint (R-LIFE-17).**

### Subprocess Cancellation in disable()

Extensions that spawn subprocesses (`Gio.Subprocess`) must cancel or kill them in
`disable()` to prevent orphaned processes. Use `.force_exit()`, `.send_signal()`,
or a `Gio.Cancellable` that is cancelled in `disable()`.

> **Reviewer says:** "Don't forget to cancel the subprocess on destroy or disable."

**Automatically checked by ego-lint (R-LIFE-18).**

### Main.notify() Notification Sources

`Main.notify()` creates notification sources that should be tracked. If the extension
may create notifications during its lifetime, consider storing the source and destroying
it in `disable()` to prevent stale notifications.

### Signal Disconnection on Destroyed Objects

Signals on extension-owned objects that are `.destroy()`ed in `disable()` do not
strictly need explicit disconnection — destruction auto-disconnects. However, explicit
disconnection before destruction is preferred for reviewer clarity and avoids
accidental callbacks during teardown.

### GNOME 50 One-Shot Timeouts

`GLib.timeout_add_once()`, `GLib.idle_add_once()`, and
`GLib.timeout_add_seconds_once()` (new in GNOME 50) do **not** return a source ID,
meaning they cannot be cancelled with `GLib.Source.remove()`. Extensions using these
must use a `_destroyed` guard in the callback as the only way to prevent
use-after-disable:

```javascript
GLib.timeout_add_once(GLib.PRIORITY_DEFAULT, 500, () => {
    if (this._destroyed) return;  // Only protection available
    this._applyUpdate();
});
```
