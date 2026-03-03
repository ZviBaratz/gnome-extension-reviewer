# Field Test: Dash to Panel

**Date**: 2026-03-03
**Target**: [Dash to Panel](https://github.com/home-sweet-gnome/dash-to-panel) (latest main)
**Extension**: `dash-to-panel@jderose9.github.com` — GNOME 46-49, 17 JS files, ~16,583 lines, GPL-2.0

## Extension Profile

| Property | Value |
|----------|-------|
| UUID | `dash-to-panel@jderose9.github.com` |
| GNOME versions | 46, 47, 48, 49 |
| JS files | 17 (in `src/`) |
| Total JS lines | 16,583 |
| Largest file | prefs.js (4,052 lines, 132KB) |
| License | GPL-2.0 |
| Session modes | Not declared |
| EGO status | Approved, 1.6M+ downloads |
| Commit | `ebf64ab50b28d1eb6db45861f882bc2180f34f07` |

### Key Patterns (New to Field Tests)

- **Massive preferences file**: 4,052-line prefs.js (132KB) — stress-tests `check-prefs.py`
- **Panel widget lifecycle**: Custom panel/taskbar/dock with multi-monitor coordination
- **Custom actor subclasses**: 10 `GObject.registerClass` across 5 files (TaskbarActor, PreviewMenu, Preview, Panel, SecondaryPanel, etc.)
- **Window preview management**: windowPreview.js (1,431 lines) exercises Meta API window tracking
- **Heavy prototype overrides**: 24 prototype references in panelManager.js (LookingGlass, AppIcon, Workspace overrides)
- **Multi-monitor panel sync**: panelManager.js orchestrates per-monitor panel instances
- **Desktop Icons integration**: Cross-extension coordination with Desktop Icons NG
- **Version-compat ternaries**: `Config.PACKAGE_VERSION >= '48'` guards for GNOME 46-49 range
- **Settings import/export**: dconf dump/load for settings backup in prefs UI

### File Size Distribution

| File | Lines | Key Pattern |
|------|-------|------------|
| prefs.js | 4,052 | Prefs stress test |
| appIcons.js | 2,401 | App icon management |
| taskbar.js | 1,815 | Taskbar widget |
| panel.js | 1,680 | Panel lifecycle |
| windowPreview.js | 1,431 | Window previews |
| panelManager.js | 1,133 | Multi-monitor orchestrator |
| utils.js | 969 | Version compat utilities |
| intellihide.js | 588 | Auto-hide logic |
| overview.js | 579 | Overview integration |

## ego-lint Results

| Status | Count |
|--------|-------|
| PASS   | 162   |
| FAIL   | 19    |
| WARN   | 99    |
| SKIP   | 17    |
| **Total** | **297** |

Exit code: 1

## FAIL Classification (19 total)

### True Positives (10 FAILs)

| Rule | File:Line | Detail |
|------|-----------|--------|
| css/shell-class-override | stylesheet.css | `.popup-menu` overrides Shell theme class |
| R-DEPR-05 | desktopIconsIntegration.js:60 | `import * as ExtensionUtils` from deprecated path |
| R-DEPR-05 | desktopIconsIntegration.js:68 | `ExtensionUtils.ExtensionState.ENABLED` deprecated |
| R-DEPR-05 | desktopIconsIntegration.js:69 | `ExtensionUtils.ExtensionState.ACTIVE` via deprecated module |
| R-DEPR-08 | prefs.js:3868 | `GLib.spawn_command_line_sync('dconf dump ...')` deprecated |
| R-SEC-22 | prefs.js:3868 | `dconf dump` subprocess spawning |
| R-SEC-22 | prefs.js:3889 | `dconf load` subprocess spawning |
| R-VER46-05 | desktopIconsIntegration.js:68 | `ExtensionState.ENABLED` renamed to `ACTIVE` in GNOME 46 |
| init/shell-modification | taskbar.js:46 | `const SearchController = Main.overview.searchController` at **module scope** |
| init/shell-modification | extension.js:55 | `this._realHasOverview = Main.sessionMode.hasOverview` in Extension **constructor** |

### False Positives (9 FAILs)

#### 1. R-DEPR-06 — Tweener in comments (2 FAILs)

**Files**: utils.js:486, utils.js:497

The `\bTweener\b` pattern matches in **comments only**:
```js
//the original animations used Tweener instead of Clutter animations, so we
//map Tweener easing equations to Clutter animation modes
```
The actual code is a Clutter animation wrapper — no Tweener API is imported or called. The extension successfully uses `actor.ease()` with Tweener-style property names (time/delay in seconds) for backward compatibility.

**FP root cause**: Pattern does not distinguish comments from code.

#### 2. R-DEPR-05 — Commented-out code (1 FAIL)

**File**: prefs.js:151

```js
// this._settings = ExtensionUtils.getSettings('org.gnome.shell.extensions.dash-to-panel');
```
A commented-out line of old code. The active code uses `settings` parameter passed to the constructor.

**FP root cause**: Pattern does not distinguish comments from code.

#### 3. R-VER48-02 — Version-guarded Meta API (2 FAILs)

**Files**: utils.js:233, utils.js:237

The code correctly uses version detection:
```js
let v48 = Config.PACKAGE_VERSION >= '48'
v48
  ? global.compositor.enable_unredirect()
  : Meta.enable_unredirect_for_display(global.display)
```
The deprecated `Meta.enable_unredirect_for_display` is only called on GNOME 47 and below where it exists. The guard-pattern `if (Meta.disable_unredirect` does not recognize `Config.PACKAGE_VERSION >= '48'` as an equivalent guard.

**FP root cause**: Guard-pattern only recognizes feature-detection guards, not version comparison guards.

#### 4. init/shell-modification — Class methods in enable() chain (4 FAILs)

**Files**: taskbar.js:376-378, desktopIconsIntegration.js:76

- taskbar.js:376-378: `Main.overview` signal connections inside `_signalsHandler.add()` in the Taskbar class constructor. The Taskbar class is instantiated during `enable()` via panelManager.
- desktopIconsIntegration.js:76: `Main.extensionManager` access in `DesktopIconsUsableAreaClass` constructor, which is instantiated at `panelManager.js:120` during `enable()`.

These all execute within the `enable()` call chain, not at module load time. The checker cannot trace the instantiation path.

**FP root cause**: `check-init.py` flags shell state access in any constructor, regardless of whether the constructor runs during enable().

## WARN Classification (99 total)

### By Category

| Category | Count | Assessment |
|----------|-------|------------|
| R-SEC-03 (HTTP URLs) | 18 | **FP** — All in GPL license headers (`http://www.gnu.org/licenses/`) |
| lifecycle/prototype-override | 14 | **TP** — Extensive prototype patching in panelManager.js |
| R-SLOP-11 (GLib.source_remove) | 6 | **TP** — Should use `GLib.Source.remove()` |
| R-SLOP-24 (new Gio.Settings) | 5 | **FP** — All for system schemas (desktop.interface, desktop.notifications, etc.) |
| R-SLOP-01 (JSDoc) | 5 | **Debatable** — Provenance score 4 should suppress but doesn't (see bug below) |
| lifecycle/destroy-no-null | 5 | **TP** — Destroy without null assignment |
| gobject/missing-gtypename | 5 | **TP** — registerClass without GTypeName |
| R-QUAL-27 (PACKAGE_VERSION string compare) | 4 | **TP** — String comparison on version is unreliable |
| R-SEC-09 (extension system) | 2 | **TP** — extensionManager interference |
| R-PREFS-04b/04c | 2 | **TP** — GTK widgets with Adw equivalents |
| R-SLOP-38 (long identifiers) | 2 | **FP** — `sortWindowsCompareFunction` (26 chars), `taskbarBoxAllocationChangedId` (30 chars) are descriptive |
| R-QUAL-31 (_onDestroy) | 2 | **TP** — Should use `destroy()` with `super.destroy()` |
| R-QUAL-30 (lookupByURL) | 2 | **TP** — Should use base class methods |
| lifecycle/untracked-timeout | 2 | **Debatable** — Both are `GLib.idle_add` one-shots inside signal handlers |
| lifecycle/timeout-return-value | 2 | **TP** — Missing SOURCE_REMOVE/SOURCE_CONTINUE |
| R-SLOP-03 (version field) | 1 | **TP** — Deprecated for GNOME 45+ |
| R-SLOP-29b (empty destroy) | 1 | **Debatable** — ProximityRectWatch `destroy() {}` is a class hierarchy placeholder |
| R-SLOP-35 (Object.freeze) | 1 | **FP** — `Object.freeze(monitorInfos)` prevents accidental mutation of shared state |
| R-SLOP-40 (Promise wrapper) | 1 | **TP** — Should use `Gio._promisify()` |
| R-VER48-04 (St.Widget.vertical) | 1 | **TP** — Deprecated in GNOME 48 |
| metadata/* | 4 | **Expected** — UUID mismatch (cloned dir), non-standard field, deprecated version, session-modes |
| quality/* | 6 | **Mostly TP** — Module state, code volume, comment density, file complexity, private API, repeated settings |
| lifecycle/* (other) | 4 | **TP** — Signal balance, connectObject migration, async guard, impossible state |
| disclosure/* | 2 | **TP** — Private API and file I/O undisclosed |
| accessibility/widget-role | 1 | **TP** — 6 custom St.Widget subclasses without accessible_role |

### Summary

| Assessment | Count |
|------------|-------|
| True Positive | 62 |
| False Positive | 26 |
| Debatable | 8 |
| Expected/Informational | 3 |

## SKIP Analysis (17)

All SKIPs are correct:
- Polkit: No polkit files (3 SKIPs) ✓
- R-WEB-01/02/10/11: Version-gated for GNOME 44 (4 SKIPs) ✓
- R-DEPR-04-legacy: Version-gated (1 SKIP) ✓
- R-VER50-*: Not applicable for 46-49 (5 SKIPs) ✓
- ESLint: No eslint config (1 SKIP) ✓
- Schema usage: Dynamic key access (2 SKIPs) ✓
- Package: No zip file (1 SKIP) ✓

## Notable Findings

### 1. Resource graph: zero orphans on 17-file extension

The resource graph scanned 17 files with depth 2 and found **0 orphans**. This is remarkable for an extension of this complexity. Dash to Panel uses a centralized signal handler pattern (`_signalsHandler.add()`) and explicit cleanup in `disable()` that the resource graph correctly validates.

### 2. Provenance post-filter bug

Provenance score is 4 (strong hand-written indicators: domain vocabulary ×13, nontrivial algorithms ×108, debug comments ×9, consistent naming style). The post-filter reports `[PASS] provenance/jsdoc-suppressed — Suppressed 5 JSDoc warnings` but the same 5 R-SLOP-01 WARNs still appear in the output. The filter logs the suppression but does not actually convert the WARNs to PASS.

### 3. GPL license headers flood R-SEC-03

18 of 99 WARNs (18%) are `R-SEC-03` hits on `http://www.gnu.org/licenses/` in GPL boilerplate present in every file. This is pure noise — GPL license URLs are canonical and cannot change to HTTPS (the FSF uses both, but the license text specifies HTTP).

### 4. R-SLOP-24 on system schemas

5 WARNs are R-SLOP-24 ("new Gio.Settings() is incorrect in GNOME 45+") firing on system schemas:
- `org.gnome.desktop.interface`
- `org.gnome.desktop.default-applications.terminal`
- `org.gnome.desktop.notifications`
- `org.gnome.shell.app-switcher`
- `WindowManager.SHELL_KEYBINDINGS_SCHEMA`

`this.getSettings()` only works for the extension's own schema. Using `new Gio.Settings({schema_id: ...})` for system schemas is the correct and only API.

### 5. Config.PACKAGE_VERSION guard idiom

Dash to Panel uses `Config.PACKAGE_VERSION >= '48'` for version-compat (utils.js). This works for single-digit major versions (string comparison '48' > '46' is correct), but R-QUAL-27 correctly flags it as unreliable — `'9' > '48'` is true in string comparison. The extension happens to work because GNOME major versions are all two digits (currently 46-49).

### 6. dconf dump/load in prefs is a real pattern

The settings import/export feature using `dconf dump`/`dconf load` (prefs.js:3868-3900) is caught by both R-DEPR-08 and R-SEC-22. While technically correct (spawning CLI tools is discouraged), this is a widely-used pattern for settings backup/restore that appears in many popular extensions. EGO reviewers may flag this but it's unlikely to be a hard blocker for an established extension.

## Detection Gaps

### 1. Comment-awareness for pattern rules (P1)

R-DEPR-06 and R-DEPR-05 fire on comments and commented-out code, producing 3 false FAILs. Pattern rules should skip comment lines (lines starting with `//` or inside `/* */` blocks). This affects any rule that matches an API name appearing in explanatory comments.

**Impact on Dash to Panel**: 3 false FAILs (15.8% of total)

### 2. Config.PACKAGE_VERSION guard for R-VER48-02 (P1)

The guard-pattern for R-VER48-02 is `if (Meta.disable_unredirect` (feature detection). Dash to Panel uses `Config.PACKAGE_VERSION >= '48'` instead — a different but equally valid version-compat pattern. Need a new guard-pattern recognizing `PACKAGE_VERSION.*'48'` or `PACKAGE_VERSION.*48`.

**Impact on Dash to Panel**: 2 false FAILs

### 3. R-SEC-03 should skip license headers (P1)

18 false WARNs from GPL boilerplate. Could be addressed by:
- Guard-pattern matching `GNU General Public License` in preceding lines
- Or skipping the first N lines of files (license headers are typically at the top)
- Or skipping lines matching `gnu.org/licenses`

**Impact on Dash to Panel**: 18 false WARNs (18% of all WARNs)

### 4. R-SLOP-24 should recognize system schemas (P1)

All 5 R-SLOP-24 hits are on system schemas. Could be addressed by:
- Guard-pattern matching `schema_id:.*org.gnome.desktop` or `schema_id:.*org.gnome.shell` (non-extensions schemas)
- Or exclusion when schema string doesn't match extension UUID pattern

**Impact on Dash to Panel**: 5 false WARNs

### 5. init/shell-modification constructor-in-enable detection (P2)

4 false FAILs from shell state access in constructors of classes that are instantiated during enable(). This would require call-chain analysis or per-file whitelisting. Complex to fix generically.

**Impact on Dash to Panel**: 4 false FAILs

### 6. Provenance post-filter not actually suppressing WARNs (P1)

The post-filter counts and reports suppressed R-SLOP-01 warnings but doesn't remove them from the WARN output. Investigate the suppression logic in `ego-lint.sh`.

**Impact on Dash to Panel**: 5 unsuppressed R-SLOP-01 WARNs

## Comparison with Prior Field Tests

| Metric | Hara-hachi-bu | AppIndicator | Clipboard Ind. | V-Shell | Blur my Shell | GSConnect | **Dash to Panel** |
|--------|--------------|--------------|----------------|---------|---------------|-----------|-------------------|
| JS files | 17 | 17 | 6 | 28 | 48 | 65 | **17** |
| Lines | ~3,500 | ~5,000 | ~1,500 | ~19,200 | ~5,500 | ~24,700 | **~16,600** |
| Largest file | — | — | — | — | — | — | **4,052 (prefs.js)** |
| GNOME versions | 45-48 | 45-50 | 46-49 | 45-49 | 46-49 | 46-49 | **46-49** |
| Total checks | 236 | 272 | 236 | 360 | 330 | 345 | **297** |
| PASS | 205 | 178 | 190 | 177 | 186 | 168 | **162** |
| FAIL | 0 | 11 | 2 | 3 | 7 | 11 | **19** |
| WARN | 8 | 69 | 27 | 17 | 120 | 149 | **99** |
| SKIP | 23 | 14 | 17 | 17 | 17 | 17 | **17** |
| FP FAILs | 0 | — | — | 0 | 14 | — | **9** |
| Resource orphans | 0 | — | — | — | 0 | — | **0** |
| Provenance score | 3 | — | — | — | 0 | — | **4** |
| Key patterns | Small personal | D-Bus server | Clipboard/keys | Shell overrides | Effects/GLSL | D-Bus daemon | **Panel widgets, massive prefs, prototype overrides** |

### What Dash to Panel uniquely reveals

1. **Comment-matching in FAIL-severity patterns**: First field test where R-DEPR-06 fires on comments (Tweener mentioned in explanatory text). This pattern would affect any extension with comments about migration from deprecated APIs.

2. **Version-compat guard diversity**: V-Shell uses `if (Clutter.ClickAction)` (feature detection), Blur my Shell uses ternary guards — Dash to Panel uses `Config.PACKAGE_VERSION >= '48'` (version comparison). Each triggers different guard-pattern gaps.

3. **GPL license header noise at scale**: With 17 files all having GPL headers, R-SEC-03 produces 18 WARNs. This is the noisiest false-positive pattern per-extension we've seen.

4. **System schema usage pattern**: First field test where R-SLOP-24 fires on system schemas (desktop.interface, desktop.notifications, shell.app-switcher). Common in panel/dock extensions that integrate with system settings.

5. **Prefs file complexity**: 4,052-line prefs.js successfully processed by check-prefs.py with only 2 relevant WARNs (R-PREFS-04b/04c). The check handles extreme file sizes well.

## Priority Improvements

### P0 — None

No credibility-damaging false FAILs at the same scale as previous field tests (cf. Blur my Shell's 13 GObject.registerClass FPs). The 9 FP FAILs are distributed across 3 root causes.

### P1 — Significant noise reduction

1. **Comment-awareness for pattern rules**: Skip lines starting with `//` or inside `/* */` blocks. Fixes R-DEPR-06 (2 FP FAILs) and R-DEPR-05 (1 FP FAIL) on Dash to Panel. Would benefit all extensions with migration comments.

2. **R-VER48-02 guard for `PACKAGE_VERSION >= '48'`**: Add guard-pattern recognizing `PACKAGE_VERSION.*'48'\|PACKAGE_VERSION.*48`. Fixes 2 FP FAILs.

3. **R-SEC-03 guard for license headers**: Add guard-pattern `gnu\.org/licenses` or `General Public License`. Fixes 18 FP WARNs.

4. **R-SLOP-24 guard for system schemas**: Add guard-pattern for `schema_id:.*org\.gnome\.(desktop|shell\b(?!\.extensions))`. Fixes 5 FP WARNs.

5. **Provenance post-filter bug**: Investigate why R-SLOP-01 WARNs aren't actually suppressed despite the filter reporting suppression. Fixes 5 unsuppressed WARNs.

### P2 — Future improvements

6. **init/shell-modification call-chain awareness**: Recognize constructors called from enable() chain. Fixes 4 FP FAILs but requires non-trivial analysis.

7. **R-SLOP-38 tolerance for domain-specific identifiers**: 25-char threshold is too aggressive for descriptive GLib signal IDs and comparison functions. Consider raising to 30 or adding domain-vocabulary exemptions.

## Calibration Lessons Learned

1. **Pattern rules matching in comments is a systemic issue**: Any FAIL-severity rule matching an API name will produce false positives when that name appears in explanatory comments. This affects R-DEPR-05, R-DEPR-06, and potentially others. A global comment-skipping preprocessor would address this class of FPs.

2. **Version-compat guard idioms are extension-specific**: Each major extension uses a different guard style (feature detection, ternary, PACKAGE_VERSION comparison). The guard-pattern system needs to accommodate all three idioms.

3. **License header URLs are the largest single source of false WARNs**: In extensions with GPL headers in every file, R-SEC-03 produces N false WARNs where N equals the file count. A single guard-pattern fix would eliminate the most common false WARN across all GPL-licensed extensions.

4. **System schema access is a panel/dock extension pattern**: Extensions that integrate with GNOME desktop settings (interface, notifications, keybindings) correctly use `new Gio.Settings({schema_id: ...})`. R-SLOP-24 cannot distinguish this from incorrect extension settings access.

5. **Provenance score 4 with JSDoc**: Dash to Panel has a high provenance score (domain vocabulary ×13, nontrivial algorithms ×108) yet the post-filter doesn't suppress JSDoc WARNs. This suggests a bug in the suppression pipeline rather than a threshold issue.

6. **Resource graph handles large extensions well**: 17 files, depth 2, 0 orphans. The centralized `_signalsHandler.add()` pattern is well-recognized by the resource graph.
