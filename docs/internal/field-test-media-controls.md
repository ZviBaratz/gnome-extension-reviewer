# Field Test: Media Controls

**Extension**: Media Controls (`mediacontrols@cliffniff.github.com`)
**Source**: https://github.com/cliffniff/media-controls
**Category**: Audio/media control (MPRIS)
**Downloads**: ~437,000
**GNOME versions**: 46, 47, 48, 49
**Codebase**: 17 JS files, 5,064 lines (hand-written JavaScript, no TypeScript compilation)
**Layout**: `src/` directory (modern build-system layout)
**License**: GPL-2.0-or-later

## Why This Extension

First audio/media extension tested. Exercises under-represented patterns:
- D-Bus proxy lifecycle (MPRIS bus interaction, 3 proxies per player)
- Signal-heavy architecture (41 manual .connect() calls)
- `src/` directory layout (build-system pattern, metadata.json in src/)
- Extensive TypeScript-compatible JSDoc typing strategy
- Custom St.Widget subclasses with GObject.registerClass

## Architecture Overview

- **extension.js** (787 LOC): Main entry point, player discovery via D-Bus NameOwnerChanged, keybinding lifecycle
- **PlayerProxy.js** (609 LOC): MPRIS D-Bus wrapper — 3 proxies per player (Mpris, MprisPlayer, Properties), change-listener Map, fallback polling
- **PanelButton.js** (1,236 LOC): Panel button + popup menu UI, extends PanelMenu.Button, `onDestroy()` cleanup via destroy signal
- **ScrollingLabel.js** (391 LOC): Animated scrolling text widget, extends St.ScrollView, `destroy()` override with timer cleanup
- **MenuSlider.js** (278 LOC): Track position slider, extends St.BoxLayout, `onDestroy()` via destroy signal connection
- **prefs.js** (393 LOC): Preferences with AppChooser, BlacklistedPlayers, ElementList, LabelList widgets
- **types/dbus.js** (239 LOC): Full MPRIS D-Bus type definitions in JSDoc

Import segregation is clean: shell helpers in `helpers/shell/`, prefs helpers in `helpers/prefs/`, shared utils in `utils/`.

## Raw Results

```
432 checks — 135 passed, 3 failed, 246 warnings, 48 skipped
Exit code: 1
```

### Results by Check Name

| Check | Count | Severity | Assessment |
|-------|-------|----------|------------|
| R-SLOP-02 (JSDoc @returns) | 103 | WARN | **FP** — intentional TypeScript-compatible JSDoc |
| R-SLOP-01 (JSDoc @param) | 70 | WARN | **FP** — same |
| resource-tracking/no-destroy-method | 45 | WARN | **FP** — `onDestroy()` not recognized as cleanup |
| R-SLOP-11 (GLib.source_remove) | 10 | WARN | **TP** — should use `GLib.Source.remove()` |
| R-SLOP-17 (typeof method guard) | 3 | WARN | **Debatable** — defensive check for optional API methods |
| lifecycle/prototype-override | 2 | WARN | **TP** — MprisSource.prototype._addPlayer not restored |
| metadata/exists | 1 | FAIL | **FP** — metadata.json in `src/`, no fallback |
| file-structure/metadata.json | 1 | FAIL | **FP** — same |
| css/shell-class-override | 1 | FAIL | **TP** — `.panel-button` overrides Shell theme class |
| lifecycle/signal-balance | 1 | WARN | **Needs analysis** — 41 connects vs 10 disconnects |
| lifecycle/async-destroyed-guard | 1 | WARN | **TP** |
| lifecycle/soup-session-abort | 1 | WARN | **TP** — no abort() on disable |
| async/no-cancellable | 1 | WARN | **TP** — async calls without Gio.Cancellable |
| async/missing-cancellable | 1 | WARN | **TP** — _async() without cancellable |
| quality/constructor-resources | 1 | WARN | **TP** — .connect() in AppChooser constructor |
| quality/comment-density | 1 | WARN | **TP advisory** — utils/common.js 45% comments |
| quality/private-api | 1 | WARN | **TP** — Main.panel private API access |
| quality/excessive-null-checks | 1 | WARN | **TP advisory** — 117 null checks, ratio 0.025 |
| R-QUAL-33 (Gio._promisify) | 1 | WARN | **TP advisory** — 4 files with undocumented promisify |

**Total**: 218 FP (89%), 28 TP/debatable (11%)

## False Positive Analysis

### 1. R-SLOP-01/02 JSDoc Flood (173 WARNs)

**Root cause**: Provenance score 3, threshold >= 4 for suppression.

Media Controls uses intentional TypeScript-compatible JSDoc throughout all 17 files. The project includes `jsconfig.json`, `@girs/*` type packages, and a dedicated `types/dbus.js` with full MPRIS type definitions. This is clearly a deliberate typing strategy, not AI slop.

The provenance score of 3 means "strong hand-written indicators" (domain vocabulary: 12 hits, nontrivial algorithms: 40 hits, consistent naming). The threshold of >= 4 is too conservative for JSDoc suppression.

**Fix**: Lower provenance threshold to >= 3.

### 2. resource-tracking/no-destroy-method (45 WARNs)

**Root cause**: `build-resource-graph.py` recognizes `destroy()`, `disable()`, and `_destroy*()` as cleanup methods, but NOT `onDestroy()`.

Both MenuSlider.js and PanelButton.js use `this.connect("destroy", this.onDestroy.bind(this))` to register cleanup handlers. The `onDestroy()` method contains proper signal disconnection, timer removal, and null assignments. The resource graph doesn't recognize this pattern.

- MenuSlider.js: 8 resource warnings, has `onDestroy()` at line 250
- PanelButton.js: 37 resource warnings, has `onDestroy()` at line 1186

**Fix**: Add `onDestroy()` recognition in build-resource-graph.py cleanup method detection.

### 3. metadata.json Missing (2 FAILs)

**Root cause**: ego-lint.sh has `src/` fallback for extension.js but NOT for metadata.json. check-metadata.py also lacks the fallback.

Media Controls uses a build-system layout with all source in `src/` — metadata.json lives at `src/metadata.json`, which is standard for extensions using gnome-extensions pack with a build step.

**Fix**: Add consistent `src/` fallback for metadata.json in ego-lint.sh and check-metadata.py.

## True Positives

### Lifecycle Issues
- **prototype-override** (2): `MprisSource.prototype._addPlayer` is monkey-patched but the original is not saved/restored in `disable()`. Genuine concern for multi-extension compatibility.
- **soup-session-abort** (1): Soup.Session created for album art fetching but no `.abort()` in cleanup path. Pending HTTP requests will continue after disable.
- **async-destroyed-guard** (1): Multiple async/await chains without `_destroyed` guard. Extension could act on stale state after disable if async operations complete late.
- **signal-balance** (1): 41 manual `.connect()` vs 10 `.disconnect()`. Needs deeper analysis — some may use `.connectObject()` auto-management, some may be on child widgets (auto-cleaned on destroy).

### Async Safety
- **no-cancellable + missing-cancellable** (2): D-Bus proxy creation and file operations use async without `Gio.Cancellable`. These should be cancellable via disable() to prevent stale state.

### CSS
- **shell-class-override** (1 FAIL): `.panel-button` in stylesheet.css overrides GNOME Shell's panel button styling for ALL panel buttons, not just this extension's. Also uses `.popup-menu-container` and `.popup-menu-box` (not flagged but same concern).

### Code Quality
- **constructor-resources** (1): AppChooser.js:51 has `.connect()` in constructor. Since this is a prefs widget (not extension lifecycle), the impact is limited but still worth noting.
- **GLib.source_remove** (10): Uses non-idiomatic `GLib.source_remove()` instead of `GLib.Source.remove()`. Functional but not correct GJS API.

## Calibration Lessons

1. **`onDestroy()` is a common cleanup pattern** — build-resource-graph.py should recognize it alongside `destroy()`, `disable()`, and `_destroy*()`
2. **Provenance threshold of 4 is too conservative for JSDoc suppression** — score 3 is sufficient to indicate hand-written code, especially when JSDoc is extensive and consistent
3. **`src/` layout support remains inconsistent** — extension.js has fallback, metadata.json does not. Need systematic audit of all src/ fallbacks
4. **TypeScript-compatible JSDoc is becoming more common** — popular extensions like Media Controls use it intentionally. The R-SLOP-01/02 rules need better calibration for this pattern
5. **D-Bus proxy lifecycle is well-handled** — no false positives from D-Bus-specific checks. The MPRIS pattern (3 proxies per player, NameOwnerChanged tracking) exercises these checks well
6. **CSS shell-class-override works correctly** — caught legitimate `.panel-button` override. However, it missed `.popup-menu-container` and `.popup-menu-box` (potential gap in the shell class list)

## Comparison with Prior Tests

| Metric | Media Controls | Avg of Prior 8 |
|--------|---------------|----------------|
| FP rate (pre-fix) | 89% | ~40-76% |
| Dominant FP cause | JSDoc + onDestroy | Varied |
| True positive rate | 11% | ~24-60% |
| Security issues | 0 | 0-6 |
| Code provenance | 3/5 | 2-4/5 |

The high FP rate is driven by two specific gaps. After fixes, the extension's true positive findings are meaningful and actionable.
