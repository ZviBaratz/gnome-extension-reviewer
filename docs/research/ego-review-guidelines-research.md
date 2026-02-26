# EGO Review Guidelines - Comprehensive Research Document

**Date:** 2026-02-25
**Sources:** Official gjs.guide documentation, GNOME wiki archives, GNOME blog posts, community discussions
**Purpose:** Serve as a persistent reference for all GNOME Shell extension review requirements

---

## Table of Contents

1. [Initialization and Lifecycle](#1-initialization-and-lifecycle)
2. [Object and Resource Cleanup](#2-object-and-resource-cleanup)
3. [Signal Management](#3-signal-management)
4. [Main Loop Sources](#4-main-loop-sources)
5. [Library and Import Restrictions](#5-library-and-import-restrictions)
6. [Deprecated Modules](#6-deprecated-modules)
7. [Code Quality and Readability](#7-code-quality-and-readability)
8. [AI-Generated Code](#8-ai-generated-code)
9. [Metadata Requirements](#9-metadata-requirements)
10. [GSettings Schema Requirements](#10-gsettings-schema-requirements)
11. [Packaging and File Requirements](#11-packaging-and-file-requirements)
12. [Security and Privacy](#12-security-and-privacy)
13. [Subprocess and Script Requirements](#13-subprocess-and-script-requirements)
14. [Session Modes](#14-session-modes)
15. [Licensing and Attribution](#15-licensing-and-attribution)
16. [Content and Code of Conduct](#16-content-and-code-of-conduct)
17. [Functionality Requirements](#17-functionality-requirements)
18. [Extension System Interference](#18-extension-system-interference)
19. [CSS and Stylesheet Guidelines](#19-css-and-stylesheet-guidelines)
20. [Translations and i18n](#20-translations-and-i18n)
21. [Preferences (prefs.js)](#21-preferences-prefsjs)
22. [ESModules Migration (GNOME 45+)](#22-esmodules-migration-gnome-45)
23. [Version-Specific API Changes](#23-version-specific-api-changes)
24. [Monkey-Patching and InjectionManager](#24-monkey-patching-and-injectionmanager)
25. [Extension Class Structure](#25-extension-class-structure)
26. [Network Access and Data Sharing](#26-network-access-and-data-sharing)
27. [Development Tools and Linting](#27-development-tools-and-linting)
28. [Common Rejection Reasons Summary](#28-common-rejection-reasons-summary)
29. [Notification and Dialog Lifecycle](#29-notification-and-dialog-lifecycle)
30. [Search Provider Contract](#30-search-provider-contract)
31. [Accessibility Requirements](#31-accessibility-requirements)
32. [Sources](#32-sources)

---

## 1. Initialization and Lifecycle

### Three Core Principles (from official guidelines)

1. "Don't create or modify anything before `enable()` is called"
2. "Use `enable()` to create objects, connect signals and add main loop sources"
3. "Use `disable()` to cleanup anything done in `enable()`"

### Initialization Phase

| Requirement | Severity | Category |
|---|---|---|
| MUST NOT create objects during initialization (constructor/import time) | **MUST** (hard reject) | lifecycle |
| MUST NOT connect signals during initialization | **MUST** (hard reject) | lifecycle |
| MUST NOT add main loop sources during initialization | **MUST** (hard reject) | lifecycle |
| MUST NOT modify GNOME Shell during initialization | **MUST** (hard reject) | lifecycle |
| MAY create static data structures (RegExp, Map) | Allowed | lifecycle |
| MAY create instances of built-in JavaScript objects | Allowed | lifecycle |
| All GObject classes (Gio.Settings, St.Widget) are disallowed during init | **MUST** (hard reject) | lifecycle |

**Rationale:** Initialization occurs when `extension.js` is imported and the Extension class is constructed. Creating GObjects or connecting signals at this stage prevents proper cleanup and causes memory leaks, since `disable()` may never be called if the extension fails to enable.

**Code pattern (correct):**
```javascript
export default class MyExtension extends Extension {
    // Constructor: static resources ONLY
    // No GObject creation, no signal connections

    enable() {
        // All dynamic resource creation here
        this._settings = this.getSettings();
        this._indicator = new PanelMenu.Button(0.0, this.metadata.name, false);
    }

    disable() {
        // All cleanup here
        this._indicator?.destroy();
        this._indicator = null;
        this._settings = null;
    }
}
```

**Code pattern (REJECTED):**
```javascript
export default class MyExtension extends Extension {
    constructor(metadata) {
        super(metadata);
        // REJECTED: GObject creation in constructor
        this._settings = new Gio.Settings({schema_id: 'org.gnome.shell.extensions.example'});
        // REJECTED: Signal connection in constructor
        this._handlerId = global.display.connect('window-created', () => {});
    }
}
```

---

## 2. Object and Resource Cleanup

| Requirement | Severity | Category |
|---|---|---|
| Any objects/widgets created MUST be destroyed in `disable()` | **MUST** (hard reject) | lifecycle |
| All dynamically stored memory MUST be cleared in `disable()` | **MUST** (hard reject) | lifecycle |
| SHOULD NOT call `GObject.Object.run_dispose()` unless absolutely necessary | **SHOULD NOT** | lifecycle |
| If `run_dispose()` is used, MUST include comment explaining why | **MUST** (if used) | lifecycle |

**Rationale:** Undestroyed objects persist after the extension disables, causing memory leaks and potentially interfering with Shell operation. This is the **most common reason for rejection**.

**Correct cleanup pattern:**
```javascript
disable() {
    // Destroy widgets
    this._indicator?.destroy();
    this._indicator = null;

    // Clear data structures
    this._cache?.clear();
    this._cache = null;

    // Null out settings
    this._settings = null;
}
```

**Note on `run_dispose()`:** Generally unnecessary. Proper cleanup patterns (destroying widgets, disconnecting signals, removing sources) make `run_dispose()` avoidable. If absolutely necessary, a comment explaining the real-world situation that requires it is mandatory.

---

## 3. Signal Management

| Requirement | Severity | Category |
|---|---|---|
| Any signal connections MUST be disconnected in `disable()` | **MUST** (hard reject) | lifecycle |
| Handler IDs MUST be stored for later disconnection | **MUST** (hard reject) | lifecycle |
| Handler IDs SHOULD be verified before disconnecting | SHOULD | lifecycle |

**Rationale:** Orphaned signal connections cause memory leaks and can trigger callbacks on destroyed objects, leading to crashes.

**Correct pattern:**
```javascript
enable() {
    this._handlerId = global.display.connect('window-created', (display, window) => {
        // handle window creation
    });
}

disable() {
    if (this._handlerId) {
        global.display.disconnect(this._handlerId);
        this._handlerId = null;
    }
}
```

**For multiple signals, consider a tracking array or using `connectObject()`/`disconnectObject()` patterns where available.**

---

## 4. Main Loop Sources

| Requirement | Severity | Category |
|---|---|---|
| All main loop sources MUST be removed in `disable()` | **MUST** (hard reject) | lifecycle |
| Sources MUST be removed even if callback returns `GLib.SOURCE_REMOVE` | **MUST** (hard reject) | lifecycle |

**Rationale:** Lingering timers and idle sources consume resources and can execute callbacks on destroyed objects.

**Correct pattern:**
```javascript
enable() {
    this._sourceId = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 5, () => {
        // periodic task
        return GLib.SOURCE_CONTINUE;
    });
}

disable() {
    if (this._sourceId) {
        GLib.Source.remove(this._sourceId);
        this._sourceId = null;
    }
}
```

**Important:** Even if the callback returns `GLib.SOURCE_REMOVE` (or `false`), the source should still be tracked and removed in `disable()` because there is no guarantee the callback will have executed before `disable()` is called.

---

## 5. Library and Import Restrictions

### GNOME Shell Process (extension.js)

| Requirement | Severity | Category |
|---|---|---|
| MUST NOT import `Gdk` in Shell process | **MUST** (hard reject) | imports |
| MUST NOT import `Gtk` in Shell process | **MUST** (hard reject) | imports |
| MUST NOT import `Adw` in Shell process | **MUST** (hard reject) | imports |

**Rationale:** These libraries conflict with Clutter and Shell libraries and will crash GNOME Shell.

### Preferences Process (prefs.js)

| Requirement | Severity | Category |
|---|---|---|
| MUST NOT import `Clutter` in preferences | **MUST** (hard reject) | imports |
| MUST NOT import `Meta` in preferences | **MUST** (hard reject) | imports |
| MUST NOT import `St` in preferences | **MUST** (hard reject) | imports |
| MUST NOT import `Shell` in preferences | **MUST** (hard reject) | imports |

**Rationale:** These libraries conflict with Gtk and other libraries used in the preferences process and will crash the preferences window.

### Import Syntax (GNOME 45+)

```javascript
// GI Libraries
import GLib from 'gi://GLib';
import Gio from 'gi://Gio';
import St from 'gi://St';

// Versioned GI Libraries
import Soup from 'gi://Soup?version=3.0';
import Gtk from 'gi://Gtk?version=4.0';  // prefs.js only

// GNOME Shell modules (extension.js)
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';

// GNOME Shell modules (prefs.js) - different path!
import {ExtensionPreferences} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

// Extension-local modules
import * as MyModule from './myModule.js';

// Extension class
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
```

**Critical note:** Resource paths differ between extension.js and prefs.js contexts:
- Extension: `resource:///org/gnome/shell/...`
- Preferences: `resource:///org/gnome/Shell/Extensions/js/...`

---

## 6. Deprecated Modules

| Requirement | Severity | Category |
|---|---|---|
| MUST NOT import `ByteArray` (use TextDecoder/TextEncoder) | **MUST** (hard reject) | deprecated |
| MUST NOT import `Lang` (use ES6 classes) | **MUST** (hard reject) | deprecated |
| MUST NOT import `Mainloop` (use GLib or setTimeout/setInterval) | **MUST** (hard reject) | deprecated |
| MUST NOT use `imports.misc.extensionUtils` (use Extension class) | **MUST** (hard reject) | deprecated |

**Rationale:** Deprecated modules are unreliable, may be removed at any time, and indicate the extension has not been updated for current GNOME Shell versions.

**Migration examples:**

```javascript
// OLD (rejected): ByteArray
const ByteArray = imports.byteArray;
let str = ByteArray.toString(data);

// NEW: TextDecoder
let decoder = new TextDecoder();
let str = decoder.decode(data);

// OLD (rejected): Lang
const Lang = imports.lang;
var MyClass = new Lang.Class({...});

// NEW: ES6 class
class MyClass extends GObject.Object {...}

// OLD (rejected): Mainloop
const Mainloop = imports.mainloop;
Mainloop.timeout_add(1000, callback);

// NEW: GLib
GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1000, callback);
```

---

## 7. Code Quality and Readability

| Requirement | Severity | Category |
|---|---|---|
| Code MUST be readable and reviewable JavaScript | **MUST** (hard reject) | code-quality |
| Code MUST NOT be minified | **MUST** (hard reject) | code-quality |
| Code MUST NOT be obfuscated | **MUST** (hard reject) | code-quality |
| TypeScript MUST be transpiled to well-formatted JavaScript | **MUST** (hard reject) | code-quality |
| MUST NOT print excessively to log | **MUST** (hard reject) | code-quality |
| Log should contain only important messages and errors | **MUST** | code-quality |
| Specific code-style is NOT enforced | Informational | code-quality |
| Code MUST be formatted in a way that can be easily reviewed | **MUST** (hard reject) | code-quality |
| If codebase is too messy to properly review, MAY be rejected | **MAY** reject | code-quality |

**Rationale:** Unreadable code cannot be security reviewed. Excessive logging pollutes system journals and impacts performance. Reviewers need to understand what the code does to approve it.

**Logging best practices:**
- Use `console.log()` sparingly for important messages
- Use `console.error()` for errors
- Use `console.debug()` for development (remove before submission)
- Never log in tight loops or frequent callbacks
- Never log sensitive data

### Accessibility

Accessibility is **a hard requirement** for GNOME Shell extensions. Custom widgets MUST provide appropriate accessible roles, labels, and keyboard navigation. Extensions that introduce visual UI elements without accessibility support may be rejected. See [Section 31: Accessibility Requirements](#31-accessibility-requirements) for full details.

---

## 8. AI-Generated Code

| Requirement | Severity | Category |
|---|---|---|
| Extensions MUST NOT be submitted if primarily AI-generated | **MUST** (hard reject) | code-quality |
| Using AI as learning aid or code completion is permitted | Allowed | code-quality |
| Developers MUST be able to justify and explain submitted code | **MUST** | code-quality |

### AI Slop Rejection Triggers

The following patterns indicate AI-generated code and will trigger rejection:

1. **Large amounts of unnecessary code** - excessive boilerplate, redundant checks
2. **Inconsistent code style** - mixed conventions, formatting inconsistencies
3. **Imaginary API usage** - calling methods/properties that don't exist
4. **Comments serving as LLM prompts** - inline comments that read like instructions to an AI
5. **Excessive defensive programming** - unnecessary try-catch blocks, redundant type checks

### Specific AI Pattern Example (REJECTED)

```javascript
// REJECTED: AI slop - defensive programming overkill
destroy() {
    try {
        if (typeof super.destroy === 'function') {
            super.destroy();
        }
    } catch (e) {
        console.warn(`${e.message}`);
    }
}
```

**Correct version:**
```javascript
destroy() {
    super.destroy();
}
```

### Additional AI Slop Indicators

- Unnecessary `try-catch` wrapping straightforward operations
- Redundant type-checking before calling guaranteed parent methods
- `console.warn()` wrapping for basic function calls
- Excessive null/undefined guards where values are guaranteed
- Boilerplate comments explaining obvious code
- Inconsistent naming conventions within same file
- Methods that do nothing meaningful
- Copied patterns that don't apply to the context

**Rationale:** AI-generated code often contains non-functional patterns, imaginary APIs, and unnecessary complexity. The surge of AI-generated submissions created a "domino effect" where bad practices spread to other extensions, increasing the review backlog beyond 15,000 lines weekly.

**Source:** Blog post by Javad Rahmatzadeh (GNOME extension reviewer), December 2025.

---

## 9. Metadata Requirements

### metadata.json Required Fields

| Field | Format | Severity | Requirements |
|---|---|---|---|
| `uuid` | `extension-id@namespace` | **MUST** | Only numbers, letters, period, underscore, dash. MUST NOT use `gnome.org` as namespace. |
| `name` | String | **MUST** | Short descriptive string (e.g., "Click To Focus") |
| `description` | String | **MUST** | Single-sentence explanation. Supports `\n` and `\t`. |
| `shell-version` | Array of strings | **MUST** | Only stable releases. Max one development release. MUST NOT claim future versions. |
| `url` | URL string | **MUST** (for EGO) | Repository URL for code and issue tracking |

### metadata.json Optional Fields

| Field | Format | Requirements |
|---|---|---|
| `gettext-domain` | String | Conventionally matches UUID |
| `settings-schema` | String | Convention: `org.gnome.shell.extensions.<name>` |
| `session-modes` | Array of strings | Valid: `user`, `unlock-dialog`. MUST be dropped if only `user`. |
| `version` | Integer | Controlled by EGO website. Developers should not set. |
| `version-name` | String (1-16 chars) | Only letters, numbers, space, period. Regex: `/^(?!^[. ]+$)[a-zA-Z0-9 .]{1,16}$/` |
| `donations` | Object | Valid keys: `buymeacoffee`, `custom`, `github`, `kofi`, `liberapay`, `opencollective`, `patreon`, `paypal`. Max 3 array elements per key. MUST be dropped if not used. MUST only contain valid keys. |

### UUID Rules

| Requirement | Severity |
|---|---|
| MUST contain only numbers, letters, period, underscore, dash | **MUST** (hard reject) |
| MUST be in form `extension-id@namespace` (contains `@`) | **MUST** (hard reject) |
| MUST NOT use `gnome.org` as namespace (without GNOME Foundation permission) | **MUST** (hard reject) |
| Directory name MUST match UUID | **MUST** (hard reject) |

### shell-version Rules

| Requirement | Severity |
|---|---|
| MUST contain only stable GNOME Shell releases | **MUST** (hard reject) |
| MAY contain at most one development release | **MUST** |
| MUST NOT claim support for future versions | **MUST** (hard reject) |
| Format for GNOME 40+: major version only (e.g., `"45"`, `"46"`) | **MUST** |
| Format for GNOME 3.x: `"3.38"`, `"3.36"` etc. | **MUST** |
| ESM extensions (GNOME 45+) cannot support pre-45 versions | Constraint |

### Minimal Valid metadata.json

```json
{
    "uuid": "example@gjs.guide",
    "name": "Example Extension",
    "description": "An example extension",
    "shell-version": ["47"],
    "url": "https://github.com/example/example-extension"
}
```

---

## 10. GSettings Schema Requirements

| Requirement | Severity | Category |
|---|---|---|
| Schema ID MUST use `org.gnome.shell.extensions` as base | **MUST** (hard reject) | schema |
| Schema path MUST use `/org/gnome/shell/extensions/` as base | **MUST** (hard reject) | schema |
| Schema XML file MUST be included in extension ZIP | **MUST** (hard reject) | schema |
| Schema XML filename MUST follow `<schema-id>.gschema.xml` pattern | **MUST** (hard reject) | schema |
| Compiled schema (`gschemas.compiled`) SHOULD be included | SHOULD | schema |
| `settings-schema` key in metadata.json SHOULD match schema ID | SHOULD | schema |

**Rationale:** Malformed schemas break the preferences dialog and prevent users from configuring the extension.

**Correct schema structure:**
```
schemas/
  org.gnome.shell.extensions.example.gschema.xml
  gschemas.compiled
```

**Schema XML example:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<schemalist>
  <schema id="org.gnome.shell.extensions.example"
          path="/org/gnome/shell/extensions/example/">
    <key name="show-indicator" type="b">
      <default>true</default>
      <summary>Show indicator</summary>
      <description>Whether to show the panel indicator</description>
    </key>
  </schema>
</schemalist>
```

---

## 11. Packaging and File Requirements

| Requirement | Severity | Category |
|---|---|---|
| Extension MUST contain `extension.js` | **MUST** (hard reject) | packaging |
| Extension MUST contain `metadata.json` | **MUST** (hard reject) | packaging |
| SHOULD NOT include build/install scripts | SHOULD NOT | packaging |
| SHOULD NOT include `.po`/`.pot` translation source files | SHOULD NOT | packaging |
| SHOULD NOT include unused icons/images/media | SHOULD NOT | packaging |
| MAY be rejected for unreasonable amount of unnecessary data | **MAY** reject | packaging |
| MUST NOT include binary executables or libraries | **MUST** (hard reject) | packaging |

### Expected File Structure

```
extension-name@namespace/
  extension.js          (required)
  metadata.json         (required)
  prefs.js              (optional - preferences UI)
  stylesheet.css        (optional - custom styling)
  schemas/              (optional - GSettings)
    org.gnome.shell.extensions.name.gschema.xml
    gschemas.compiled
  locale/               (optional - translations)
    en/LC_MESSAGES/name.mo
    fr/LC_MESSAGES/name.mo
  icons/                (optional - custom icons)
  lib/                  (optional - helper modules)
```

### Files That Should NOT Be Included

- `Makefile`, `meson.build`, build scripts
- `.po`, `.pot` translation source files (only compiled `.mo` needed)
- `.git`, `.gitignore`, `.github/`
- `node_modules/`, `package.json`, `package-lock.json`
- `.eslintrc`, `tsconfig.json`
- `README.md`, `CHANGELOG.md` (harmless but unnecessary)
- Test files, development scripts
- Large unused images/media
- Binary executables or shared libraries

---

## 12. Security and Privacy

### Clipboard Access

| Requirement | Severity | Category |
|---|---|---|
| Extensions accessing clipboard MUST declare it in description | **MUST** (hard reject) | security |
| MUST NOT share clipboard data with third parties without explicit user interaction | **MUST** (hard reject) | security |
| MUST NOT ship with default keyboard shortcuts for clipboard interaction | **MUST** (hard reject) | security |

### Telemetry

| Requirement | Severity | Category |
|---|---|---|
| MUST NOT use telemetry tools to track users | **MUST** (hard reject) | security |
| MUST NOT share user data online | **MUST** (hard reject) | security |

### General Security

| Requirement | Severity | Category |
|---|---|---|
| Extensions are reviewed for malicious code and malware | Informational | security |
| Extensions are reviewed for security risks | Informational | security |
| Extensions are NOT reviewed for bugs | Informational | security |

---

## 13. Subprocess and Script Requirements

| Requirement | Severity | Category |
|---|---|---|
| Spawning privileged subprocesses SHOULD be avoided | **SHOULD NOT** | security |
| If necessary, privileged subprocess MUST use `pkexec` | **MUST** (hard reject) | security |
| Privileged subprocess MUST NOT be user-writable executable or script | **MUST** (hard reject) | security |
| Scripts MUST be written in GJS unless absolutely necessary | **MUST** | scripts |
| MUST NOT include binary executables or libraries | **MUST** (hard reject) | scripts |
| Processes MUST be spawned carefully and exit cleanly | **MUST** | scripts |
| Scripts MUST be distributed under OSI-approved license | **MUST** | scripts |
| Python, HTML, web JS modules are out of scope for review | Informational | scripts |
| MAY install modules from pip/npm/yarn requiring explicit user action | Allowed | scripts |

**Rationale:** User-writable privileged executables enable privilege escalation attacks. Historical vulnerabilities in `pkexec` (CVE-2021-4034 "PwnKit") demonstrate the risk.

---

## 14. Session Modes

### Available Modes

| Mode | Description |
|---|---|
| `user` | Standard mode when user is logged in and active (default) |
| `unlock-dialog` | Active when screen is locked |
| `gdm` | Login screen (GDM) |

### Requirements for `unlock-dialog`

| Requirement | Severity | Category |
|---|---|---|
| Using `unlock-dialog` MUST be necessary for correct operation | **MUST** (hard reject) | session-modes |
| All keyboard event signals MUST be disconnected in lock screen mode | **MUST** (hard reject) | session-modes |
| `disable()` function MUST include comment explaining why used | **MUST** (hard reject) | session-modes |
| Extensions MUST NOT disable selectively | **MUST** (hard reject) | session-modes |
| `session-modes` field MUST be dropped if only using `user` | **MUST** (hard reject) | metadata |

**Rationale:** Lock screen access poses security risks. Keyboard event signals on the lock screen could be used for keylogging or bypassing the lock screen.

**Mode transition handling:**
```javascript
enable() {
    this._sessionId = Main.sessionMode.connect('updated',
        this._onSessionModeChanged.bind(this));
}

_onSessionModeChanged() {
    // Check current mode and adapt behavior
    if (Main.sessionMode.currentMode === 'unlock-dialog') {
        // Disable keyboard listeners, hide sensitive UI
    }
}

disable() {
    if (this._sessionId) {
        Main.sessionMode.disconnect(this._sessionId);
        this._sessionId = null;
    }
}
```

**Important:** Extensions must be prepared to handle `disable()` being called at any time without errors. When checking the current mode, verify both `currentMode` and `parentMode` since custom modes may inherit from `user`.

---

## 15. Licensing and Attribution

| Requirement | Severity | Category |
|---|---|---|
| MUST be distributed under terms compatible with GPL-2.0-or-later | **MUST** (hard reject) | licensing |
| If containing code from other extensions, MUST include original author attribution | **MUST** (hard reject) | licensing |
| Attribution MUST be in distributed files (not just repo) | **MUST** (hard reject) | licensing |

**Rationale:** GNOME Shell is licensed under GPL-2.0-or-later. Extensions that are not GPL-compatible cannot be distributed through EGO. Unattributed derivative code violates the GPL and is a license violation.

**Compatible licenses include:** GPL-2.0-or-later, GPL-3.0-or-later, LGPL-2.1-or-later, MIT (with dual-licensing), BSD (with dual-licensing).

---

## 16. Content and Code of Conduct

| Requirement | Severity | Category |
|---|---|---|
| MUST NOT violate GNOME Code of Conduct in name, description, text, icons, emojis, screenshots | **MUST** (hard reject) | content |
| MUST NOT promote national or international political agendas | **MUST** (hard reject) | content |
| MUST NOT include copyrighted content without express permission | **MUST** (hard reject) | content |
| MUST NOT include trademarked content without express permission | **MUST** (hard reject) | content |
| Forbidden: brand names/phrases, logos/artwork, audio/video/multimedia | **MUST** (hard reject) | content |

**Rationale:** Code of Conduct violations can harm vulnerable community members. Political content may be criminal to access in some jurisdictions. Copyright/trademark violations expose GNOME Foundation to legal liability.

---

## 17. Functionality Requirements

| Requirement | Severity | Category |
|---|---|---|
| Extensions that are fundamentally broken MUST be rejected | **MUST** (hard reject) | functionality |
| Extensions with no purpose or functionality MUST be rejected | **MUST** (hard reject) | functionality |
| Extensions MAY be approved with broken non-critical features | Informational | functionality |
| Extensions are NOT tested for bugs during review | Informational | functionality |

**Rationale:** Non-functional extensions provide no value to users and waste reviewer time.

---

## 18. Extension System Interference

| Requirement | Severity | Category |
|---|---|---|
| Modifying, reloading, or interacting with other extensions is generally discouraged | **GENERALLY** discouraged | extension-system |
| Case-by-case review; may be rejected at reviewer discretion | **MAY** reject | extension-system |

**Rationale:** Extension isolation ensures that one extension's behavior doesn't break others. Interfering with the extension system can cause cascading failures.

---

## 19. CSS and Stylesheet Guidelines

### stylesheet.css Scope

- Applies ONLY to GNOME Shell and extensions (Clutter/St widgets)
- Does NOT apply to preferences window or other GTK applications
- Loaded automatically when present in the extension directory

### Supported Selectors

- Element selectors: `StLabel`, `StButton`, `StBoxLayout`
- Class selectors: `.my-extension-class`
- GType name selectors (for custom GObject subclasses with `GTypeName`)

### Best Practices (not explicitly in guidelines but implicit)

| Practice | Severity | Category |
|---|---|---|
| Use unique class names prefixed with extension name to avoid conflicts | SHOULD | css |
| Avoid styling global Shell elements without scoping | SHOULD | css |
| Avoid `!important` except when necessary to override Shell theme | SHOULD | css |
| Keep CSS minimal and relevant | SHOULD | css |

---

## 20. Translations and i18n

### Setup Requirements

| Requirement | Severity | Category |
|---|---|---|
| Set `gettext-domain` in metadata.json (recommended method) | SHOULD | i18n |
| Compiled `.mo` files go in `locale/<lang>/LC_MESSAGES/` directory | MUST (if using translations) | i18n |
| Source `.po`/`.pot` files should NOT be included in zip | SHOULD NOT | packaging |

### Translation Functions

```javascript
// In extension.js
import {Extension, gettext as _} from 'resource:///org/gnome/shell/extensions/extension.js';

// In prefs.js
import {ExtensionPreferences, gettext as _} from
    'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

// Usage
_('Translatable string')                    // gettext
ngettext('%d item', '%d items', count)       // plural forms
pgettext('context', 'Ambiguous string')      // contextual
_('You have %d notifications').format(count) // interpolation
```

### GNOME 45+ Changes

- `initTranslations()` is deprecated; use `gettext-domain` in metadata.json instead
- Translation functions are exported from the Extension module
- Use `String.prototype.format()` for string interpolation (not template literals for translatable strings)

---

## 21. Preferences (prefs.js)

### Structure Requirements

| Requirement | Severity | Category |
|---|---|---|
| MUST extend `ExtensionPreferences` class | **MUST** | preferences |
| MUST implement `fillPreferencesWindow()` or `getPreferencesWidget()` | **MUST** | preferences |
| MUST use GTK4 and Adwaita (not GTK3) | **MUST** (hard reject) | preferences |
| MUST NOT import Shell, Clutter, Meta, St | **MUST** (hard reject) | preferences |
| Preferences run in separate process from Shell | Informational | preferences |
| SHOULD follow GNOME Human Interface Guidelines | SHOULD | preferences |

### Async Preferences (GNOME 47+)

Starting with GNOME 47, `fillPreferencesWindow()` and `getPreferencesWidget()` are `await`-ed by the extension system. This means these methods can be declared `async` and use `await` internally (e.g., for loading resources or fetching settings asynchronously). Extensions targeting GNOME 47+ can take advantage of this to perform async initialization in their preferences window setup without blocking the UI.

### Correct Pattern

```javascript
import Gio from 'gi://Gio';
import Adw from 'gi://Adw';
import {ExtensionPreferences, gettext as _} from
    'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class MyExtensionPreferences extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const settings = this.getSettings();

        const page = new Adw.PreferencesPage({
            title: _('General'),
            icon_name: 'dialog-information-symbolic',
        });

        const group = new Adw.PreferencesGroup({
            title: _('Appearance'),
        });

        const row = new Adw.SwitchRow({
            title: _('Show Indicator'),
        });

        settings.bind('show-indicator', row, 'active',
            Gio.SettingsBindFlags.DEFAULT);

        group.add(row);
        page.add(group);
        window.add(page);
    }
}
```

---

## 22. ESModules Migration (GNOME 45+)

### Mandatory Changes

GNOME 45 introduced a mandatory shift from the legacy `imports.*` system to standard ECMAScript Modules (ESM). This is the single largest breaking change in GNOME Shell extension history.

### Import Migration Reference

| Old Pattern | New Pattern |
|---|---|
| `const GLib = imports.gi.GLib;` | `import GLib from 'gi://GLib';` |
| `imports.gi.versions.Soup = '3.0'; const Soup = imports.gi.Soup;` | `import Soup from 'gi://Soup?version=3.0';` |
| `const Main = imports.ui.main;` | `import * as Main from 'resource:///org/gnome/shell/ui/main.js';` |
| `const Me = imports.misc.extensionUtils.getCurrentExtension();` | `import {Extension} from '...extension.js';` then `Extension.lookupByURL(import.meta.url)` |
| `const MyModule = Me.imports.MyModule;` | `import * as MyModule from './MyModule.js';` |

### Extension Class Migration

```javascript
// OLD (pre-45, REJECTED for GNOME 45+)
function init() { }
function enable() { }
function disable() { }

// NEW (GNOME 45+)
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class MyExtension extends Extension {
    enable() { }
    disable() { }
}
```

### Key Constraints

| Constraint | Detail |
|---|---|
| ESM files cannot be loaded by pre-45 GNOME Shell | Must upload separate versions for pre/post-45 |
| `import`/`export` statements are only valid in modules | Cannot mix ESM and legacy imports |
| `shell-version` should only contain `"45"` or later | Remove old versions from metadata |
| `Extension` and `ExtensionPreferences` MUST be default exports | `export default class ...` |

### GNOME 45 Additional Changes

- `log()` is now alias for `console.log()`; adopt `console.*` methods
- `Meta.Rectangle` replaced with `Mtk.Rectangle` (alias provided)
- Use `Clutter.Event` getters instead of direct field access
- New `SearchController.addProvider()`/`removeProvider()` methods
- `Panel.toggleAppMenu()` removed; `Panel.toggleQuickSettings()` added
- New `animationUtils` module: `wiggle()`, `adjustAnimationTime()`

---

## 23. Version-Specific API Changes

### GNOME 46

| Change | Migration |
|---|---|
| `MessageTray.NotificationBanner` removed | Use alternative notification APIs |
| `BlurEffect.sigma` property changed | Check current API |
| `Meta.later_add`/`Meta.later_remove` deprecated | Use alternative scheduling |

### GNOME 47

| Change | Migration |
|---|---|
| Various internal class restructuring | Check GNOME Shell source |

### GNOME 48

| Change | Migration |
|---|---|
| `.vertical` property deprecated | Use `orientation: Clutter.Orientation.VERTICAL` |
| `Clutter.Image` removed | Use `St.ImageContent` |
| `Meta.disable_unredirect_for_display` moved | Use `Meta.Compositor.disable_unredirect` |
| `Meta.enable_unredirect_for_display` moved | Use `Meta.Compositor.enable_unredirect` |
| `Meta.get_window_actors` moved | Use `Meta.Compositor.get_window_actors` |
| `Meta.get_window_group_for_display` moved | Use `Meta.Compositor.get_window_group` |
| `Meta.get_top_window_group_for_display` moved | Use `Meta.Compositor.get_top_window_group` |
| `Meta.CursorTracker.get_for_display()` removed | Use `global.backend.get_cursor_tracker()` |
| `Clutter.Stage.get_key_focus()` returns null (not stage) when no focus | Update null checks |
| `Shell.SnippetHook.FRAGMENT` moved | Use `Cogl.SnippetHook.FRAGMENT` |
| `NotificationMessage` moved from calendar.js to messageList.js | Update import path |
| `InputSourceManager._switchInputSource` signature changed | Added `event` parameter |
| WindowManager methods gained `event` parameter | Update method signatures |
| New `ExtensionBase.getLogger()` method | Use for structured logging |
| CSS class `.quick-menu-toggle` renamed | Use `.quick-toggle-has-menu` |

#### `getLogger()` (GNOME 48+)

GNOME 48 introduces `ExtensionBase.getLogger()`, which returns a structured logger scoped to the extension. This replaces ad-hoc `console.log()` calls with a logger that automatically prefixes messages with the extension name. Usage:

```javascript
export default class MyExtension extends Extension {
    enable() {
        this._logger = this.getLogger();
        this._logger.message('Extension enabled');  // prefixed with extension name
    }
}
```

The logger supports `message()`, `warning()`, and `critical()` methods. Extensions targeting GNOME 48+ SHOULD prefer `getLogger()` over raw `console.*` calls for better log hygiene.

#### QuickMenuToggle CSS Rename (GNOME 48+)

The CSS class `.quick-menu-toggle` was renamed to `.quick-toggle-has-menu` in GNOME 48. Extensions that style QuickSettings toggles with menus must update their stylesheets:

```css
/* GNOME 47 and earlier */
.quick-menu-toggle { ... }

/* GNOME 48+ */
.quick-toggle-has-menu { ... }
```

This is a **blocking** change — the old class no longer matches any element, so styles silently stop working. Automated check: R-VER48-07.

### GNOME 49

| Change | Migration |
|---|---|
| `Meta.Rectangle` fully removed (alias dropped) | Use `Mtk.Rectangle` |
| `Clutter.ClickAction`/`Clutter.TapAction` changes | Check current API |
| `Window.maximize()` signature changed | Use `set_maximize_flags()` then `maximize()` |
| `CursorTracker.set_pointer_visible` changes | Check current API |
| `AppMenuButton` removed from panel.js | No replacement — was unused since GNOME 43 |
| Gesture API migration | Check updated `Clutter.GestureAction` subclasses |

#### `maximize()` Signature Change (GNOME 49+)

In GNOME 49, `Meta.Window.maximize()` lost the `MaximizeFlags` parameter. Code that passes `Meta.MaximizeFlags.BOTH` (or similar) to `maximize()` will throw a type error.

```javascript
// GNOME 48 and earlier
window.maximize(Meta.MaximizeFlags.BOTH);

// GNOME 49+
window.set_maximize_flags(Meta.MaximizeFlags.BOTH);
window.maximize();
```

Automated check: R-VER49-08.

#### AppMenuButton Removal (GNOME 49+)

`AppMenuButton` has been fully removed from `panel.js` in GNOME 49. It was deprecated since GNOME 43 and was a no-op, but extensions that reference it (e.g., `Main.panel.statusArea.AppMenuButton`) will throw. There is no direct replacement — the app menu functionality was moved to the window header bar.

Automated check: R-VER49-09.

---

## 24. Monkey-Patching and InjectionManager

### Overview

Extensions work by patching GNOME Shell at runtime ("monkey-patching"). Two approaches exist:

1. **Non-invasive** (preferred): Adding new UI elements (buttons, menu items) without modifying existing code. Lower breakage risk.
2. **Invasive**: Replacing or modifying existing Shell methods. Higher breakage risk but enables more functionality.

### InjectionManager (Recommended)

The `InjectionManager` class provides safe method overriding with automatic restoration.

```javascript
import {InjectionManager} from 'resource:///org/gnome/shell/extensions/extension.js';

export default class MyExtension extends Extension {
    enable() {
        this._injectionManager = new InjectionManager();

        // Override a method
        this._injectionManager.overrideMethod(
            SomeClass.prototype,
            'someMethod',
            originalMethod => {
                return function (...args) {
                    // Custom behavior before
                    const result = originalMethod.call(this, ...args);
                    // Custom behavior after
                    return result;
                };
            }
        );
    }

    disable() {
        // Restores ALL overridden methods
        this._injectionManager.clear();
        this._injectionManager = null;
    }
}
```

### Key InjectionManager Methods

| Method | Purpose |
|---|---|
| `overrideMethod(prototype, methodName, createOverrideFunc)` | Replace a method |
| `restoreMethod(prototype, methodName)` | Restore single method |
| `clear()` | Restore all methods at once |

### Arrow Functions vs Function Expressions

This is a subtle but critical distinction when patching:

- **Arrow functions** capture `this` from the enclosing scope (the extension instance)
- **Function expressions** create their own `this` binding (the object being patched)

```javascript
// Arrow: `this` is the extension
this._injectionManager.overrideMethod(Panel.prototype, 'toggleCalendar',
    originalMethod => {
        return (...args) => {
            console.debug(`${this.metadata.name}: toggling`); // this = extension
            originalMethod.call(Main.panel, ...args);
        };
    });

// Function expression: `this` is the Panel instance
this._injectionManager.overrideMethod(Panel.prototype, 'toggleQuickSettings',
    originalMethod => {
        const metadata = this.metadata; // capture before
        return function (...args) {
            console.debug(`${metadata.name}: toggling`);
            originalMethod.call(this, ...args); // this = Panel
        };
    });
```

### Cleanup Requirement

All monkey patches MUST be restored in `disable()`. Using `InjectionManager.clear()` is the recommended approach as it handles all restorations atomically.

---

## 25. Extension Class Structure

### Required Exports

```javascript
// extension.js - MUST be default export
export default class MyExtension extends Extension {
    enable() { /* ... */ }
    disable() { /* ... */ }
}

// prefs.js - MUST be default export
export default class MyPreferences extends ExtensionPreferences {
    fillPreferencesWindow(window) { /* ... */ }
}
```

### Extension Base Properties and Methods

| Property/Method | Type | Description |
|---|---|---|
| `this.uuid` | `string` | Extension UUID |
| `this.metadata` | `object` | metadata.json contents |
| `this.dir` | `Gio.File` | Extension directory |
| `this.path` | `string` | Extension directory path |
| `this.getSettings(schema?)` | `Gio.Settings` | Load GSettings |
| `this.openPreferences()` | `void` | Open preferences dialog |
| `this.initTranslations(domain?)` | `void` | Initialize gettext (deprecated) |
| `Extension.lookupByUUID(uuid)` | `Extension` | Static: find by UUID |
| `Extension.lookupByURL(url)` | `Extension` | Static: find by import.meta.url |

---

## 26. Network Access and Data Sharing

| Requirement | Severity | Category |
|---|---|---|
| Network access is permitted but subject to review | Informational | security |
| Content accessed/served MUST NOT violate Code of Conduct | **MUST** (hard reject) | security |
| Clipboard data MUST NOT be shared with third parties without explicit user interaction | **MUST** (hard reject) | security |
| User data MUST NOT be shared online (telemetry prohibition) | **MUST** (hard reject) | security |

**Note:** Extensions that make network requests (using `Soup`, `Gio.SocketClient`, etc.) are permitted but will receive extra scrutiny during review for data exfiltration and privacy concerns.

---

## 27. Development Tools and Linting

### ESLint Configuration

The GNOME Shell project provides official ESLint configurations:
- `plugin:gjs/extension` - for extension code
- `plugin:gjs/application` - for standalone GJS apps

### Recommended ESLint Rules

From GNOME Shell's ESLint config:
- `array-callback-return`
- `no-await-in-loop`
- `no-constant-binary-expression`
- `no-constructor-return`
- `no-new-native-nonconstructor`
- `no-promise-executor-return`
- `no-self-compare`
- `no-template-curly-in-string`
- `no-unmodified-loop-condition`
- `no-unreachable-loop`
- `no-unused-private-class-members`
- `no-use-before-define`

### TypeScript

TypeScript is permitted but MUST be transpiled to well-formatted, readable JavaScript before submission. The transpiled output is what reviewers will review.

---

## 28. Common Rejection Reasons Summary

Ordered roughly by frequency (based on reviewer discussions and guidelines):

| # | Reason | Category | Severity |
|---|---|---|---|
| 1 | Not undoing `enable()` work in `disable()` (signals, objects, sources) | lifecycle | **MUST** |
| 2 | AI-generated code patterns | code-quality | **MUST** |
| 3 | Importing GTK/Gdk/Adw in Shell process | imports | **MUST** |
| 4 | Importing Clutter/Meta/St/Shell in preferences | imports | **MUST** |
| 5 | Using deprecated modules (ByteArray, Lang, Mainloop) | deprecated | **MUST** |
| 6 | Minified or obfuscated code | code-quality | **MUST** |
| 7 | Excessive logging | code-quality | **MUST** |
| 8 | Malformed metadata.json (bad UUID, invalid shell-version) | metadata | **MUST** |
| 9 | Malformed GSettings schemas | schema | **MUST** |
| 10 | Creating objects in constructor/init | lifecycle | **MUST** |
| 11 | Including binary executables | packaging | **MUST** |
| 12 | Undeclared clipboard access | security | **MUST** |
| 13 | Telemetry or user tracking | security | **MUST** |
| 14 | License violations (non-GPL-compatible, missing attribution) | licensing | **MUST** |
| 15 | Copyright/trademark violations | content | **MUST** |
| 16 | Code of Conduct violations | content | **MUST** |
| 17 | Political content | content | **MUST** |
| 18 | No functionality or fundamentally broken | functionality | **MUST** |
| 19 | User-writable privileged executables | security | **MUST** |
| 20 | Excessive unnecessary files in package | packaging | **MAY** |
| 21 | Code too messy to review | code-quality | **MAY** |
| 22 | `session-modes` violations (unnecessary unlock-dialog) | session-modes | **MUST** |

---

## 29. Notification and Dialog Lifecycle

### MessageTray.Source Patterns

Extensions that create notifications MUST manage `MessageTray.Source` lifecycle correctly. Each notification source MUST connect to its own `destroy` signal for safe cleanup and potential reuse.

| Requirement | Severity | Category |
|---|---|---|
| Notification sources MUST be destroyed in `disable()` | **MUST** | lifecycle |
| MUST connect to `destroy` signal on Source for safe reuse | **MUST** | lifecycle |
| MUST NOT hold stale references to destroyed sources | **MUST** | lifecycle |

**Correct pattern:**
```javascript
enable() {
    this._source = new MessageTray.Source({
        title: this.metadata.name,
        iconName: 'dialog-information-symbolic',
    });
    this._source.connect('destroy', () => {
        this._source = null;
    });
    Main.messageTray.add(this._source);
}

disable() {
    this._source?.destroy();
    this._source = null;
}
```

### Dialog Lifecycle States

Modal dialogs in GNOME Shell transition through defined lifecycle states. Extensions that create dialogs MUST respect these states to avoid crashes or UI freezes.

| State | Constant | Meaning |
|---|---|---|
| `OPENED` | `ModalDialog.State.OPENED` | Dialog is fully visible and interactive |
| `CLOSED` | `ModalDialog.State.CLOSED` | Dialog is fully closed and destroyed |
| `OPENING` | `ModalDialog.State.OPENING` | Transition animation in progress (opening) |
| `CLOSING` | `ModalDialog.State.CLOSING` | Transition animation in progress (closing) |
| `FADED_OUT` | `ModalDialog.State.FADED_OUT` | Dialog has faded out but is not yet destroyed |

Extensions MUST NOT interact with dialogs in transitional states (`OPENING`, `CLOSING`). Attempting to close or destroy a dialog during `OPENING` or operate on a dialog in `FADED_OUT` state leads to undefined behavior.

---

## 30. Search Provider Contract

Extensions that implement search providers MUST follow the `SearchProvider` interface contract. Search providers are registered with the Shell's search system and have strict lifecycle requirements.

### Required Interface

| Method/Property | Contract |
|---|---|
| `get id()` | MUST return the extension UUID |
| `get appInfo()` | MUST return `null` (extension search providers are not apps) |
| `canLaunchSearch` | MUST return `false` unless the extension provides a dedicated search UI |
| `getInitialResultSet(terms, cancellable)` | Return initial results for search terms |
| `getSubsearchResultSet(previousResults, terms, cancellable)` | Refine previous results |
| `getResultMetas(ids, cancellable)` | Return metadata for result IDs |
| `activateResult(id, terms)` | Handle result activation |
| `createIcon(size)` | Create icon at given size; MUST account for display scaling factor |

### Lifecycle

| Requirement | Severity | Category |
|---|---|---|
| MUST register provider in `enable()` | **MUST** | lifecycle |
| MUST unregister provider in `disable()` | **MUST** | lifecycle |
| MUST NOT hold references to Shell objects after `disable()` | **MUST** | lifecycle |

**Correct pattern:**
```javascript
enable() {
    this._provider = new MySearchProvider(this);
    Main.overview.searchController.addProvider(this._provider);
}

disable() {
    Main.overview.searchController.removeProvider(this._provider);
    this._provider = null;
}
```

### Icon Scaling

`createIcon(size)` receives the logical icon size. The implementation MUST account for the display scaling factor when creating icons from custom sources (e.g., cairo surfaces, pixel buffers). Standard `Gio.Icon` implementations handle scaling automatically.

---

## 31. Accessibility Requirements

Accessibility is a hard requirement for GNOME Shell extensions. Extensions that introduce custom UI elements MUST provide proper accessibility support.

### Requirements

| Requirement | Severity | Category |
|---|---|---|
| Custom widgets MUST set `accessible-role` | **MUST** | accessibility |
| Interactive elements MUST have `accessible-name` or `label-actor` | **MUST** | accessibility |
| Dynamic state changes MUST be reflected in `Atk.StateType` | **MUST** | accessibility |
| All interactive UI MUST be keyboard-navigable | **MUST** | accessibility |
| Focus order MUST be logical and predictable | **MUST** | accessibility |
| MUST NOT rely solely on color to convey information | **MUST** | accessibility |
| Custom containers MUST implement proper focus chain | **MUST** | accessibility |

### accessible-role

Every custom widget that is not a standard GTK/St widget MUST declare its role using the `accessible-role` property from `Atk.Role`:

```javascript
const myButton = new St.Button({
    style_class: 'my-custom-button',
    accessible_role: Atk.Role.PUSH_BUTTON,
    accessible_name: _('Toggle feature'),
});
```

### label-actor Relationships

When a label visually describes another widget, the relationship MUST be declared so screen readers can associate them:

```javascript
const label = new St.Label({text: _('Volume')});
const slider = new Slider.Slider(0.5);
slider.accessible_name = label.text;
```

### Atk.StateType Synchronization

If a custom widget has dynamic state (e.g., toggled, expanded, selected), the accessible state MUST be synchronized:

```javascript
this._button.connect('clicked', () => {
    this._active = !this._active;
    this._button.add_accessible_state(
        this._active ? Atk.StateType.CHECKED : Atk.StateType.ENABLED
    );
});
```

### Keyboard Navigation

All interactive elements MUST be reachable via Tab/Shift+Tab and activatable via Enter/Space. Custom containers that manage their own children MUST implement `vfunc_navigate_focus()` or use `St.Widget`'s built-in focus management with `can_focus: true`.

---

## 32. Sources

### Primary Official Sources

1. [GNOME Shell Extensions Review Guidelines](https://gjs.guide/extensions/review-guidelines/review-guidelines.html) - The authoritative review guidelines document
2. [Anatomy of an Extension](https://gjs.guide/extensions/overview/anatomy.html) - File structure and metadata.json specification
3. [Creating Extensions](https://gjs.guide/extensions/development/creating.html) - Extension creation requirements
4. [Extension Class (ESModule)](https://gjs.guide/extensions/topics/extension.html) - Extension class API and InjectionManager
5. [Preferences](https://gjs.guide/extensions/development/preferences.html) - Preferences dialog requirements
6. [Translations](https://gjs.guide/extensions/development/translations.html) - i18n requirements
7. [Session Modes](https://gjs.guide/extensions/topics/session-modes.html) - Session mode specification
8. [Imports and Modules](https://gjs.guide/extensions/overview/imports-and-modules.html) - ESModules import system
9. [Updates and Breakage](https://gjs.guide/extensions/overview/updates-and-breakage.html) - API stability and monkey-patching

### Migration Guides

10. [Port Extensions to GNOME Shell 45](https://gjs.guide/extensions/upgrading/gnome-shell-45.html) - ESModules migration
11. [Port Extensions to GNOME Shell 48](https://gjs.guide/extensions/upgrading/gnome-shell-48.html) - GNOME 48 API changes

### Blog Posts and Discussions

12. [AI and GNOME Shell Extensions](https://blogs.gnome.org/jrahmatzadeh/2025/12/06/ai-and-gnome-shell-extensions/) - Javad Rahmatzadeh's blog post on AI code rejection policy
13. [Extensions in GNOME 45](https://blogs.gnome.org/shell-dev/2023/09/02/extensions-in-gnome-45/) - ESModules announcement
14. [No AI Slops! GNOME Now Forbids Vibe Coded Extensions](https://itsfoss.com/news/no-ai-extension-gnome/) - Coverage of AI policy
15. [GNOME Will Reject Shell Extensions With AI-Generated Code](https://linuxiac.com/gnome-will-reject-shell-extensions-with-ai-generated-code/) - Additional AI policy coverage

### Wiki Archives

16. [Projects/GnomeShell/Extensions/Review](https://wiki.gnome.org/Projects/GnomeShell/Extensions/Review) - GNOME Wiki review page (redirects to gjs.guide)
17. [Projects/GnomeShell/Extensions/ExtensionsGuidelines](https://wiki.gnome.org/Projects/GnomeShell/Extensions/ExtensionsGuidelines) - GNOME Wiki extension guidelines

### ESLint and Tooling

18. [GJS Style Guide](https://gjs.guide/guides/gjs/style-guide.html) - Official GJS style guide
19. [eslint-plugin-gjs](https://www.npmjs.com/package/eslint-plugin-gjs) - GJS ESLint plugin
20. [GNOME Shell ESLint rules](https://codeberg.org/kiyui/gjs-eslintrc) - Mirror of GNOME Shell's ESLint config

### Community Resources

21. [Requirements and tips for getting your GNOME Shell Extension approved](https://blog.mecheye.net/2012/02/requirements-and-tips-for-getting-your-gnome-shell-extension-approved/) - Classic tips post (older but still relevant for fundamentals)
22. [GNOME Discourse Extensions Tag](https://discourse.gnome.org/tag/extensions) - Community discussion forum
