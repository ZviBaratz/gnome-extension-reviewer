# Phase 1: Deep Read of Official GNOME Shell Extension Review Guidelines

**Date:** 2026-02-26
**Sources:** gjs.guide/extensions/review-guidelines, anatomy, session-modes, extension, imports-and-modules, preferences, translations, accessibility, search-provider, updates-and-breakage, upgrading/gnome-shell-{45,46,47,48,49,50}
**Method:** Line-by-line extraction of every MUST, SHOULD, MAY, recommendation, and implicit requirement. Cross-referenced against `ego-review-guidelines-research.md` and `gap-analysis.md`.

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
23. [Extension Class Structure](#23-extension-class-structure)
24. [Monkey-Patching and InjectionManager](#24-monkey-patching-and-injectionmanager)
25. [Network Access and Data Sharing](#25-network-access-and-data-sharing)
26. [Search Providers](#26-search-providers)
27. [Accessibility](#27-accessibility)
28. [Version-Specific API Changes (GNOME 45-50)](#28-version-specific-api-changes)
29. [GObject Patterns](#29-gobject-patterns)
30. [Updates and Breakage Philosophy](#30-updates-and-breakage-philosophy)

---

## 1. Initialization and Lifecycle

### Finding: Three core principles stated verbatim
- **Guideline text:** The guidelines begin with three numbered rules: (1) "Don't create or modify anything before `enable()` is called", (2) "Use `enable()` to create objects, connect signals and add main loop sources", (3) "Use `disable()` to cleanup anything done in `enable()`"
- **Severity:** MUST (foundational principles)
- **Current coverage:** Covered - R-INIT-01 (check-init.py), R-QUAL-08 (check-quality.py constructor-resources)
- **Gap:** None for the MUST. However, the three rules are stated as general guidelines, implying they should be treated as the review framework's organizing principle, not just three discrete checks. Our tools check specific instantiations but do not surface the principle itself.
- **Impact:** These are the most important rules -- violations are the #1 rejection cause.

### Finding: Static data structures ARE permitted during initialization
- **Guideline text:** From the review guidelines: Extensions MAY create "static data structures (objects like maps, constants)" and "Built-in JavaScript objects (Regexp, Map, Date)" during initialization. Also "Reasonable amounts of static data in constructor" and "ES6 class instances assigned to module scope variables."
- **Severity:** Allowed (clarification of MUST NOT)
- **Current coverage:** Partial - check-init.py uses a regex that could false-positive on `new Map()` or `new RegExp()` at module scope
- **Gap:** check-init.py's GObject constructor detection (R-INIT-01) uses `new\s+(St|Gio|GLib|Clutter|Meta|Shell|GObject|Pango|Soup|Atk|Gdk|Gtk|Adw|Graphene|Mtk|Cogl)\.` which correctly excludes built-in JS objects. However, `new Map()` at module scope might be incorrectly flagged by R-QUAL-08 if a custom class named `Map` is used. Low risk.
- **Impact:** Low -- false positives possible but rare.

### Finding: Module-scope mutable state is an AI slop indicator
- **Guideline text:** Not in the official guidelines directly, but R-QUAL-04 in our rules catches `let` or `var` at module scope. The guidelines say "MUST NOT create any objects...during initialization" which implicitly covers mutable state that holds GObjects.
- **Severity:** Advisory (our rule) / MUST (if the state holds GObjects)
- **Current coverage:** Covered - R-QUAL-04 (check-quality.py)
- **Gap:** The severity distinction between `let x = 0;` (advisory, just style) and `let proxy = new DBusProxy();` (MUST NOT, hard reject) is not granular in R-QUAL-04. Both get the same advisory treatment.
- **Impact:** Medium -- a module-scope `let` holding a GObject instance should be blocking, not advisory.

---

## 2. Object and Resource Cleanup

### Finding: "Any objects or widgets created" -- the word "any" is absolute
- **Guideline text:** "Any objects or widgets created by an extension MUST be destroyed in `disable()`"
- **Severity:** MUST (hard reject)
- **Current coverage:** Partial - R-LIFE-01 (signal balance), check-lifecycle.py, check-resources.py (cross-file), lifecycle-checklist.md
- **Gap:** No general "created in enable() but not destroyed in disable()" check exists. The signal balance heuristic catches signal leaks, and cross-file resource tracking catches certain resource types, but a general `new SomeWidget()` in enable() without a matching `.destroy()` in disable() is not tracked systematically. This would require full data-flow analysis which is beyond static regex.
- **Impact:** High -- this is the single most common rejection reason.

### Finding: "dynamically stored memory MUST be cleared" -- nulling references
- **Guideline text:** "All dynamically stored memory MUST be cleared in `disable()`"
- **Severity:** MUST (hard reject)
- **Current coverage:** Tier 3 Only - lifecycle-checklist.md
- **Gap:** No automated check verifies that `= null` follows `.destroy()` calls. The checklist covers this but the linter does not check for `this._foo.destroy()` without a subsequent `this._foo = null`.
- **Impact:** Medium -- reviewers frequently flag this. The pattern `widget.destroy()` without `widget = null` is a common feedback item.

### Finding: run_dispose -- SHOULD NOT plus conditional MUST
- **Guideline text:** "Extensions SHOULD NOT call `GObject.Object.run_dispose()` unless absolutely necessary. If absolutely necessary, any call to this method MUST have a comment explaining the real-world situation that makes it a requirement."
- **Severity:** SHOULD NOT (usage) / MUST (comment if used)
- **Current coverage:** Covered - R-SEC-06 (pattern detection), R-QUAL-21 (comment verification)
- **Gap:** None. Both the detection and comment check are implemented.
- **Impact:** Low -- run_dispose is rare in practice.

---

## 3. Signal Management

### Finding: Signal connections MUST be disconnected -- stored ID requirement
- **Guideline text:** "Any signal connections made by an extension MUST be disconnected in `disable()`" and the examples show storing handler IDs.
- **Severity:** MUST (hard reject)
- **Current coverage:** Partial - R-LIFE-01 (signal balance heuristic, tolerance +2)
- **Gap:** The balance heuristic tolerates up to 2 more connects than disconnects, which means small signal leaks (1-2 signals) are not flagged. Per-signal tracking (matching specific connect calls to specific disconnect calls) is not implemented. Also, the heuristic does not distinguish `connectObject` from manual `connect` -- `connectObject` signals are cleaned up by `disconnectObject(this)` which may not be counted correctly in the balance.
- **Impact:** High -- signal leaks are the second most common rejection reason.

### Finding: connectObject is the preferred pattern
- **Guideline text:** Not in the review guidelines directly, but the session-modes documentation and extension class documentation both demonstrate `connectObject` as the preferred pattern. The lifecycle checklist says "PREFERRED: connectObject with automatic cleanup."
- **Severity:** Recommended (not MUST, but reviewers prefer it)
- **Current coverage:** Tier 3 Only - lifecycle-checklist.md mentions it
- **Gap:** No automated check suggests migrating from manual connect/disconnect to connectObject when 3+ signal pairs exist. This is a review-quality suggestion, not a rejection trigger.
- **Impact:** Low -- not a rejection cause, but improves review outcomes.

---

## 4. Main Loop Sources

### Finding: Sources MUST be removed even if callback returns SOURCE_REMOVE
- **Guideline text:** "All sources MUST be removed in `disable()`, even if the callback function will eventually return `false` or `GLib.SOURCE_REMOVE`."
- **Severity:** MUST (hard reject)
- **Current coverage:** Partial - R-LIFE-02 (untracked timeout), R-LIFE-12 (source-remove-verify)
- **Gap:** The rationale is critical: "there is no guarantee the callback will have executed before `disable()` is called." Our checks verify that the return value is stored and that `GLib.Source.remove()` is called, but do not specifically flag the case where a developer might argue "it returns SOURCE_REMOVE so I don't need cleanup."
- **Impact:** Medium -- this is a common misunderstanding. Developers think SOURCE_REMOVE self-cleans.

### Finding: GLib one-shot functions in GNOME 50
- **Guideline text:** From GNOME 50 migration guide: "New introspectable timeout/idle functions: `GLib.idle_add_once()`, `GLib.timeout_add_once()`, `GLib.timeout_add_seconds_once()`."
- **Severity:** Informational (new API)
- **Current coverage:** Missing
- **Gap:** No rule or guidance about the GNOME 50 one-shot functions. These are interesting because `timeout_add_once` does NOT return a source ID (it cannot be removed early). Extensions using these in enable() still need a way to guard against callbacks firing after disable(). We should at minimum document this nuance, and possibly add a check for `timeout_add_once` without `_destroyed` guards.
- **Impact:** Medium for GNOME 50+ targeting extensions -- new footgun.

---

## 5. Library and Import Restrictions

### Finding: Import restrictions are bidirectional and absolute
- **Guideline text:** "Extensions MUST NOT import `Gdk`, `Gtk` or `Adw` in the GNOME Shell process" and "Extensions MUST NOT import `Clutter`, `Meta`, `St` or `Shell` in the preferences process"
- **Severity:** MUST (hard reject, will crash)
- **Current coverage:** Covered - R-IMPORT-01 through R-IMPORT-07, check-imports.sh
- **Gap:** check-imports.sh checks `extension.js` and `lib/**/*.js` for GTK-side imports, and `prefs.js` for Shell-side imports. However, if an extension has helper modules imported by BOTH extension.js and prefs.js (shared utilities), the check may not catch a shared module that imports St. The import segregation depends on correctly identifying which files are extension-runtime vs prefs-runtime.
- **Impact:** Medium -- shared utility modules are an edge case but do exist in complex extensions.

### Finding: Resource paths differ between extension.js and prefs.js
- **Guideline text:** From GNOME 45 migration guide: "In `prefs.js`, resource paths start with `resource:///org/gnome/Shell/Extensions/js/`, while in the `extension.js` case, they start with `resource:///org/gnome/shell/`." Note the case difference (Shell/Extensions vs shell).
- **Severity:** MUST (wrong path = import failure)
- **Current coverage:** Missing
- **Gap:** No check validates that prefs.js uses the correct resource path prefix (`/org/gnome/Shell/Extensions/js/`) vs extension.js using (`/org/gnome/shell/`). Using the extension.js path in prefs.js will cause a runtime import failure.
- **Impact:** Medium -- this is a subtle case-sensitivity issue that trips up developers.

---

## 6. Deprecated Modules

### Finding: Four deprecated modules are hard rejects
- **Guideline text:** ByteArray ("use TextDecoder/TextEncoder"), Lang ("use ES6 Classes"), Mainloop ("use GLib functions"), extensionUtils ("use Extension class")
- **Severity:** MUST (hard reject for all four)
- **Current coverage:** Covered - R-DEPR-01 (Mainloop), R-DEPR-02 (Lang), R-DEPR-03 (ByteArray), R-DEPR-05 (ExtensionUtils)
- **Gap:** None -- all four are covered with blocking severity.
- **Impact:** Low (already covered).

### Finding: Tweener is deprecated (removed)
- **Guideline text:** Not in the review guidelines directly but in our rules reference: R-DEPR-06 covers Tweener. The GNOME 45+ migration made Clutter animations the standard.
- **Severity:** MUST (blocking -- Tweener is removed)
- **Current coverage:** Covered - R-DEPR-06
- **Gap:** None.
- **Impact:** Low.

### Finding: imports.format is deprecated
- **Guideline text:** Not in review guidelines but in our rules: R-DEPR-10. The `imports.format` module was removed.
- **Severity:** MUST (blocking)
- **Current coverage:** Covered - R-DEPR-10
- **Gap:** None.
- **Impact:** Low.

### Finding: initTranslations() is deprecated
- **Guideline text:** From GNOME 45 migration guide: "`initTranslations()` Deprecated. Use `gettext-domain` in metadata.json instead."
- **Severity:** SHOULD NOT (deprecated, not hard reject)
- **Current coverage:** Missing
- **Gap:** No check warns about calling `this.initTranslations()` when `gettext-domain` is already declared in metadata.json. While not a hard reject, reviewers may flag it as unnecessary.
- **Impact:** Low -- deprecated but harmless.

---

## 7. Code Quality and Readability

### Finding: "Following a specific code style is not a requirement" but messy code MAY be rejected
- **Guideline text:** "Following a specific code style is not a requirement for approval, but if the codebase of an extension is too messy to properly review it MAY be rejected."
- **Severity:** MAY (reviewer discretion)
- **Current coverage:** Partial - R-FILE-06 (minification), R-QUAL-10 (code volume), R-QUAL-12 (file complexity)
- **Gap:** "Too messy to properly review" is subjective. We check for minification and excessive size but not for inconsistent indentation, mixed coding styles within a file, or extremely long functions without structure. An automated "reviewability score" could catch the worst cases.
- **Impact:** Medium -- this is a real rejection reason for egregiously messy code.

### Finding: TypeScript transpilation must produce "well-formatted JavaScript"
- **Guideline text:** "TypeScript must be transpiled to well-formatted JavaScript"
- **Severity:** MUST (hard reject)
- **Current coverage:** Partial - R-FILE-06 catches minified output
- **Gap:** "Well-formatted" is not defined precisely. TypeScript transpilers can produce readable but clearly machine-generated code (helper functions like `__awaiter`, `__spreadArray`, emitted class decorators). We do not flag these TS transpilation artifacts. A check for common TS helper function signatures (e.g., `var __awaiter`, `var __extends`) could identify poorly-configured transpilation.
- **Impact:** Low-medium -- most TS developers transpile to readable ES6, but some use older target settings.

### Finding: Logging requirements are strict
- **Guideline text:** "Extensions MUST NOT print excessively to the log. The log should only be used for important messages and errors."
- **Severity:** MUST (hard reject for excessive logging)
- **Current coverage:** Covered - R-LOG-01 (console.log is FAIL), R-QUAL-13 (debug volume), R-QUAL-17 (logging volume)
- **Gap:** The guideline says "should only be used for important messages and errors." Our R-LOG-01 makes console.log a hard FAIL, which may be slightly stricter than the guideline (which says "excessively"). However, EGO reviewers do reject console.log usage, so our severity is appropriate.
- **Impact:** Low (already well-covered).

### Finding: Linting with ESLint is recommended but not required
- **Guideline text:** The guidelines "recommend" using ESLint with the official GJS config. "Following a specific code style is not a requirement for approval."
- **Severity:** Recommended (not MUST or SHOULD)
- **Current coverage:** Covered - ego-lint can optionally run ESLint if installed
- **Gap:** None -- this is purely advisory.
- **Impact:** None.

---

## 8. AI-Generated Code

### Finding: The AI policy is a hard reject with specific enumerated triggers
- **Guideline text:** "Submissions with large amounts of unnecessary code, inconsistent code style, imaginary API usage, comments serving as LLM prompts, or other indications of AI-generated output will be rejected."
- **Severity:** MUST (hard reject)
- **Current coverage:** Covered - R-SLOP-01 through R-SLOP-29, R-QUAL-01 through R-QUAL-26, ai-slop-checklist.md (43 items)
- **Gap:** The phrase "or other indications" is open-ended. New AI patterns emerge constantly. Our coverage is broad but inherently incomplete.
- **Impact:** High -- AI-generated code is a top rejection reason.

### Finding: "code completions" are explicitly permitted
- **Guideline text:** "While it is not prohibited to use AI as a learning aid or a development tool (i.e. code completions), extension developers should be able to justify and explain the code they submit, within reason."
- **Severity:** Allowed (with caveat)
- **Current coverage:** Tier 3 Only - ai-slop-checklist.md
- **Gap:** The "justify and explain" requirement is a semantic check that can only be done in review. Our automated checks cannot assess developer understanding. This is inherently Tier 3.
- **Impact:** Low (not automatable).

### Finding: "Unnecessary code" is a specific rejection trigger
- **Guideline text:** "large amounts of unnecessary code" -- this is a distinct trigger from inconsistent style or imaginary APIs.
- **Severity:** MUST (hard reject)
- **Current coverage:** Partial - R-QUAL-10 (code volume), R-SLOP-29 (empty destroy), various dead-code patterns
- **Gap:** "Unnecessary code" includes: boilerplate methods that do nothing, unused imports, methods that are never called, configuration objects with default values. We check some of these but not systematically. An "unused export" or "dead method" detector would be valuable.
- **Impact:** Medium -- boilerplate bloat from AI generation is a common pattern.

---

## 9. Metadata Requirements

### Finding: UUID format is strictly defined with two parts
- **Guideline text:** "This must be of the form `extension-id@namespace`. `extension-id` and `namespace` MUST only contain numbers, letters, period (`.`), underscore (`_`) and dash (`-`). Extensions MUST NOT use `gnome.org` as the namespace, but may use a registered web domain or accounts such as `username.github.io` and `username.gmail.com`."
- **Severity:** MUST (hard reject)
- **Current coverage:** Covered - R-META-01, R-META-02, R-META-03, R-META-04, R-META-13 (check-metadata.py)
- **Gap:** The guideline says the UUID has two parts: `extension-id` and `namespace`, separated by `@`. Our R-META-13 checks for `@` presence and R-META-03 checks character set, but we do not explicitly validate that there are exactly two parts (no check for multiple `@` signs or empty parts before/after `@`).
- **Impact:** Low -- malformed UUIDs are rare.

### Finding: shell-version format rules -- major version only for GNOME 40+
- **Guideline text:** From anatomy page: "For versions through 3.38, use format like `"3.38"`. From GNOME 40 onward, use major version only (e.g., `"40"`, `"41"`)."
- **Severity:** MUST
- **Current coverage:** Partial - check-metadata.py validates array type and some version constraints
- **Gap:** No check validates the format of individual version entries. A version like `"45.0"` or `"45.1"` should be flagged for GNOME 40+ (should be just `"45"`). Also, no check flags `"3.36"` alongside `"45"` in the same submission (impossible to support both with ESM).
- **Impact:** Low-medium -- format violations are uncommon but possible with AI generation.

### Finding: version field is explicitly "Deprecated" and for "internal use"
- **Guideline text:** From anatomy page and review guidelines: The `version` field is listed as "Deprecated: This field is set for internal use by `extensions.gnome.org`."
- **Severity:** SHOULD NOT (deprecated) / Advisory
- **Current coverage:** Covered - R-META-15 (advisory), R-SLOP-03 (advisory)
- **Gap:** None -- both detect it as advisory.
- **Impact:** Low.

### Finding: version-name has a precise regex and character limit
- **Guideline text:** "User-visible version string (1-16 characters, letters/numbers/spaces/periods). Matches regex: `/^(?!^[. ]+$)[a-zA-Z0-9 .]{1,16}$/`"
- **Severity:** MUST (hard reject if present and invalid)
- **Current coverage:** Covered - R-META-20 (check-metadata.py)
- **Gap:** None -- check-metadata.py validates the regex.
- **Impact:** Low.

### Finding: version-name IS a recognized field (contradicts R-SLOP-04)
- **Guideline text:** The anatomy page lists `version-name` as a recognized optional field with specific validation rules.
- **Severity:** N/A (rule correction needed)
- **Current coverage:** Incorrectly flagged - R-SLOP-04 says "version-name is not a recognized metadata.json field" and suggests removing it
- **Gap:** R-SLOP-04 is WRONG. `version-name` is a legitimate optional field defined in the anatomy page. It has a specific format (1-16 chars, regex validated). R-SLOP-04 should be removed or changed to only fire when the value fails the regex validation (which R-META-20 already handles). Additionally, check-metadata.py's `STANDARD_FIELDS` set does not include `version-name`, so it also gets flagged as non-standard by the metadata check. Both R-SLOP-04 in patterns.yaml and the STANDARD_FIELDS set in check-metadata.py need to be corrected. This is a double false positive.
- **Impact:** High -- this causes incorrect guidance to developers. Extensions with legitimate version-name values get flagged as both AI slop and non-standard metadata.

### Finding: donations field has exactly 8 valid keys with max 3 array entries
- **Guideline text:** From anatomy page: "donations: Object with optional keys: `buymeacoffee`, `custom`, `github`, `kofi`, `liberapay`, `opencollective`, `patreon`, `paypal`. Values are usernames (handles) or URLs for custom entries; arrays limited to 3 entries maximum."
- **Severity:** MUST (hard reject on invalid keys; MUST be dropped if not used)
- **Current coverage:** Covered - R-META-18 (invalid keys), R-META-24 (empty donations)
- **Gap:** The "max 3 array elements per key" constraint may not be checked. Need to verify check-metadata.py validates array lengths.
- **Impact:** Low -- most extensions use 1-2 donation links.

### Finding: The original-author field is recognized
- **Guideline text:** R-META-14 in our rules-reference lists `original-author` as a recognized field. The anatomy page does not explicitly list it, but it is used in practice for forked extensions.
- **Severity:** Informational
- **Current coverage:** Covered - R-META-14 recognizes it
- **Gap:** None.
- **Impact:** None.

### Finding: url field is MUST for EGO submission
- **Guideline text:** From anatomy page: "Required for extensions submitted to extensions.gnome.org."
- **Severity:** MUST (for EGO)
- **Current coverage:** Covered - R-META-22 (now FAIL per gap-analysis fix)
- **Gap:** None after severity fix.
- **Impact:** Low (already fixed).

### Finding: session-modes ["user"] MUST be dropped
- **Guideline text:** "This MUST be dropped if you are only using `user` mode."
- **Severity:** MUST (hard reject)
- **Current coverage:** Covered - R-META-09 (now FAIL per gap-analysis fix)
- **Gap:** None after severity fix.
- **Impact:** Low (already fixed).

### Finding: url field format validation
- **Guideline text:** The anatomy page shows url as "A repository URL where code lives and issues can be reported." The review guidelines example shows a GitHub URL.
- **Severity:** MUST (valid URL)
- **Current coverage:** Partial - check-metadata.py validates URL format
- **Gap:** Need to verify the URL format validation checks for valid URL patterns (starts with http:// or https://, no spaces, etc.).
- **Impact:** Low.

---

## 10. GSettings Schema Requirements

### Finding: Four schema rules are all MUST
- **Guideline text:** Schema ID base (`org.gnome.shell.extensions`), path base (`/org/gnome/shell/extensions`), XML file inclusion, and filename pattern are all stated with "MUST."
- **Severity:** MUST (hard reject for all four)
- **Current coverage:** Covered - R-SCHEMA-01 through R-SCHEMA-07, check-schema.sh
- **Gap:** R-SCHEMA-05 was previously advisory but gap-analysis says it should be FAIL per "The Schema XML filename MUST follow pattern." Verify this was fixed.
- **Impact:** Low -- schema issues are caught.

### Finding: Compiled schemas -- GNOME 44+ auto-compiles but zip still needs them
- **Guideline text:** From preferences page: "As of GNOME 44, settings schemas are compiled automatically for extensions installed with the `gnome-extensions` tool, GNOME Extensions website, or compatible applications."
- **Severity:** SHOULD (compiled schemas in zip) per guidelines / FAIL for GNOME 45+ per R-PKG-12
- **Current coverage:** Covered - R-PKG-12 (gschemas.compiled in zip for GNOME 45+)
- **Gap:** The guideline says SHOULD for compiled schemas. Our R-PKG-12 makes it a FAIL for GNOME 45+. This might be slightly stricter than the guideline, but R-PKG-11 (in rules-reference) already requires compiled schemas if schema XML exists. The difference is that R-PKG-12 specifically flags compiled schemas that are present in the zip (which is correct -- they should NOT be in the zip for GNOME 45+ since auto-compilation handles it). Actually, re-reading: R-PKG-12 FIALs if `gschemas.compiled` IS in the zip for 45+ targets, because auto-compilation makes them unnecessary and they may be stale. This is correct.
- **Impact:** Low -- correctly handled.

### Finding: settings-schema key in metadata SHOULD match schema ID
- **Guideline text:** From preferences page: "Defining a `settings-schema` key in metadata.json allows GNOME Shell to automatically use the correct schema ID."
- **Severity:** SHOULD (strong recommendation)
- **Current coverage:** Covered - R-SCHEMA-02 (blocking -- must match if both exist), R-META-10 (prefix check)
- **Gap:** None.
- **Impact:** Low.

---

## 11. Packaging and File Requirements

### Finding: "Unreasonable amount of unnecessary data" MAY cause rejection
- **Guideline text:** "Extension submissions should not include files that are not necessary... examples include: build or install scripts, .po and .pot files, unused icons, images or other media." Plus: "MAY be rejected for unreasonable amount of unnecessary data."
- **Severity:** SHOULD NOT (files) / MAY (rejection for bulk)
- **Current coverage:** Covered - R-PKG-01 through R-PKG-09 (specific forbidden files), check-package.sh
- **Gap:** We check for specific forbidden files (node_modules, .git, .claude, .pot, .pyc, .env) but do not flag other unnecessary files like `Makefile`, `meson.build`, `tsconfig.json`, `.eslintrc`, `README.md`, `CHANGELOG.md`, test files, or development scripts. While these are SHOULD NOT (not MUST NOT), flagging them as advisory would help.
- **Impact:** Low -- unless the extension ships megabytes of build artifacts.

### Finding: Specific list of unnecessary files from guidelines
- **Guideline text:** Guidelines enumerate: "build or install scripts, .po and .pot files, unused icons, images or other media"
- **Severity:** SHOULD NOT
- **Current coverage:** Partial - .pot files are checked (R-PKG-05), but .po files, build scripts, and unused media are not flagged
- **Gap:** Missing advisory checks for: .po files in zip (only compiled .mo should be included), Makefile/meson.build in zip, tsconfig.json in zip, package.json in zip, .eslintrc in zip. These should be advisory-level warnings.
- **Impact:** Low-medium -- reviewers notice and may ask for cleanup.

---

## 12. Security and Privacy

### Finding: Clipboard access -- three distinct requirements
- **Guideline text:** (1) "MUST declare it in the description", (2) "MUST NOT share clipboard data with a third-party without explicit user interaction", (3) "MUST NOT ship with default keyboard shortcuts for interacting with clipboard data"
- **Severity:** MUST (hard reject for all three)
- **Current coverage:** Covered - quality/clipboard-disclosure (detection + description cross-ref), R-SEC-16 (clipboard + keybinding). R-SEC-07 removed (redundant with quality/clipboard-disclosure).
- **Gap:** Requirement (2) -- "MUST NOT share clipboard data with third-party" -- is only Tier 3 (security-checklist.md). No automated check cross-references clipboard access with network requests (Soup, Gio.SocketClient).
- **Impact:** Medium -- this is a security-critical requirement.

### Finding: Telemetry is an absolute prohibition
- **Guideline text:** "Extensions MUST NOT use any telemetry tools to track users and share the user data online."
- **Severity:** MUST (hard reject)
- **Current coverage:** Covered - R-SEC-08 (pattern: analytics/telemetry/trackEvent)
- **Gap:** Telemetry can be obfuscated. Our pattern matching catches common identifiers but custom telemetry implementations (e.g., sending anonymous pings to a custom server) would only be caught during Tier 3 review.
- **Impact:** Low -- most telemetry uses identifiable patterns.

### Finding: Reviews focus on security and malware, not functionality
- **Guideline text:** "Extensions are reviewed, but not always tested for functionality so an extension MAY be approved with broken functionality or inoperable preferences window."
- **Severity:** Informational
- **Current coverage:** Documented in research doc
- **Gap:** None -- this informs our review approach.
- **Impact:** None.

---

## 13. Subprocess and Script Requirements

### Finding: "Spawning privileged subprocesses should be avoided at all costs"
- **Guideline text:** "Spawning privileged subprocesses should be avoided at all costs. If absolutely necessary, the subprocess MUST be run with `pkexec` and MUST NOT be an executable or script that can be modified by a user process."
- **Severity:** SHOULD NOT (general) / MUST (pkexec if necessary) / MUST NOT (user-writable target)
- **Current coverage:** Covered - R-SEC-04 (pkexec/sudo detection), R-SEC-18 (user-writable target)
- **Gap:** R-SEC-04 flags both pkexec and sudo but does not clearly distinguish that sudo is never acceptable (pkexec is the only allowed mechanism). The severity should differentiate: sudo = FAIL, pkexec = WARN (acceptable but scrutinized).
- **Impact:** Low-medium -- sudo vs pkexec distinction matters.

### Finding: Scripts MUST be in GJS "unless absolutely necessary"
- **Guideline text:** "Scripts MUST be written in GJS, unless absolutely necessary"
- **Severity:** MUST (with narrow exception)
- **Current coverage:** Covered - ego-lint.sh `non-gjs-scripts` (FAIL without pkexec justification, WARN with pkexec)
- **Gap:** The "absolutely necessary" exception is narrow. The main legitimate case is privileged helper scripts that must run as root (where GJS isn't available). Our current logic correctly FAILs non-GJS scripts unless pkexec is detected, then WARNs.
- **Impact:** Low (correctly handled).

### Finding: Scripts must be OSI-licensed
- **Guideline text:** "Scripts must be distributed under an OSI approved license"
- **Severity:** MUST
- **Current coverage:** Tier 3 Only - licensing-checklist.md
- **Gap:** No automated check verifies that non-GJS scripts in the extension have license headers or are covered by the main LICENSE file.
- **Impact:** Low -- non-GJS scripts are rare.

### Finding: Extensions MAY install pip/npm/yarn modules with explicit user action
- **Guideline text:** "Extensions may install modules from well-known services such as `pip`, `npm` or `yarn` but MUST require explicit user action."
- **Severity:** MAY (allowed with MUST condition)
- **Current coverage:** Missing
- **Gap:** No check verifies that pip/npm/yarn install commands require user action (e.g., a button in prefs). An extension that auto-installs npm packages in enable() would violate this MUST.
- **Impact:** Low -- this pattern is very rare in practice.

### Finding: Python, HTML, web JS modules are "out of scope for review"
- **Guideline text:** "Python, HTML, web JS modules are out of scope for review"
- **Severity:** Informational
- **Current coverage:** Missing documentation
- **Gap:** This is important context: reviewers will NOT review Python helper scripts or HTML files in detail. However, they still must be OSI-licensed.
- **Impact:** Low.

---

## 14. Session Modes

### Finding: disable() is called on session mode transitions, not just extension toggle
- **Guideline text:** From session-modes page: "When the session mode changes between `user` and `unlock-dialog`, GNOME Shell may call `disable()` and `enable()` on extensions."
- **Severity:** Informational (design constraint)
- **Current coverage:** Documented in lifecycle-checklist.md
- **Gap:** The phrase "may call" is important -- it is not guaranteed. Extensions must handle both cases: mode transition triggering enable/disable, and staying enabled across transitions.
- **Impact:** Low -- informational.

### Finding: Parent mode must be checked too
- **Guideline text:** From session-modes page: "the parent mode must be checked as well" and code example shows checking both `currentMode` and `parentMode`.
- **Severity:** SHOULD (to handle custom modes correctly)
- **Current coverage:** Missing
- **Gap:** No check verifies that extensions checking session mode also check `parentMode`. Custom modes may inherit from `user`, so checking only `currentMode === 'user'` misses custom user modes.
- **Impact:** Low -- custom modes are rare.

### Finding: All keyboard event signals MUST be disconnected in unlock-dialog
- **Guideline text:** "All signals related to keyboard events MUST be disconnected in unlock-dialog session mode"
- **Severity:** MUST (hard reject)
- **Current coverage:** Covered - R-LIFE-11 (check-lifecycle.py lockscreen-signals)
- **Gap:** R-LIFE-11 checks for key-press-event, key-release-event, and captured-event signals when unlock-dialog is declared. It may miss custom keyboard event handling via `Clutter.InputDevice` or other non-signal keyboard APIs.
- **Impact:** Low (edge case).

### Finding: Extensions MUST NOT disable selectively
- **Guideline text:** "Extensions MUST NOT disable selectively."
- **Severity:** MUST (hard reject)
- **Current coverage:** Covered - R-LIFE-13 (check-lifecycle.py)
- **Gap:** R-LIFE-13 detects `if (...) return;` in disable(). It correctly excludes null guards like `if (!this._x) return;`. However, it may miss more subtle selective disable patterns like `if (condition) { /* only partial cleanup */ }` without an early return.
- **Impact:** Low -- early return is the most common pattern.

---

## 15. Licensing and Attribution

### Finding: GPL-2.0-or-later compatibility is absolute
- **Guideline text:** "GNOME Shell is licensed under the terms of the `GPL-2.0-or-later`, which means that derived works like extensions MUST be distributed under compatible terms."
- **Severity:** MUST (hard reject)
- **Current coverage:** Partial - R-FILE-03 checks for LICENSE file existence with GPL-compatibility scanning
- **Gap:** Compatibility verification is limited to SPDX identifier scanning. Complex license situations (dual licensing, license exceptions, MIT-only without dual-licensing) are not fully automated.
- **Impact:** Medium -- license violations are rare but serious.

### Finding: Attribution MUST be in distributed files, not just repo
- **Guideline text:** "If your extension contains code from another extension it MUST include attribution to the original author in the distributed files."
- **Severity:** MUST (hard reject)
- **Current coverage:** Tier 3 Only - licensing-checklist.md (L2)
- **Gap:** No automated check detects code copied from other extensions or verifies attribution. This is inherently a semantic check.
- **Impact:** Low (not automatable).

---

## 16. Content and Code of Conduct

### Finding: Five distinct content prohibitions
- **Guideline text:** (1) Code of Conduct violations in name/description/text/icons/emojis/screenshots, (2) Political agendas, (3) Copyrighted content without permission, (4) Trademarked content without permission, (5) Brand names/logos/multimedia
- **Severity:** MUST (hard reject for all)
- **Current coverage:** Tier 3 Only - licensing-checklist.md (L3-L5)
- **Gap:** None -- these are inherently semantic checks not suitable for automation.
- **Impact:** Low (not automatable).

---

## 17. Functionality Requirements

### Finding: Fundamentally broken extensions are rejected despite "not tested"
- **Guideline text:** "if an extension is tested and found to be fundamentally broken it will be rejected"
- **Severity:** MUST (hard reject if tested)
- **Current coverage:** Uncovered
- **Gap:** Requires runtime testing. Not feasible for static analysis.
- **Impact:** Low (inherently not automatable for static analysis tools).

---

## 18. Extension System Interference

### Finding: Interfering with other extensions is "generally discouraged" but not prohibited
- **Guideline text:** "Extensions which modify, reload or interact with other extensions or the extension system are generally discouraged. While not strictly prohibited, these extensions will be reviewed on a case-by-case basis and may be rejected at the reviewer's discretion."
- **Severity:** MAY (reviewer discretion)
- **Current coverage:** Missing
- **Gap:** No check detects extensions that interact with the extension system. Patterns like `ExtensionManager.lookup()`, `Extension.lookupByUUID()` with a different UUID, or `Main.extensionManager.enableExtension()` could be flagged as advisory. R-SLOP-25 checks for `Main.extensionManager.enable/disable` but as an AI slop indicator, not as extension-system interference.
- **Impact:** Low -- this is a niche case.

---

## 19. CSS and Stylesheet Guidelines

### Finding: stylesheet.css applies ONLY to GNOME Shell (Clutter/St widgets)
- **Guideline text:** From preferences page and general docs: stylesheet.css "Applies ONLY to GNOME Shell and extensions" and "Does NOT apply to preferences window or other GTK applications"
- **Severity:** Informational
- **Current coverage:** Documented
- **Gap:** No check warns about GTK-specific CSS properties in stylesheet.css (e.g., `background-image: url()` for GTK widgets, or GTK widget selectors like `GtkBox`). These would be silently ignored.
- **Impact:** Low.

### Finding: Unscoped overrides of Shell theme classes are risky
- **Guideline text:** Not explicitly in guidelines but implied: "Use unique class names prefixed with extension name to avoid conflicts" is a best practice.
- **Severity:** SHOULD (best practice)
- **Current coverage:** Covered - R-CSS-01 (advisory), check-css.py (shell class override detection)
- **Gap:** None -- advisory is appropriate.
- **Impact:** Low.

---

## 20. Translations and i18n

### Finding: String.prototype.format() is required for translatable strings with interpolation
- **Guideline text:** From translations page: "When translatable strings have interpolated values, like `%s` or `%d`, extensions should use the `String.prototype.format()` method."
- **Severity:** SHOULD (strong recommendation)
- **Current coverage:** Partial - R-I18N-01 checks for template literals inside gettext `_()`
- **Gap:** R-I18N-01 catches `` _(`...${var}...`) `` but does not check for incorrect use of concatenation in gettext (e.g., `_('Hello ' + name)` which breaks translation extraction). Also no check for missing `.format()` when using `%s`/`%d` placeholders.
- **Impact:** Medium -- string concatenation in gettext is a common i18n mistake that breaks translations.

### Finding: gettext-domain should match UUID
- **Guideline text:** From anatomy page: "A Gettext translation domain, typically matching the UUID."
- **Severity:** SHOULD (convention)
- **Current coverage:** Missing
- **Gap:** From gap-analysis.md's remaining gaps: "`gettext-domain` consistency with po/locale structure" is listed as open. No check validates that gettext-domain matches UUID or that locale/ files use the correct domain.
- **Impact:** Low -- mismatched domains cause runtime translation failures but are not a review rejection trigger per se.

### Finding: Only compiled .mo files should be in zip, not .po/.pot
- **Guideline text:** From packaging guidelines: ".po and .pot files" should not be in the zip. From translations page: compiled .mo files go in `locale/<lang>/LC_MESSAGES/`.
- **Severity:** SHOULD NOT (.po) / MUST NOT (.pot per R-PKG-05)
- **Current coverage:** Partial - R-PKG-05 checks .pot files. No check for .po files in zip.
- **Gap:** .po source files in the zip are not flagged. While .pot is blocked (R-PKG-05), .po files are only SHOULD NOT and have no automated check.
- **Impact:** Low -- .po files are harmless but unnecessary.

### Finding: String concatenation breaks xgettext extraction
- **Guideline text:** Not explicitly stated but implied by the format() recommendation: "Template literals should replace format() in non-gettext contexts" -- meaning template literals should NOT be used in gettext contexts.
- **Severity:** SHOULD NOT (breaks tooling)
- **Current coverage:** Covered - R-I18N-01 (template literal in gettext)
- **Gap:** Missing check for concatenation: `_('Hello ' + name)` -- xgettext cannot extract the full string from concatenated expressions.
- **Impact:** Medium -- this breaks the translation pipeline.

---

## 21. Preferences (prefs.js)

### Finding: prefs.js MUST extend ExtensionPreferences
- **Guideline text:** From GNOME 45 migration: "you should export a default class extending `ExtensionPreferences`"
- **Severity:** MUST (GNOME 45+)
- **Current coverage:** Covered - R-PREFS-02 (check-prefs.py, strengthened to verify extends clause)
- **Gap:** None after strengthening.
- **Impact:** Low.

### Finding: fillPreferencesWindow is recommended over getPreferencesWidget
- **Guideline text:** From extension class docs: "It is recommended to override the `fillPreferencesWindow()`" and "getPreferencesWidget() -- Legacy approach; skipped if `fillPreferencesWindow()` exists"
- **Severity:** Recommended (fillPreferencesWindow preferred)
- **Current coverage:** Covered - R-PREFS-01 checks for either method, detects dual-pattern conflict
- **Gap:** No advisory for using getPreferencesWidget instead of fillPreferencesWindow. While both are valid, reviewers may prefer the newer pattern.
- **Impact:** Low.

### Finding: Async prefs methods (GNOME 47+)
- **Guideline text:** From GNOME 47 migration: "The `getPreferencesWidget` and `fillPreferencesWindow` functions in `prefs.js` are now awaited when the preference window opens."
- **Severity:** Informational (new capability)
- **Current coverage:** Missing
- **Gap:** No documentation or check about async prefs methods. Extensions targeting GNOME 47+ can use `async fillPreferencesWindow()`. This is purely informational -- no check needed, but the review should be aware that async prefs are valid for 47+.
- **Impact:** Low.

### Finding: Prefs run in separate process -- import restrictions apply
- **Guideline text:** "Extension preferences run in a separate process, without access to code in GNOME Shell, and are written with GTK4 and Adwaita."
- **Severity:** MUST (architectural constraint)
- **Current coverage:** Covered - check-imports.sh validates import restrictions
- **Gap:** None.
- **Impact:** Low.

### Finding: GNOME HIG compliance is recommended but not required
- **Guideline text:** "it is recommended that extension preferences follow the GNOME Human Interface Guidelines"
- **Severity:** Recommended (not required for approval)
- **Current coverage:** Tier 3 Only - mentioned in code-quality-checklist.md
- **Gap:** None -- advisory only.
- **Impact:** Low.

---

## 22. ESModules Migration (GNOME 45+)

### Finding: ESM is mandatory for GNOME 45+
- **Guideline text:** "GNOME Shell 45 moved to ESM (ECMAScript modules). That means you MUST use the standard `import` declaration instead of relying on the previous `imports.*` approach."
- **Severity:** MUST (hard reject for GNOME 45+ targeting extensions using legacy imports)
- **Current coverage:** Covered - R-DEPR-04 (legacy imports), R-META-25 (ESM version floor)
- **Gap:** R-DEPR-04 is advisory severity. For extensions targeting GNOME 45+, legacy imports should be blocking (they will fail at runtime). The severity should be conditional on target version.
- **Impact:** Medium -- extensions claiming GNOME 45+ support with legacy imports will fail.

### Finding: ESM extensions cannot support pre-45 versions
- **Guideline text:** "Since ESM files contain `import` and `export` keywords, your extension modules won't be compatible with older GNOME Shell versions."
- **Severity:** Constraint (technical incompatibility)
- **Current coverage:** Covered - R-META-25 (esm-version-floor)
- **Gap:** None.
- **Impact:** Low.

### Finding: Multi-versioning via EGO is supported
- **Guideline text:** "The good news is that [e.g.o](https://extensions.gnome.org/) supports multi versioning - you can still submit multiple packages with different shell versions."
- **Severity:** Informational
- **Current coverage:** Not documented in our tools
- **Gap:** ego-submit could mention this option when an extension has pre-45 version targets.
- **Impact:** Low.

---

## 23. Extension Class Structure

### Finding: Extension and ExtensionPreferences MUST be default exports
- **Guideline text:** From GNOME 45 migration: "`extension.js` MUST export a default class containing `enable()` and `disable()` methods"
- **Severity:** MUST (hard reject)
- **Current coverage:** Covered - R-FILE-07 (check-lifecycle.py), R-PREFS-02 (check-prefs.py)
- **Gap:** None.
- **Impact:** Low.

### Finding: Constructor metadata argument must be passed to parent
- **Guideline text:** From extension class docs: "the `metadata` argument must be passed to the parent class"
- **Severity:** MUST (will break if not passed)
- **Current coverage:** Missing
- **Gap:** No check verifies that `super(metadata)` is called in extension constructors that override the constructor. If a developer writes `constructor(metadata) { /* forgets super() */ }`, the extension will fail to initialize.
- **Impact:** Low -- most developers use `super()` correctly or don't override the constructor at all.

### Finding: ExtensionBase "should never be subclassed directly"
- **Guideline text:** From extension class docs: ExtensionBase "should never be subclassed directly."
- **Severity:** SHOULD NOT
- **Current coverage:** Missing
- **Gap:** No check detects `extends ExtensionBase` instead of `extends Extension` or `extends ExtensionPreferences`. This would indicate a misunderstanding of the class hierarchy.
- **Impact:** Low -- this would likely cause runtime errors that are self-correcting.

---

## 24. Monkey-Patching and InjectionManager

### Finding: InjectionManager is the recommended approach
- **Guideline text:** From extension class docs: InjectionManager provides "overrideMethod", "restoreMethod", and "clear" for safe monkey-patching.
- **Severity:** Recommended (not MUST, but preferred over direct prototype modification)
- **Current coverage:** Covered - R-LIFE-10 (check-lifecycle.py) detects InjectionManager without .clear() and direct prototype modifications
- **Gap:** None.
- **Impact:** Low.

### Finding: Arrow functions vs function expressions in overrides -- subtle this binding
- **Guideline text:** The extension class docs explain: "Arrow functions capture `this` from the enclosing scope (the extension instance)" while "Function expressions create their own `this` binding (the object being patched)."
- **Severity:** Informational (correctness concern, not review requirement)
- **Current coverage:** Missing
- **Gap:** No check detects incorrect `this` usage in InjectionManager overrides. An arrow function that tries to use `this` as the patched object (instead of the extension) would silently malfunction.
- **Impact:** Low -- this is a correctness issue, not a review requirement.

---

## 25. Network Access and Data Sharing

### Finding: Network access is permitted but receives extra scrutiny
- **Guideline text:** "Network access is permitted but subject to review" and "Extensions that make network requests (using `Soup`, `Gio.SocketClient`, etc.) are permitted but will receive extra scrutiny during review."
- **Severity:** Allowed (with scrutiny)
- **Current coverage:** Partial - R-SEC-19 (network disclosure), R-LIFE-15 (Soup.Session abort)
- **Gap:** No check for Gio.SocketClient or other non-Soup network APIs. R-SEC-19 checks for Soup/HTTP but not raw socket usage.
- **Impact:** Low -- Soup is the standard network API for extensions.

---

## 26. Search Providers

### Finding: Search provider interface has a strict contract
- **Guideline text:** From search-provider page: Required properties: `appInfo` (Gio.AppInfo or null), `canLaunchSearch` (boolean), `id` (unique identifier). Required methods: `getInitialResultSet`, `getResultMetas`, `activateResult`, `getSubsearchResultSet`, `filterResults`, `launchSearch`, `createResultObject`.
- **Severity:** MUST (interface contract)
- **Current coverage:** Tier 3 Only - lifecycle-checklist.md
- **Gap:** No automated check validates the search provider interface. A check could detect `SearchProvider` class definitions and verify they implement the required methods.
- **Impact:** Low -- search providers are a niche feature.

### Finding: Search providers must handle Gio.Cancellable
- **Guideline text:** "All asynchronous methods must handle `Gio.Cancellable` and respect cancellation signals."
- **Severity:** MUST (interface contract)
- **Current coverage:** Missing
- **Gap:** No check verifies that search provider async methods accept and respect cancellable parameters.
- **Impact:** Low.

---

## 27. Accessibility

### Finding: Accessibility is "a foundational requirement rather than an optional feature"
- **Guideline text:** From accessibility page: "Accessibility represents a foundational requirement rather than an optional feature."
- **Severity:** MUST (hard requirement per our research doc)
- **Current coverage:** Tier 3 Only - accessibility checklist (A1-A7) in code-quality-checklist.md
- **Gap:** No automated check detects accessibility issues. Checks could include: custom St.Widget subclasses without accessible-role, St.Button without accessible-name, interactive widgets without can_focus: true.
- **Impact:** Medium -- accessibility violations are increasingly flagged by reviewers.

### Finding: Standard widgets handle accessibility automatically
- **Guideline text:** From accessibility page: "Standard widgets automatically support accessibility without additional intervention" and "Broken accessibility indicates either design flaws or incorrect widget configuration."
- **Severity:** Informational (reduces scope of checks needed)
- **Current coverage:** Documented
- **Gap:** This means accessibility checks only need to fire for CUSTOM widgets/containers, not standard St.Button, St.Label, etc. used with default configuration.
- **Impact:** Low -- narrows the check scope.

### Finding: Atk.Role, Atk.RelationType, Atk.StateType management
- **Guideline text:** From accessibility page: Role via `St.Widget:accessible-role`, relationships via `St.Widget:label-actor`, states via `add_accessible_state()`/`remove_accessible_state()`.
- **Severity:** MUST (for custom widgets)
- **Current coverage:** Tier 3 Only - accessibility checklist items A1-A3
- **Gap:** Could potentially automate: detect `GObject.registerClass` with custom widgets that extend `St.Widget` without setting `accessible_role` in properties.
- **Impact:** Low-medium -- depends on extension complexity.

---

## 28. Version-Specific API Changes

### Finding: GNOME 46 -- ExtensionState enum renamed
- **Guideline text:** From GNOME 46 migration: `ENABLED` -> `ACTIVE`, `DISABLED` -> `INACTIVE`, `DISABLING` -> `DEACTIVATING`, `ENABLING` -> `ACTIVATING`
- **Severity:** Breaking (if using old enum names on GNOME 46+)
- **Current coverage:** Covered - R-VER46-05 detects `ExtensionState.(ENABLED|DISABLED|INITIALIZED|DEACTIVATING|ACTIVATING)` with min-version 46
- **Gap:** None.
- **Impact:** Low.

### Finding: GNOME 46 -- Clutter.Container removed
- **Guideline text:** From GNOME 46 migration: "Clutter.Container: Removed. Use `Clutter.Actor.add_child()`/`remove_child()` instead of `add_actor()`/`remove_actor()`."
- **Severity:** Breaking (GNOME 46+)
- **Current coverage:** Covered - R-VER46-01 (add_actor), R-VER46-02 (remove_actor), R-VER46-07 (Clutter.Container) -- all version-gated to min-version 46
- **Gap:** None.
- **Impact:** Low (already covered).

### Finding: GNOME 46 -- BlurEffect.sigma replaced by radius
- **Guideline text:** "Shell.BlurEffect: Replace `sigma` with `radius` (radius = sigma * 2.0)"
- **Severity:** Breaking (GNOME 46+)
- **Current coverage:** Covered - R-VER46-06 detects `BlurEffect.*\.sigma` and `BlurEffect({...sigma` with min-version 46
- **Gap:** None.
- **Impact:** Low.

### Finding: GNOME 46 -- Gio.UnixInputStream moved
- **Guideline text:** "Gio.UnixInputStream: Moved to GioUnix; use `GioUnix.InputStream` instead."
- **Severity:** Breaking (GNOME 46+)
- **Current coverage:** Covered - R-VER46-04 detects `Gio.UnixInputStream` with min-version 46
- **Gap:** None.
- **Impact:** Low.

### Finding: GNOME 46 -- Style class renames
- **Guideline text:** Multiple CSS class renames: `app-well-app` -> `overview-tile`, `app-well-app-running-dot` -> `app-grid-running-dot`, `edit-folder-button` -> `icon-button`, calendar/date/message class changes.
- **Severity:** Breaking (GNOME 46+ -- styles silently stop working)
- **Current coverage:** Missing
- **Gap:** No check detects old GNOME 46 CSS class names in stylesheet.css. While these are CSS-only changes (styles silently fail rather than crash), they indicate the extension has not been updated. Low priority since the failure is silent.
- **Impact:** Low -- styles fail silently, no crash.

### Finding: GNOME 47 -- PopupBaseMenuItem selected class removed
- **Guideline text:** "The `selected` style class name is no longer applied when a menu item is selected. Instead, the `:selected` pseudo-class is used."
- **Severity:** Breaking (GNOME 47+ -- custom menu item styling)
- **Current coverage:** Missing
- **Gap:** No check detects `.selected` CSS class applied to popup menu items for GNOME 47+ targets.
- **Impact:** Low.

### Finding: GNOME 47 -- Clutter.Color removed
- **Guideline text:** "`Clutter.Color` has been removed from the API. Its functionality merged into `Cogl.Color()`."
- **Severity:** Breaking (GNOME 47+)
- **Current coverage:** Covered - R-VER47-01 detects `Clutter.Color` with min-version 47
- **Gap:** None.
- **Impact:** Low.

### Finding: GNOME 47 -- Accent color CSS variables
- **Guideline text:** "Use `-st-accent-color` and `-st-accent-fg-color` CSS variables in `stylesheet.css`"
- **Severity:** Informational (new feature)
- **Current coverage:** Missing documentation
- **Gap:** No documentation about accent color CSS variables. Extensions that hardcode accent colors could use these variables instead.
- **Impact:** Low.

### Finding: GNOME 48 -- Clutter.Image removed
- **Guideline text:** "`Clutter.Image` removed; use `St.ImageContent` instead"
- **Severity:** Breaking (GNOME 48+)
- **Current coverage:** Covered - R-VER48-01 detects `Clutter.Image` with min-version 48
- **Gap:** None.
- **Impact:** Low.

### Finding: GNOME 48 -- vertical property deprecated
- **Guideline text:** "The `vertical` property is deprecated; use `orientation: Clutter.Orientation.VERTICAL` instead."
- **Severity:** SHOULD NOT (deprecated, GNOME 48+)
- **Current coverage:** Covered - R-VER48-04 detects `.vertical =` assignment with min-version 48, advisory severity
- **Gap:** R-VER48-04 catches assignment (`.vertical = true`) but may not catch property in constructor config objects (`new St.BoxLayout({ vertical: true })`). The pattern `\\.vertical\\s*=` misses the object literal form.
- **Impact:** Low -- the assignment form is the common pattern.

### Finding: GNOME 48 -- Meta functions moved to Meta.Compositor
- **Guideline text:** Multiple Meta functions moved: `Meta.disable_unredirect_for_display` -> `Meta.Compositor.disable_unredirect`, `Meta.get_window_actors` -> `Meta.Compositor.get_window_actors`, etc. Also `Meta.CursorTracker.get_for_display()` removed.
- **Severity:** Breaking (GNOME 48+)
- **Current coverage:** Covered - R-VER48-02 detects `Meta.(disable_unredirect_for_display|enable_unredirect_for_display|get_window_actors|get_window_group_for_display|get_top_window_group_for_display)` with min-version 48. R-VER48-03 detects `CursorTracker.get_for_display` with min-version 48.
- **Gap:** None.
- **Impact:** Low.

### Finding: GNOME 48 -- Quick menu toggle CSS rename
- **Guideline text:** `.quick-menu-toggle` -> `.quick-toggle-has-menu`
- **Severity:** Breaking (GNOME 48+)
- **Current coverage:** Covered - R-VER48-07
- **Gap:** None.
- **Impact:** Low.

### Finding: GNOME 48 -- getLogger() method
- **Guideline text:** "ExtensionBase now provides a `getLogger()` method" with methods: `log()`, `warn()`, `error()`, `info()`, `debug()`, `assert()`, `trace()`, `group()`, `groupEnd()`
- **Severity:** Informational (new API)
- **Current coverage:** Documented in research doc but no rule
- **Gap:** No advisory suggesting use of getLogger() instead of console.* for GNOME 48+ targets. This was intentionally omitted (R-VER48-08 was removed as too noisy).
- **Impact:** Low -- advisory only.

### Finding: GNOME 48 -- Window manager method signatures changed
- **Guideline text:** `_startSwitcher()`, `_startA11ySwitcher()`, `_switchToApplication()`, `_openNewApplicationWindow()`, `_showWorkspaceSwitcher()` all gained an `event` parameter.
- **Severity:** Breaking (GNOME 48+ if using InjectionManager on these methods)
- **Current coverage:** Missing
- **Gap:** No check detects InjectionManager overrides of these methods without the new event parameter for GNOME 48+ targets.
- **Impact:** Low -- these are rarely patched.

### Finding: GNOME 48 -- NotificationMessage moved to messageList.js
- **Guideline text:** "`NotificationMessage` and `MediaMessage` moved to `/ui/messageList.js`"
- **Severity:** Breaking (GNOME 48+ import path change)
- **Current coverage:** Missing
- **Gap:** No check detects old import paths for NotificationMessage from calendar.js for GNOME 48+.
- **Impact:** Low.

### Finding: GNOME 48 -- InputSourceManager._switchInputSource signature change
- **Guideline text:** Changed from `(display, window, binding)` to `(display, window, event, binding)`
- **Severity:** Breaking (GNOME 48+)
- **Current coverage:** Missing
- **Gap:** No check for InjectionManager overrides of _switchInputSource with wrong signature.
- **Impact:** Low.

### Finding: GNOME 49 -- Meta.Rectangle fully removed
- **Guideline text:** "GNOME Shell 49 removed `Meta.Rectangle`"
- **Severity:** Breaking (GNOME 49+)
- **Current coverage:** Covered - R-VER49-01 (from patterns.yaml)
- **Gap:** Need to verify this is covered. The research doc mentions Meta.Rectangle -> Mtk.Rectangle.
- **Impact:** Low.

### Finding: GNOME 49 -- maximize()/unmaximize() signature changes
- **Guideline text:** "The `maximize()` and `unmaximize()` methods no longer accept `Meta.MaximizeFlags` parameters."
- **Severity:** Breaking (GNOME 49+)
- **Current coverage:** Covered - R-VER49-08
- **Gap:** None.
- **Impact:** Low.

### Finding: GNOME 49 -- ClickAction/TapAction/DragAction/SwipeAction removed, replaced by gestures
- **Guideline text:** "Clutter.ClickAction() and Clutter.TapAction() have been removed. You should now use `Clutter.ClickGesture()` and `Clutter.LongPressGesture()`."
- **Severity:** Breaking (GNOME 49+)
- **Current coverage:** Covered - R-VER49-02 (ClickAction -> ClickGesture), R-VER49-03 (TapAction -> LongPressGesture), R-VER49-06 (DragAction -> DragGesture), R-VER49-07 (SwipeAction -> SwipeGesture) -- all version-gated to min-version 49
- **Gap:** None -- all four removed Clutter action classes are covered.
- **Impact:** Low (already covered).

### Finding: GNOME 49 -- CursorTracker changes
- **Guideline text:** "`Meta.CursorTracker.set_pointer_visible()` method has been replaced by `inhibit_cursor_visibility()` and `uninhibit_cursor_visibility()`."
- **Severity:** Breaking (GNOME 49+)
- **Current coverage:** Covered - existing rule detects `CursorTracker.set_pointer_visible()` with appropriate min-version
- **Gap:** None.
- **Impact:** Low.

### Finding: GNOME 49 -- AppMenuButton removed
- **Guideline text:** "GNOME Shell 49 removes the `AppMenuButton` from `js/ui/panel.js`."
- **Severity:** Breaking (GNOME 49+)
- **Current coverage:** Covered - R-VER49-09
- **Gap:** None.
- **Impact:** Low.

### Finding: GNOME 50 -- releaseKeyboard/holdKeyboard removed
- **Guideline text:** "`misc/keyboardManager.js` eliminated `releaseKeyboard()` and `holdKeyboard()` methods."
- **Severity:** Breaking (GNOME 50+)
- **Current coverage:** Covered - R-VER50-01/02
- **Gap:** None.
- **Impact:** Low.

### Finding: GNOME 50 -- restart/show-restart-message signals removed
- **Guideline text:** "`show-restart-message` and `restart` signals removed from `global.display`; X11 support dropped entirely."
- **Severity:** Breaking (GNOME 50+)
- **Current coverage:** Covered - R-VER50-03/04
- **Gap:** None.
- **Impact:** Low.

### Finding: GNOME 50 -- easeAsync() method
- **Guideline text:** "A promise-based animation method: `await actor.easeAsync({...})`"
- **Severity:** Informational (new API)
- **Current coverage:** Missing documentation
- **Gap:** No documentation about easeAsync(). Not a check-worthy item, but useful for ego-review to know about.
- **Impact:** Low.

### Finding: GNOME 50 -- GLib one-shot timeout functions
- **Guideline text:** "`GLib.idle_add_once()`, `GLib.timeout_add_once()`, `GLib.timeout_add_seconds_once()`"
- **Severity:** Informational (new API with lifecycle implications)
- **Current coverage:** Missing
- **Gap:** These one-shot functions do not return a source ID, meaning they CANNOT be removed with `GLib.Source.remove()`. Extensions using these in enable() have no way to cancel them in disable(). A `_destroyed` flag check inside the callback is the only safety mechanism. No check warns about this footgun.
- **Impact:** Medium -- new API with a hidden lifecycle trap.

---

## 29. GObject Patterns

### Finding: GObject.registerClass requirements not in review guidelines
- **Guideline text:** The review guidelines do not explicitly cover GObject.registerClass, GTypeName validation, or GObject subclassing patterns.
- **Severity:** N/A (not in guidelines)
- **Current coverage:** Covered - check-gobject.py handles registerClass patterns
- **Gap:** Our coverage exceeds the guidelines here. check-gobject.py validates GTypeName uniqueness and registerClass patterns, which is proactive quality checking beyond the review requirements.
- **Impact:** Low.

---

## 30. Updates and Breakage Philosophy

### Finding: There is no stable extension API
- **Guideline text:** From updates-and-breakage: "there is no way to prevent an extension from patching and breaking any API that could be devised." Extensions are patches, not plugins.
- **Severity:** Informational (design philosophy)
- **Current coverage:** Documented
- **Gap:** This philosophy informs why version-gated checks are important -- every GNOME version can break any extension.
- **Impact:** Low (contextual).

### Finding: Non-invasive patching has minimal breakage risk
- **Guideline text:** "Non-invasive patching: Simply adds UI elements (buttons, menu items) without modifying underlying code, presenting minimal breakage risk."
- **Severity:** Informational
- **Current coverage:** Not documented in rules
- **Gap:** ego-review could note this distinction during Phase 2 (lifecycle audit) -- extensions that only add UI elements are lower risk than those that patch Shell methods.
- **Impact:** Low.

### Finding: GNOME Platform APIs are stable, Shell internals are not
- **Guideline text:** "GLib, GObject, GIO (extremely stable), and Clutter, Mutter, St, Shell (quite stable but subject to change)"
- **Severity:** Informational
- **Current coverage:** Implicit in version-gated rules
- **Gap:** None -- our version-gated rules already target Shell/Clutter/Mutter API changes.
- **Impact:** Low.

---

## Summary of Critical Findings

### False Positive / Incorrect Rule

| Finding | Rule / Code | Issue | Priority |
|---|---|---|---|
| version-name IS a recognized field | R-SLOP-04 (patterns.yaml) | Incorrectly flags legitimate field as AI slop | **P0 -- fix immediately** |
| version-name not in STANDARD_FIELDS | check-metadata.py line 196 | Missing from STANDARD_FIELDS set, causing false non-standard-field WARN | **P0 -- fix immediately** |

### Missing Checks (Potential New Rules)

| Finding | Suggested Rule | Severity | Priority |
|---|---|---|---|
| Resource path case mismatch (prefs vs extension) | R-IMPORT-08 | blocking | P1 |
| GNOME 50: one-shot timeout lifecycle trap | R-VER50-05 | advisory (50+) | P2 |
| String concatenation in gettext | R-I18N-02 | advisory | P2 |
| destroy() without subsequent = null | R-QUAL-27 | advisory | P2 |
| GNOME 48: vertical in constructor config object | Enhance R-VER48-04 | advisory (48+) | P2 |
| .po files in zip | R-PKG-13 | advisory | P3 |
| Build files in zip (Makefile, tsconfig, etc.) | R-PKG-14 | advisory | P3 |
| GNOME 46: CSS class renames (app-well-app, calendar) | R-VER46-08+ | advisory (46+) | P3 |
| GNOME 47: .selected CSS class -> :selected pseudo-class | R-VER47-02 | advisory (47+) | P3 |
| initTranslations() deprecated | R-DEPR-11 | advisory | P3 |
| GNOME 48: WM method signature changes (event param) | R-VER48-09 | advisory (48+) | P3 |
| GNOME 48: NotificationMessage import path change | R-VER48-10 | blocking (48+) | P3 |
| GNOME 48: InputSourceManager signature change | R-VER48-11 | advisory (48+) | P3 |

**Note:** Many items initially flagged as missing were found to already be covered after cross-referencing with `rules/patterns.yaml`. The following were verified as covered: R-VER46-01 through R-VER46-07, R-VER47-01, R-VER48-01 through R-VER48-07, R-VER49-01 through R-VER49-09, R-VER50-01 through R-VER50-04.

### Severity Mismatches

| Finding | Current | Should Be | Rule |
|---|---|---|---|
| R-DEPR-04 (legacy imports) for GNOME 45+ targets | advisory | blocking (conditional on target) | R-DEPR-04 |
| Module-scope mutable state holding GObjects | advisory | blocking (if holding GObject) | R-QUAL-04 |

### Coverage Gaps in Existing Checks

| Finding | Current Check | Gap |
|---|---|---|
| Signal balance heuristic tolerance +2 | R-LIFE-01 | Small leaks (1-2 signals) not flagged |
| Shared utility modules imported by both extension.js and prefs.js | check-imports.sh | Import segregation may miss shared modules |
| sudo vs pkexec distinction | R-SEC-04 | sudo should be FAIL, pkexec should be WARN |
| shell-version entry format validation | check-metadata.py | "45.0" format not flagged for GNOME 40+ |
| donations array length limit | check-metadata.py | Max 3 entries per key may not be validated |
| Clipboard + network data exfiltration | quality/clipboard-disclosure | No cross-reference of clipboard with Soup/network |

### Documentation-Only Items (No Rule Needed)

| Finding | Action |
|---|---|
| GNOME 47 async prefs methods | Document in ego-review Phase 2 |
| GNOME 47 accent color CSS variables | Document in ego-review |
| GNOME 50 easeAsync() method | Document in ego-review |
| Non-invasive vs invasive patching risk | Document in ego-review Phase 2 |
| Python/HTML/web JS out of review scope | Document in ego-review |
| Multi-versioning via EGO | Document in ego-submit |
