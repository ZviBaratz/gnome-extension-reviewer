# EGO Lint Rules Reference

Complete catalog of rules checked by the ego-lint skill. Each rule includes its
severity, the script that checks it, and guidance on how to fix violations.

## Severity Levels

- **blocking** — Must be fixed before EGO submission. The extension will be rejected.
- **advisory** — Should be fixed. Reviewers may flag these or request changes.
- **info** — Informational. No action required.

---

## Metadata (R-META)

Rules for `metadata.json` validity and EGO requirements.

### R-META-01: UUID must be present
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: `metadata.json` must contain a `uuid` field.
- **Rationale**: The UUID is the primary identifier for the extension on EGO and in GNOME Shell. Without it, the extension cannot be loaded.
- **Fix**: Add a `uuid` field to `metadata.json`. Format: `extension-name@your-domain`.

### R-META-02: UUID must match directory name
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: The `uuid` value in `metadata.json` must exactly match the extension directory name.
- **Rationale**: GNOME Shell locates extensions by directory name and validates it against the metadata UUID. A mismatch prevents the extension from loading.
- **Fix**: Rename the directory to match the UUID, or update the UUID to match the directory name.

### R-META-03: UUID format (alphanumeric + . _ - @)
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: The UUID must contain only alphanumeric characters, periods, underscores, hyphens, and the `@` symbol.
- **Rationale**: GNOME Shell enforces this character set. Invalid characters will prevent installation.
- **Fix**: Remove any characters not matching `[a-zA-Z0-9._@-]` from the UUID.

### R-META-04: No @gnome.org namespace
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: The UUID must not use the `@gnome.org` domain suffix.
- **Rationale**: The `@gnome.org` namespace is reserved for official GNOME extensions. Using it for third-party extensions will cause rejection.
- **Fix**: Change the domain portion of the UUID to your own domain (e.g., `my-extension@example.com`).

### R-META-05: name field required
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: `metadata.json` must contain a `name` field with a non-empty string value.
- **Rationale**: The name is displayed on EGO and in GNOME Extensions app. It is a required field for submission.
- **Fix**: Add `"name": "Your Extension Name"` to `metadata.json`.

### R-META-06: description field required
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: `metadata.json` must contain a `description` field with a non-empty string value.
- **Rationale**: The description appears on the EGO listing page. It is a required field for submission.
- **Fix**: Add `"description": "Brief description of what the extension does"` to `metadata.json`.

### R-META-07: shell-version must be array
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: The `shell-version` field must be a JSON array of version strings.
- **Rationale**: GNOME Shell uses this array to determine compatibility. A non-array value will fail validation.
- **Fix**: Use an array format: `"shell-version": ["47", "48"]`.

### R-META-08: shell-version should include current stable (48)
- **Severity**: advisory
- **Checked by**: check-metadata.py
- **Rule**: The `shell-version` array should include the current stable GNOME Shell version (`"48"`).
- **Rationale**: Extensions not targeting the current stable release have limited audience and may be deprioritized in review. Reviewers may ask why the current version is missing.
- **Fix**: Add `"48"` to the `shell-version` array.

### R-META-09: No session-modes ["user"]
- **Severity**: advisory
- **Checked by**: check-metadata.py
- **Rule**: If `session-modes` is present and contains only `["user"]`, it should be removed.
- **Rationale**: `["user"]` is the default value. Including it explicitly is redundant and signals unfamiliarity with the metadata spec. EGO reviewers may flag it.
- **Fix**: Remove the `session-modes` key from `metadata.json` entirely. Only include it if you need `"unlock-dialog"` or other non-default modes.

### R-META-10: settings-schema prefix must be org.gnome.shell.extensions.*
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: If `settings-schema` is declared, it must start with `org.gnome.shell.extensions.`.
- **Rationale**: GNOME Shell's extension system expects GSettings schemas under this prefix. A different prefix will fail to load settings.
- **Fix**: Rename the schema ID to `org.gnome.shell.extensions.your-extension-name`.

### R-META-11: url field recommended for EGO listing
- **Severity**: advisory
- **Checked by**: manual review
- **Rule**: `metadata.json` should include a `url` field pointing to the project homepage or repository.
- **Rationale**: The URL is displayed on the EGO listing page. It helps users find documentation, report issues, and contribute. Reviewers expect it for established projects.
- **Fix**: Add `"url": "https://github.com/your-username/your-extension"` to `metadata.json`.

### R-META-12: description should disclose permissions
- **Severity**: advisory
- **Checked by**: manual review
- **Rule**: If the extension uses clipboard access, network requests, or privilege escalation (pkexec), the description should mention this.
- **Rationale**: EGO reviewers scrutinize extensions that use elevated permissions. Proactive disclosure builds trust and speeds up the review process.
- **Fix**: Add a note to the description, e.g., "This extension uses pkexec to write battery thresholds via a helper script."

---

## Schema (R-SCHEMA)

Rules for GSettings schema files.

### R-SCHEMA-01: Schema file must exist if settings-schema declared
- **Severity**: blocking
- **Checked by**: check-schema.sh
- **Rule**: If `metadata.json` declares a `settings-schema`, a corresponding `.gschema.xml` file must exist in the `schemas/` directory.
- **Rationale**: GNOME Shell will attempt to load the schema at runtime. A missing file causes a hard error.
- **Fix**: Create the schema file at `schemas/org.gnome.shell.extensions.your-extension.gschema.xml`.

### R-SCHEMA-02: Schema ID must match metadata settings-schema
- **Severity**: blocking
- **Checked by**: check-schema.sh
- **Rule**: The `id` attribute of the `<schema>` element must exactly match the `settings-schema` value in `metadata.json`.
- **Rationale**: A mismatch means the extension will compile the schema but fail to find it at runtime, causing a GSettings error.
- **Fix**: Ensure the `id="..."` in the schema XML matches the `settings-schema` value in `metadata.json` exactly.

### R-SCHEMA-03: Schema path must start with /org/gnome/shell/extensions/
- **Severity**: blocking
- **Checked by**: check-schema.sh
- **Rule**: The `path` attribute of the `<schema>` element must start with `/org/gnome/shell/extensions/`.
- **Rationale**: GNOME Shell's extension settings loader expects schemas under this dconf path. A different path prefix will cause settings to be inaccessible.
- **Fix**: Set the path to `/org/gnome/shell/extensions/your-extension-name/`.

### R-SCHEMA-04: Schema must compile without errors
- **Severity**: blocking
- **Checked by**: check-schema.sh
- **Rule**: Running `glib-compile-schemas` on the `schemas/` directory must succeed without errors.
- **Rationale**: The compiled schema binary (`gschemas.compiled`) is what GNOME Shell actually reads. If compilation fails, the extension cannot load settings.
- **Fix**: Fix XML syntax errors, missing closing tags, invalid key types, or invalid default values reported by the compiler.

### R-SCHEMA-05: Schema filename should match ID
- **Severity**: advisory
- **Checked by**: check-schema.sh
- **Rule**: The schema filename should match the schema ID (e.g., `org.gnome.shell.extensions.my-ext.gschema.xml` for schema ID `org.gnome.shell.extensions.my-ext`).
- **Rationale**: While not strictly required, mismatched filenames cause confusion during review and maintenance. EGO reviewers may flag it.
- **Fix**: Rename the schema file to match its ID.

---

## Imports (R-IMPORT)

Rules for import segregation between extension runtime and preferences UI.

### R-IMPORT-01: No gi://Gtk in extension runtime
- **Severity**: blocking
- **Checked by**: check-imports.sh
- **Rule**: Files loaded during extension runtime (`extension.js` and its `lib/` imports) must not import `gi://Gtk`.
- **Rationale**: GTK cannot be used in GNOME Shell's Clutter/Mutter environment. Importing it in extension runtime causes a conflict and will crash the shell or be rejected by reviewers.
- **Fix**: Move GTK-dependent code to `prefs.js` or a file only imported by `prefs.js`.

### R-IMPORT-02: No gi://Gdk in extension runtime
- **Severity**: blocking
- **Checked by**: check-imports.sh
- **Rule**: Files loaded during extension runtime must not import `gi://Gdk`.
- **Rationale**: GDK is part of the GTK stack and cannot coexist with GNOME Shell's display server. Same restriction as GTK.
- **Fix**: Move GDK-dependent code to `prefs.js` or a prefs-only module.

### R-IMPORT-03: No gi://Adw in extension runtime
- **Severity**: blocking
- **Checked by**: check-imports.sh
- **Rule**: Files loaded during extension runtime must not import `gi://Adw`.
- **Rationale**: Adwaita (libadwaita) depends on GTK4. Importing it in extension runtime triggers the GTK conflict.
- **Fix**: Move Adwaita-dependent code to `prefs.js` or a prefs-only module.

### R-IMPORT-04: No gi://Clutter in prefs
- **Severity**: blocking
- **Checked by**: check-imports.sh
- **Rule**: `prefs.js` and its imports must not import `gi://Clutter`.
- **Rationale**: Clutter is a GNOME Shell runtime library not available in the GTK preferences process. Importing it will cause an error when opening preferences.
- **Fix**: Move Clutter-dependent code to `extension.js` or a `lib/` module only imported at runtime.

### R-IMPORT-05: No gi://Meta in prefs
- **Severity**: blocking
- **Checked by**: check-imports.sh
- **Rule**: `prefs.js` and its imports must not import `gi://Meta`.
- **Rationale**: Mutter's Meta library is only available in GNOME Shell's process. It cannot be loaded in the preferences GTK process.
- **Fix**: Move Meta-dependent code to `extension.js` or a runtime-only module.

### R-IMPORT-06: No gi://St in prefs
- **Severity**: blocking
- **Checked by**: check-imports.sh
- **Rule**: `prefs.js` and its imports must not import `gi://St`.
- **Rationale**: St (Shell Toolkit) is GNOME Shell's UI library built on Clutter. It is not available in the GTK preferences process.
- **Fix**: Move St-dependent code to `extension.js` or a runtime-only module.

### R-IMPORT-07: No gi://Shell in prefs
- **Severity**: blocking
- **Checked by**: check-imports.sh
- **Rule**: `prefs.js` and its imports must not import `gi://Shell`.
- **Rationale**: The Shell library is only available within GNOME Shell's process. Importing it in preferences will fail.
- **Fix**: Move Shell-dependent code to `extension.js` or a runtime-only module.

---

## Logging (R-LOG)

Rules for logging practices in GNOME Shell extensions.

### R-LOG-01: No console.log()
- **Severity**: blocking
- **Checked by**: ego-lint.sh
- **Rule**: Extension code must not use `console.log()`.
- **Rationale**: EGO reviewers reject extensions that use `console.log()` because it produces output at the default journal log level, cluttering the system log for all users. `console.debug()` is filtered out unless the user explicitly enables debug logging.
- **Fix**: Replace `console.log(msg)` with `console.debug(msg)` for operational messages, or remove the call if it was for development debugging.

### R-LOG-02: No log() global function
- **Severity**: advisory
- **Checked by**: manual review
- **Rule**: Extension code should not use the global `log()` function.
- **Rationale**: The global `log()` function is a legacy GJS API. Modern extensions should use `console.debug()` or `console.error()` for structured logging.
- **Fix**: Replace `log(msg)` with `console.debug(msg)`.

### R-LOG-03: No print() for debugging
- **Severity**: advisory
- **Checked by**: manual review
- **Rule**: Extension code should not use `print()` or `printerr()` for logging.
- **Rationale**: `print()` writes directly to stdout, which is not captured by the journal in typical GNOME Shell setups. It is a sign of leftover debug code.
- **Fix**: Replace with `console.debug()` or remove entirely.

### R-LOG-04: console.debug() is acceptable for operational messages
- **Severity**: info
- **Checked by**: reference only
- **Rule**: `console.debug()` is the recommended way to log operational messages in GNOME Shell extensions.
- **Rationale**: `console.debug()` output is filtered by default and only visible when users opt in to debug-level logging. This keeps the system journal clean while still providing diagnostic information when needed.
- **Fix**: No action required. This is the correct practice.

---

## Deprecated APIs (R-DEPR)

Rules for deprecated GJS/GNOME APIs that must not be used in modern extensions.

### R-DEPR-01: No Mainloop import
- **Severity**: blocking
- **Checked by**: ego-lint.sh
- **Rule**: Extension code must not import or use `Mainloop`.
- **Rationale**: `Mainloop` is a deprecated GJS compatibility module. It was removed in recent GJS versions. Extensions using it will fail on current GNOME Shell.
- **Fix**: Replace `Mainloop.timeout_add(ms, callback)` with `GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, callback)`. Replace `Mainloop.source_remove(id)` with `GLib.Source.remove(id)`.

### R-DEPR-02: No Lang import
- **Severity**: blocking
- **Checked by**: ego-lint.sh
- **Rule**: Extension code must not import or use `Lang`.
- **Rationale**: `Lang` provided `Lang.Class` and `Lang.bind`, which predate ES6 classes and arrow functions. It is deprecated and signals legacy code that reviewers will reject.
- **Fix**: Replace `Lang.Class` with ES6 `class` syntax. Replace `Lang.bind(this, fn)` with arrow functions or `.bind(this)`.

### R-DEPR-03: No ByteArray import
- **Severity**: blocking
- **Checked by**: ego-lint.sh
- **Rule**: Extension code must not import or use `ByteArray`.
- **Rationale**: `ByteArray` is deprecated in modern GJS. The standard Web APIs `TextEncoder` and `TextDecoder` are now available and preferred.
- **Fix**: Replace `ByteArray.toString(bytes)` with `new TextDecoder().decode(bytes)`. Replace `ByteArray.fromString(str)` with `new TextEncoder().encode(str)`.

### R-DEPR-04: No imports.* legacy import style
- **Severity**: advisory
- **Checked by**: manual review
- **Rule**: Extension code should use ESM `import` syntax, not the legacy `imports.*` style.
- **Rationale**: GNOME 45+ requires ESM modules. The legacy `imports.*` style will not work on GNOME 45 and later. While older extensions may still use it for backward compatibility, new submissions should use ESM.
- **Fix**: Convert `const { Foo } = imports.gi.Foo` to `import Foo from 'gi://Foo'`. Convert `const ExtMe = imports.misc.extensionUtils` to `import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js'`.

---

## Web APIs (R-WEB)

Rules for browser/Node.js APIs that are not available in GJS.

### R-WEB-01: No setTimeout()
- **Severity**: blocking
- **Checked by**: ego-lint.sh
- **Rule**: Extension code must not use `setTimeout()`.
- **Rationale**: `setTimeout` is a browser/Node.js API that does not exist in GJS. Some polyfills may add it, but EGO reviewers reject extensions that rely on non-standard globals.
- **Fix**: Replace `setTimeout(callback, ms)` with `GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, () => { callback(); return GLib.SOURCE_REMOVE; })`. Remember to store the returned ID and call `GLib.Source.remove(id)` in `destroy()`.

### R-WEB-02: No setInterval()
- **Severity**: blocking
- **Checked by**: ego-lint.sh
- **Rule**: Extension code must not use `setInterval()`.
- **Rationale**: Same as `setTimeout` — it is not a native GJS API.
- **Fix**: Replace `setInterval(callback, ms)` with `GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, () => { callback(); return GLib.SOURCE_CONTINUE; })`. Store the ID and remove it in `destroy()`.

### R-WEB-03: No fetch()
- **Severity**: blocking
- **Checked by**: ego-lint.sh
- **Rule**: Extension code must not use `fetch()`.
- **Rationale**: The Fetch API is not available in GJS. Network requests must use GLib/Gio or Soup APIs.
- **Fix**: For HTTP requests, use `Soup.Session` with `Soup.Message`. For local file I/O, use `Gio.File`. For simple GET requests, `Soup.Session.send_and_read_async()` is the modern async pattern.

---

## Files (R-FILE)

Rules for required and forbidden files in the extension source.

### R-FILE-01: extension.js must exist
- **Severity**: blocking
- **Checked by**: ego-lint.sh
- **Rule**: The extension directory must contain an `extension.js` file.
- **Rationale**: `extension.js` is the entry point for GNOME Shell extensions. Without it, the extension cannot be loaded.
- **Fix**: Create `extension.js` with the required `enable()` and `disable()` methods (or extend the `Extension` class).

### R-FILE-02: metadata.json must exist
- **Severity**: blocking
- **Checked by**: ego-lint.sh
- **Rule**: The extension directory must contain a `metadata.json` file.
- **Rationale**: `metadata.json` provides essential metadata (UUID, name, shell-version) that GNOME Shell needs to identify and load the extension.
- **Fix**: Create `metadata.json` with at minimum `uuid`, `name`, `description`, and `shell-version` fields.

### R-FILE-03: LICENSE or COPYING should exist
- **Severity**: advisory
- **Checked by**: ego-lint.sh
- **Rule**: The extension directory should contain a `LICENSE`, `LICENSE.md`, `COPYING`, or similar license file.
- **Rationale**: EGO requires extensions to be open source. While the license can be specified in metadata, a dedicated license file is standard practice and expected by reviewers.
- **Fix**: Add a `LICENSE` file with the full text of your chosen open source license (GPL-2.0+, GPL-3.0, MIT, etc.).

### R-FILE-04: No binary files (.so, .o, .exe, .bin)
- **Severity**: blocking
- **Checked by**: ego-lint.sh
- **Rule**: The extension must not contain compiled binary files.
- **Rationale**: EGO does not allow binary files because they cannot be reviewed for security. All code must be source (JavaScript, XML, CSS, etc.).
- **Fix**: Remove binary files. If native code is needed, provide build instructions and have users compile locally, or use GJS bindings for existing system libraries.

### R-FILE-05: No AI artifacts (CLAUDE.md, .claude/, Cursor rules)
- **Severity**: blocking
- **Checked by**: check-package.sh + manual review
- **Rule**: The extension must not contain AI assistant configuration files such as `CLAUDE.md`, `.claude/`, `.cursorrules`, `.cursor/`, or similar.
- **Rationale**: These files are development tools, not part of the extension. Including them in a submission signals an unclean build process and may raise reviewer concerns.
- **Fix**: Add these paths to `.gitignore` and exclude them from the packaging script. Verify with `check-package.sh` before submission.

---

## Package (R-PKG)

Rules for the zip archive submitted to EGO.

### R-PKG-01: No node_modules/ in zip
- **Severity**: blocking
- **Checked by**: check-package.sh
- **Rule**: The submission zip must not contain a `node_modules/` directory.
- **Rationale**: `node_modules` can contain thousands of files and megabytes of code that reviewers cannot audit. It also signals that the extension depends on npm packages, which is not the GNOME extension model.
- **Fix**: Add `node_modules/` to your exclusion list in the packaging script. If you use npm for development tools (ESLint, etc.), ensure they are devDependencies only.

### R-PKG-02: No .git/ in zip
- **Severity**: blocking
- **Checked by**: check-package.sh
- **Rule**: The submission zip must not contain a `.git/` directory.
- **Rationale**: The `.git/` directory contains the full repository history and can be very large. It is not part of the extension and wastes reviewer time.
- **Fix**: Exclude `.git/` from the packaging script. Use `zip -r extension.zip . -x '.git/*'` or equivalent.

### R-PKG-03: No .claude/ in zip
- **Severity**: blocking
- **Checked by**: check-package.sh
- **Rule**: The submission zip must not contain a `.claude/` directory.
- **Rationale**: AI assistant configuration directories are development tools. Including them in the submission is unprofessional and may delay review.
- **Fix**: Exclude `.claude/` from the packaging script.

### R-PKG-04: No CLAUDE.md in zip
- **Severity**: blocking
- **Checked by**: check-package.sh
- **Rule**: The submission zip must not contain a `CLAUDE.md` file.
- **Rationale**: Same as R-PKG-03. AI configuration files do not belong in a distribution package.
- **Fix**: Exclude `CLAUDE.md` from the packaging script.

### R-PKG-05: No .pot files in zip
- **Severity**: blocking
- **Checked by**: check-package.sh
- **Rule**: The submission zip must not contain `.pot` (Portable Object Template) files.
- **Rationale**: `.pot` files are translation templates generated from source code. They are build artifacts, not runtime files. Only compiled `.mo` files and `.po` source translations should be included.
- **Fix**: Exclude `*.pot` from the packaging script. Include `po/*.po` files and any compiled `locale/` directory.

### R-PKG-06: No .pyc or __pycache__ in zip
- **Severity**: blocking
- **Checked by**: check-package.sh
- **Rule**: The submission zip must not contain `.pyc` files or `__pycache__/` directories.
- **Rationale**: Python bytecode files are build artifacts. They indicate that Python scripts were run in the source tree without cleaning up.
- **Fix**: Exclude `__pycache__/` and `*.pyc` from the packaging script.

### R-PKG-07: No .env files in zip
- **Severity**: blocking
- **Checked by**: check-package.sh
- **Rule**: The submission zip must not contain `.env` files.
- **Rationale**: `.env` files often contain secrets, API keys, or environment-specific configuration. They are a security risk and have no place in a GNOME Shell extension package.
- **Fix**: Exclude `.env` and `.env.*` from the packaging script. Add them to `.gitignore`.

### R-PKG-08: extension.js must be in zip
- **Severity**: blocking
- **Checked by**: check-package.sh
- **Rule**: The submission zip must contain `extension.js` at the archive root.
- **Rationale**: GNOME Shell expects `extension.js` at the top level of the extracted extension directory. If it is missing or nested in a subdirectory, the extension will fail to load.
- **Fix**: Ensure your packaging script creates the zip from inside the extension directory, not from a parent directory. The zip should not contain a top-level directory wrapper.

### R-PKG-09: metadata.json must be in zip
- **Severity**: blocking
- **Checked by**: check-package.sh
- **Rule**: The submission zip must contain `metadata.json` at the archive root.
- **Rationale**: Same as R-PKG-08. GNOME Shell requires `metadata.json` at the top level to identify and validate the extension.
- **Fix**: Same approach as R-PKG-08. Verify by running `unzip -l your-extension.zip | head` and confirming files are at the root level.

---

## CSS (R-CSS)

Rules for stylesheet.css styling practices.

### R-CSS-01: Class names should be scoped
- **Severity**: advisory
- **Checked by**: ego-lint.sh
- **Rule**: Custom CSS class names should use an extension-specific prefix to avoid collisions with GNOME Shell's built-in styles.
- **Rationale**: GNOME Shell extensions share a global CSS namespace. Unscoped class names like `.container` or `.label` may conflict with Shell's own styles or other extensions, causing visual glitches.
- **Fix**: Prefix all custom class names with your extension name or abbreviation (e.g., `.myext-container`, `.myext-label`). Alternatively, scope styles under a parent class unique to your extension.

### R-CSS-02: Avoid styling GNOME Shell built-in classes without scoping
- **Severity**: advisory
- **Checked by**: manual review
- **Rule**: If the extension styles GNOME Shell built-in classes (e.g., `.popup-menu-item`, `.panel-button`), the selectors should be scoped under an extension-specific parent class.
- **Rationale**: Unscoped overrides of built-in Shell classes affect the entire desktop, not just the extension's UI. This can break other extensions or Shell elements.
- **Fix**: Wrap your UI in a container with a unique class and scope all built-in class overrides under it: `.myext-panel .popup-menu-item { ... }`.

---

## Web APIs — Extended (R-WEB, continued)

Additional web/browser API rules detected by pattern matching.

### R-WEB-04: No XMLHttpRequest
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not use `XMLHttpRequest`.
- **Rationale**: `XMLHttpRequest` is a browser API not available in GJS. Extensions must use `Soup.Session` for HTTP requests.
- **Fix**: Replace with `Soup.Session` and `Soup.Message` for HTTP requests, or `Gio.File` for local file I/O.

### R-WEB-05: No requestAnimationFrame()
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not use `requestAnimationFrame()`.
- **Rationale**: `requestAnimationFrame` is a browser rendering API. GNOME Shell uses Clutter's animation framework instead.
- **Fix**: Use Clutter animation APIs such as `Clutter.Timeline`, `St.Adjustment`, or property transitions via `ease()`.

### R-WEB-06: No DOM APIs (document.*)
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not use `document.createElement`, `document.getElementById`, `document.querySelector`, or similar DOM APIs.
- **Rationale**: There is no DOM in GNOME Shell. The UI is built with Clutter/St actors, not HTML elements.
- **Fix**: Use `St.Widget` subclasses (`St.BoxLayout`, `St.Label`, `St.Button`, etc.) to build UI elements.

### R-WEB-07: No window object usage
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not reference the `window` global object (e.g., `window.setTimeout`, `window.location`).
- **Rationale**: The `window` global does not exist in GJS. Any reference to it indicates browser-targeted code that will fail at runtime.
- **Fix**: Remove `window.` references. Use the appropriate GJS/GNOME API for the intended functionality.

### R-WEB-08: No localStorage
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not use `localStorage` or `sessionStorage`.
- **Rationale**: Web Storage APIs are not available in GJS. Extensions must use GSettings for persistent configuration.
- **Fix**: Use `Gio.Settings` (via `this.getSettings()` in the Extension class) for persistent key-value storage.

### R-WEB-09: No require() (Node.js)
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not use `require()` to load modules.
- **Rationale**: `require()` is a Node.js/CommonJS API. GJS uses ESM `import` syntax (GNOME 45+) or the legacy `imports.*` system.
- **Fix**: Replace `require('module')` with `import ... from 'gi://Module'` or the appropriate GJS import syntax.

---

## Deprecated APIs — Extended (R-DEPR, continued)

Additional deprecated API rules detected by pattern matching.

### R-DEPR-05: No ExtensionUtils (removed in GNOME 45+)
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not import or use `ExtensionUtils`.
- **Rationale**: `ExtensionUtils` was removed in GNOME 45 when extensions migrated to ESM. Its functionality is now provided by the `Extension` base class.
- **Fix**: Replace `ExtensionUtils.getCurrentExtension()` with `this` (inside the Extension class). Replace `ExtensionUtils.getSettings()` with `this.getSettings()`. Replace `ExtensionUtils.initTranslations()` with the Extension class's built-in translation support.

### R-DEPR-06: No Tweener (removed)
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not import or use `Tweener`.
- **Rationale**: `Tweener` was GNOME Shell's legacy animation library. It was removed and replaced with Clutter's native property transitions and `ease()` methods.
- **Fix**: Replace `Tweener.addTween(actor, { ... })` with `actor.ease({ ... })` using Clutter's built-in animation support.

### R-DEPR-07: No imports.misc.convenience (removed in GNOME 45+)
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not import `imports.misc.convenience`.
- **Rationale**: The `convenience` module was a GNOME Shell internal that provided helper functions like `getSettings()` and `initTranslations()`. It was removed in GNOME 45 along with the legacy import system.
- **Fix**: Use the `Extension` base class methods: `this.getSettings()` for GSettings access and the built-in translation support for i18n.

---

## AI Slop Signals (R-SLOP)

Rules that detect patterns commonly found in AI-generated extensions. These are advisory signals — they do not necessarily indicate incorrect code, but they correlate strongly with low-quality AI output that EGO reviewers will scrutinize.

### R-SLOP-01: TypeScript-style @param JSDoc
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: JSDoc comments should not use TypeScript-style `@param {Type} name` annotations.
- **Rationale**: GNOME Shell extensions are plain JavaScript (not TypeScript). JSDoc type annotations in the `{Type}` format are a strong signal that code was generated by an AI trained primarily on TypeScript codebases. EGO reviewers recognize this pattern.
- **Fix**: Remove type annotations from JSDoc comments, or remove JSDoc entirely if the code is self-documenting. GJS does not process JSDoc types.

### R-SLOP-02: TypeScript-style @returns JSDoc
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: JSDoc comments should not use TypeScript-style `@returns {Type}` annotations.
- **Rationale**: Same as R-SLOP-01. `@returns {Type}` is a TypeScript convention that has no effect in GJS and signals AI-generated code.
- **Fix**: Remove `@returns {Type}` annotations from JSDoc comments.

### R-SLOP-03: Deprecated version field in metadata
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: `metadata.json` should not contain a numeric `version` field.
- **Rationale**: The `version` field in `metadata.json` is deprecated. EGO manages versioning automatically. Including it is harmless but signals unfamiliarity with current EGO practices, often because an AI template included it.
- **Fix**: Remove the `"version"` key from `metadata.json`. EGO assigns version numbers on upload.

### R-SLOP-04: Non-standard version-name field
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: `metadata.json` should not contain a `version-name` field.
- **Rationale**: `version-name` is not a recognized `metadata.json` field. It appears in AI-generated extensions that hallucinate npm-style metadata fields.
- **Fix**: Remove `"version-name"` from `metadata.json`.

### R-SLOP-05: Non-standard homepage field
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: `metadata.json` should not contain a `homepage` field.
- **Rationale**: The correct field name is `url`, not `homepage`. `homepage` is an npm `package.json` convention that AIs frequently mix up with GNOME metadata.
- **Fix**: Rename `"homepage"` to `"url"` in `metadata.json`.

### R-SLOP-06: Non-standard bug-report-url field
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: `metadata.json` should not contain a `bug-report-url` field.
- **Rationale**: `bug-report-url` is not a recognized `metadata.json` field. The standard `url` field should point to the project repository where issues can be filed.
- **Fix**: Remove `"bug-report-url"` from `metadata.json`. Use the `"url"` field to link to the project repository.

---

## Code Quality Heuristics (R-QUAL)

Heuristic rules that detect code patterns commonly seen in AI-generated or over-engineered extensions. These are advisory-only — they flag code that EGO reviewers are likely to question but do not block submission.

### R-QUAL-01: Excessive try-catch density
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Extension code should not wrap every few lines in try-catch blocks.
- **Rationale**: Excessive try-catch usage is a hallmark of AI-generated code that defensively wraps everything. It obscures control flow, hides bugs, and makes the code harder to review. Well-structured GNOME extensions use try-catch sparingly for specific error-prone operations (file I/O, DBus calls).
- **Fix**: Remove unnecessary try-catch blocks. Let errors propagate naturally and handle them at appropriate boundaries. Use try-catch only around operations that can legitimately fail (network, file system, DBus).

### R-QUAL-02: Impossible state checks
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Extension code should not check for states that are impossible given its configuration. For example, checking `Main.sessionMode.isLocked` without declaring `unlock-dialog` in `session-modes`.
- **Rationale**: If the extension does not declare `unlock-dialog` in `session-modes`, it is never active on the lock screen, so checking lock state is dead code. This pattern is common in AI-generated extensions that copy-paste lock-screen handling without understanding when it applies.
- **Fix**: Either add `"unlock-dialog"` to `session-modes` in `metadata.json` (if lock-screen support is intended) or remove the lock-state checking code.

### R-QUAL-03: Over-engineered async coordination
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Extension code should not use patterns like `_pendingDestroy` combined with `_initializing` flags for async lifecycle coordination.
- **Rationale**: This pattern appears in AI-generated extensions that over-engineer enable/disable lifecycle management. GNOME Shell guarantees that `disable()` runs after `enable()` completes, so complex coordination flags are unnecessary and indicate misunderstanding of the extension lifecycle.
- **Fix**: Remove coordination flags. Trust the GNOME Shell extension lifecycle: `enable()` and `disable()` are called sequentially. If async operations need cleanup, use `GLib.Source.remove()` or `Gio.Cancellable`.

### R-QUAL-04: Module-level mutable state
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Extension code should avoid declaring mutable variables (`let` or `var`) at module scope (outside any class or function).
- **Rationale**: Module-level mutable state persists across enable/disable cycles, leading to subtle bugs. GNOME Shell extensions should keep all mutable state inside the `Extension` class instance, which is created fresh on each enable cycle.
- **Fix**: Move mutable state into the Extension class as instance properties. Use `const` for module-level declarations that are truly constant (imports, enums, configuration).

### R-QUAL-05: Empty catch blocks
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Extension code should not have empty `catch` blocks that silently swallow errors.
- **Rationale**: Empty catch blocks hide bugs and make debugging impossible. If an error occurs, it disappears silently. At minimum, errors should be logged with `console.debug()` or `console.error()`.
- **Fix**: Add error logging to catch blocks: `catch (e) { console.debug('Operation failed:', e.message); }`. If the error is truly expected and ignorable, add a comment explaining why.

---

## Metadata — Extended (R-META, continued)

Additional metadata rules from enhanced check-metadata.py checks.

### R-META-13: UUID must contain @
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: The `uuid` field in `metadata.json` must contain an `@` character.
- **Rationale**: The standard UUID format for GNOME Shell extensions is `extension-name@domain`. While the `@` is not strictly enforced by GNOME Shell itself, EGO requires it and reviewers will reject UUIDs without it.
- **Fix**: Add an `@` and domain to the UUID: `my-extension@example.com`.

### R-META-14: Non-standard metadata fields
- **Severity**: advisory
- **Checked by**: check-metadata.py
- **Rule**: `metadata.json` should only contain recognized fields (`uuid`, `name`, `description`, `shell-version`, `session-modes`, `settings-schema`, `url`, `version`, `gettext-domain`, `original-author`, `donations`).
- **Rationale**: Non-standard fields are ignored by GNOME Shell and EGO. Their presence often indicates AI-generated metadata that hallucinated npm or other ecosystem conventions. Reviewers may question unfamiliar fields.
- **Fix**: Remove any fields not in the recognized set. Use `url` instead of `homepage`, and remove fields like `author`, `license`, `version-name`, or `bug-report-url`.

### R-META-15: Deprecated version field
- **Severity**: advisory
- **Checked by**: check-metadata.py
- **Rule**: `metadata.json` should not contain a `version` field.
- **Rationale**: The `version` field is deprecated. EGO manages extension versioning automatically and increments it on each upload. Including a manual version number is harmless but unnecessary and may confuse contributors.
- **Fix**: Remove `"version"` from `metadata.json`.

---

## Package — Extended (R-PKG, continued)

Additional package validation rules.

### R-PKG-10: No nested zip structure
- **Severity**: blocking
- **Checked by**: check-package.sh
- **Rule**: The zip archive must have `extension.js` and `metadata.json` at the archive root, not nested inside a subdirectory.
- **Rationale**: GNOME Shell extracts the zip directly into the extensions directory. If files are nested inside a subdirectory (e.g., `my-extension/extension.js`), the extension will fail to load because GNOME Shell expects files at the top level.
- **Fix**: Create the zip from inside the extension directory: `cd my-extension && zip -r ../my-extension.zip .` instead of `zip -r my-extension.zip my-extension/`.

### R-PKG-11: Missing compiled schemas
- **Severity**: blocking
- **Checked by**: check-package.sh
- **Rule**: If the extension includes `.gschema.xml` files in `schemas/`, the compiled `schemas/gschemas.compiled` file must also be present in the zip.
- **Rationale**: GNOME Shell loads GSettings schemas from the compiled binary, not the XML source. If the compiled file is missing, the extension's settings will fail to load at runtime.
- **Fix**: Run `glib-compile-schemas schemas/` before packaging to generate `schemas/gschemas.compiled`. Include it in the zip.

---

## Schema — Extended (R-SCHEMA, continued)

Additional GSettings schema validation rules.

### R-SCHEMA-06: Schema path must end with trailing slash
- **Severity**: blocking
- **Checked by**: check-schema.sh
- **Rule**: The `path` attribute of the `<schema>` element must end with a `/` character.
- **Rationale**: dconf paths are directory-like and must end with a trailing slash. A missing trailing slash causes GSettings to fail to locate the schema path at runtime.
- **Fix**: Add a trailing slash to the schema path: `path="/org/gnome/shell/extensions/my-extension/"`.
