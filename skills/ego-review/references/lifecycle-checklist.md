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
