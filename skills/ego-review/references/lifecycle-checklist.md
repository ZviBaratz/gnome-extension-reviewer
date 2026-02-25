# Lifecycle Checklist

Resource management is the single most common cause of EGO rejections. Every
resource created during `enable()` must be destroyed during `disable()`.

## Resource Creation/Destruction Table

| Resource Type | Create in enable() | Destroy in disable() | Pattern |
|---|---|---|---|
| Widgets / UI elements | `new St.Widget()`, `new PopupMenu.PopupMenuItem()` | `widget.destroy()` then `= null` | Destroy removes from parent and frees |
| GObject signal connections | `obj.connect('signal', handler)` | `obj.disconnect(id)` then `id = null` | Store returned ID for later disconnect |
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

## Common Lifecycle Mistakes

### Forgetting to null references
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
