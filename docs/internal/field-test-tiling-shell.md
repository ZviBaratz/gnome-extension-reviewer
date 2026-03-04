# Field Test #8 — Tiling Shell

## Pre-flight

- **Extension**: Tiling Shell (`tilingshell@ferrarodomenico.com`)
- **Source**: https://github.com/domferr/tilingshell — release v17.3, tag commit `cc7ee6d`
- **GNOME versions**: 45, 46, 47, 48, 49
- **File count**: 64 JS files, 11,371 lines
- **License**: GPL-2.0 (in source repo, but **not included in release zip**)
- **Why this extension**: Window management/tiling — keybinding lifecycle, window signal tracking, multi-monitor state, compiled TypeScript output, settings overrides. None of the first 7 field tests cover this category.

## Step 1: ego-lint

```bash
./ego-lint --verbose /tmp/tilingshell-built
```

### Initial Results (before fixes)

| Status | Count |
|--------|-------|
| PASS   | 177   |
| FAIL   | 21    |
| WARN   | 145   |
| SKIP   | 17    |
| Exit   | 1     |

### Classification of Each FAIL

| # | Rule | File:Line | TP/FP | Root Cause (if FP) |
|---|------|-----------|-------|-------------------|
| 1 | license | — | TP | No LICENSE/COPYING in release zip |
| 2 | no-console-log | extension.js:394 | Borderline | Logger wrapper pattern; `console.log("[tilingshell]", ...)` |
| 3 | minified-js | prefs.js | **FP** | 1 line at 762 chars (keyboard constant chain) in 1404-line readable file |
| 4 | R-SEC-22 | settingsExport.js:24 | TP | `Gio.Subprocess.new(["dconf", "load", ...])` |
| 5 | R-SEC-22 | settingsExport.js:45 | TP | `Gio.Subprocess.new(["dconf", "dump", ...])` |
| 6 | R-VER49-08 | gnomesupport.js:29 | **FP** | Ternary guard: `get_maximized ? .maximize(MaximizeFlags) : .maximize()` |
| 7 | R-VER49-11 | gnomesupport.js:33 | **FP** | Ternary guard: `get_maximized ? .unmaximize(MaximizeFlags) : .unmaximize()` |
| 8 | init/shell-modification | globalState.js:64 | **FP** | Inside constructor signal callback (not module scope) |
| 9 | init/shell-modification | globalState.js:92 | **FP** | Inside constructor signal callback |
| 10 | init/shell-modification | ui.js:3 | **FP** | Module-scope arrow fn definition `() => Main.layoutManager.monitors` (lazy) |
| 11-15 | init/shell-modification | defaultMenu.js:146,150,194,196,200 | **FP** | Inside DefaultMenu constructor (called from enable()) |
| 16 | init/shell-modification | indicator.js:29 | **FP** | Constructor `Main.panel.addToStatusArea()` (enable() chain) |
| 17 | init/shell-modification | tilingManager.js:84 | **FP** | Constructor `Main.layoutManager.getWorkAreaForMonitor()` |
| 18-19 | init/shell-modification | layoutEditor.js:29,40 | **FP** | Constructor shell access (enable() chain) |
| 20-21 | init/shell-modification | editorDialog.js:28,30 | **FP** | Constructor shell access (enable() chain) |

**Summary**: 3 TP, 2 borderline, 16 FP — **76% false positive rate**

### Classification of Key WARNs

| Rule | Count | Legitimate? | Notes |
|------|-------|-------------|-------|
| resource-tracking/no-destroy-method | 64 | Mostly TP | Compiled TS creates many small classes without explicit destroy() |
| R-DEPR-09 (var usage) | 18 | TP | esbuild `__defProp`/`__publicField` helpers use `var` |
| quality/constructor-resources | 10 | Mixed | Some are real (signal connects in ctors), some are esbuild patterns |
| R-QUAL-31 (_onDestroy naming) | 6 | TP | Cleanup methods not named `destroy()` |
| R-SLOP-38 (verbose param names) | 5 | FP | TS compiled names like `tilePreviewAnimationTime` are domain-specific |
| lifecycle/prototype-override | 4 | TP | Alt-tab and window menu overrides |
| R-SLOP-08 (non-existent API) | 3 | FP | `MaximizeFlags.BOTH` flagged but it exists; compiled code patterns |
| lifecycle/destroy-no-null | 5 | TP | `.destroy()` without null assignment |
| R-SLOP-24 (new Gio.Settings) | 2 | FP | Settings helper class, not direct construction |
| gobject/cairo-dispose | 1 | TP | Drawing callback leaks Cairo context |
| async/missing-cancellable | 1 | TP | Async operation without cancellable |

### Results After Fixes

| Status | Count |
|--------|-------|
| PASS   | 182   |
| FAIL   | 4     |
| WARN   | 144   |
| SKIP   | 17    |
| Exit   | 1     |

Remaining FAILs (all legitimate):
1. license — no LICENSE in zip (TP)
2. no-console-log — logger wrapper (borderline)
3. R-SEC-22 ×2 — dconf CLI spawn (TP)

## Step 2: ego-review

_Not run — field test focused on ego-lint FP reduction._

## Step 3: ego-simulate

_Not run — field test focused on ego-lint FP reduction._

## Fixes Implemented

### False Positives Fixed

| Rule/Check | Root Cause | Fix | FPs Eliminated |
|------------|-----------|-----|----------------|
| init/shell-modification (constructors) | Shell globals in non-extension.js constructors always flagged | Only check constructors in extension.js (same as GOBJECT_CONSTRUCTORS) | 13 |
| init/shell-modification (arrow fn) | `const fn = () => Main.x` treated as module-scope access | Detect arrow function definitions and skip | 1 |
| R-VER49-08 | Same-line ternary `get_maximized ?` not recognized as guard | Added `guard-pattern: "get_maximized\\s*\\?"` with `guard-window: 1` | 1 |
| R-VER49-11 | Same as R-VER49-08 | Same guard-pattern | 1 |
| minified-js | Single line > 500 chars triggers FAIL | Require 3+ lines > 500 chars (1 long line in readable file is not minification) | 1 |

**Total: 17 FP FAILs eliminated** (21 → 4 FAILs, all remaining are legitimate)

### Test Fixtures Added/Updated

| Fixture | What It Tests |
|---------|--------------|
| init-time-safety@test | Module-scope violation detected; arrow fn definition skipped; helper constructor skipped |
| gnome49-compat@test (updated) | Ternary version-compat guard suppresses R-VER49-08/11 |
| minified-js@test (updated) | 3 long lines required for minified detection |

### Test Assertions Added

- `init-time-safety`: 4 assertions (exit code, FAIL on module scope, no FP on helper, no FP on arrow fn)
- `gnome49-compat`: 2 assertions (no R-VER49-08/11 with ternary guard)
- Total: 6 new assertions

## Regression Verification

```bash
bash tests/run-tests.sh                    # 525 passed, 0 failed
./ego-lint --verbose /tmp/tilingshell-built # 4 FAIL (was 21)
./ego-lint --verbose ~/.local/share/gnome-shell/extensions/hara-hachi-bu@ZviBaratz  # 0 FAIL, 9 WARN
```

| Target | Before | After |
|--------|--------|-------|
| Tiling Shell | 21 FAIL, 145 WARN | 4 FAIL, 144 WARN |
| hara-hachi-bu baseline | 0 FAIL, 9 WARN | 0 FAIL, 9 WARN |
| Test suite | 515 pass (1 fail) | 525 pass, 0 fail |

## Calibration Lessons Learned

1. **Compiled TypeScript creates systematic FP patterns**: esbuild output uses `var` (R-DEPR-09), verbose parameter names (R-SLOP-38), and `__defProp` helpers that trigger quality heuristics. These are build artifacts, not author choices.

2. **Constructor-from-enable() is the #1 FP source**: 13 of 16 FPs were Shell globals in constructors of classes only instantiated from `enable()`. The fix (only check extension.js constructors) eliminates this entire class of FPs across all extensions — not just Tiling Shell. This also fixes the 4 known Dash to Panel FPs.

3. **Arrow function definitions at module scope are lazy**: `const fn = () => Main.x` doesn't execute at module scope. This pattern is common in utility modules.

4. **Same-line ternary guards need `guard-window: 1`**: Version compat patterns like `api.exists ? old(args) : new()` have the guard and the deprecated API on the same line. `guard-window: 1` (minimum valid value; 0 is rejected by `--validate`) handles this.

5. **Single long line ≠ minification**: Compiled TS may have one or two very long lines (keyboard constant chains, export lists) in otherwise readable files. Requiring 3+ long lines eliminates these FPs while still catching truly minified bundles.

6. **Tiling extensions exercise unique lifecycle patterns**: Keybinding add/remove, window signal tracking, multi-monitor state, and settings overrides are all present. The `resource-tracking/no-destroy-method` WARN (64 hits) highlights how compiled TS class hierarchies create many small classes without explicit cleanup methods — a potential area for future improvement.
