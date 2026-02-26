# Phase 1: Gold-Standard Extension Patterns

**Date:** 2026-02-26
**Method:** Web research across GitHub, GitLab, DeepWiki, gjs.guide, GNOME Discourse, extensions.gnome.org review pages, and developer blog posts. Analyzed architecture, lifecycle management, signal handling, settings patterns, preferences structure, error handling, import conventions, widget lifecycle, and metadata usage across 5 popular, reviewer-approved GNOME Shell extensions.
**Complementary to:** `ego-review-guidelines-research.md` (formal requirements), `phase1-discourse-findings.md` (rejection patterns), `phase1-guidelines-deep-read.md` (MUST/SHOULD extraction)

---

## Section 1: Extension Profiles

### 1. AppIndicator and KStatusNotifierItem Support

- **Source:** https://github.com/ubuntu/gnome-shell-extension-appindicator
- **Complexity:** Complex (D-Bus protocol, legacy X11 tray, multi-layer icon management)
- **GNOME versions:** 47, 48, 49
- **Maintainer:** Ubuntu (canonical team)
- **EGO page:** https://extensions.gnome.org/extension/615/appindicator-support/

**Notable patterns:**
- **Modular file architecture**: Separate files per concern -- `extension.js` (thin entry point), `appIndicator.js` (AppIndicator data model), `statusNotifierWatcher.js` (D-Bus registry/lifecycle), `dbusMenu.js` (menu protocol), `iconCache.js` (icon management), `indicatorStatusIcon.js` (visual representation), `util.js` (shared utilities). Extension.js is kept thin, delegating all heavy logic to domain-specific modules.
- **D-Bus lifecycle management**: StatusNotifierWatcher acts as a central registry. Each indicator's lifecycle is tracked: the watcher connects to the 'destroy' signal of each AppIndicator to remove it from the internal map. When an application disappears without unregistering (detected via 'name-owner-changed'), the watcher destroys the indicator after a 500ms grace period.
- **Cancellable for async cleanup**: Uses `Gio.Cancellable` instances that are cancelled in `disable()`/`destroy()` to abort pending D-Bus operations.
- **Layered cleanup in destroy**: The destroy method performs sequential cleanup: destroy all registered indicators, cancel the cancellable, emit StatusNotifierHostUnregistered signal, release D-Bus name, unexport D-Bus interface, destroy D-Bus resources, clean up internal data structures.
- **Signal connection per-object tracking**: Signals connected to external objects are stored and disconnected individually during destroy rather than using a bulk approach.

**File structure:**
```
extension.js              # Thin entry point (enable/disable)
appIndicator.js           # AppIndicator data model and icon management
statusNotifierWatcher.js  # D-Bus registry and lifecycle management
dbusMenu.js               # D-Bus menu protocol implementation
iconCache.js              # Icon caching and rendering
indicatorStatusIcon.js    # Visual representation in panel
util.js                   # Shared utility functions
trayIconsReloaded.js      # Legacy X11 tray icon support
metadata.json
prefs.js
schemas/
stylesheet.css
```

---

### 2. Caffeine

- **Source:** https://github.com/eonpatapon/gnome-shell-extension-caffeine
- **Complexity:** Simple-Medium (Quick Settings toggle, inhibitor management)
- **GNOME versions:** 45+ (supports through 48)
- **Maintainer:** eonpatapon
- **EGO page:** https://extensions.gnome.org/extension/517/caffeine/

**Notable patterns:**
- **Quick Settings integration**: Uses the modern `QuickSettings.SystemIndicator` pattern (GNOME 43+) rather than legacy PanelMenu.Button. The Quick Settings toggle is a separate class extending `QuickSettingsMenu.QuickToggle`.
- **Clean enable/disable symmetry**: enable() creates indicator, registers settings listeners, connects signals. disable() destroys indicator, disconnects all signals, nulls all references. Each resource created in enable() has an explicit corresponding cleanup in disable().
- **GSettings binding for toggle state**: Uses `settings.bind()` with `Gio.SettingsBindFlags.DEFAULT` for bidirectional binding between GSettings and the toggle's `checked` property. This eliminates manual signal management for the core state.
- **Inhibitor pattern**: Uses `Gio.DBus.session.call()` to acquire and release screensaver inhibitors through the session bus. The inhibitor cookie is stored and released in disable().
- **Simple file structure**: Flat directory, no subdirectories beyond schemas/. Appropriate for the extension's scope.

**File structure:**
```
caffeine@patapon.info/
  extension.js            # Main extension with Quick Settings indicator
  prefs.js                # Preferences with Adw widgets
  metadata.json
  schemas/
    org.gnome.shell.extensions.caffeine.gschema.xml
    gschemas.compiled
  stylesheet.css
  icons/                  # Symbolic icons for toggle states
```

---

### 3. Blur my Shell

- **Source:** https://github.com/aunetx/blur-my-shell
- **Complexity:** Complex (GLSL shaders, pipeline system, multi-component blur)
- **GNOME versions:** 46, 47, 48
- **Maintainer:** aunetx
- **EGO page:** https://extensions.gnome.org/extension/3193/blur-my-shell/

**Notable patterns:**
- **Component-based architecture**: The extension manages discrete blur targets (panel, overview, dash, lock screen, screenshot, window list, applications) as separate component modules. Each component has its own enable/disable lifecycle, allowing the main extension to delegate management.
- **Effect pipeline system**: Configurable pipeline of visual effects (gaussian blur, Monte Carlo blur, corners, pixelization). Each effect is a separate class with its own resource management.
- **Session-modes support**: Properly declares both `user` and `unlock-dialog` session modes in metadata.json, with conditional component initialization for lock screen blur.
- **Settings updater**: Includes a version migration system that updates user settings when upgrading from previous versions, ensuring smooth transitions without manual reconfiguration.
- **Performance tier system**: Three "hack levels" to balance visual quality against system performance, acknowledging that not all systems can handle dynamic blur.
- **Compatibility with other extensions**: Explicitly handles interactions with Dash to Panel, Hide Top Bar, Just Perfection, and other extensions that modify the same Shell surfaces.

**File structure:**
```
src/
  extension.js            # Thin orchestrator
  preferences/            # Prefs UI components
  components/             # Per-target blur components (panel, overview, dash, etc.)
  conveniences/           # Shared utilities and helpers
  effects/                # GLSL shader effects
  dbus/                   # D-Bus interface for screenshots
metadata.json
stylesheet.css
schemas/
```

---

### 4. Dash to Panel

- **Source:** https://github.com/home-sweet-gnome/dash-to-panel
- **Complexity:** Complex (panel replacement, multi-monitor, window management, intellihide)
- **GNOME versions:** 45, 46, 47, 48
- **Maintainers:** jderose9, charlesg99
- **EGO page:** https://extensions.gnome.org/extension/1160/dash-to-panel/

**Notable patterns:**
- **Modular panel system**: Each monitor gets its own panel instance, managed by a central coordinator. The extension handles dynamic monitor addition/removal by creating/destroying panel instances.
- **Conflict management**: Automatically detects and disables conflicting extensions (Ubuntu Dock / Dash to Dock) via `global.settings.set_strv('disabled-extensions', ...)` during enable, and restores them during disable.
- **InjectionManager usage**: Uses GNOME Shell's `InjectionManager` class for cleanly patching Shell methods (e.g., overriding panel layout, workspace switching). All injections are reversed via `injectionManager.clear()` in disable().
- **Signal management at scale**: With many signal connections across multiple monitors and panels, uses structured tracking (arrays of handler IDs per source object) for reliable cleanup.
- **Settings-driven feature flags**: Nearly every aspect of the panel is controlled by GSettings preferences, with settings change handlers that dynamically reconfigure UI without requiring extension restart.
- **Derived from Dash to Dock**: Significant portions of code share lineage with Dash to Dock, demonstrating the common fork-and-specialize pattern in the GNOME extension ecosystem.

**File structure:**
```
extension.js              # Enable/disable with conflict management
panel.js                  # Per-monitor panel implementation
panelManager.js           # Multi-panel coordinator
panelSettings.js          # Settings binding and feature flags
taskbar.js                # Application launcher/task switcher
appIcons.js               # Application icon management
windowPreview.js          # Window preview on hover
intellihide.js            # Auto-hide logic
utils.js                  # Shared utilities
prefs.js                  # Preferences window
metadata.json
schemas/
stylesheet.css
```

---

### 5. Vitals

- **Source:** https://github.com/corecoding/Vitals
- **Complexity:** Medium (sensor polling, system data aggregation, panel menu)
- **GNOME versions:** 45, 46, 47, 48
- **Maintainer:** corecoding
- **EGO page:** https://extensions.gnome.org/extension/1460/vitals/

**Notable patterns:**
- **Async polling with cleanup**: Uses `GLib.timeout_add_seconds()` for periodic sensor polling. The timeout ID is stored and removed via `GLib.Source.remove()` in disable(). Polling is async to prevent UI blocking.
- **Sensor abstraction**: Each sensor type (temperature, voltage, fan, memory, CPU, network, storage) has its own data source module. The main extension aggregates results from all sensor modules.
- **Menu-based UI**: Uses `PanelMenu.Button` for the panel indicator with a dropdown menu showing sensor readings. Menu items are dynamically rebuilt when sensor configuration changes.
- **GTop integration**: Uses GTop (GNOME's system monitoring library) for hardware data, with fallback to `/proc` and `/sys` filesystem reads.
- **Flat file structure**: Despite medium complexity, keeps all JS files in the root directory. This is appropriate for extensions where the number of files is manageable (under ~15).
- **Forked from Freon**: Originally derived from gnome-shell-extension-freon, demonstrating clean fork-and-extend practices.

**File structure:**
```
extension.js              # Main extension and panel menu
prefs.js                  # Preferences
sensors.js                # Sensor data aggregation
menuItem.js               # Custom menu item widgets
values.js                 # Value formatting and units
processor.js              # CPU sensor data
memory.js                 # Memory sensor data
storage.js                # Storage sensor data
network.js                # Network sensor data
metadata.json
schemas/
stylesheet.css
```

---

## Section 2: Cross-Extension Patterns

### Pattern 1: Thin Extension Entry Point

- **Description:** The extension.js file is kept minimal -- it contains the Extension class with enable() and disable() methods that delegate all significant logic to imported modules. Extension.js acts as an orchestrator, not a monolith.
- **Used by:** AppIndicator, Blur my Shell, Dash to Panel
- **Why it works:** Reviewers can quickly verify the enable/disable lifecycle is correct by reading a short file. Separation of concerns makes it easier to audit individual components. Changes to internal logic do not require re-reviewing the lifecycle contract.
- **Current plugin coverage:** Not explicitly checked. ego-lint validates enable/disable symmetry (R-LIFE-01) and resource cleanup (check-lifecycle.py), but does not flag monolithic extension.js files.
- **Recommendation:** Add a Tier 3 checklist item (code-quality) recommending component delegation for extensions with 500+ lines in extension.js. Not suitable for automated enforcement since simple extensions legitimately keep everything in one file.

---

### Pattern 2: Structured Signal Tracking

- **Description:** Signal handler IDs are stored in a structured way (object property per signal source, or array of `{object, handlerId}` tuples) and disconnected in a loop during cleanup. Modern extensions increasingly use `connectObject()`/`disconnectObject()` (GNOME 42+) which provides automatic cleanup when the connecting object is destroyed.
- **Used by:** AppIndicator, Dash to Panel, Blur my Shell, Vitals
- **Why it works:** Prevents the common "forgot to disconnect one signal" bug. Makes the cleanup path auditable -- a reviewer can verify that every connect has a matching disconnect by scanning the data structure. `connectObject()` eliminates the tracking burden entirely.
- **Current plugin coverage:** Partial. R-LIFE-01 (signal balance) checks that connect count roughly matches disconnect count. check-lifecycle.py detects untracked signal connections. But neither checks for the structured tracking pattern specifically.
- **Recommendation:** Add a Tier 3 checklist item recommending `connectObject()`/`disconnectObject()` as the preferred signal management pattern for new extensions targeting GNOME 42+. Consider a Tier 1 pattern rule that emits an informational note when `connectObject` is available but traditional `connect`/`disconnect` is used.

---

### Pattern 3: Component Lifecycle Delegation

- **Description:** Complex extensions decompose into components, each with its own enable/disable (or connect/disconnect, or show/hide) lifecycle. The main extension enables/disables each component, and each component manages its own signals, widgets, and resources. The main extension's disable() calls each component's cleanup method.
- **Used by:** Blur my Shell (blur targets as components), Dash to Panel (per-monitor panels), AppIndicator (watcher vs. indicators vs. tray)
- **Why it works:** Localizes cleanup responsibility. A reviewer can audit each component's cleanup independently. Prevents the "did they remember to clean up X in disable()" problem by making each module responsible for its own resources. Makes enable/disable order explicit.
- **Current plugin coverage:** Partially covered by check-resources.py (cross-file resource graph) which tracks resource creation and destruction across files. The ego-review Phase 2 lifecycle audit uses the resource graph. But no check specifically validates that delegated components have matching cleanup.
- **Recommendation:** Enhance the resource graph (build-resource-graph.py) to detect component lifecycle patterns (classes with enable/disable or connect/disconnect methods) and verify each component's cleanup is called from the main extension's disable(). Add to the lifecycle checklist.

---

### Pattern 4: GSettings Binding Over Manual Signal Management

- **Description:** Instead of connecting to `settings.connect('changed::key', callback)` and manually disconnecting in disable(), gold-standard extensions use `settings.bind(key, widget, property, flags)` for UI synchronization. The binding is automatically cleaned up when the widget is destroyed.
- **Used by:** Caffeine (toggle state), Dash to Panel (feature flags), Vitals (sensor selection)
- **Why it works:** Eliminates an entire class of signal-leak bugs. The reviewer does not need to verify that every settings signal is disconnected because the binding lifecycle is tied to the widget lifecycle. Reduces boilerplate code.
- **Current plugin coverage:** R-QUAL-23 checks for correct `Gio.SettingsBindFlags` usage. No check recommends `settings.bind()` over manual `settings.connect('changed::...')`.
- **Recommendation:** Add a Tier 3 checklist item (code-quality) noting that `settings.bind()` is preferred over manual `connect('changed::key')` when the purpose is UI synchronization. Not suitable for a FAIL rule since manual connection is sometimes necessary (e.g., when the handler does more than set a property).

---

### Pattern 5: Cancellable for Async Operation Cleanup

- **Description:** Extensions that perform async operations (D-Bus calls, file I/O, subprocess communication) create a `Gio.Cancellable` instance, pass it to all async operations, and call `cancellable.cancel()` in disable() to abort pending operations. This prevents callbacks from firing after the extension is disabled.
- **Used by:** AppIndicator (D-Bus operations), GSConnect (device communication)
- **Why it works:** Solves the "async callback fires after disable()" problem comprehensively. A single cancellable per extension (or per component) ensures all pending operations are aborted. This is especially important for D-Bus operations which may have unpredictable latency.
- **Current plugin coverage:** check-async.py detects `_destroyed` guard patterns and cancellable usage. The ego-review async audit (Phase 3) checks for cancellable patterns. But no check specifically flags async operations that lack a cancellable parameter.
- **Recommendation:** Strengthen check-async.py to warn when `_async` method calls lack a cancellable parameter. Add examples of the cancellable pattern to the lifecycle checklist.

---

### Pattern 6: Import Organization Convention

- **Description:** Imports are organized into three groups, separated by blank lines: (1) GObject Introspection (`gi://`) imports, (2) GNOME Shell resource (`resource:///`) imports, (3) local relative (`./`) imports. Within each group, imports are typically alphabetized.
- **Used by:** All five extensions, consistent with gjs.guide documentation
- **Why it works:** Makes it immediately clear what external dependencies the extension uses. Reviewers can quickly spot prohibited imports (GTK in extension.js, Shell libraries in prefs.js). Consistent ordering reduces cognitive load during review.
- **Current plugin coverage:** check-imports.sh validates import segregation (no GTK in extension.js, no Shell libs in prefs.js). But import ordering is not checked.
- **Recommendation:** No automated enforcement needed -- import ordering is a style preference. But add to the code-quality checklist as a recommended practice that signals code maturity.

---

### Pattern 7: Optional Chaining for Defensive Cleanup

- **Description:** The disable() method uses optional chaining (`?.`) for destruction calls: `this._indicator?.destroy()` followed by `this._indicator = null`. This prevents errors if disable() is called when the object was never created (e.g., if enable() threw an error partway through).
- **Used by:** Caffeine, Vitals, pattern shown in gjs.guide examples
- **Why it works:** Makes disable() idempotent -- it can be called safely regardless of how far enable() got before failing. Prevents secondary errors during cleanup that would mask the original error. Aligns with the official gjs.guide example code.
- **Current plugin coverage:** Not checked. The plugin does not distinguish between `this._indicator.destroy()` and `this._indicator?.destroy()` in disable().
- **Recommendation:** Add a Tier 3 checklist item noting that `?.` in disable() is a best practice for defensive cleanup. Not suitable for a FAIL rule since both forms are technically correct when enable() completed successfully.

---

### Pattern 8: Null Assignment After Destroy

- **Description:** After calling `.destroy()` on a widget or object, the reference is explicitly set to `null`. This is a universal pattern: `this._widget.destroy(); this._widget = null;` (or with optional chaining: `this._widget?.destroy(); this._widget = null;`).
- **Used by:** All five extensions, consistently required by reviewers
- **Why it works:** Prevents use-after-free errors where code attempts to access a destroyed GObject. Helps the garbage collector by breaking reference cycles. Reviewers explicitly flag missing null assignments (see phase1-discourse-findings.md, Finding #4 and #14).
- **Current plugin coverage:** Partial. The lifecycle checklist mentions nulling references. No automated check verifies that `.destroy()` calls are followed by `= null`.
- **Recommendation:** Add a Tier 2 check in check-lifecycle.py that warns when `.destroy()` is called on a member variable without a subsequent `= null` assignment. This is a high-signal, low-false-positive check.

---

### Pattern 9: Explicit Error Boundaries in Callbacks

- **Description:** Signal callbacks and timeout callbacks that interact with external systems (D-Bus, file system, subprocess) wrap their body in try/catch with `logError(e)`. This prevents a single failing callback from crashing the extension or leaving it in an inconsistent state.
- **Used by:** AppIndicator (D-Bus callbacks), Vitals (sensor polling callbacks)
- **Why it works:** GNOME Shell will disable an extension that throws an unhandled exception. By catching errors at callback boundaries, the extension remains functional even when individual operations fail. This is especially important for sensor polling and D-Bus communication where external factors can cause unpredictable failures.
- **Current plugin coverage:** check-quality.py flags excessive try-catch usage (AI slop pattern). But no check validates that high-risk callbacks have error boundaries.
- **Recommendation:** This is a nuanced pattern -- the right amount of try-catch depends on context. Add to the code-quality checklist as guidance: "Callbacks that interact with external systems (D-Bus, file I/O, subprocess) SHOULD have error boundaries. Callbacks for internal operations (settings changes, UI updates) generally SHOULD NOT."

---

### Pattern 10: Metadata Best Practices

- **Description:** Gold-standard extensions consistently include these metadata.json fields beyond the minimum: `url` (repository link, required for EGO), `settings-schema` (when using GSettings), `session-modes` (explicitly declaring supported modes), and `shell-version` with only major versions (no minor versions for GNOME 40+).
- **Used by:** All five extensions
- **Why it works:** `url` gives reviewers access to the full git history. `settings-schema` enables `this.getSettings()` without arguments. `session-modes` makes lock-screen behavior explicit rather than relying on defaults. Major-only shell versions prevent unnecessary breakage warnings.
- **Current plugin coverage:** check-metadata.py validates required fields, UUID format, shell-version, session-modes, settings-schema, and version-name. This is well-covered.
- **Recommendation:** check-metadata.py already covers this well. Consider adding a WARN for missing `url` field (currently only checked during package validation).

---

### Pattern 11: Build System and Development Infrastructure

- **Description:** Well-maintained extensions include build infrastructure: a `Makefile` or `meson.build` for building/packaging, ESLint configuration for code quality, and `.editorconfig` or similar for consistent formatting. Some include CI/CD via GitHub Actions.
- **Used by:** AppIndicator (Makefile), Blur my Shell (Makefile), Dash to Panel (Makefile), GSConnect (meson.build)
- **Why it works:** Build systems ensure reproducible packaging. ESLint catches common errors before submission. CI/CD prevents regressions. These are not reviewed by EGO but correlate strongly with extension quality and maintainability.
- **Current plugin coverage:** Not applicable -- these are development-time tools, not runtime code. check-package.sh validates the final zip contents.
- **Recommendation:** Add a note to ego-scaffold templates suggesting ESLint configuration and a Makefile for packaging. Not a review check, but scaffolding guidance.

---

### Pattern 12: GTypeName Namespacing

- **Description:** Custom GObject subclasses use `GObject.registerClass()` with a `GTypeName` that includes a namespace prefix (e.g., `Gjs_CaffeineToggle`, `Gjs_VitalsMenuButton`). This prevents type name collisions when multiple extensions register classes.
- **Used by:** Extensions with custom widgets (Caffeine, Vitals, Dash to Panel, Blur my Shell)
- **Why it works:** GType names are global in the GNOME Shell process. Two extensions registering a class with the same GTypeName will cause a crash. Namespacing prevents this. When GTypeName is omitted, GJS auto-generates a unique name (prefixed with `Gjs_`), which is also acceptable.
- **Current plugin coverage:** check-gobject.py validates GObject.registerClass patterns and GTypeName format. This is covered.
- **Recommendation:** Already covered. The existing check is sufficient.

---

### Pattern 13: Preferences Using Adwaita Widgets

- **Description:** Modern prefs.js extends `ExtensionPreferences` and uses Adwaita (`Adw`) widgets: `Adw.PreferencesPage`, `Adw.PreferencesGroup`, `Adw.SwitchRow`, `Adw.ActionRow`, `Adw.SpinRow`, etc. Settings are bound to rows using `settings.bind()`.
- **Used by:** Caffeine, Blur my Shell, Vitals, Dash to Panel (all targeting GNOME 45+)
- **Why it works:** Adwaita preferences widgets provide a consistent, native-looking settings UI. Using `settings.bind()` on rows eliminates manual signal management. The `fillPreferencesWindow(window)` method is the standard entry point. Storing settings on `window._settings` prevents premature garbage collection.
- **Current plugin coverage:** check-prefs.py validates ExtensionPreferences base class, GTK4/Adwaita patterns, and memory leak detection. R-PREFS-04 flags GTK3 widget usage.
- **Recommendation:** Already well-covered. Consider adding a WARN-level check for preferences that use manual `connect('changed::...')` instead of `settings.bind()` for simple UI synchronization.

---

### Pattern 14: Conflict-Aware Extensions

- **Description:** Extensions that modify the same Shell surfaces as other popular extensions include explicit conflict detection and handling. They either disable conflicting extensions programmatically or adapt their behavior when conflicts are detected.
- **Used by:** Dash to Panel (disables Ubuntu Dock), Blur my Shell (adapts to Dash to Panel, Hide Top Bar, Just Perfection)
- **Why it works:** Prevents user confusion when two extensions fight over the same panel/dock. Programmatic conflict management is more reliable than documentation. Reviewers appreciate extensions that handle edge cases gracefully.
- **Current plugin coverage:** Not checked. This is a design-level concern beyond automated linting.
- **Recommendation:** No automated check appropriate. Add to ego-review Phase 5 (code quality) as a consideration for extensions that modify core Shell UI elements.

---

### Pattern 15: Version Migration for Settings

- **Description:** Extensions that change their GSettings schema between versions include migration logic that converts old settings values to the new format, preventing data loss or broken configurations after updates.
- **Used by:** Blur my Shell (settings updater), Dash to Panel (settings migration)
- **Why it works:** Users update extensions frequently. Without migration, schema changes can cause the extension to fail silently or lose user customizations. Reviewers value this as a sign of mature, user-considerate development.
- **Current plugin coverage:** Not checked. This is an optional enhancement, not a requirement.
- **Recommendation:** No automated check. Add a mention to the ego-scaffold guide for extensions with complex settings.

---

## Section 3: Anti-Patterns Observed in Rejected Extensions (Contrast)

For context, here are patterns that the gold-standard extensions consistently avoid, which are commonly seen in rejected submissions:

| Anti-Pattern | Gold Standard Alternative | Our Coverage |
|---|---|---|
| Monolithic extension.js (1000+ lines, all logic inline) | Thin entry point with module delegation | Not checked |
| `connect()` without storing handler ID | `connectObject()` or stored ID with disconnect | R-LIFE-01 (partial) |
| `GLib.timeout_add()` without storing/removing source ID | Stored ID + `GLib.Source.remove()` in disable() | R-LIFE-02, R-LIFE-12 |
| Missing `= null` after `.destroy()` | Always null after destroy | Tier 3 only |
| Manual `settings.connect('changed::...')` for simple UI binding | `settings.bind()` | Not checked |
| `try {} catch(e) {}` (empty catch) around everything | Targeted error boundaries with `logError(e)` | R-SLOP-29 (empty catch) |
| Async operations without cancellable | `Gio.Cancellable` passed to all async calls | check-async.py (partial) |
| GTypeName collision (generic names like "MyWidget") | Namespaced GTypeName or omitted (auto-generated) | check-gobject.py |
| Module-level side effects (code at import time) | All initialization in enable() | R-INIT-01 |
| Legacy `imports.` syntax (pre-GNOME 45) | ESModules with `import`/`export` | check-imports.sh |

---

## Section 4: Recommendations Summary

### High Priority (consider adding to automated checks or checklists)

1. **Null after destroy check** (Pattern 8): Add Tier 2 check in check-lifecycle.py for `.destroy()` without subsequent `= null`. High signal, low false positives.
2. **connectObject recommendation** (Pattern 2): Add Tier 3 checklist item recommending `connectObject()`/`disconnectObject()` for GNOME 42+.
3. **Cancellable in async calls** (Pattern 5): Strengthen check-async.py to warn on `_async()` calls without cancellable parameter.

### Medium Priority (add to checklists, not automated checks)

4. **Thin extension entry point** (Pattern 1): Checklist note for extensions over 500 lines in extension.js.
5. **settings.bind() preference** (Pattern 4): Checklist note recommending `settings.bind()` over manual `connect('changed::...')`.
6. **Defensive cleanup with ?.** (Pattern 7): Checklist note recommending optional chaining in disable().
7. **Error boundaries in external callbacks** (Pattern 9): Checklist guidance on when try-catch is appropriate.
8. **Import organization** (Pattern 6): Checklist note on gi:// / resource:// / relative grouping.

### Low Priority (informational, no action needed)

9. **Build system** (Pattern 11): Already covered by ego-scaffold guidance.
10. **GTypeName** (Pattern 12): Already covered by check-gobject.py.
11. **Adwaita prefs** (Pattern 13): Already covered by check-prefs.py.
12. **Conflict management** (Pattern 14): Design-level, not automatable.
13. **Settings migration** (Pattern 15): Optional enhancement, mention in scaffold guide.

---

## Sources

- [AppIndicator Extension - GitHub](https://github.com/ubuntu/gnome-shell-extension-appindicator)
- [AppIndicator Architecture - DeepWiki](https://deepwiki.com/ubuntu/gnome-shell-extension-appindicator/1-overview)
- [AppIndicator System - DeepWiki](https://deepwiki.com/ubuntu/gnome-shell-extension-appindicator/3-appindicator-system)
- [Status Notifier Watcher - DeepWiki](https://deepwiki.com/ubuntu/gnome-shell-extension-appindicator/4-status-notifier-watcher)
- [Caffeine Extension - GitHub](https://github.com/eonpatapon/gnome-shell-extension-caffeine)
- [Blur my Shell - GitHub](https://github.com/aunetx/blur-my-shell)
- [Blur my Shell - DeepWiki](https://deepwiki.com/aunetx/blur-my-shell)
- [Dash to Panel - GitHub](https://github.com/home-sweet-gnome/dash-to-panel)
- [Vitals Extension - GitHub](https://github.com/corecoding/Vitals)
- [GSConnect - GitHub](https://github.com/GSConnect/gnome-shell-extension-gsconnect)
- [Extension (ESModule) - gjs.guide](https://gjs.guide/extensions/topics/extension.html)
- [Review Guidelines - gjs.guide](https://gjs.guide/extensions/review-guidelines/review-guidelines.html)
- [Imports and Modules - gjs.guide](https://gjs.guide/extensions/overview/imports-and-modules.html)
- [Preferences - gjs.guide](https://gjs.guide/extensions/development/preferences.html)
- [Quick Settings - gjs.guide](https://gjs.guide/extensions/topics/quick-settings.html)
- [Memory Management Tips - gjs.guide](https://gjs.guide/guides/gjs/memory-management.html)
- [GObject Subclassing - gjs.guide](https://gjs.guide/guides/gobject/subclassing.html)
- [Async Programming - gjs.guide](https://gjs.guide/guides/gjs/asynchronous-programming.html)
- [connectObject/disconnectObject - GNOME Discourse](https://discourse.gnome.org/t/description-of-the-connectobject-and-disconnectobject-methods/16726)
- [Signal Disconnection - GNOME Discourse](https://discourse.gnome.org/t/is-disconnecting-from-signals-always-required/14862)
- [Port to GNOME Shell 42 - gjs.guide](https://gjs.guide/extensions/upgrading/gnome-shell-42.html)
- [Port to GNOME Shell 45 - gjs.guide](https://gjs.guide/extensions/upgrading/gnome-shell-45.html)
- [AI and GNOME Shell Extensions - Blog](https://blogs.gnome.org/jrahmatzadeh/2025/12/06/ai-and-gnome-shell-extensions/)
- [Caffeine Review v51 - EGO](https://extensions.gnome.org/review/45237)
- [Blur my Shell Review v56 - EGO](https://extensions.gnome.org/review/51732)
