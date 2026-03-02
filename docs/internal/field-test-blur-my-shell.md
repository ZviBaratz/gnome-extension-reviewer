# Field Test: Blur my Shell

**Date**: 2026-03-01 (ego-lint), 2026-03-02 (ego-review, ego-simulate)
**Target**: [Blur my Shell](https://github.com/aunetx/blur-my-shell) v70 (latest main)
**Extension**: `blur-my-shell@aunetx` — GNOME 46-49, 48 JS files, 10 GLSL shaders, ~5500 non-blank lines, GPL-3.0

## Extension Profile

| Property | Value |
|----------|-------|
| UUID | `blur-my-shell@aunetx` |
| GNOME versions | 46, 47, 48, 49 |
| JS files | 49 |
| GLSL shaders | 10 |
| Total JS lines | 7,743 |
| License | GPL-3.0 |
| Session modes | unlock-dialog, user |
| GitHub stars | 2K+ |
| EGO status | Approved, actively maintained |

### Key Patterns (New to Field Tests)

- **GLSL shader pipeline**: 10 `.glsl` files for blur/color/noise effects
- **Clutter effect classes**: `GObject.registerClass` on `Clutter.ShaderEffect` subclasses
- **Multi-component architecture**: 9 components (panel, overview, lockscreen, appfolders, applications, dash_to_dock, screenshot, window_list, coverflow_alt_tab) each with enable/disable
- **`src/` build layout**: Extension source in `src/` subdirectory (Meson build system)
- **Custom signal management**: `Connections` class wrapping `.connect()`/`.disconnect()` with auto-cleanup
- **Effects pipeline**: `PipelinesManager` → `Pipeline` → effects with chained rendering
- **D-Bus service**: Pick-window service for preferences integration
- **Conditional prefs/shell code**: `utils.IS_IN_PREFERENCES` ternary guards for shell-only modules
- **Prototype overrides**: UnlockDialog method replacement for lockscreen blur

## ego-lint Results

### Before Fixes

| Status | Count |
|--------|-------|
| PASS   | 177   |
| FAIL   | 21    |
| WARN   | 120   |
| SKIP   | 20    |
| **Total** | **338** |

Exit code: 1

### After Fixes

| Status | Count | Delta |
|--------|-------|-------|
| PASS   | 186   | +9    |
| FAIL   | 7     | -14   |
| WARN   | 120   | 0 (net: -2 FP suppressed, +1 css/important, +1 prefs check) |
| SKIP   | 17    | -3    |
| **Total** | **330** | -8  |

Exit code: 1 (7 true positive FAILs remain)

### Fixes Applied

1. **GObject.registerClass exemption** (`check-init.py`): Exempt `GObject.registerClass` from GOBJECT_CONSTRUCTORS detection (-13 false FAILs)
2. **`src/` layout support** (`ego-lint.sh`, `check-css.py`, `check-prefs.py`): Check `src/extension.js`, `src/stylesheet.css`, `src/prefs.js` as fallbacks (-1 false FAIL, -3 SKIPs, enables CSS+prefs checking)
3. **R-SLOP-24 guard-pattern** (`patterns.yaml`): Suppress for non-extension schemas like `org.gnome.mutter` (-1 false WARN)
4. **R-SLOP-38 guard-pattern** (`patterns.yaml`): Suppress for parameter default values (-1 false WARN on declaration, 1 variable-use WARN remains)

## FAIL Classification

### False Positives (16 FAILs)

#### 1. init/shell-modification on GObject.registerClass (13 FAILs)

**Files**: All 13 effects files under `src/effects/` + `src/components/appfolders.js`

**Root cause**: `check-init.py` GOBJECT_CONSTRUCTORS regex matches `new GObject.registerClass(...)` at module scope. However, `GObject.registerClass()` returns a **class constructor**, not an instance — the actual constructor body only executes when the class is instantiated (inside `enable()`). This is the standard, correct way to define GObject subclasses in GJS.

Additionally, the effects files use a `utils.IS_IN_PREFERENCES` ternary guard:
```js
export const ColorEffect = utils.IS_IN_PREFERENCES ?
    { default_params: DEFAULT_PARAMS } :
    new GObject.registerClass({...}, class ColorEffect extends Clutter.ShaderEffect {...});
```

**Fix needed**: Exempt `GObject.registerClass` from the GOBJECT_CONSTRUCTORS pattern in `check-init.py`. It's class registration, not resource allocation.

**Priority**: **P0** — 13 false FAILs from a single pattern. Damages credibility with experienced GNOME developers.

#### 2. file-structure/extension.js (1 FAIL)

**Root cause**: ego-lint checks `$EXT_DIR/extension.js` but this extension uses a `src/` subdirectory layout. The actual file is at `src/extension.js`.

**Fix needed**: Check for `extension.js` in common locations: root, `src/`, `src/extension.js`.

**Priority**: **P1** — Many popular extensions use `src/` layout with Meson build systems.

#### 3. R-DEPR-06: Tweener usage (2 unique FAILs, reported as 4 line hits)

**File**: `src/components/appfolders.js`
**Lines**: 8, 9, 53, 97

**Classification**: **True Positive** — `const Tweener = imports.tweener.tweener;` uses the legacy `imports.` system. Tweener was removed in GNOME 42+, and this extension targets 46-49. The code even has a TODO: "drop Tweener in favour of Clutter's `ease`". This is dead/broken code that would fail at runtime on GNOME 46+.

#### 4. R-VER47-01: Clutter.Color usage (2 FAILs)

**File**: `src/components/appfolders.js:12-13`

**Code**:
```js
const transparent = Clutter.Color ?
    Clutter.Color.from_pixel(0x00000000) :
    new Cogl.Color({...});
```

**Classification**: **Semi-FP** — The code correctly handles the Clutter.Color removal with a runtime feature check. The pattern rule doesn't recognize this guard. However, the Tweener usage on line 9 (`imports.tweener.tweener`) means this file would crash before reaching this code on GNOME 46+, so the guard is irrelevant in practice.

### True Positives (5 FAILs)

| Rule | File | Detail | Notes |
|------|------|--------|-------|
| R-DEPR-06 (×4) | appfolders.js:8,9,53,97 | Tweener usage via legacy `imports.` | Would crash on GNOME 46+ |
| R-VER47-01 (×2) | appfolders.js:12-13 | Clutter.Color (guarded but file is broken anyway) | Dead code path |

## WARN Classification

### By Category (120 total)

| Category | Count | Assessment |
|----------|-------|------------|
| resource-tracking/destroy-not-called | 63 | **FP** — Components use `.disable()` not `.destroy()` |
| quality/constructor-resources | 17 | **Mostly FP** — Pipeline instances managed via parent lifecycle |
| resource-tracking/no-destroy-method | 10 | **FP (design)** — Utility classes use `disconnect_all()`, `remove()` |
| lifecycle/prototype-override | 6 | **TP** — Correctly flags lockscreen UnlockDialog overrides |
| R-I18N-01 | 4 | **TP** — Template literals in `_()` break xgettext extraction |
| lifecycle/untracked-timeout | 4 | **2 TP, 2 FP** — prefs.js timeouts auto-cleanup on window close |
| R-SLOP-38 | 1 | **FP** — `dash_not_already_destroyed` is descriptive, not AI verbosity |
| R-SLOP-24 | 1 | **FP** — `new Gio.Settings({schema: 'org.gnome.mutter'})` accesses non-extension schema |
| R-SLOP-16 | 1 | **TP** — `GLib.file_get_contents()` is synchronous file read |
| R-SLOP-03 | 1 | **TP** — `version` field deprecated for GNOME 45+ |
| R-SEC-09 | 1 | **TP** — `Main.extensionManager` access for Dash to Panel compatibility |
| R-DEPR-09 | 1 | **TP** — `var x, y;` should use `let` |
| resource-tracking/ownership | 1 | TP — Resource ownership question |
| quality/repeated-settings | 1 | **TP** — Multiple `getSettings()` calls (defensible with wrapper class) |
| quality/private-api | 1 | **TP** — `Main.overview._overview.controls._appDisplay` private access |
| quality/module-state | 1 | **TP** — `sigma` and `brightness` module-level vars not reset in disable |
| quality/empty-catch | 1 | **TP** — Empty catch in paint_signals.js |
| metadata/uuid-matches-dir | 1 | **Expected** — Cloned to different directory name |
| metadata/non-standard-field | 1 | **TP** — `original-authors` is non-standard |
| metadata/deprecated-version | 1 | **TP** — version field deprecated |
| lifecycle/signal-balance | 1 | **TP (by design)** — 125 connects vs 28 disconnects; Connections class auto-cleans |
| lifecycle/async-destroyed-guard | 1 | **TP (low risk)** — `await import()` in utils.js without guard |

### Notable FP Patterns

**Resource tracking dominates noise** (73 of 120 WARNs = 61%):
- The `disable()` method pattern is not recognized as equivalent to `destroy()`
- Components have `enable()`/`disable()` lifecycle, not `constructor()`/`destroy()`
- The `Connections` wrapper class handles signal cleanup but isn't recognized

**R-SLOP-24 false positive** on non-extension GSettings:
- `new Gio.Settings({schema: 'org.gnome.mutter'})` correctly uses direct construction for a system schema
- `this.getSettings()` only works for the extension's own schema

## SKIP Analysis (20)

All SKIPs are correct:
- Polkit: No polkit files (3 SKIPs) ✓
- CSS: stylesheet at `src/stylesheet.css` not found at root (2 SKIPs) — **detection gap**
- R-WEB-01/02/10/11: Version-gated for GNOME 44 (4 SKIPs) ✓
- R-DEPR-04-legacy: Version-gated (1 SKIP) ✓
- R-VER50-*: Not applicable for 46-49 (5 SKIPs) ✓
- ESLint: No eslint config (1 SKIP) ✓
- Schema usage: Dynamic key access (2 SKIPs) ✓
- Prefs: `prefs.js` at `src/prefs.js` not found at root (1 SKIP) — **detection gap**
- Package: No zip file (1 SKIP) ✓

## Detection Gaps

### 1. `src/` subdirectory layout (P1)

Many build-system extensions use `src/` for source files. ego-lint doesn't find:
- `src/extension.js` → FAIL instead of PASS
- `src/stylesheet.css` → SKIP CSS checks entirely
- `src/prefs.js` → SKIP prefs checks entirely

**Affected checks**: file-structure, check-css.py, check-prefs.py, check-imports.sh, console.log, deprecated modules

### 2. GLSL shader files not checked (P2)

ego-lint doesn't examine `.glsl` files. Potential checks:
- Syntax validation (GLSL syntax errors)
- Orphan shaders (referenced by JS but not present, or present but not referenced)
- This is a niche gap — most extensions don't have shaders

### 3. `GObject.registerClass` exemption (P0)

Covered in FP section. Class registration is not resource allocation.

### 4. Component lifecycle pattern (`disable()` not `destroy()`) (P2)

The resource graph only recognizes `.destroy()` as cleanup. Many GNOME extensions use `.disable()` patterns. Adding `.disable()` recognition would reduce WARNs significantly.

### 5. Non-extension GSettings construction (P1)

R-SLOP-24 doesn't recognize `new Gio.Settings({schema: 'org.gnome...'})` as legitimate when accessing system schemas.

## Step 2: ego-review

Run via ego-submit parallel pipeline (3 agents):
- Agent 1: ego-lint + package validation
- Agent 2: lifecycle/signals/security (Phases 2-4)
- Agent 3: quality/AI patterns/metadata (Phases 5-5a + 4)

### Verdict

**NEEDS FIXES** | **Risk: MEDIUM** (1 hard blocker + 4 advisory)

### Blocking Issues

| # | Issue | File:Line | Category |
|---|-------|-----------|----------|
| — | None found by manual review | — | — |

No issues were classified as BLOCKING by the manual review. The Tweener import (caught by ego-lint as R-DEPR-06) is the only hard blocker — it's a lint finding, not a review finding. The manual review focused on lifecycle/signal/security issues where it found advisory-level concerns only.

### Advisory Issues

| # | Severity | File:Line | Description |
|---|----------|-----------|-------------|
| L-1 | ADVISORY | panel.js:70 | `setTimeout(_ => this.enable(), 1)` in `reset()` — source ID not stored, can fire after disable |
| L-2 | ADVISORY | panel.js:91 | `GLib.idle_add()` in `blur_dtp_panels` — source ID not stored, can fire after disable |
| L-3 | ADVISORY | coverflow_alt_tab.js:69 | `actor.destroy` missing parentheses — property access, not function call. Background actors never destroyed (orphaned resource) |
| L-10 | ADVISORY | window_list.js:111 | `splice(pipeline, 1)` passes object instead of index — NaN coerced to 0, always removes first element |

### Resource Summary

| Category | Count | Balanced | Notes |
|----------|-------|----------|-------|
| Signal connections (via Connections) | ~55 | All balanced | `Connections.disconnect_all()` safety net in `disable()` |
| Signal connections (direct) | ~18 | All balanced | Effects `vfunc_set_actor`, DashInfos, panel windows |
| Timer sources | 2 untracked | 2 unbalanced (L-1, L-2) | `setTimeout`/`GLib.idle_add` without stored IDs |
| D-Bus exports | 1 | Balanced | Session bus at `/dev/aunetx/BlurMyShell`, unexported on disable |
| Prototype overrides | 3 | All balanced | UnlockDialog, WorkspaceAnimationController, AppFolderDialog — originals saved, restored on disable |
| Effects pool | ~N pooled | Individual remove balanced | `EffectsManager.destroy_all()` never called but individual cleanup covers it |

### Issues ego-lint Could Not Detect

1. **Bug: `actor.destroy` missing parentheses (L-3)**: `coverflow_alt_tab.js:69` — `this.background_actors.forEach((actor) => actor.destroy)` is a no-op (property access vs function call). Requires semantic understanding that `actor.destroy` without `()` does nothing. ego-lint's pattern matching cannot distinguish property access from method calls.

2. **Bug: `splice(pipeline, 1)` wrong argument (L-10)**: `window_list.js:111` passes an object where an index is expected. JavaScript silently coerces to NaN→0. ego-lint cannot reason about argument types in `Array.splice()`.

3. **Timer source ID tracking (L-1, L-2)**: ego-lint flagged `setTimeout` as WARN but couldn't determine that the return value (source ID) is discarded. The lint would need data-flow analysis to verify that timer IDs are stored for later cancellation.

4. **`PipelinesManager.destroy()` / `EffectsManager.destroy_all()` not called in `disable()`**: The settings cleanup covers `PipelinesManager` indirectly via `disconnect_all_settings()`, and individual component cleanup handles effects. But the explicit destroy paths are never taken. ego-lint's resource tracker would need cross-method analysis to verify that alternative cleanup paths cover the same resources.

5. **`global.blur_my_shell` set before sub-objects initialized**: `extension.js:32` sets `global.blur_my_shell = this` before `_effects_manager` and `_pipelines_manager` are assigned (lines 50-53). Safe in practice because component constructors don't access these, but requires understanding constructor execution order.

### Security Findings

| # | Severity | Description |
|---|----------|-------------|
| SEC-1 | INFO | D-Bus `pick()` method at `/dev/aunetx/BlurMyShell` has no authentication — acceptable within session bus trust model |
| SEC-3 | INFO (clean) | No subprocess spawning, no command injection vectors, no `eval()` |
| SEC-5 | INFO (clean) | No credentials or secrets in code |
| SEC-6 | INFO (clean) | No network requests, no external data transmission |

### Disclosure Matrix

| Capability | Found in Code | Disclosed in Metadata | Status |
|---|---|---|---|
| Clipboard | No | N/A | OK |
| Network | No | N/A | OK |
| pkexec | No | N/A | OK |
| Subprocess | No | N/A | OK |
| Private API | Yes — `Main.overview._overview`, `Main.screenshotUI._windowSelectors`, `icon._dialog`, `dash_container._slider`, `actor._windowList` | No | WARN |
| File I/O | Yes — own bundled files only (iface.xml, GLSL shaders) | No | OK |
| Prototype Patching | Yes — UnlockDialog, WorkspaceAnimationController, AppFolderDialog | No | WARN |
| D-Bus Export | Yes — session bus `/dev/aunetx/BlurMyShell` | No | INFO |
| Clutter Debug Flags | Yes — disables clipped redraws at hacks level 2 | No | WARN |

### AI Pattern Analysis

**Score**: 0/46 triggered | **Provenance**: 0/5 (strongly hand-written) | **Assessment**: PASS

Evidence of genuine authorship: Rust-style `///` doc comments consistent throughout, organic TODO/FIXME comments referencing real GNOME Shell bugs (gnome-shell#2857), natural bugs (missing parentheses at `coverflow_alt_tab.js:69`) that AI would be unlikely to produce, per-component spacing alignment in copy-pasted `_log` methods, custom GLSL shaders with experimental commented-out code, single-developer commit history on GitHub.

## Step 3: ego-simulate

### Score

| Taxonomy Reason | Weight | Evidence |
|-----------------|--------|----------|
| #5 Deprecated modules (Tweener) | 10 | `appfolders.js:9` — `imports.tweener.tweener` |
| #14 Timeout leak | 5 | `panel.js:70` setTimeout, `panel.js:91` GLib.idle_add — IDs not stored |
| R-VER47-01 (ego-lint unmapped FAIL) | 5 | `appfolders.js:12-13` — Clutter.Color reference (has runtime guard but lint flagged) |
| #19 Empty catch blocks | 3 | `paint_signals.js:28` — `catch (e) { }` |
| **Total** | **23** | |

### Verdict

**Score: 23** — Will be rejected — address Tweener blocker first

The Tweener import (`appfolders.js:9`) is the single hard blocker (weight 10, independently sufficient for rejection). The extension targets GNOME 48 and 49 where `imports.tweener.tweener` does not exist — this would crash at runtime. The fix is straightforward: replace Tweener with Clutter's `ease()` API.

The remaining concerns (timer leak, empty catch, Clutter.Color backward compat) would generate reviewer comments but are not independently blocking. Once Tweener is replaced, the effective score drops to 13 — "may pass, but expect revision requests."

### Calibration Check

Blur my Shell is approved on EGO at version 70. Expected: score should reflect that the Tweener usage is a genuine problem for the declared GNOME versions.

**Result: PARTIALLY CALIBRATED** — The rejection verdict is driven by the Tweener import (weight 10), which IS a genuine runtime failure on GNOME 46+. However, Blur my Shell remains approved on EGO, suggesting either: (1) the `appfolders.js` Tweener code path is not reached in practice on GNOME 46+ (the `imports.tweener.tweener` line may error silently or the module may have a shim), or (2) the EGO review for v70 was an update review that diffed against the previous approved version and did not re-examine this legacy code.

**Cross-tool calibration**:
- ego-review risk: MEDIUM (1 hard blocker via lint + 4 advisory)
- ego-simulate score: 23 (1 weight-10 hard blocker + structural/style concerns)
- Both agree: Tweener is the primary issue; lifecycle bugs (L-3, L-10) are secondary

## Comparison with Prior Field Tests

| Metric | Hara-hachi-bu | AppIndicator | Clipboard Indicator | V-Shell | **Blur my Shell** |
|--------|--------------|--------------|--------------------|---------|--------------------|
| JS files | 17 | 17 | 6 | 28 | **48** |
| Lines | ~3,500 | ~5,000 | ~1,500 | ~19,200 | **~5,500** |
| GNOME versions | 45-48 | 45-50 | 46-49 | 45-49 | **46-49** |
| Total checks | 235 | 272 | 216 | 360 | **330** |
| PASS | 204 | 178 | 179 | 177 | **186** |
| FAIL (after fixes) | 0 | 11 | 1 | 23 (all FP) | **7** |
| WARN | 8 | 69 | 24 | 143 | **120** |
| SKIP | 23 | 14 | 12 | 17 | **17** |
| False FAILs fixed | 0 | — | 26 | 0 | **14** |
| ego-simulate score | — | — | — | 8 | **23** |
| ego-review risk | — | — | — | LOW | **MEDIUM** |
| Key patterns | D-Bus consumer | D-Bus server | clipboard/keybindings | shell overrides, private API | **effects pipeline, multi-component, GLSL** |

## Priority Improvements

### P0 — Credibility-damaging false FAILs

1. **Exempt `GObject.registerClass` from init/shell-modification**: The GOBJECT_CONSTRUCTORS regex should not match `GObject.registerClass` since it returns a class, not an instance. Fix in `check-init.py`. (-13 false FAILs)

### P1 — Significant gaps

2. **Support `src/` subdirectory layout**: Check `src/extension.js`, `src/prefs.js`, `src/stylesheet.css` as fallbacks. Fix in `ego-lint.sh`, `check-css.py`, `check-prefs.py`. (-1 false FAIL, enables CSS and prefs checking)

3. **Add guard-pattern to R-SLOP-24**: Suppress when schema is a system schema (e.g., `org.gnome.mutter`, `org.gnome.desktop.*`). Fix in `rules/patterns.yaml`. (-1 false WARN)

4. **Add guard-pattern to R-SLOP-38**: Suppress for function parameter default values (`parameter_name = value`). Fix in `rules/patterns.yaml`. (-1 false WARN)

### P2 — Detection improvements (future)

5. **Recognize `.disable()` as cleanup method** in resource graph
6. **GLSL shader orphan detection**
7. **Multi-component lifecycle validation**

## Verdict

Blur my Shell exposed a **critical false positive pattern** (GObject.registerClass at module scope) that would affect any extension with custom GObject subclasses — a very common GNOME extension pattern. The `src/` layout gap affects many build-system extensions.

The 16 false FAILs are dominated by a single root cause (GObject.registerClass). After fixing P0+P1 items, the expected result would be ~5 true FAILs (Tweener + Clutter.Color) and ~45 WARNs (down from 120 after resource tracking noise reduction is addressed separately).

The high WARN count (120) is mostly from resource-tracking/destroy-not-called (63), which reflects a detection gap in recognizing the `disable()` lifecycle pattern. This is an architectural improvement for a future session.

### Full Pipeline Assessment (2026-03-02)

The ego-submit parallel pipeline (3 agents) completed in ~6 minutes wall-clock, followed by ego-simulate. Key findings:

1. **ego-review found 4 advisory bugs that ego-lint missed**: `actor.destroy` without parens (L-3), `splice` with wrong argument type (L-10), uncancellable `setTimeout` (L-1), and uncancellable `GLib.idle_add` (L-2). All require semantic analysis beyond pattern matching.

2. **ego-simulate score of 23 is driven by a single hard blocker** (Tweener, weight 10). Without Tweener, the score drops to 13, consistent with an extension that would pass with revision requests. The timer leak and empty catch are legitimate but non-blocking concerns.

3. **AI provenance score 0/5**: The codebase is unambiguously hand-written by a single experienced developer. No AI slop signals triggered.

4. **Disclosure gaps exist but are non-blocking**: Private API usage, prototype patching, and Clutter debug flag manipulation are undisclosed in the metadata description. A reviewer would ask about these but would not reject for an established extension.

5. **Security is clean**: No subprocess spawning, network access, credentials, or command injection vectors. The D-Bus pick service is within the session bus trust model.

## Calibration Lessons Learned

1. **ego-lint `no-console-log` check missed 12 instances**: All `console.log` calls in `_log()` methods across component files were not detected. The check likely doesn't traverse into `src/` subdirectories deeply enough or the regex doesn't match the debug-gated pattern. This is a detection gap to investigate.

2. **Backward-compat ternaries produce lint false positives**: `Clutter.Color ? Clutter.Color.from_pixel(...) : new Cogl.Color(...)` is flagged as R-VER47-01 FAIL even though the deprecated API is only reached on GNOME 46 where it still exists. Static analysis cannot trace the runtime guard. Same pattern seen in V-Shell with `Clutter.ClickAction || Clutter.ClickGesture`.

3. **`actor.destroy` vs `actor.destroy()` is undetectable by pattern matching**: The missing-parens bug at `coverflow_alt_tab.js:69` is a subtle JavaScript pitfall (property access returns the function object, doesn't call it). Only AST-level analysis could distinguish method calls from property accesses.

4. **Parallel 3-agent pipeline effective for 48-file extension**: Agent isolation was clean — lint/package agent, lifecycle/signal/security agent, and quality/AI/metadata agent produced complementary findings with minimal overlap. The only duplication was on the `actor.destroy` bug (caught by both lifecycle and quality agents), resolved by preferring the lifecycle agent's categorization.

5. **ego-simulate score calibration for established extensions**: Score 23 for a v70 approved extension confirms that the Tweener import is a genuine issue that _should_ be caught, even if EGO's update review process may have missed it. The taxonomy scoring is conservative but directionally correct.
