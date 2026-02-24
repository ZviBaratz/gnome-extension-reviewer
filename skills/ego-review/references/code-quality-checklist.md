# Code Quality Checklist

EGO reviewers check for deprecated APIs, banned web patterns, and common
mistakes from AI-generated code. This checklist covers what they look for
and the correct replacements.

## Deprecated Modules and Their Replacements

These legacy modules are banned in GNOME 45+ extensions. Any use will be
rejected.

| Deprecated | Replacement | Removed In |
|---|---|---|
| `Mainloop` | `GLib.timeout_add()` / `GLib.Source.remove()` | GNOME 45 |
| `Mainloop.idle_add()` | `GLib.idle_add()` | GNOME 45 |
| `Lang` | ES6 classes (`class Foo extends Bar {}`) | GNOME 44 |
| `Lang.bind()` | Arrow functions or `Function.prototype.bind()` | GNOME 44 |
| `ByteArray` | `TextEncoder` / `TextDecoder` | GNOME 44 |
| `imports.*` syntax | ESM `import` syntax | GNOME 45 |
| `const Main = imports.ui.main` | `import * as Main from 'resource:///org/gnome/shell/ui/main.js'` | GNOME 45 |

### Import style (GNOME 45+)

```javascript
// WRONG: legacy imports
const { St, Clutter, GLib } = imports.gi;
const Main = imports.ui.main;
const ExtensionUtils = imports.misc.extensionUtils;

// CORRECT: ESM imports
import St from 'gi://St';
import Clutter from 'gi://Clutter';
import GLib from 'gi://GLib';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';
```

## Web API Ban List

GJS is not a browser. These web APIs do not exist or behave incorrectly:

| Banned | GJS Replacement | Notes |
|---|---|---|
| `setTimeout(fn, ms)` | `GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, fn)` | Callback must return `GLib.SOURCE_REMOVE` or `GLib.SOURCE_CONTINUE` |
| `setInterval(fn, ms)` | `GLib.timeout_add()` returning `GLib.SOURCE_CONTINUE` | Must store ID for cleanup |
| `clearTimeout(id)` | `GLib.Source.remove(id)` | Note: `GLib.Source.remove`, not `GLib.source_remove` |
| `clearInterval(id)` | `GLib.Source.remove(id)` | Same API as clearTimeout |
| `fetch(url)` | `Soup.Session` + `send_and_read_async` | Use libsoup3 for GNOME 45+ |
| `XMLHttpRequest` | `Soup.Session` | XHR does not exist in GJS |
| `Promise.race()` | Manual implementation or avoid | Check `_destroyed` after any await |
| `Promise.all()` | Acceptable with care | Guard: `results.length > 0 && results.every(...)` |
| `requestAnimationFrame` | `Clutter.Timeline` or `GLib.timeout_add` | No rAF in GJS |
| `document.*` / `window.*` | N/A | No DOM in GJS; use St/Clutter widgets |
| `localStorage` | `GSettings` or `GLib.get_user_data_dir()` | No localStorage in GJS |
| `JSON.parse(fetch(...))` | `Soup.Session` + `JSON.parse(decoder.decode(bytes))` | Combine network + parsing correctly |

### Timeout pattern comparison

```javascript
// WEB (wrong in GJS)
const id = setTimeout(() => doStuff(), 5000);
clearTimeout(id);

// GJS (correct)
const id = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 5000, () => {
    doStuff();
    return GLib.SOURCE_REMOVE; // One-shot; use SOURCE_CONTINUE for repeating
});
GLib.Source.remove(id);
```

## AI Code Detection Heuristics

EGO reviewers are trained to spot AI-generated code that uses imaginary APIs.
Common hallucination patterns:

### Imaginary APIs

- `Meta.Screen` -- does not exist; use `global.display` or `global.workspace_manager`
- `Shell.WindowTracker.get_default().get_active_window()` -- no such method; use `global.display.get_focus_window()`
- `Main.overview.toggle()` without checking `Main.overview.visible` first
- `St.Button.set_label()` -- correct method is `set_child()` with an `St.Label`
- `Clutter.Actor.set_position(x, y)` -- correct for Clutter, but wrong if applied to an St widget with layout manager
- `GLib.file_get_contents()` returning a string -- it returns `[ok, contents, length]`; contents is a `Uint8Array`

### Hallucinated imports

- `import Meta from 'gi://Meta'` in prefs.js -- Meta is not available in preferences context
- `import Shell from 'gi://Shell'` in prefs.js -- Shell is not available in preferences context
- `import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js'` in prefs.js -- UI modules are extension-only

### AI code telltale signs

- Overly verbose comments explaining obvious code (`// Loop through the array`)
- TypeScript-style JSDoc type annotations (`@param {string} name`)
- Methods that don't exist on GJS objects but exist in web APIs
- `try/catch` around every single line instead of logical blocks
- Unused imports at the top of the file

## Private API Documentation

Use of private (underscore-prefixed) properties on GNOME Shell objects is
sometimes unavoidable. Reviewers will flag it but may accept it with proper
documentation.

**Requirements for private API usage:**

1. Add a comment explaining WHY the private API is needed
2. State that no public alternative exists
3. Note which GNOME Shell versions were tested
4. Be prepared for breakage across GNOME versions

```javascript
// Private API: Main.panel.statusArea.quickSettings._indicators
// No public API exists for reordering Quick Settings indicators.
// Tested on GNOME 45, 46, 47, 48.
const indicators = Main.panel.statusArea.quickSettings._indicators;
```

**Common private APIs used by extensions:**

| Private API | Purpose | Public Alternative |
|---|---|---|
| `_indicators` | Quick Settings indicator reordering | None |
| `_delegate` | Accessing actor's owning object | None (use `connectObject` owner) |
| `_menus` | PopupMenu submenu access | `menu.box.get_children()` (partial) |

## Excessive Logging

EGO reviewers reject extensions with noisy logging. GNOME Shell's journal is
shared by all extensions and the shell itself.

| Method | Verdict | Use For |
|---|---|---|
| `console.log()` | **BANNED** | Do not use in production |
| `print()` | **BANNED** | Do not use (goes to stdout, not journal) |
| `log()` | **BANNED** | Deprecated global function |
| `console.debug()` | Acceptable | Operational messages (init, state changes) |
| `console.warn()` | Acceptable | Recoverable issues, deprecation notices |
| `console.error()` | Acceptable | Actual errors that need attention |

**Rule of thumb:** A reviewer should be able to enable the extension and see
zero journal output during normal operation. `console.debug` messages only
appear when the user explicitly enables debug output.

## Error Handling Patterns

### Async operations

Every `async` function and every `.then()` chain needs error handling:

```javascript
// CORRECT: try/catch around async
async _loadData() {
    try {
        const result = await this._fetchSomething();
        if (this._destroyed) return;
        this._processResult(result);
    } catch (e) {
        if (!this._destroyed)
            console.error('Failed to load data:', e.message);
    }
}
```

### File operations

```javascript
// CORRECT: handle missing files
_readConfig() {
    const file = Gio.File.new_for_path(path);
    try {
        const [ok, contents] = file.load_contents(null);
        return new TextDecoder().decode(contents);
    } catch (e) {
        if (e.matches(Gio.IOErrorEnum, Gio.IOErrorEnum.NOT_FOUND))
            return null; // File doesn't exist yet, that's OK
        console.error('Failed to read config:', e.message);
        return null;
    }
}
```

### D-Bus operations

```javascript
// CORRECT: handle proxy unavailability
_getProfile() {
    if (!this._proxy) {
        console.warn('D-Bus proxy not available');
        return null;
    }
    try {
        return this._proxy.ActiveProfile;
    } catch (e) {
        console.error('Failed to read profile:', e.message);
        return null;
    }
}
```

### Never swallow errors silently

```javascript
// WRONG: silent catch
try { riskyOperation(); } catch (e) { }

// WRONG: catch with only a comment
try { riskyOperation(); } catch (e) { /* ignore */ }

// CORRECT: at minimum log the error
try {
    riskyOperation();
} catch (e) {
    console.error('riskyOperation failed:', e.message);
}
```

## GObject Patterns

### Class registration

All GObject subclasses must use `GObject.registerClass`:

```javascript
const MyWidget = GObject.registerClass(
class MyWidget extends St.BoxLayout {
    constructor(params) {
        super(params);
        // property initialization only
    }
});
```

### Destroy chaining

Always chain the parent destroy method:

```javascript
destroy() {
    // Clean up own resources first
    if (this._timeoutId) {
        GLib.Source.remove(this._timeoutId);
        this._timeoutId = null;
    }

    // Then chain to parent
    super.destroy();
}
```

### Signal emission after property changes

When implementing custom GObject properties, emit `notify` after changes:

```javascript
set myProperty(value) {
    if (this._myProperty === value)
        return;
    this._myProperty = value;
    this.notify('my-property');
}
```

### connectObject for automatic cleanup

Always prefer `connectObject` over manual `connect` + stored IDs:

```javascript
// PREFERRED
someObject.connectObject(
    'notify::active-profile', () => this._onProfileChanged(),
    'notify::battery-level', () => this._onBatteryChanged(),
    this  // owner -- disconnectObject(this) cleans up all at once
);

// Cleanup: one call disconnects everything
someObject.disconnectObject(this);
```

## Preferences (prefs.js) Constraints

The preferences window runs in a separate process with a GTK4 context, not
the GNOME Shell process. This means:

- **No Shell imports** (`gi://Shell`, `gi://Meta`, `gi://St`, `gi://Clutter`)
- **No GNOME Shell UI imports** (`resource:///org/gnome/shell/ui/*`)
- **Use GTK4 + Adwaita** (`gi://Gtk`, `gi://Adw`)
- **Use `ExtensionPreferences`** base class, not `Extension`
- **GSettings** are accessed via `this.getSettings()` in the prefs class

```javascript
// prefs.js (GNOME 45+)
import Adw from 'gi://Adw';
import Gtk from 'gi://Gtk';
import { ExtensionPreferences } from
    'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class MyPrefs extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const settings = this.getSettings();
        // Build GTK4/Adw UI
    }
}
```
