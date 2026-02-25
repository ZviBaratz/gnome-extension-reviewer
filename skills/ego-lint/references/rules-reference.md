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
- **Checked by**: apply-patterns.py
- **Rule**: Extension code should not use the global `log()` function.
- **Rationale**: The global `log()` function is a legacy GJS API. Modern extensions should use `console.debug()` or `console.error()` for structured logging.
- **Fix**: Replace `log(msg)` with `console.debug(msg)`.
- **Tested by**: `tests/fixtures/logging-patterns@test/`

### R-LOG-03: No print() for debugging
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: Extension code should not use `print()` or `printerr()` for logging.
- **Rationale**: `print()` writes directly to stdout, which is not captured by the journal in typical GNOME Shell setups. It is a sign of leftover debug code.
- **Fix**: Replace with `console.debug()` or remove entirely.
- **Tested by**: `tests/fixtures/logging-patterns@test/`

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
- **Checked by**: apply-patterns.py
- **Rule**: Extension code should use ESM `import` syntax, not the legacy `imports.*` style.
- **Rationale**: GNOME 45+ requires ESM modules. The legacy `imports.*` style will not work on GNOME 45 and later. While older extensions may still use it for backward compatibility, new submissions should use ESM.
- **Fix**: Convert `const { Foo } = imports.gi.Foo` to `import Foo from 'gi://Foo'`. Convert `const ExtMe = imports.misc.extensionUtils` to `import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js'`.
- **Tested by**: `tests/fixtures/deprecated-imports/`

### R-DEPR-08: No spawn_command_line_sync
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: Extension code should not use `GLib.spawn_command_line_sync()`.
- **Rationale**: `spawn_command_line_sync` is deprecated in favor of `Gio.Subprocess`, which provides better error handling, cancellation support, and does not block the main loop.
- **Fix**: Use `new Gio.Subprocess({argv: [...], flags: ...})` instead.

### R-DEPR-09: No var declarations
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: Extension code should use `const` or `let` instead of `var`.
- **Rationale**: `var` has function scope rather than block scope, which causes subtle bugs in closures and loops. Modern JavaScript uses `const` (preferred) and `let` (when reassignment is needed). EGO reviewers view `var` usage as a sign of outdated or AI-generated code.
- **Fix**: Replace `var` with `const` (preferred) or `let` (when reassignment is needed).

### R-DEPR-10: No imports.format
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not use `imports.format`.
- **Rationale**: The `imports.format` module is deprecated and was removed in modern GJS. It provided a `format()` string method that is superseded by ES6 template literals.
- **Fix**: Replace `format()` calls with template literals: `` `my ${variable} string` ``.

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

### R-WEB-10: No clearTimeout()
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not use `clearTimeout()`.
- **Rationale**: `clearTimeout` is a browser API not available in GJS. GLib timer sources are removed with `GLib.Source.remove()`.
- **Fix**: Store the return value of `GLib.timeout_add()` and pass it to `GLib.Source.remove(sourceId)`.
- **Tested by**: `tests/fixtures/web-apis/`

### R-WEB-11: No clearInterval()
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not use `clearInterval()`.
- **Rationale**: Same as R-WEB-10. `clearInterval` is a browser API. Use `GLib.Source.remove()`.
- **Fix**: Store the return value of `GLib.timeout_add()` and pass it to `GLib.Source.remove(sourceId)`.
- **Tested by**: `tests/fixtures/web-apis/`

### R-WEB-12: Promise.race() without destroyed guards
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: Extension code should avoid `Promise.race()` without `_destroyed` guards.
- **Rationale**: `Promise.race()` resolves when the first promise completes, but the losing promises continue executing. In GNOME extensions, this can cause callbacks to run after `disable()` has been called, leading to use-after-free errors or acting on stale state.
- **Fix**: Ensure `_destroyed` is checked after the race resolves. Consider whether a simpler alternative (e.g., `Gio.Cancellable`) would be safer.

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

### R-SCHEMA-07: Schema filename should match schema ID
- **Severity**: advisory
- **Checked by**: check-schema.sh
- **Rule**: The schema filename should follow the convention `<schema-id>.gschema.xml` (e.g., `org.gnome.shell.extensions.my-ext.gschema.xml` for schema ID `org.gnome.shell.extensions.my-ext`).
- **Rationale**: While GNOME Shell does not enforce a filename convention, mismatched filenames cause confusion during review and maintenance. EGO reviewers expect the filename to match the schema ID for clarity.
- **Fix**: Rename the schema file to match its ID: `mv schemas/old-name.gschema.xml schemas/org.gnome.shell.extensions.your-extension.gschema.xml`.

---

## Security (R-SEC)

Rules for security-sensitive patterns that will cause EGO rejection.

### R-SEC-01: No eval()
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not use `eval()`.
- **Rationale**: `eval()` executes arbitrary code strings, creating a code injection attack surface. No legitimate GNOME extension use case requires it.
- **Fix**: Remove `eval()`. Use `JSON.parse()` for data parsing, lookup tables for dynamic dispatch.
- **Tested by**: `tests/fixtures/security-patterns@test/`

### R-SEC-02: No new Function()
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not use `new Function()`.
- **Rationale**: `new Function()` is equivalent to `eval()` — it creates a function from a code string, enabling code injection.
- **Fix**: Replace with a direct function definition or a lookup table.
- **Tested by**: `tests/fixtures/security-patterns@test/`

### R-SEC-03: Use HTTPS instead of HTTP
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: Network URLs should use HTTPS, not HTTP (except localhost/127.0.0.1/[::1]).
- **Rationale**: HTTP traffic is unencrypted and vulnerable to man-in-the-middle attacks. EGO reviewers expect HTTPS for any external network communication.
- **Fix**: Change `http://` to `https://`.
- **Tested by**: `tests/fixtures/security-patterns@test/`

### R-SEC-04: No pkexec/sudo
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not use `pkexec` or `sudo` for privilege escalation.
- **Rationale**: Privilege escalation is a near-instant rejection from EGO reviewers. Extensions should not require root access. Hardware access can be achieved through udev rules or systemd services with capabilities.
- **Fix**: Use a udev rule to grant write access to sysfs files, or a systemd service with capabilities.
- **Tested by**: `tests/fixtures/security-patterns@test/` (fixture does not include pkexec, but rule matches in hara-hachi-bu)

### R-SEC-05: No shell injection via /bin/sh -c
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: Subprocess calls should not use `/bin/sh -c` to execute shell strings.
- **Rationale**: Passing commands through a shell interpreter risks command injection if any part of the command is derived from user input or external data. Using an explicit argv array avoids this risk.
- **Fix**: Pass command and arguments as separate argv array elements instead of a shell string.
- **Tested by**: `tests/fixtures/security-patterns@test/`

---

## Imports — Extended (R-IMPORT, continued)

### R-IMPORT-08: No Shell UI modules in prefs.js
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: `prefs.js` must not import Shell UI modules via `resource:///org/gnome/shell/ui/`.
- **Rationale**: The preferences window runs in a separate GTK process that does not have access to GNOME Shell's UI modules. Importing them will cause an error when opening preferences.
- **Fix**: Use only GTK/Adw/Gio/GLib in preferences code. Shell UI modules are only available in the extension runtime.

---

## Code Quality Heuristics — Extended (R-QUAL, continued)

### R-QUAL-06: Excessive _destroyed flag density
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Extension code should not have an excessive density of `_destroyed`, `_pendingDestroy`, or `_initializing` checks (ratio > 0.02 with >= 10 occurrences).
- **Rationale**: High density of destroyed-flag checks indicates over-defensive coding, typically from AI-generated code that inserts guards after every operation. This makes code harder to read and maintain.
- **Fix**: Trust the GNOME Shell extension lifecycle. Use a single `_destroyed` check at the entry point of async callbacks, not between every line.
- **Tested by**: `tests/fixtures/destroyed-density@test/`

### R-QUAL-07: No mock/test code in production
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Extension submissions should not contain mock or test files (MockDevice.js, test*.js, *.spec.js) or runtime mock triggers (MOCK_MODE, use_mock).
- **Rationale**: Mock and test code is for development only. Shipping it in a production extension wastes space, confuses reviewers, and suggests an unclean build process.
- **Fix**: Remove mock/test files from the extension directory. Add them to `.gitignore` or a separate `tests/` directory excluded from packaging.
- **Tested by**: `tests/fixtures/mock-in-production@test/`

### R-QUAL-08: No resource allocation in constructors
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Constructors should not call `this.getSettings()`, `.connect()`, `.connectObject()`, `timeout_add`, or `new Gio.DBusProxy()`.
- **Rationale**: GNOME Shell extensions should perform resource allocation in `enable()` and cleanup in `disable()`. Allocating resources in constructors means they persist across enable/disable cycles, leading to resource leaks and zombie signal handlers.
- **Fix**: Move resource allocation from `constructor()`/`_init()` to `enable()`. Move cleanup to `disable()`.

---

## Files — Extended (R-FILE, continued)

### R-FILE-06: No minified or bundled JavaScript
- **Severity**: blocking
- **Checked by**: ego-lint.sh
- **Rule**: Extension code must not be minified or bundled (webpack, rollup, etc.).
- **Rationale**: EGO reviewers must be able to read and audit all code. Minified code (lines > 500 chars) or bundled code (webpack boilerplate) cannot be reviewed and will be rejected.
- **Fix**: Submit readable, unminified source code. Do not use bundlers for GNOME extensions — GJS supports ESM imports natively.
- **Tested by**: `tests/fixtures/minified-js@test/`

---

## AI Slop Signals — Extended (R-SLOP, continued)

### R-SLOP-07: Magic button numbers
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: Extension code should use `Clutter.BUTTON_PRIMARY`, `Clutter.BUTTON_MIDDLE`, and `Clutter.BUTTON_SECONDARY` instead of magic numbers 1, 2, 3.
- **Rationale**: Magic button numbers are a common AI-generated code pattern. Using Clutter constants is more readable and follows GNOME coding conventions.
- **Fix**: Replace `.get_button() === 1` with `.get_button() === Clutter.BUTTON_PRIMARY`, 2 with `Clutter.BUTTON_MIDDLE`, 3 with `Clutter.BUTTON_SECONDARY`.

---

## Lifecycle (R-LIFE)

Rules for extension lifecycle management: enable/disable hooks, signal cleanup, and timeout tracking.

### R-LIFE-01: Signal Balance
- **Severity**: advisory
- **Checked by**: check-lifecycle.py
- **Rule**: Detects imbalance between manual `.connect()` and `.disconnect()` calls (threshold: >2 imbalance).
- **Rationale**: Unmatched signal connections are the #1 cause of extension rejections. Leaked signals cause memory leaks and crash loops.
- **Fix**: For each `.connect()` call, ensure a matching `.disconnect()` in disable/destroy. Consider using `connectObject()` for automatic cleanup.
- **Tested by**: `tests/fixtures/lifecycle-basic@test/`

### R-LIFE-02: Untracked Timeouts
- **Severity**: advisory
- **Checked by**: check-lifecycle.py
- **Rule**: `timeout_add` or `idle_add` call whose return value is not stored.
- **Rationale**: Without the source ID, the timeout cannot be removed in disable(), causing callbacks after extension teardown.
- **Fix**: Store the return value: `this._timeoutId = GLib.timeout_add(...)` and call `GLib.Source.remove(this._timeoutId)` in disable().
- **Tested by**: `tests/fixtures/lifecycle-basic@test/`

### R-LIFE-03: Missing enable/disable
- **Severity**: blocking
- **Checked by**: check-lifecycle.py
- **Rule**: extension.js must define both `enable()` and `disable()` methods.
- **Rationale**: These are the fundamental lifecycle hooks. Missing either means the extension cannot be properly managed.
- **Fix**: Add the missing method. `disable()` must reverse everything `enable()` sets up.
- **Tested by**: `tests/fixtures/lifecycle-basic@test/`

### R-LIFE-04: connectObject Migration Advisory
- **Severity**: advisory
- **Checked by**: check-lifecycle.py
- **Rule**: Suggests `connectObject()` when 3+ manual connect/disconnect pairs exist without any connectObject usage.
- **Rationale**: `connectObject()` provides automatic cleanup via `disconnectObject(this)`, reducing boilerplate and leak risk.
- **Fix**: Migrate manual connect/disconnect pairs to `connectObject()` with `this` as the last argument.
- **Tested by**: `tests/fixtures/lifecycle-basic@test/`

### R-LIFE-05: Async/await without _destroyed guard
- **Severity**: advisory
- **Checked by**: check-lifecycle.py
- **Rule**: Extensions using `async`/`await` should have a `_destroyed` or `_isDestroyed` flag to guard against acting on stale state after `disable()`.
- **Rationale**: When an async function suspends at `await`, the extension may be disabled before the promise resolves. Without a `_destroyed` guard, the resumed code will operate on a torn-down extension, causing errors or zombie behavior.
- **Fix**: Add a `_destroyed = false` flag in `enable()`, set it to `true` in `disable()`, and check it after each `await`: `if (this._destroyed) return;`.

### R-LIFE-06: Timeout callback missing SOURCE_REMOVE/SOURCE_CONTINUE
- **Severity**: advisory
- **Checked by**: check-lifecycle.py
- **Rule**: Callbacks passed to `GLib.timeout_add()` or `GLib.idle_add()` should explicitly return `GLib.SOURCE_REMOVE` or `GLib.SOURCE_CONTINUE`.
- **Rationale**: If a timeout callback does not return `GLib.SOURCE_REMOVE` (or `false`), the default return value of `undefined` is falsy and the timeout is removed — but this is implicit and confusing. If the intent is to repeat, forgetting `SOURCE_CONTINUE` silently breaks the timer. Explicit return values make the intent clear and are expected by EGO reviewers.
- **Fix**: Add `return GLib.SOURCE_REMOVE;` for one-shot timeouts or `return GLib.SOURCE_CONTINUE;` for repeating timeouts at the end of the callback.

### R-LIFE-07: D-Bus proxy without signal disconnect
- **Severity**: advisory
- **Checked by**: check-lifecycle.py
- **Rule**: Extensions that create D-Bus proxies (`Gio.DBusProxy`, `makeProxyWrapper`) should disconnect their signal handlers in `disable()`.
- **Rationale**: D-Bus proxy signals persist across enable/disable cycles if not explicitly disconnected. This causes leaked signal handlers that fire callbacks on a disabled extension, leading to errors and resource leaks.
- **Fix**: Call `.disconnect()` or `.disconnectObject()` on the proxy in `disable()` to clean up signal handlers.

### R-LIFE-08: File monitor without cancel
- **Severity**: advisory
- **Checked by**: check-lifecycle.py
- **Rule**: Extensions that create file monitors (`monitor_file()`, `monitor_directory()`, `monitor_children()`) must call `.cancel()` in `disable()`.
- **Rationale**: File monitors continue to fire `changed` signals after the extension is disabled if not cancelled. This causes callbacks to run on torn-down state, leading to errors.
- **Fix**: Store the monitor reference and call `this._monitor.cancel()` in `disable()`.

### R-LIFE-09: Keybinding add without remove
- **Severity**: blocking
- **Checked by**: check-lifecycle.py
- **Rule**: Every `Main.wm.addKeybinding()` call must have a matching `Main.wm.removeKeybinding()` call.
- **Rationale**: Keybindings that are not removed in `disable()` persist after the extension is disabled. They continue to intercept key events, potentially conflicting with other extensions or GNOME Shell itself. This is a common cause of EGO rejection.
- **Fix**: Call `Main.wm.removeKeybinding('keybinding-name')` in `disable()` for each keybinding added in `enable()`.

---

## Files — Extended (R-FILE, continued)

### R-FILE-07: Missing Default Export
- **Severity**: advisory
- **Checked by**: check-lifecycle.py
- **Rule**: extension.js missing `export default class` — required for GNOME 45+.
- **Rationale**: GNOME 45 switched to ESM modules. Extensions must use `export default class` extending `Extension`.
- **Fix**: Use `export default class MyExtension extends Extension { ... }` pattern.
- **Tested by**: `tests/fixtures/lifecycle-basic@test/`

---

## AI Slop Signals — Extended (R-SLOP, continued)

### R-SLOP-08: Hallucinated Meta/Shell APIs
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: Detects `Meta.Screen`, `Meta.Cursor`, `Shell.ActionMode.ALL`, `Shell.WindowTracker.get_default().get_active_window`.
- **Rationale**: These APIs don't exist in GNOME Shell. LLMs hallucinate them from outdated docs or other frameworks.
- **Fix**: Use `global.display`/`Meta.Display` instead of `Meta.Screen`. Check https://gjs-docs.gnome.org.
- **Tested by**: `tests/fixtures/hallucinated-apis@test/`

### R-SLOP-09: St Widget Setter Methods
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: `St.Button.set_label()`, `St.Label.set_text()`, `St.Widget.set_icon_name()` — setter methods don't exist.
- **Rationale**: St widgets use GObject properties, not GTK-style setter methods.
- **Fix**: Use property assignment: `button.label = 'text'` instead of `button.set_label('text')`.
- **Tested by**: `tests/fixtures/hallucinated-apis@test/`

### R-SLOP-10: Hallucinated Clutter Methods
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: `Clutter.Actor.show_all()`, `hide_all()`, `set_position()`, `set_size()` are GTK methods, not Clutter.
- **Rationale**: LLMs confuse GTK and Clutter widget APIs.
- **Fix**: Use `actor.show()`/`hide()` for visibility. Use `actor.set({x, y, width, height})` for geometry.
- **Tested by**: `tests/fixtures/hallucinated-apis@test/`

### R-SLOP-11: Non-existent GLib Methods
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: `GLib.timeout_add_seconds_full` and `GLib.source_remove` don't exist in GJS bindings.
- **Rationale**: LLMs confuse C API names with GJS binding names.
- **Fix**: Use `GLib.timeout_add_seconds()` and `GLib.Source.remove()`.
- **Tested by**: `tests/fixtures/hallucinated-apis@test/`

### R-SLOP-12: typeof super.destroy Guard
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: `typeof super.destroy === 'function'` check is unnecessary — super.destroy() always exists on GObject classes.
- **Rationale**: Canonical AI slop signal identified by JustPerfection in the GNOME AI policy blog post.
- **Fix**: Remove the typeof check and call `super.destroy()` directly.
- **Tested by**: `tests/fixtures/hallucinated-apis@test/`

### R-SLOP-13: Redundant instanceof this
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: `this instanceof ClassName` inside a class method is always true.
- **Rationale**: Classic defensive programming pattern that AI generates unnecessarily.
- **Fix**: Remove the redundant instanceof check.
- **Tested by**: `tests/fixtures/hallucinated-apis@test/`

### R-SLOP-16: Hallucinated GLib.file_get_contents
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not use `GLib.file_get_contents()`.
- **Rationale**: `GLib.file_get_contents()` does not exist in GJS. LLMs hallucinate this from the C API (`g_file_get_contents`), but GJS does not expose it. The correct approach is to use `Gio.File` methods.
- **Fix**: Use `const file = Gio.File.new_for_path(path); const [ok, contents] = file.load_contents(null);` then `new TextDecoder().decode(contents)` to get a string.

---

## Security — Extended (R-SEC, continued)

### R-SEC-06: run_dispose Usage
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: `GObject.run_dispose()` should not be used unless absolutely necessary.
- **Rationale**: `run_dispose()` forcefully disposes GObject resources and can cause issues if not used carefully.
- **Fix**: Remove `run_dispose()` call. If genuinely needed, add a comment explaining why.
- **Tested by**: `tests/fixtures/hallucinated-apis@test/`

### R-SEC-07: Clipboard access disclosure
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: Extensions using `St.Clipboard` must disclose clipboard access in the `metadata.json` description.
- **Rationale**: Clipboard access is a sensitive permission. EGO reviewers expect the extension description to mention it so users can make an informed decision before installing.
- **Fix**: Add clipboard usage disclosure to your extension description on EGO (e.g., "This extension reads/writes the system clipboard").

### R-SEC-08: No telemetry or analytics
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: Extension code must not contain telemetry, analytics, or user tracking code (`analytics`, `telemetry`, `trackEvent`, `trackPage`, `GA_TRACKING_ID`, `gtag`).
- **Rationale**: Telemetry and analytics are explicitly banned in GNOME extensions. EGO reviewers will reject any extension that tracks user behavior.
- **Fix**: Remove all telemetry/analytics code. EGO explicitly bans user tracking.

### R-SEC-09: Extension system interference
- **Severity**: advisory
- **Checked by**: apply-patterns.py
- **Rule**: Extension code should not use `Main.extensionManager`, `ExtensionManager`, or `lookupByUUID` to interact with or modify other extensions.
- **Rationale**: Interfering with the extension system (enabling, disabling, or inspecting other extensions) is discouraged and requires explicit justification during EGO review.
- **Fix**: Avoid interacting with other extensions unless absolutely necessary. If needed, document the justification clearly in the EGO submission.

### R-SEC-10: No pip install
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code and scripts must not run `pip install`.
- **Rationale**: GNOME extensions must not automatically install packages. Automatic package installation is a security risk and a policy violation that will cause immediate EGO rejection. Extensions should be self-contained or document manual dependency installation steps.
- **Fix**: Remove automatic `pip install` commands. If a Python dependency is needed, document the manual installation steps in the extension description or README.

### R-SEC-11: No npm install
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code and scripts must not run `npm install`.
- **Rationale**: Same as R-SEC-10. Automatic package installation is banned. Extensions must not install npm packages at runtime or during setup scripts that run without explicit user action.
- **Fix**: Remove automatic `npm install` commands. If a Node.js dependency is needed, document the manual installation steps.

### R-SEC-12: No system package installation (apt/dnf/yum/pacman/zypper)
- **Severity**: blocking
- **Checked by**: apply-patterns.py
- **Rule**: Extension code and scripts must not run system package managers (`apt`, `apt-get`, `dnf`, `yum`, `pacman`, `zypper`).
- **Rationale**: Same as R-SEC-10. Automatic system package installation requires root access and is a severe security risk. EGO reviewers will reject any extension that attempts to install system packages.
- **Fix**: Remove automatic package installation commands. Document any required system packages in the extension description so users can install them manually.

---

## Code Quality Heuristics — Extended (R-QUAL, continued)

### R-QUAL-10: Code Volume
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Flags extensions with more than 8000 non-blank JS lines.
- **Rationale**: Large codebases are harder to review and more likely to contain unreviewed AI-generated code.
- **Fix**: Ensure all code is necessary and has been manually reviewed.
- **Tested by**: `tests/fixtures/quality-signals@test/`

### R-QUAL-11: Comment Density
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Flags files where >40% of lines (after first 10) are comments.
- **Rationale**: Excessive comments explaining obvious code is a strong AI slop signal.
- **Fix**: Remove redundant comments. Only keep comments that explain non-obvious logic or API quirks.
- **Tested by**: `tests/fixtures/quality-signals@test/`

---

## Metadata — Extended (R-META, continued)

### R-META-16: Missing gettext-domain
- **Severity**: advisory
- **Checked by**: check-metadata.py
- **Rule**: locale/ directory exists but gettext-domain not set in metadata.json.
- **Rationale**: Without gettext-domain, translations in locale/ won't be used.
- **Fix**: Add `"gettext-domain": "your-extension-name"` to metadata.json.
- **Tested by**: `tests/fixtures/metadata-polish@test/`

### R-META-17: Future shell-version
- **Severity**: advisory
- **Checked by**: check-metadata.py
- **Rule**: shell-version entry newer than current stable (48).
- **Rationale**: Speculative or AI-hallucinated shell versions indicate unreviewed metadata.
- **Fix**: Only list shell versions that have been tested.
- **Tested by**: `tests/fixtures/metadata-polish@test/`

### R-META-18: Invalid donations field keys
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: The `donations` field in `metadata.json` must only contain keys from the allowlist: `buymeacoffee`, `custom`, `github`, `kofi`, `liberapay`, `opencollective`, `patreon`, `paypal`.
- **Rationale**: EGO validates the `donations` field and rejects extensions with unrecognized donation platform keys. Using an invalid key will prevent submission.
- **Fix**: Use only the allowed keys. Remove any keys not in the allowlist (e.g., remove `"stripe"` or `"venmo"`).

### R-META-19: Invalid session-modes value
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: Each entry in the `session-modes` array must be either `"user"` or `"unlock-dialog"`.
- **Rationale**: GNOME Shell only recognizes these two session modes. Any other value will be silently ignored or cause validation failure on EGO.
- **Fix**: Remove invalid session-modes entries. Use `"user"` for normal desktop mode and `"unlock-dialog"` for lock screen access.

### R-META-20: version-name format
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: If present, the `version-name` field must be 1-16 characters, containing only alphanumeric characters, spaces, and dots, and must not consist entirely of dots or spaces.
- **Rationale**: EGO validates the `version-name` format on upload. Values that are too long, contain special characters, or are blank will cause submission failure.
- **Fix**: Use a short version label like `"1.0"`, `"2.1 beta"`, or `"v3"`. Remove the field entirely if not needed.

### R-META-21: Invalid shell-version entry
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: Each entry in the `shell-version` array must be a valid version string matching the format `"NN"` (e.g., `"45"`) or `"NN.NN"` (e.g., `"3.38"`).
- **Rationale**: GNOME Shell validates version strings at install time. Invalid entries (empty strings, non-numeric values, trailing dots) will prevent the extension from loading.
- **Fix**: Use valid version strings like `"45"`, `"46"`, `"47"`, `"48"`, or `"3.38"` for legacy versions.

### R-META-22: Missing url field
- **Severity**: advisory
- **Checked by**: check-metadata.py
- **Rule**: `metadata.json` should contain a `url` field.
- **Rationale**: The `url` field is displayed on the EGO listing page and helps users find the project homepage, documentation, and issue tracker. Its absence makes the extension harder for users to evaluate and for reviewers to verify.
- **Fix**: Add `"url": "https://github.com/your-username/your-extension"` to `metadata.json`.

### R-META-23: Too many development shell-version entries
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: The `shell-version` array must not contain more than one development (unreleased) GNOME version.
- **Rationale**: Development versions are versions newer than the current stable release (48). Listing multiple development versions is a strong indicator of AI-hallucinated metadata, since only one GNOME development version exists at any time. EGO will reject such submissions.
- **Fix**: Remove extra development versions from `shell-version`. At most one development version (the current GNOME development branch) should be listed, and only if you have actually tested against it.

### R-META-24: Empty donations field
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: If the `donations` field is present in `metadata.json`, it must not be an empty object.
- **Rationale**: An empty `donations` object (`"donations": {}`) serves no purpose and will be flagged by EGO validation. It is typically a leftover from AI-generated metadata templates.
- **Fix**: Either add valid donation links (e.g., `"donations": {"github": "your-username"}`) or remove the `donations` field entirely.

### R-META-25: ESM imports with pre-45 shell-version
- **Severity**: blocking
- **Checked by**: check-metadata.py
- **Rule**: If `extension.js` uses ESM imports (`import ... from ...`), the `shell-version` array must not include GNOME versions before 45 (e.g., `"40"`, `"41"`, `"42"`, `"43"`, `"44"`).
- **Rationale**: ESM modules were introduced in GNOME 45. Extensions using ESM syntax cannot run on GNOME 40-44, which used the legacy `imports.*` module system. Listing pre-45 versions with ESM code is contradictory and indicates untested compatibility claims.
- **Fix**: Remove pre-45 versions from `shell-version` if your extension uses ESM imports. If you need to support older GNOME versions, you must use the legacy `imports.*` module system (or maintain separate branches).

---

## Package — Extended (R-PKG, continued)

### R-PKG-12: Package Size
- **Severity**: advisory
- **Checked by**: check-package.sh
- **Rule**: Zip file exceeds 5MB.
- **Rationale**: Large packages slow down review and may contain unnecessary files.
- **Fix**: Remove unnecessary files (build artifacts, documentation, test fixtures) from the package.

---

## Preferences (R-PREFS)

Rules for `prefs.js` validation and EGO compliance.

### R-PREFS-01: Dual prefs pattern
- **Severity**: blocking
- **Checked by**: check-prefs.py
- **Rule**: `prefs.js` must not define both `getPreferencesWidget()` and `fillPreferencesWindow()`.
- **Rationale**: These are mutually exclusive preference APIs. `getPreferencesWidget()` creates a standalone widget, while `fillPreferencesWindow()` populates an existing `Adw.PreferencesWindow`. Defining both indicates confusion about the prefs API and will cause unpredictable behavior. GNOME 45+ uses `fillPreferencesWindow()`.
- **Fix**: Remove one of the two methods. For GNOME 45+, use `fillPreferencesWindow(window)` and add pages/groups to the provided window. For older versions, use `getPreferencesWidget()`.

### R-PREFS-02: Missing default export
- **Severity**: advisory
- **Checked by**: check-prefs.py
- **Rule**: `prefs.js` should use `export default class` extending `ExtensionPreferences`.
- **Rationale**: GNOME 45 switched to ESM modules. The preferences entry point must use `export default class` extending `ExtensionPreferences` for the extension system to load it correctly.
- **Fix**: Use `export default class MyPrefs extends ExtensionPreferences { ... }` pattern.

### R-PREFS-03: Shell UI resource paths in prefs
- **Severity**: blocking
- **Checked by**: check-prefs.py
- **Rule**: `prefs.js` must not import modules via `resource:///org/gnome/shell/ui/` paths.
- **Rationale**: The preferences window runs in a separate GTK process that does not have access to GNOME Shell's UI modules. Importing Shell UI modules (e.g., `Main`, `PanelMenu`, `PopupMenu`) in `prefs.js` will cause an import error when the user opens preferences.
- **Fix**: Use only GTK/Adw/Gio/GLib imports in `prefs.js`. Shell UI modules are only available in `extension.js` and its runtime imports.

---

## Version Compatibility (R-VER)

Rules for APIs removed or changed in specific GNOME Shell versions. These rules are **version-gated**: they only fire when the extension's `shell-version` in `metadata.json` targets the relevant GNOME version or newer. For example, R-VER46-01 only triggers if the extension lists GNOME 46 or later in `shell-version`.

### GNOME 46 (R-VER46)

### R-VER46-01: add_actor() removed
- **Severity**: blocking
- **Checked by**: apply-patterns.py (version-gated, min-version: 46)
- **Rule**: Extension code must not use `.add_actor()` when targeting GNOME 46+.
- **Rationale**: `Clutter.Container.add_actor()` was removed in GNOME 46. It was the legacy method for adding child actors to containers. The replacement `add_child()` has been available since GNOME 3.x and is the standard method.
- **Fix**: Replace `.add_actor(child)` with `.add_child(child)`.

### R-VER46-02: remove_actor() removed
- **Severity**: blocking
- **Checked by**: apply-patterns.py (version-gated, min-version: 46)
- **Rule**: Extension code must not use `.remove_actor()` when targeting GNOME 46+.
- **Rationale**: `Clutter.Container.remove_actor()` was removed in GNOME 46 alongside `add_actor()`. The replacement `remove_child()` has been available since GNOME 3.x.
- **Fix**: Replace `.remove_actor(child)` with `.remove_child(child)`.

### R-VER46-03: Clutter.cairo_set_source_color removed
- **Severity**: blocking
- **Checked by**: apply-patterns.py (version-gated, min-version: 46)
- **Rule**: Extension code must not use `Clutter.cairo_set_source_color()` when targeting GNOME 46+.
- **Rationale**: The `Clutter.cairo_set_source_color()` helper function was removed in GNOME 46. Cairo color operations should use the cairo context's own methods instead.
- **Fix**: Replace `Clutter.cairo_set_source_color(cr, color)` with `cr.setSourceColor(color)`.

### R-VER46-04: Gio.UnixInputStream moved
- **Severity**: blocking
- **Checked by**: apply-patterns.py (version-gated, min-version: 46)
- **Rule**: Extension code must not use `Gio.UnixInputStream` when targeting GNOME 46+.
- **Rationale**: In GNOME 46, Unix-specific I/O classes were moved from `Gio` to a separate `GioUnix` namespace. `Gio.UnixInputStream` no longer exists; it was relocated to `GioUnix.InputStream`.
- **Fix**: Replace `import Gio from 'gi://Gio'` with `import GioUnix from 'gi://GioUnix'` and use `GioUnix.InputStream` instead of `Gio.UnixInputStream`.

### R-VER46-05: ExtensionState enum renamed
- **Severity**: blocking
- **Checked by**: apply-patterns.py (version-gated, min-version: 46)
- **Rule**: Extension code must not use the old `ExtensionState` enum values (`ENABLED`, `DISABLED`, `INITIALIZED`, `DEACTIVATING`, `ACTIVATING`) when targeting GNOME 46+.
- **Rationale**: The `ExtensionState` enum values were renamed in GNOME 46 to better reflect their meaning: `ENABLED` became `ACTIVE`, `DISABLED` became `INACTIVE`, `ACTIVATING` became `ENABLING`, and `DEACTIVATING` became `DISABLING`.
- **Fix**: Replace `ExtensionState.ENABLED` with `ExtensionState.ACTIVE`, `DISABLED` with `INACTIVE`, `ACTIVATING` with `ENABLING`, and `DEACTIVATING` with `DISABLING`.

### GNOME 47 (R-VER47)

### R-VER47-01: Clutter.Color removed
- **Severity**: blocking
- **Checked by**: apply-patterns.py (version-gated, min-version: 47)
- **Rule**: Extension code must not use `Clutter.Color` when targeting GNOME 47+.
- **Rationale**: `Clutter.Color` was removed in GNOME 47. Color handling was moved to the Cogl library, which is the underlying graphics layer.
- **Fix**: Replace `Clutter.Color` with `Cogl.Color`. Import Cogl with `import Cogl from 'gi://Cogl'` and use `new Cogl.Color()`.

### GNOME 48 (R-VER48)

### R-VER48-01: Clutter.Image removed
- **Severity**: blocking
- **Checked by**: apply-patterns.py (version-gated, min-version: 48)
- **Rule**: Extension code must not use `Clutter.Image` when targeting GNOME 48+.
- **Rationale**: `Clutter.Image` was removed in GNOME 48. Image content handling was moved to St (Shell Toolkit), which provides `St.ImageContent` as the replacement.
- **Fix**: Replace `Clutter.Image` with `St.ImageContent`. St is already available in extension runtime, so no additional imports are needed.

### R-VER48-02: Meta display functions moved to Meta.Compositor
- **Severity**: blocking
- **Checked by**: apply-patterns.py (version-gated, min-version: 48)
- **Rule**: Extension code must not call `Meta.disable_unredirect_for_display()`, `Meta.enable_unredirect_for_display()`, `Meta.get_window_actors()`, `Meta.get_window_group_for_display()`, or `Meta.get_top_window_group_for_display()` when targeting GNOME 48+.
- **Rationale**: These display management functions were moved from the `Meta` namespace to `Meta.Compositor` in GNOME 48. They are now accessible via `global.compositor`.
- **Fix**: Access these functions via `global.compositor` instead of `Meta` directly. For example, replace `Meta.get_window_actors()` with `global.compositor.get_window_actors()`.

### R-VER48-03: CursorTracker.get_for_display changed
- **Severity**: blocking
- **Checked by**: apply-patterns.py (version-gated, min-version: 48)
- **Rule**: Extension code must not use `CursorTracker.get_for_display()` when targeting GNOME 48+.
- **Rationale**: `Meta.CursorTracker.get_for_display()` was changed in GNOME 48. The cursor tracker is now accessed through the backend object instead of the display.
- **Fix**: Replace `Meta.CursorTracker.get_for_display(global.display)` with `global.backend.get_cursor_tracker()`.

### R-VER48-04: St.Widget.vertical deprecated
- **Severity**: advisory
- **Checked by**: apply-patterns.py (min-version: 48)
- **Rule**: The `.vertical` property on St widgets is deprecated in GNOME 48.
- **Rationale**: Will be removed around GNOME 50. Use the orientation property instead.
- **Fix**: Use `{orientation: Clutter.Orientation.VERTICAL}` instead of `{vertical: true}`.

### GNOME 44 (R-VER44)

### R-VER44-01: Meta.later_add() removed
- **Severity**: blocking
- **Checked by**: apply-patterns.py (min-version: 44)
- **Rule**: `Meta.later_add()` was removed in GNOME 44.
- **Rationale**: Replaced by the new Laters API accessed via the compositor.
- **Fix**: Use `global.compositor.get_laters().addLater(Meta.LaterType.BEFORE_REDRAW, callback)`.

### R-VER44-02: Meta.later_remove() removed
- **Severity**: blocking
- **Checked by**: apply-patterns.py (min-version: 44)
- **Rule**: `Meta.later_remove()` was removed in GNOME 44.
- **Rationale**: Replaced by the new Laters API accessed via the compositor.
- **Fix**: Use `global.compositor.get_laters().removeLater(id)`.

### R-VER46-06: Shell.BlurEffect.sigma replaced
- **Severity**: blocking
- **Checked by**: apply-patterns.py (min-version: 46)
- **Rule**: `Shell.BlurEffect.sigma` was replaced by `.radius` in GNOME 46.
- **Rationale**: The blur API was unified. The conversion formula is `radius = sigma * 2.0`.
- **Fix**: Use `.radius` instead of `.sigma`.

### GNOME 49 (R-VER49)

### R-VER49-01: Meta.Rectangle removed
- **Severity**: blocking
- **Checked by**: apply-patterns.py (min-version: 49)
- **Rule**: `Meta.Rectangle` was completely removed in GNOME 49.
- **Rationale**: Replaced by the Mtk toolkit rectangle type.
- **Fix**: Import `Mtk` from `'gi://Mtk'` and use `Mtk.Rectangle` instead.

### R-VER49-02: Clutter.ClickAction removed
- **Severity**: blocking
- **Checked by**: apply-patterns.py (min-version: 49)
- **Rule**: `Clutter.ClickAction` was removed in GNOME 49.
- **Rationale**: Replaced by the gesture-based input API.
- **Fix**: Use `new Clutter.ClickGesture()` instead.

### R-VER49-03: Clutter.TapAction removed
- **Severity**: blocking
- **Checked by**: apply-patterns.py (min-version: 49)
- **Rule**: `Clutter.TapAction` was removed in GNOME 49.
- **Rationale**: Replaced by the gesture-based input API.
- **Fix**: Use `new Clutter.LongPressGesture()` instead.

### R-VER49-04: Meta.Window.get_maximized() removed
- **Severity**: blocking
- **Checked by**: apply-patterns.py (min-version: 49)
- **Rule**: `Meta.Window.get_maximized()` was removed in GNOME 49.
- **Rationale**: Simplified window state API.
- **Fix**: Use `window.is_maximized()` instead.

### R-VER49-05: CursorTracker.set_pointer_visible() removed
- **Severity**: blocking
- **Checked by**: apply-patterns.py (min-version: 49)
- **Rule**: `CursorTracker.set_pointer_visible()` was removed in GNOME 49.
- **Rationale**: Replaced by inhibit/uninhibit pattern.
- **Fix**: Use `tracker.inhibit_cursor_visibility()` / `uninhibit_cursor_visibility()`.

---

## Code Quality Heuristics — Extended (R-QUAL, continued)

### quality/file-complexity: Per-file line count
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Warns if any single `.js` file exceeds 1000 non-blank lines.
- **Rationale**: Monolithic files are harder to review and maintain. EGO reviewers often suggest splitting large files into modules.
- **Fix**: Split large files into focused modules in a `lib/` directory.

### quality/debug-volume: Excessive console.debug() calls
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Warns if more than 20 `console.debug()` calls are found across the codebase.
- **Rationale**: While `console.debug()` is acceptable (unlike `console.log()`), excessive debug logging clutters the system journal and signals unfinished development.
- **Fix**: Remove or reduce debug logging to essential messages before submission.

### quality/notification-volume: Excessive Main.notify() calls
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Warns if more than 3 `Main.notify()` call sites are found.
- **Rationale**: Excessive system notifications are intrusive to users and reviewers push back on notification-heavy extensions.
- **Fix**: Reduce notification frequency; consider using the extension's own UI for status updates.

### quality/private-api: Private GNOME Shell API access
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Detects access to underscore-prefixed properties on GNOME Shell objects (`Main.panel._*`, `statusArea._*`, `quickSettings._*`, etc.).
- **Rationale**: Private APIs can break without notice between GNOME versions. Reviewers require justification and version pinning for private API usage.
- **Fix**: Document why the private API is necessary, which GNOME versions it was tested on, and pin `shell-version` accordingly.

### quality/gettext-pattern: Direct Gettext.dgettext() usage
- **Severity**: advisory
- **Checked by**: check-quality.py
- **Rule**: Warns when `Gettext.dgettext()` is used directly instead of the Extension API.
- **Rationale**: The `Extension` and `ExtensionPreferences` base classes provide `this.gettext()` which automatically uses the correct domain. Direct `dgettext` hardcodes the domain string.
- **Fix**: Use `this.gettext('string')` from the Extension base class instead of `Gettext.dgettext('domain', 'string')`.

---

## Metadata — Extended (R-META, continued)

### metadata/session-modes-consistency: SessionMode usage without declaration
- **Severity**: advisory
- **Checked by**: check-metadata.py
- **Rule**: Warns if the extension code references `Main.sessionMode.currentMode` or `sessionMode.isLocked` but `metadata.json` does not declare `session-modes` with `unlock-dialog`.
- **Rationale**: Code that checks session mode without the proper declaration is either dead code (the extension won't run in lock screen mode) or a misunderstanding of the lifecycle.
- **Fix**: Either add `"session-modes": ["user", "unlock-dialog"]` to metadata.json, or remove the session mode checks from the code.

---

## Inline Checks (ego-lint.sh)

### polkit-files: Polkit policy/rules file detection
- **Severity**: advisory
- **Checked by**: ego-lint.sh
- **Rule**: Detects `.policy` and `.rules` files in the extension directory.
- **Rationale**: Polkit policy files grant privilege escalation capabilities and require careful security review. Reviewers pay special attention to extensions shipping polkit rules.
- **Fix**: Document why polkit access is necessary. Ensure policy defaults use `auth_admin_keep` (not `yes`). Include reviewer notes explaining the privilege escalation model.
