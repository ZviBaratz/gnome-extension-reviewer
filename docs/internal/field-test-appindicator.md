# Field Test: AppIndicator/KStatusNotifierItem Support

**Date**: 2026-03-01
**Target**: [gnome-shell-extension-appindicator](https://github.com/ubuntu/gnome-shell-extension-appindicator) (latest main)
**Extension**: `appindicatorsupport@rgcjonas.gmail.com` — GNOME 45-50, 17 JS files (15 root + 2 prefs), GPL-2.0
**Key patterns**: D-Bus service host (StatusNotifierWatcher protocol), custom signal abstraction (`connectSmart`/`disconnectSmart`), `promiseUtils.js` (CancellablePromise), GSettings (10 keys), GTK4/Adwaita prefs, XEmbed tray icons, icon pixmap conversion

## Why This Extension

Previous field tests (hara-hachi-bu, Clipboard Indicator) covered consumer-side patterns. AppIndicator exercises:
- **D-Bus-as-server**: acquiring bus names, exporting objects, implementing D-Bus interfaces
- **Custom signal abstractions**: `connectSmart`/`disconnectSmart` auto-cleanup pattern
- **Multi-file resource graphs across 17 files**: deeply interconnected module structure
- **Legacy compatibility shims**: runtime feature detection for GNOME 45-50 range
- **Non-JS resource files**: `interfaces-xml/` directory with D-Bus XML definitions

## ego-lint Results

### Before Fixes

| Status | Count |
|--------|-------|
| PASS   | 174   |
| FAIL   | 14    |
| WARN   | 78    |
| SKIP   | 14    |
| **Total** | **280** |

Exit code: 1

### After Fixes

| Status | Count |
|--------|-------|
| PASS   | 178   |
| FAIL   | 11    |
| WARN   | 69    |
| SKIP   | 14    |
| **Total** | **272** |

Exit code: 1 (6 true positives remain, 3 init-time FPs, 2 borderline)

### Metrics

| Metric | Value |
|--------|-------|
| JS files | 17 |
| Total lines | 5655 |
| Largest file | appIndicator.js (1604) |
| CSS lines | 0 |
| Schema keys | 10 |
| Resource graph | 16 files, 84 creates, 113 destroys, 0 orphans |
| Code provenance | score=4 (domain-vocabulary(51), nontrivial-algorithms(10), debug-comments(10), consistent-naming-style) |

## Finding Classification

### FAIL — True Positives (6 of 14)

1. **R-DEPR-04 ×3**: Legacy `imports.*` syntax in indicatorStatusIcon.js:540 (`imports.gi.Meta.is_wayland_compositor()`), interfaces.js:25 (`imports.gi.GLib.file_get_contents()`), appIndicator.js:44 (`imports.gi.Cogl.PixelFormat.ARGB_8888`). Correct — GNOME 45+ should use ESM imports exclusively.

2. **R-VER44-01/02**: `Meta.later_add()` and `Meta.later_remove()` in promiseUtils.js:295/307. Correctly flagged — these APIs were removed in GNOME 44, and the extension targets GNOME 45+. The `MetaLaterPromise` class is likely dead code.

3. **metadata/future-shell-version**: `shell-version` includes `"50"` which is newer than current stable (49). Correct advisory — EGO may reject future versions.

### FAIL — False Positives (8 of 14)

4. **R-SLOP-16** (interfaces.js:25): `GLib.file_get_contents()` flagged as "does not exist in GJS". **INCORRECT** — `GLib.file_get_contents()` IS a valid GI binding for `g_file_get_contents()`. Returns `[Boolean, Uint8Array]`. The rule was written assuming AI hallucination, but this API actually exists. **Needs fix: remove or rewrite R-SLOP-16.**

5. **R-VER46-01/02** (util.js:380/387): `add_actor()`/`remove_actor()` flagged as removed in GNOME 46. The code is a **compatibility shim** with runtime detection:
   ```javascript
   if (obj.add_actor) obj.add_actor(actor);
   else obj.add_child(actor);
   ```
   The pattern rule can't see the conditional guard. For GNOME 46+ where `add_actor` is undefined, the code correctly falls through to `add_child()`. **Needs fix: pattern rules should support a suppression pattern for defensive checks.**

6. **no-deprecated-modules** (1 FAIL): Counts `imports.gi.` usage — overlaps with R-DEPR-04. Minor duplication, not a significant FP.

7. **non-gjs-scripts** (1 FAIL): Flags `indicator-test-tool/ksni.py` as a non-GJS script. This is a **developer test tool**, not part of the extension. However, the detection is technically correct since it ships in the source tree. Borderline TP — the tool shouldn't ship in the EGO package, but source-level review can't distinguish dev tools from shipped files.

8. **init/shell-modification ×3**: promiseUtils.js:47, statusNotifierWatcher.js:49, appIndicator.js:412. All three are **False Positives** with two distinct issues:
   - **Wrong line numbers**: `check-init.py` strips multi-line `/* */` comments without preserving line counts (collapses to empty string, shifting subsequent lines). Line 47 in promiseUtils.js is actually `new GLib.Error()` — not a shell modification.
   - **Over-broad constructor flagging**: The check flags `new GLib.Error()`, `new Gio.Cancellable()` in constructors of non-GObject classes (CancellablePromise, StatusNotifierWatcher, AppIndicator). These classes are only instantiated during enable() flow, not at init time. The check can't trace call graphs to distinguish init-time from runtime construction.
   - **Missed real init-time concern**: The Extension constructor (extension.js) calls `Interfaces.initialize(this)` and creates `new Util.NameWatcher(...)` — both before enable() — but these are NOT flagged because `Util.NameWatcher` doesn't match the GI namespace pattern. **False negative.**

### WARN — True Positives (notable)

| Check | Finding | Classification |
|-------|---------|----------------|
| license | "could not confirm GPL-compatibility" | **TP** — LICENSE is plain GPL-2.0 text, not SPDX-tagged. Detection could improve. |
| R-SEC-06 | `run_dispose()` in statusNotifierWatcher.js:281 | **TP** — run_dispose needs justification |
| R-LOG-03 ×11 | `print()`/`printerr()` in indicator-test-tool/ | **TP** — dev tool, but correct for production audit |
| R-QUAL-26 | Custom Logger class in util.js | **TP** — Logger wraps GLib.log_structured; `console.debug` is preferred |
| R-QUAL-33 | `Gio._promisify()` in 4 files at module scope | **TP** — correct advisory, permanent prototype mutation |
| metadata/uuid-matches-dir | UUID ≠ directory name | **TP** — expected for cloned repos |
| quality/module-state | `settingsManager.js:17` mutable module-level `let` | **TP** — intentional singleton but valid concern |
| quality/mock-in-production | `indicator-test-tool/testTool.js` | **TP** — test files shouldn't ship |
| quality/constructor-resources ×8 | `.connect()` in constructors | **Mixed** — extension.js:36 is TP (Extension constructor runs before enable). promiseUtils.js:53/148 and indicatorStatusIcon.js:270/470/474/479/484 are FP (runtime-only constructors, cleaned up via destroy/connectSmart). |
| quality/private-api | `Main.layoutManager` access | **TP** — needs reviewer justification |
| lifecycle/signal-balance | 66 connects vs 18 disconnects | **FP** — doesn't account for `connectSmart` which auto-disconnects on destroy. The 66/.connect() count includes internal connectSmart calls. |
| lifecycle/untracked-timeout ×5 | Timer returns not stored | **Mixed** — promiseUtils.js:55 is FP (GSource-based promise with _cleanup). indicator-test-tool/ entries are TP but irrelevant (dev tool). |
| lifecycle/destroy-no-null ×5 | `.destroy()` without nulling | **TP** — style advisory, valid |
| gobject/missing-gtypename ×5 | GObject.registerClass without GTypeName | **TP** — genuine collision risk |
| async/missing-cancellable | dbusMenu.js:761, appIndicator.js:1350 | **TP** — async ops should use cancellable |
| disclosure/private-api | Undisclosed in metadata description | **TP** — reviewers expect disclosure |
| disclosure/file-io | Undisclosed in metadata description | **TP** — reviewers expect disclosure |

### WARN — False Positives (notable)

| Check | Finding | Classification |
|-------|---------|----------------|
| R-SLOP-13 ×3 | `this instanceof` in dbusMenu.js:698/707/720 | **FP** — These are methods in `MenuItemFactory` object, bound to different `shellItem` types via `connectSmart`. `this` CAN be different types (PopupMenuItem vs PopupSubMenuMenuItem). The instanceof check is valid. |
| R-SLOP-35 ×3 | `Object.freeze()` in appIndicator.js:46/53/59 | **FP** — Standard JS enum pattern (`SNICategory`, `SNIStatus`, `SNIconType`). Object.freeze for immutable enum objects is idiomatic, not AI smell. |
| R-SLOP-38 ×4 | Over-long identifiers (>20 chars) | **FP** — `brightnessContrastEffect` and similar are standard Clutter API names. Domain-specific compound nouns, not AI verbosity. |
| R-QUAL-31 ×7 | `_onDestroy()` should be `destroy()` | **FP** — `_onDestroy()` is the signal handler pattern from PanelMenu.Button. The code checks `if (!super._onDestroy)` before connecting, consistent with Shell's internal convention. Renaming to `destroy()` would conflict with GObject's own `destroy()`. |
| lifecycle/connectObject-migration | 6 manual signal connections | **FP** — Extension uses `connectSmart()` which provides equivalent auto-cleanup functionality. The check only looks for `connectObject` as the migration target. |
| quality/redundant-cleanup | 4 verbose destroy guards | **Borderline** — `if (x) x.destroy()` vs `x?.destroy()` is a style preference. The extension predates optional chaining. |

### SKIP — Correctly Applied (14)

- R-WEB-01/02/10/11: Timer APIs correctly skipped for GNOME 45+
- R-DEPR-04-legacy: Correctly skipped (extension is GNOME 45+)
- css/scoping, css/shell-class-override: No stylesheet.css — correct
- polkit/* ×3: No polkit files — correct
- eslint: No eslint config — correct
- package/exists: No zip — correct
- schema-usage/* ×2: Dynamic key access detected — correct (extension uses `settings.get_string()` with dynamic key names)

### PASS — Notable True Negatives

- **lifecycle/dbus-export-leak**: Correctly PASS — `export()`/`unexport()` paired in statusNotifierWatcher.js
- **prefs/extends-base**: Correctly detects ExtensionPreferences in `prefs.js` (not in `preferences/` subdirectory)
- **code-provenance**: score=4 correctly identifies hand-written code (51 domain vocab, 10 algorithms, consistent naming)
- **metadata/gettext-domain-consistency**: Correctly matches `AppIndicatorExtension` across JS and metadata
- **resource-tracking/ownership**: 0 orphans — correct (extension has thorough destroy chains)

## Detection Gaps Identified

### 1. ~~`connectSmart`/`disconnectSmart` invisible to resource graph~~ **RESOLVED (session 21)**

~~The extension's primary signal management abstraction (`Util.connectSmart`) is used 30+ times across 6 files. `build-resource-graph.py` doesn't recognize it.~~

**Fixed**: `connectSmart`/`disconnectSmart` added to `build-resource-graph.py` signal patterns, `check-lifecycle.py` signal balance, and `check-quality.py` constructor-resources skip.

### 2. ~~Bus name ownership lifecycle not tracked~~ **RESOLVED (session 21)**

~~`check-lifecycle.py` tracks `export()`/`unexport()` symmetry but NOT `Gio.DBus.session.own_name()`/`Gio.DBus.session.unown_name()`.~~

**Fixed**: New `check_bus_name_lifecycle()` function (R-LIFE-20) in `check-lifecycle.py`.

### 3. R-SLOP-16 (`GLib.file_get_contents`) is wrong

The rule claims this API "does not exist in GJS", but it does — it's a valid GI binding for `g_file_get_contents()`. This is a confirmed false assertion in the rule.

**Fix needed**: Remove R-SLOP-16 or change to advisory about preferring `Gio.File.load_contents()`.

### 4. `check-init.py` line numbers drift with block comments

`strip_comments()` uses `re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)` which collapses multi-line block comments to empty strings, shifting all subsequent line numbers. This causes incorrect line references in the output.

**Fix needed**: Replace `/* */` content with equivalent whitespace (one newline per removed line) to preserve line numbers.

### 5. ~~`check-init.py` too aggressive for non-Extension constructors~~ **RESOLVED (session 21)**

~~The check flags `new GLib.Error()` and `new Gio.Cancellable()` in constructors of non-GObject classes that are only instantiated at runtime.~~

**Fixed**: GObject constructor check in `check-init.py` now scoped to `extension.js` only. Shell globals still flagged in all files.

### 6. Version-gated pattern rules can't see runtime guards

R-VER46-01/02 flag `add_actor()`/`remove_actor()` even when the code has explicit runtime feature detection (`if (obj.add_actor)`). The pattern-based approach can't handle conditional usage.

**Fix needed**: Consider supporting a `guard-pattern` field (similar to `replacement-pattern`) that suppresses a match when a guard expression appears on the same or adjacent line.

### 7. R-SLOP-13 too broad for factory/mixin patterns

The rule assumes `this instanceof` inside a class method is always true. This fails for factory objects and mixin patterns where methods are bound to different types via callbacks or `call()`/`apply()`.

**Fix needed**: Restrict R-SLOP-13 to `class` method bodies (not object literal methods or factory patterns).

### 8. R-SLOP-35 too broad for standard enum patterns

`Object.freeze()` on enum-like constant objects is a standard JS pattern, not an AI smell. The rule triggers on legitimate code in well-maintained extensions.

**Fix needed**: Add suppression when `Object.freeze()` wraps a simple string/number value mapping (all values are string or number literals).

### 9. R-QUAL-31 doesn't account for Shell's `_onDestroy` convention

PanelMenu.Button and other Shell base classes use `_onDestroy()` as a signal handler convention, not as a replacement for `destroy()`. The rule incorrectly advises renaming.

**Fix needed**: Suppress R-QUAL-31 when the method is connected via `this.connect('destroy', ...)` pattern.

### 10. `quality/constructor-resources` needs scope awareness — **PARTIALLY RESOLVED (session 21)**

The check flags `.connect()` in any constructor, but constructors of runtime-only utility classes (CancellablePromise, IndicatorStatusIcon) are only called within enable() flow and have proper cleanup via destroy/cancel.

**Partial fix**: Classes using `connectSmart`/`disconnectSmart` are now skipped (recognized as lifecycle management). Classes with `destroy()` were already skipped. Remaining FPs require full scope/call-graph analysis.

### 11. ~~No `call_sync()` detection~~ **RESOLVED (session 21)**

~~No rule flags synchronous D-Bus method calls (`call_sync()`, `get_sync()`, etc.) that block the main loop.~~

**Fixed**: New R-QUAL-35 pattern rule in `patterns.yaml` detects `.call_sync()`, `.get_sync()`, `.set_sync()`, `.call_with_unix_fd_list_sync()` as advisory.

## Comparison with Prior Field Tests

| Metric | hara-hachi-bu | Clipboard Indicator | AppIndicator |
|--------|---------------|--------------------:|-------------:|
| JS files | 17 | 6 | 17 |
| Total lines | ~4500 | ~3000 | 5655 |
| Total checks | 235 | 236 | 280 |
| PASS | 204 | 190 | 174 |
| FAIL | 0 | 2 | 14 |
| WARN | 8 | 27 | 78 |
| SKIP | 23 | 17 | 14 |
| Resource graph files | 17 | 6 | 16 |
| Resource orphans | 0 | 1 | 0 |
| Code provenance | 3 | N/A | 4 |
| **FP FAILs** | **0** | **0** (post-fix) | **8** |
| **FP WARNs** | **0** | **0** (post-fix) | **~15** |

### Analysis

AppIndicator reveals significantly more false positives than prior field tests because:
1. **Custom abstractions**: `connectSmart` creates a disconnect between what ego-lint sees and what actually runs
2. **Compatibility shims**: Runtime feature detection can't be parsed by regex rules
3. **Factory patterns**: Object literal methods bound to different `this` types break AI slop heuristics
4. **Standard JS patterns**: `Object.freeze()` for enums, `_onDestroy` signal handler convention
5. **Legacy code coexistence**: GNOME 45+ extension with pre-ESM code fragments (imports.gi.*)

The extension's codebase is clearly hand-written (provenance score 4) and well-maintained by Canonical. The 78 warnings include ~15 false positives that a reviewer would need to mentally filter — significantly higher noise than prior field tests.

## Priority Improvements

### P0 — False Positive Fixes (blocking credibility)
1. **Remove/fix R-SLOP-16**: `GLib.file_get_contents()` exists in GJS
2. **Fix `check-init.py` line numbers**: Preserve line counts when stripping block comments
3. **Add guard-pattern support for version rules**: Suppress R-VER46-01/02 when runtime check present

### P1 — Noise Reduction (reviewer experience)
4. **Teach resource graph about `connectSmart`/`connectObject`**: Reduce false signal-balance warnings
5. **Restrict R-SLOP-13 scope**: Skip object literal methods
6. **Restrict R-SLOP-35 scope**: Skip simple enum mappings
7. **Restrict R-QUAL-31 scope**: Skip `_onDestroy` connected as signal handler
8. **Restrict `quality/constructor-resources`**: Only flag Extension class constructor

### P2 — New Detection Capabilities
9. **Add `own_name`/`unown_name` lifecycle tracking**
10. **Add `call_sync()` blocking D-Bus rule**
11. **Restrict `init/shell-modification`**: Don't flag non-Extension constructors

## Verdict

ego-lint correctly identifies the extension's main issues: legacy `imports.*` syntax (3 instances), dead code (`MetaLaterPromise` using removed APIs), missing GTypeName (5 instances), and GNOME 50 future version. However, 8 of 14 FAILs are false positives, and ~15 of 78 WARNs are false positives — significantly higher noise than prior field tests. The primary cause is AppIndicator's use of custom signal abstractions, runtime compatibility shims, and factory patterns that pattern-based rules can't handle.

The field test validates that ego-lint works well for "typical" extensions but reveals meaningful limitations when applied to large, protocol-implementing extensions with custom infrastructure.

## Changes Made

### P0 — False Positive Fixes
1. `rules/patterns.yaml`: R-SLOP-16 downgraded from blocking to advisory; reworded message (API exists, issue is synchronous blocking)
2. `skills/ego-lint/scripts/check-init.py`: `strip_comments()` now preserves newlines when removing block comments, fixing line number drift
3. `skills/ego-lint/scripts/apply-patterns.py`: Added `guard-pattern` field support — suppresses pattern match when guard regex matches current or previous line
4. `rules/patterns.yaml`: Added `guard-pattern` to R-VER46-01/02 for `if (obj.add_actor)` runtime checks
5. `skills/ego-lint/references/rules-reference.md`: Updated R-SLOP-16 documentation

### P1 — Noise Reduction
6. `rules/patterns.yaml`: Added `guard-pattern` to R-SLOP-13 — suppresses `!(this instanceof ...)` (negated form = polymorphic dispatch)
7. `rules/patterns.yaml`: Added `guard-pattern` to R-SLOP-35 — suppresses `const X = Object.freeze({` (enum pattern)
8. `rules/patterns.yaml`: Added `guard-pattern` to R-QUAL-31 — suppresses `.connect('destroy', ...this._onDestroy)` and `super._onDestroy()` call sites
9. `tests/fixtures/slop-object-freeze@test/extension.js`: Updated to use non-const freeze (AI pattern, not enum)

### Impact
- FAILs: 14 → 11 (-3 false positives eliminated)
- WARNs: 78 → 69 (-9 false positives eliminated)
- All 440 existing test assertions pass
- New `guard-pattern` feature reusable for future rules

### Remaining Known FPs (not fixed in session 20)
- init/shell-modification ×3: Constructors of non-Extension classes still flagged (needs call-graph analysis)
- lifecycle/signal-balance: `connectSmart` not recognized (needs resource graph enhancement)
- R-SLOP-38 ×4: Domain-specific identifiers flagged as "over-long" (hard to fix without semantic analysis)
- quality/constructor-resources ×6: Runtime-only constructors flagged (needs scope awareness)

### Session 21 Changes (2026-03-01)

1. `skills/ego-lint/scripts/check-lifecycle.py`: `check_signal_balance()` now recognizes `connectSmart`/`disconnectSmart` and `SignalTracker`/`SignalManager` — eliminates signal-balance FP
2. `skills/ego-lint/scripts/build-resource-graph.py`: `connectSmart`/`disconnectSmart` added to signal CREATE/DESTROY patterns — resource graph now tracks them
3. `skills/ego-lint/scripts/check-quality.py`: `check_constructor_resources()` recognizes `connectSmart`/`disconnectSmart` as lifecycle management — reduces constructor-resources FPs
4. `skills/ego-lint/scripts/check-init.py`: GObject constructor check scoped to `extension.js` only — eliminates 3 init/shell-modification FPs for helper file constructors
5. `rules/patterns.yaml`: R-SLOP-38 threshold raised from 20 to 25 chars — eliminates `brightnessContrastEffect` and similar standard API name FPs
6. `skills/ego-lint/scripts/check-lifecycle.py`: New `check_bus_name_lifecycle()` (R-LIFE-20) — detects missing `bus_unown_name()` (detection gap #2 closed)
7. `rules/patterns.yaml`: New R-QUAL-35 — detects synchronous D-Bus calls (`.call_sync()`, `.get_sync()`, etc.) that block compositor (detection gap #11 closed)

### Remaining Known FPs (after session 21)
- quality/constructor-resources: Some runtime-only constructors still flagged (only connectSmart skip added, not full scope analysis)
- lifecycle/untracked-timeout: promiseUtils.js GSource-based promise timeout not recognized
