# Gap Analysis: EGO Review Guidelines vs Plugin Coverage

**Date:** 2026-02-25
**Method:** Every MUST requirement from `ego-review-guidelines-research.md` was checked against the plugin's Tier 1 pattern rules (`rules/patterns.yaml`), Tier 2 scripts (`skills/ego-lint/scripts/`), and Tier 3 checklists (`skills/ego-review/references/`).

---

## Legend

- **Covered**: An automated check (Tier 1 or Tier 2) directly enforces this requirement.
- **Partial**: A check exists but only catches some cases or uses heuristics that can miss violations.
- **Tier 3 Only**: Covered by a review checklist read by Claude during `ego-review`, but no automated check.
- **Uncovered**: No automated check and no checklist item addresses this requirement.

---

## Section 1: Initialization and Lifecycle

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| MUST NOT create objects during initialization (constructor/import time) | **MUST** | Partial | R-QUAL-08 (check-quality.py `constructor-resources`) | Only checks constructor bodies for known bad patterns (getSettings, connect, timeout_add, DBusProxy). Does NOT detect GObject creation (e.g., `new St.Widget()`, `new Gio.Settings()`) in constructors. Does not check module-level code (import-time side effects). |
| MUST NOT connect signals during initialization | **MUST** | Partial | R-QUAL-08 (check-quality.py `constructor-resources`) | Checks for `.connect()` in constructors, but skips widget subclass constructors (by design). Does not check module-level signal connections. |
| MUST NOT add main loop sources during initialization | **MUST** | Partial | R-QUAL-08 (check-quality.py `constructor-resources`) | Checks for `timeout_add` in constructors. Does not check module-level `timeout_add`/`idle_add`. |
| MUST NOT modify GNOME Shell during initialization | **MUST** | Covered | R-INIT-01 (check-init.py) | Detects Shell global access (`Main.panel`, `Main.overview`, etc.) at module scope and in constructors. |
| All GObject classes disallowed during init | **MUST** | Covered | R-INIT-01 (check-init.py), R-QUAL-08 (check-quality.py) | check-init.py detects GObject constructors (`new St.`, `new Gio.`, `new GLib.`, `new Clutter.`) at module scope and in constructors via expanded regex. |

## Section 2: Object and Resource Cleanup

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| Objects/widgets created MUST be destroyed in `disable()` | **MUST** | Partial | R-LIFE-01 (signal balance), R-LIFE-02 (untracked timeouts), R-LIFE-09 (keybinding), check-lifecycle.py | Heuristic checks for signal balance and timeout tracking. No general "widget created in enable() but not destroyed in disable()" check. |
| All dynamically stored memory MUST be cleared in `disable()` | **MUST** | Tier 3 Only | lifecycle-checklist.md | Checklist covers nulling references. No automated check for missing `= null` after destroy. |
| If `run_dispose()` is used, MUST include comment explaining why | **MUST** (if used) | Partial | R-SEC-06 (pattern: `.run_dispose(`) | Detects `run_dispose()` usage but does not verify a comment exists explaining the need. |

## Section 3: Signal Management

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| Any signal connections MUST be disconnected in `disable()` | **MUST** | Partial | R-LIFE-01 (check-lifecycle.py `signal-balance`) | Heuristic balance check (warns if connects > disconnects + 2). Does not trace individual signals to verify each one is disconnected. |
| Handler IDs MUST be stored for later disconnection | **MUST** | Partial | R-LIFE-01 (indirect) | The signal balance check implicitly catches the worst cases, but unstored handler IDs from `.connect()` are not directly flagged. |

## Section 4: Main Loop Sources

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| All main loop sources MUST be removed in `disable()` | **MUST** | Covered | R-LIFE-02 (check-lifecycle.py `untracked-timeout`), R-LIFE-12 (check-lifecycle.py `source-remove-verify`) | Checks if return values are assigned AND verifies `GLib.Source.remove()` is called in `disable()` for stored IDs. |
| Sources MUST be removed even if callback returns `GLib.SOURCE_REMOVE` | **MUST** | Tier 3 Only | lifecycle-checklist.md | Checklist mentions this. No automated verification. |

## Section 5: Library and Import Restrictions

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| MUST NOT import `Gdk` in Shell process | **MUST** | Covered | R-IMPORT-02, check-imports.sh | Checks `gi://Gdk` in extension.js and lib/**/*.js. |
| MUST NOT import `Gtk` in Shell process | **MUST** | Covered | R-IMPORT-01, check-imports.sh | Checks `gi://Gtk` in extension.js and lib/**/*.js. |
| MUST NOT import `Adw` in Shell process | **MUST** | Covered | R-IMPORT-03, check-imports.sh | Checks `gi://Adw` in extension.js and lib/**/*.js. |
| MUST NOT import `Clutter` in preferences | **MUST** | Covered | R-IMPORT-04, check-imports.sh | Checks `gi://Clutter` in prefs.js. |
| MUST NOT import `Meta` in preferences | **MUST** | Covered | R-IMPORT-05, check-imports.sh | Checks `gi://Meta` in prefs.js. |
| MUST NOT import `St` in preferences | **MUST** | Covered | R-IMPORT-06, check-imports.sh | Checks `gi://St` in prefs.js. |
| MUST NOT import `Shell` in preferences | **MUST** | Covered | R-IMPORT-07, check-imports.sh | Checks `gi://Shell` in prefs.js. |

## Section 6: Deprecated Modules

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| MUST NOT import `ByteArray` | **MUST** | Covered | R-DEPR-03, ego-lint.sh `no-deprecated-modules` | Both pattern rule and inline check. |
| MUST NOT import `Lang` | **MUST** | Covered | R-DEPR-02, ego-lint.sh `no-deprecated-modules` | Both pattern rule and inline check. |
| MUST NOT import `Mainloop` | **MUST** | Covered | R-DEPR-01, ego-lint.sh `no-deprecated-modules` | Both pattern rule and inline check. |
| MUST NOT use `imports.misc.extensionUtils` | **MUST** | Covered | R-DEPR-05 | Pattern matches `ExtensionUtils`. |

## Section 7: Code Quality and Readability

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| Code MUST NOT be minified | **MUST** | Covered | R-FILE-06, ego-lint.sh `minified-js` | Checks for lines > 500 chars and webpack boilerplate. |
| Code MUST NOT be obfuscated | **MUST** | Partial | R-FILE-06 (minified-js) | Minification check catches some obfuscation (long lines). No specific check for obfuscation techniques (encoded strings, variable mangling without long lines). |
| TypeScript MUST be transpiled to well-formatted JavaScript | **MUST** | Partial | R-FILE-06 | Would catch poorly-transpiled TS (minified output). Well-formatted but clearly machine-generated TS output is not flagged. |
| MUST NOT print excessively to log | **MUST** | Covered | R-LOG-01 (console.log), R-QUAL-13 (debug volume), R-QUAL-17 (logging volume), ego-lint.sh `no-console-log` | console.log is hard FAIL. Excessive console.debug/warn/error volumes are WARN. |
| Code MUST be formatted in a way that can be easily reviewed | **MUST** | Partial | R-FILE-06 (minified), R-QUAL-10 (code volume), R-QUAL-12 (file complexity) | Catches minification and excessive size. No check for poor formatting (inconsistent indentation, no line breaks). |

## Section 8: AI-Generated Code

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| Extensions MUST NOT be submitted if primarily AI-generated | **MUST** | Partial | R-SLOP-01 through R-SLOP-17, R-QUAL-01 through R-QUAL-11, ai-slop-checklist.md | Multiple heuristic signals (try-catch density, hallucinated APIs, typeof super, comment density, impossible state, pendulum pattern). Tier 3 checklist has 18 detailed items. Inherently hard to fully automate. |
| Developers MUST be able to justify and explain submitted code | **MUST** | Tier 3 Only | ai-slop-checklist.md | Semantic requirement; only addressable during human/AI code review. |

## Section 9: Metadata Requirements

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| `uuid` must be present | **MUST** | Covered | R-META-01 (check-metadata.py) | |
| `uuid` format: only alphanumeric + . _ - @ | **MUST** | Covered | R-META-03 (check-metadata.py) | |
| `uuid` must contain `@` | **MUST** | Covered | R-META-13 (check-metadata.py) | |
| MUST NOT use `gnome.org` as namespace | **MUST** | Covered | R-META-04 (check-metadata.py) | |
| Directory name MUST match UUID | **MUST** | Covered | R-META-02 (check-metadata.py) | |
| `name` must be present | **MUST** | Covered | R-META-05 (check-metadata.py) | |
| `description` must be present | **MUST** | Covered | R-META-06 (check-metadata.py) | |
| `shell-version` must be array | **MUST** | Covered | R-META-07 (check-metadata.py) | |
| `shell-version` MUST contain only stable releases | **MUST** | Partial | R-META-17 (future-shell-version), R-META-23 (dev-limit) | Warns on future versions and multiple dev releases. Does NOT validate that entries are actual released GNOME versions (e.g., would not reject `"99"` or `"37"`). |
| MUST NOT claim support for future versions | **MUST** | Partial | R-META-17 (check-metadata.py) | Issues WARN (not FAIL) for versions > current stable. Guidelines say this is a hard reject. |
| `url` field required for EGO | **MUST** | Partial | R-META-22 (check-metadata.py) | Issues WARN, not FAIL. Guidelines say MUST for EGO submission. |
| `session-modes` MUST be dropped if only `["user"]` | **MUST** | Partial | R-META-09 (check-metadata.py) | Issues WARN, not FAIL. Guidelines explicitly call this a hard reject. |
| `donations` MUST only contain valid keys | **MUST** | Covered | R-META-18 (check-metadata.py) | FAIL on invalid keys. |
| `donations` MUST be dropped if not used | **MUST** | Covered | R-META-24 (check-metadata.py) | FAIL on empty donations. |
| `version-name` format validation | **MUST** | Covered | R-META-20 (check-metadata.py) | Validates 1-16 char regex. |

## Section 10: GSettings Schema Requirements

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| Schema ID MUST use `org.gnome.shell.extensions` as base | **MUST** | Covered | R-SCHEMA-02, R-META-10, check-schema.sh | Validated in both metadata and schema XML. |
| Schema path MUST use `/org/gnome/shell/extensions/` as base | **MUST** | Covered | R-SCHEMA-03, check-schema.sh | Validates path prefix and trailing slash. |
| Schema XML file MUST be included if settings-schema declared | **MUST** | Covered | R-SCHEMA-01, check-schema.sh | FAIL if metadata declares schema but no XML found. |
| Schema XML filename MUST follow `<schema-id>.gschema.xml` | **MUST** | Partial | R-SCHEMA-05, check-schema.sh | Issues WARN, not FAIL. Guidelines say MUST. |

## Section 11: Packaging and File Requirements

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| Extension MUST contain `extension.js` | **MUST** | Covered | R-FILE-01, ego-lint.sh `file-structure/extension.js` | |
| Extension MUST contain `metadata.json` | **MUST** | Covered | R-FILE-02, ego-lint.sh `file-structure/metadata.json` | |
| MUST NOT include binary executables or libraries | **MUST** | Covered | R-FILE-04, R-PKG-13, ego-lint.sh `no-binary-files` | Checks file extensions + ELF magic bytes. |

## Section 12: Security and Privacy

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| Clipboard access MUST be declared in description | **MUST** | Partial | R-SEC-07 (pattern: `St.Clipboard`) | Detects clipboard usage and advises disclosure. Does NOT verify that the metadata description actually contains disclosure text. |
| MUST NOT share clipboard data with third parties without explicit user interaction | **MUST** | Tier 3 Only | security-checklist.md | Requires semantic review of clipboard + network code flow. |
| MUST NOT ship with default keyboard shortcuts for clipboard interaction | **MUST** | Covered | R-SEC-16 (check-lifecycle.py `clipboard-keybinding`) | Cross-references St.Clipboard and addKeybinding in same file. |
| MUST NOT use telemetry tools to track users | **MUST** | Covered | R-SEC-08 (pattern: analytics/telemetry/trackEvent/etc.) | Pattern-based detection of common telemetry identifiers. |
| MUST NOT share user data online | **MUST** | Tier 3 Only | security-checklist.md | Requires semantic analysis of network requests and data payloads. |

## Section 13: Subprocess and Script Requirements

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| Privileged subprocess MUST use `pkexec` (not sudo directly) | **MUST** | Partial | R-SEC-04 (pattern: `pkexec`/`sudo`) | Flags both pkexec and sudo. Does not distinguish between them to enforce pkexec-only. |
| Privileged subprocess MUST NOT be user-writable executable or script | **MUST** | Uncovered | -- | No check for script permissions or paths. Requires filesystem analysis of referenced scripts. |
| Scripts MUST be written in GJS unless absolutely necessary | **MUST** | Partial | ego-lint.sh `non-gjs-scripts` | Issues WARN for .py/.sh/.rb/.pl files. Guidelines say MUST. |
| MUST NOT include binary executables or libraries | **MUST** | Covered | R-FILE-04, ego-lint.sh `no-binary-files` | |
| Scripts MUST be distributed under OSI-approved license | **MUST** | Tier 3 Only | licensing-checklist.md | Requires manual license review of included scripts. |
| MUST NOT use synchronous subprocess calls in Shell process | **MUST** | Covered | R-SEC-14 (pattern: sync subprocess), R-DEPR-08 (upgraded to blocking) | Detects `spawn_sync`, `GLib.spawn_command_line_sync`, and other synchronous subprocess patterns. Upgraded to FAIL severity as sync calls block the compositor. |

## Section 14: Session Modes

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| Using `unlock-dialog` MUST be necessary for correct operation | **MUST** | Tier 3 Only | lifecycle-checklist.md | Requires semantic understanding of why lock screen access is needed. |
| All keyboard event signals MUST be disconnected in lock screen mode | **MUST** | Uncovered | -- | No check for keyboard signals (`key-press-event`, `key-release-event`, `captured-event`) remaining connected during `unlock-dialog`. |
| `disable()` function MUST include comment explaining why `unlock-dialog` is used | **MUST** | Covered | R-LIFE-14 (check-lifecycle.py) | Warns when unlock-dialog declared but disable() has no explanatory comment. |
| Extensions MUST NOT disable selectively | **MUST** | Covered | R-LIFE-13 (check-lifecycle.py) | Detects `if (...) return;` in disable() that skips cleanup. |
| `session-modes` field MUST be dropped if only using `user` | **MUST** | Partial | R-META-09 (check-metadata.py) | Issues WARN, not FAIL. Should be FAIL per guidelines. |

## Section 15: Licensing and Attribution

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| MUST be distributed under terms compatible with GPL-2.0-or-later | **MUST** | Partial | R-FILE-03, ego-lint.sh `license` | Checks for LICENSE/COPYING file existence (WARN if missing). Does NOT validate license content/compatibility. |
| Code from other extensions MUST include original author attribution | **MUST** | Tier 3 Only | licensing-checklist.md (L2) | Requires semantic analysis to detect borrowed code. |
| Attribution MUST be in distributed files (not just repo) | **MUST** | Tier 3 Only | licensing-checklist.md (L2) | Requires semantic review. |

## Section 16: Content and Code of Conduct

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| MUST NOT violate GNOME Code of Conduct | **MUST** | Tier 3 Only | licensing-checklist.md (L5) | Requires semantic content review. Not automatable. |
| MUST NOT promote political agendas | **MUST** | Tier 3 Only | licensing-checklist.md (L4) | Requires semantic content review. Not automatable. |
| MUST NOT include copyrighted content without permission | **MUST** | Tier 3 Only | licensing-checklist.md (L3) | Requires asset review. Not automatable. |
| MUST NOT include trademarked content without permission | **MUST** | Tier 3 Only | licensing-checklist.md (L3) | Requires asset review. Not automatable. |

## Section 17: Functionality Requirements

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| Extensions that are fundamentally broken MUST be rejected | **MUST** | Uncovered | -- | Requires runtime testing. Not feasible for static analysis. |
| Extensions with no purpose or functionality MUST be rejected | **MUST** | Uncovered | -- | Requires semantic understanding of extension purpose. |

## Section 21: Preferences (prefs.js)

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| MUST extend `ExtensionPreferences` class | **MUST** | Partial | R-PREFS-02 (check-prefs.py `default-export`) | Checks for `export default class` but does NOT verify it extends `ExtensionPreferences`. |
| MUST implement `fillPreferencesWindow()` or `getPreferencesWidget()` | **MUST** | Partial | R-PREFS-01 (check-prefs.py) | Detects dual-prefs pattern conflict. Does not FAIL if neither method is present. |
| MUST use GTK4 and Adwaita (not GTK3) | **MUST** | Uncovered | -- | No check for GTK3-specific imports or patterns in prefs.js (e.g., `Gtk.init(null)`, `Gtk.Box.pack_start`, GTK3-only widget names). |
| MUST NOT import Shell, Clutter, Meta, St in prefs | **MUST** | Covered | R-IMPORT-04 through R-IMPORT-07, check-imports.sh | |

## Section 22: ESModules Migration (GNOME 45+)

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| `Extension` and `ExtensionPreferences` MUST be default exports | **MUST** | Covered | R-FILE-07 (check-lifecycle.py), R-PREFS-02 (check-prefs.py) | Checks both extension.js and prefs.js for `export default class`. |
| ESM extensions cannot support pre-45 versions | Constraint | Covered | R-META-25 (check-metadata.py `esm-version-floor`) | FAIL if ESM imports detected with pre-45 shell-version. |

## Section 24: Monkey-Patching and InjectionManager

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| All monkey patches MUST be restored in `disable()` | **MUST** | Covered | Enhanced R-LIFE-10 (check-lifecycle.py) | Detects InjectionManager without `.clear()` in disable(), and direct prototype.method = assignments without restoration. |

## Section 26: Network Access and Data Sharing

| Guideline Requirement | Severity | Currently Covered? | By Which Rule/Check? | Gap Notes |
|---|---|---|---|---|
| Content accessed/served MUST NOT violate Code of Conduct | **MUST** | Tier 3 Only | security-checklist.md | Requires semantic review. |
| Clipboard data MUST NOT be shared with third parties | **MUST** | Tier 3 Only | security-checklist.md | Requires analysis of data flow between clipboard and network code. |
| User data MUST NOT be shared online | **MUST** | Tier 3 Only | security-checklist.md | Requires semantic analysis of outbound data. |

---

## Summary: Critical Uncovered MUST Requirements

These MUST requirements have **no automated check** (not even a partial heuristic):

| # | Requirement | Section | Impact | Recommendation |
|---|---|---|---|---|
| ~~1~~ | ~~MUST NOT ship with default keyboard shortcuts for clipboard interaction~~ | ~~S12~~ | ~~Medium~~ | **Covered** — R-SEC-16 in check-lifecycle.py |
| 2 | Privileged subprocess MUST NOT be user-writable | S13 | High | Hard to check statically; add as Tier 3 checklist item if not present |
| 3 | Keyboard event signals MUST be disconnected in lock screen mode | S14 | High | Add check: if `unlock-dialog` in session-modes, verify `key-press-event`/`key-release-event` disconnection patterns |
| ~~4~~ | ~~`disable()` MUST include comment explaining `unlock-dialog` usage~~ | ~~S14~~ | ~~Medium~~ | **Covered** — R-LIFE-14 in check-lifecycle.py |
| ~~5~~ | ~~Extensions MUST NOT disable selectively~~ | ~~S14~~ | ~~Medium~~ | **Covered** — R-LIFE-13 in check-lifecycle.py |
| ~~6~~ | ~~All monkey patches MUST be restored in `disable()`~~ | ~~S24~~ | ~~High~~ | **Covered** — Enhanced R-LIFE-10 in check-lifecycle.py |
| 7 | Fundamentally broken / no-purpose extensions | S17 | Low | Not feasible for static analysis; inherently a runtime/semantic check |

## Summary: Severity Mismatches (WARN should be FAIL)

These requirements are correctly detected but the severity level is too low:

| Requirement | Current Severity | Correct Severity | Rule | Status |
|---|---|---|---|---|
| `session-modes: ["user"]` is redundant | ~~WARN~~ FAIL | FAIL (hard reject) | R-META-09 | **Fixed** |
| Future shell-version entries | ~~WARN~~ FAIL | FAIL (hard reject) | R-META-17 | **Fixed** |
| Missing `url` field in metadata | ~~WARN~~ FAIL | FAIL (for EGO) | R-META-22 | **Fixed** |
| Schema filename convention mismatch | ~~WARN~~ FAIL | FAIL | R-SCHEMA-05 (check-schema.sh) | **Fixed** |

## Summary: Covered but Weak (Partial) Checks

These requirements have checks that catch some but not all violations:

| Requirement | Weakness | Improvement | Status |
|---|---|---|---|
| No resource creation in constructors (R-QUAL-08) | Only checks 5 specific patterns; misses arbitrary GObject creation | Expand pattern list: `new St.`, `new Gio.`, `new GLib.`, `new Clutter.` | **Fixed** (check-init.py expanded regex) |
| Signal disconnect balance (R-LIFE-01) | Heuristic tolerance of +2 allows small leaks | Consider tighter threshold or per-signal tracking | Open |
| Timeout source removal in disable (R-LIFE-02) | Only checks if return value is stored, not if `Source.remove` is called | Add disable() body scan for matching `Source.remove` calls | **Fixed** (R-LIFE-12) |
| AI-generated code detection (R-SLOP-*) | Pattern-based; misses novel AI patterns | Inherent limitation; Tier 3 checklist compensates | Open (inherent) |
| Code obfuscation (R-FILE-06) | Only catches minification (long lines); not variable mangling or encoding | Add checks for high entropy variable names or base64-encoded strings | Open |
| run_dispose comment requirement | Detects usage but not comment | Add lookahead for comment on preceding/same line | **Done** (R-QUAL-21) |
| Clipboard disclosure verification (R-SEC-07) | Detects clipboard usage; does not verify description text | Cross-reference with metadata.json description content | **Done** (R-QUAL-22) |
| License file validation (R-FILE-03) | Checks existence only; not content | Parse LICENSE file for GPL-compatible license identifiers (SPDX) | **Fixed** (GPL-compatibility scanning) |
| Prefs extends ExtensionPreferences (R-PREFS-02) | Checks `export default class` but not the extends clause | Regex for `export default class \w+ extends ExtensionPreferences` | **Fixed** (R-PREFS-02 strengthened) |
| Prefs method requirement | Detects dual-pattern conflict; does not fail when neither method present | Add FAIL if prefs.js has no `fillPreferencesWindow` and no `getPreferencesWidget` | **Done** (prefs/missing-prefs-method) |

---

## Priority Recommendations

### P0: Fix severity mismatches (quick wins, no new code needed) -- DONE
1. ~~`R-META-09` (`session-modes: ["user"]`): Change WARN to FAIL~~ **Done**
2. ~~`R-META-17` (future shell-version): Change WARN to FAIL~~ **Done**
3. ~~`R-META-22` (missing url): Change WARN to FAIL~~ **Done**

### P1: Add high-impact missing checks -- Partially done
4. **InjectionManager cleanup check** -- if `InjectionManager` or `overrideMethod` found, verify `.clear()` in disable() -- **Done** (R-LIFE-10)
5. ~~**Constructor GObject creation** -- expand R-QUAL-08 patterns to include `new St.`, `new Gio.`, `new Clutter.`, `new GLib.`~~ **Done** (check-init.py)
6. ~~**GTK3 in prefs.js** -- add patterns for GTK3-specific APIs~~ **Done** (R-PREFS-04)
7. **Keyboard signals in unlock-dialog** -- if `unlock-dialog` declared, check for key event signal cleanup

### P2: Strengthen existing partial checks -- Partially done
8. ~~**Timeout removal verification** -- verify `GLib.Source.remove()` in disable() body for stored timeout IDs~~ **Done** (R-LIFE-12)
9. ~~**License content parsing** -- basic SPDX identifier detection in LICENSE/COPYING files~~ **Done** (GPL-compatibility scanning)
10. ~~**Prefs ExtensionPreferences extends check** -- verify extends clause, not just default export~~ **Done** (R-PREFS-02 strengthened)
11. **Clipboard disclosure cross-reference** -- check metadata description for clipboard disclosure when St.Clipboard detected
12. **run_dispose comment check** -- verify adjacent comment when run_dispose detected

---

## New Coverage Added (2026-02-26)

The following areas are now covered through Tier 3 review checklists:

| Area | Coverage | Where |
|---|---|---|
| Accessibility | 7 checklist items (A1-A7): accessible-role, label-actor, Atk.StateType sync, keyboard navigation, focus order, color independence, focus chain | code-quality-checklist.md |
| Notification/dialog lifecycle | MessageTray.Source destroy signal, dialog lifecycle states, stale reference detection | lifecycle-checklist.md |
| Search provider contract | id/appInfo/canLaunchSearch contract, register/unregister in enable/disable, createIcon scaling | lifecycle-checklist.md |
| Translation best practices | gettext domain setup, ngettext for plurals, no string concatenation for translated strings | code-quality-checklist.md |

## New Coverage Added (2026-02-26) — Quality Optimization

| Area | New Rules/Checks | Where |
|---|---|---|
| Selective disable (R-LIFE-13) | Detects `if (...) return;` in disable() that skips cleanup | check-lifecycle.py |
| unlock-dialog comment (R-LIFE-14) | Warns when unlock-dialog declared but disable() has no explanatory comment | check-lifecycle.py |
| Clipboard + keybinding (R-SEC-16) | Cross-references St.Clipboard and addKeybinding in same file | check-lifecycle.py |
| Prototype override (enhanced R-LIFE-10) | Detects direct prototype.method = assignments without restoration | check-lifecycle.py |
| Prefs method existence | Warns when prefs.js has neither fillPreferencesWindow nor getPreferencesWidget | check-prefs.py |
| run_dispose comment (R-QUAL-21) | Warns when run_dispose() lacks explanatory comment | check-quality.py |
| Clipboard disclosure (R-QUAL-22) | Cross-references St.Clipboard with metadata description | check-quality.py |
| CSS shell class override | Warns when stylesheet overrides known Shell theme classes at top level | check-css.py |
| Gio._promisify placement (R-INIT-02) | Warns when Gio._promisify() is inside enable() instead of module scope | check-init.py |
| Hallucinated APIs (R-SLOP-24/25/26) | new Gio.Settings(), Main.extensionManager.enable/disable, Shell.ActionMode.ALL | patterns.yaml |
| Translation anti-pattern (R-I18N-01) | Template literal inside gettext _() breaks xgettext | patterns.yaml |
| /tmp path security (R-SEC-17) | Hardcoded /tmp paths instead of XDG dirs | patterns.yaml |
| GNOME 49 compat (R-VER49-06/07) | Clutter.DragAction, Clutter.SwipeAction removed | patterns.yaml |

---

## Rejection Case Studies

Real-world EGO rejections that informed the plugin's detection rules:

### Search Light (May 2024) -- Lifecycle Violations

**Rejection reason:** Signals connected in `enable()` were not fully disconnected in `disable()`. Search provider was registered but not unregistered, leading to crashes when the extension was disabled mid-search.

**Relevant rules:** R-LIFE-01 (signal-balance), lifecycle-checklist.md (search provider cleanup)

### Blur my Shell (March 2024) -- Init-Time Violations

**Rejection reason:** GObject creation (`new Gio.Settings()`) detected in the extension constructor rather than in `enable()`. Module-level code was creating Shell modifications at import time.

**Relevant rules:** R-INIT-01 (check-init.py), R-QUAL-08 (constructor-resources)

### Wechsel (April 2024) -- Sync Subprocess, Unnecessary Metadata

**Rejection reason:** Used `GLib.spawn_command_line_sync()` to invoke external commands, blocking the compositor. Also included unnecessary metadata fields that were not part of the specification.

**Relevant rules:** R-SEC-14 (sync subprocess pattern), R-DEPR-08 (blocking subprocess upgraded to FAIL), check-metadata.py (unknown field detection)

### Power Tracker (September 2024) -- Missing URL

**Rejection reason:** Missing `url` field in metadata.json. EGO requires this field for all submissions to provide users with a link to the extension's source code or homepage.

**Relevant rules:** R-META-22 (missing url, now FAIL)

### Open Bar (February 2024) -- Orphaned Signals, Missing Timeout Cleanup

**Rejection reason:** Multiple signal connections in helper modules were never disconnected because the cleanup code only covered the main extension file. Timeouts created in a utility module were not tracked or removed in `disable()`.

**Relevant rules:** R-LIFE-01 (signal-balance), R-LIFE-02 (untracked-timeout), R-LIFE-12 (source-remove-verify), check-resources.py (cross-file orphan detection)
