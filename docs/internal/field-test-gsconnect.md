# Field Test: GSConnect v71

**Date**: 2026-03-02
**Extension**: GSConnect v71 (`gsconnect@andyholmes.github.io`)
**Source**: https://github.com/GSConnect/gnome-shell-extension-gsconnect
**License**: GPL-2.0-or-later

## Extension Profile

| Attribute | Value |
|-----------|-------|
| UUID | `gsconnect@andyholmes.github.io` |
| GNOME versions | 46, 47, 48, 49 |
| JS files | 65 |
| Total lines | 24,680 |
| CSS lines | 127 |
| Schema keys | 48 |
| Largest file | messaging.js (1,325 lines) |
| Provenance score | 4 (strong hand-written) |
| Provenance signals | domain-vocabulary (298), nontrivial-algorithms (68), debug-comments (19), consistent-naming-style |

**Architecture**: Multi-component extension with three distinct runtime contexts:
- **Shell extension** (`extension.js`, `shell/`): QuickSettings integration, notifications, clipboard, keybindings
- **Service daemon** (`service/`): D-Bus service, device management, plugin system, network backends
- **Preferences** (`preferences/`): GTK4/Adwaita preferences UI

Also includes: `nautilus-gsconnect.py` (Nautilus integration), `gsconnect-preferences` (standalone prefs launcher), `wl_clipboard.js` (Wayland clipboard helper).

## Results

### Before fixes

| Status | Count |
|--------|-------|
| PASS | 163 |
| FAIL | 19 |
| WARN | 411 |
| SKIP | 17 |
| **Total** | **610** |
| Exit code | 1 |

### After fixes

| Status | Count |
|--------|-------|
| PASS | 165 |
| FAIL | 13 |
| WARN | 411 |
| SKIP | 17 |
| **Total** | **606** |
| Exit code | 1 |

**FPs eliminated**: 6 (R-WEB-03 ×2, schema/gnome-trademark ×1, R-VER46-04 ×2, init/shell-modification GLib.Bytes ×1)

## FAIL Classification

### True Positives (10)

| Check | File(s) | Notes |
|-------|---------|-------|
| license | — | No LICENSE/COPYING file in release zip |
| non-gjs-scripts | nautilus-gsconnect.py | Python Nautilus integration plugin |
| R-DEPR-06 (×6) | messaging.js, pulseaudio.js | Tweener usage (`imports.tweener.tweener`) |
| R-DEPR-10 | setup.js | `imports.format.format` deprecated |
| init/shell-modification | extension.js:28 | `Main.panel.statusArea.quickSettings` at module scope |

### Borderline / Contextual FPs (3)

| Check | File(s) | Notes |
|-------|---------|-------|
| init/shell-modification | wl_clipboard.js:11 | `new Gio.SubprocessLauncher()` at module scope — technically a resource, but this is a helper daemon module, not extension init path |
| init/shell-modification | service/init.js:158 | `new Gio.Settings()` in service daemon — runs in separate process, not in shell |
| init/shell-modification | service/plugins/findmyphone.js:117 | `new Gio.Settings()` in plugin — same daemon context |

### Fixed False Positives (6)

| Check | File(s) | Root Cause | Fix |
|-------|---------|------------|-----|
| R-WEB-03 (P0) | messaging.js:973, contacts.js:542 | Pattern `\bfetch\s*\(` matches `.fetch()` method calls and `async fetch()` definitions | Added guard-pattern to suppress `.fetch(` and `async fetch(` |
| schema/gnome-trademark (P0) | schemas/*.gschema.xml | Case-sensitive prefix strip `org.gnome.shell.extensions.` misses mixed-case `org.gnome.Shell.Extensions.` | Made prefix stripping case-insensitive via `${var,,}` |
| R-VER46-04 (P1) | nativeMessagingHost.js:19, lan.js:19 | `Gio.UnixInputStream` in catch fallback after `import('gi://GioUnix')` — compat pattern, not legacy usage | Added guard-pattern for `\bGioUnix\b` on current/prev line |
| init/shell-modification (P2) | preferences/service.js:22 | `new GLib.Bytes(...)` is a data container, not a system resource | Added VALUE_TYPES exemption for GLib.Bytes, Variant, DateTime, etc. |

## WARN Analysis

**411 total WARNs** — breakdown by category:

| Check | Count | Assessment |
|-------|-------|------------|
| R-SLOP-01 (JSDoc @param) | 170 | **Noise**: GSConnect uses extensive typed JSDoc — legitimate for a mature, human-written project |
| R-SLOP-02 (JSDoc @returns) | 52 | Same as above |
| quality/constructor-resources | 28 | Mixed: many in `service/ui/` (daemon GTK widgets, not extension lifecycle) |
| R-SLOP-40 (new Promise wrapper) | 22 | TP advisory: GSConnect wraps many GIO async operations |
| R-SLOP-24 (new Gio.Settings) | 20 | Mixed: many in `service/` daemon (no Extension class available) |
| resource-tracking/destroy-not-called | 14 | TP: resources created but parent doesn't call destroy() |
| lifecycle/prototype-override | 10 | TP: GSConnect patches prototypes for Shell integration |
| R-SLOP-11 (full-form timer APIs) | 9 | TP advisory: uses `GLib.timeout_add_seconds_full` |
| R-QUAL-32 (unnecessary ?version=) | 7 | TP for standalone daemon scripts — version specifiers help standalone GJS |
| R-SEC-06 (run_dispose) | 6 | TP advisory: needs justification comments |
| R-QUAL-31 (_onDestroy naming) | 6 | TP advisory |
| quality/run-dispose-no-comment | 6 | TP advisory |
| lifecycle/untracked-timeout | 6 | TP: timeouts without stored IDs |
| lifecycle/destroy-no-null | 5 | TP: resources not nulled after destroy |
| R-VER48-04b ({vertical: true}) | 4 | TP: deprecated in GNOME 48 |
| R-SEC-03 (HTTP URLs) | 4 | TP advisory: protocol references |
| resource-tracking/no-destroy-method | 3 | TP: classes without destroy() |
| R-QUAL-35 (sync D-Bus) | 3 | TP advisory |
| Others | ~36 | Various individual findings |

**Key noise source**: R-SLOP-01/02 (222 hits, 54% of all WARNs) — typed JSDoc is an AI slop indicator for typical extensions but creates massive false noise for GSConnect's human-written, well-documented codebase.

## SKIP Classification

All 17 SKIPs are correct:
- R-WEB-01/02/10/11: Version-gated (max-version 44, extension targets 46+)
- R-VER50-*: Version-gated (min-version 50, extension targets 46-49)
- R-DEPR-04-legacy: Version-gated
- polkit/*: No polkit files present
- eslint: No ESLint config/binary found
- schema-usage/*: Dynamic key access detected (`get_string(key)` pattern)
- package/exists: No zip package in extracted directory

## Detection Gaps

### GSConnect-specific patterns not detected

1. **Service daemon vs extension code**: ego-lint cannot distinguish `service/` files (daemon process) from extension files (shell process). This causes FPs for init-time checks and `new Gio.Settings()` warnings in daemon code.

2. **Standalone GJS scripts**: `gsconnect-preferences` and `service/daemon.js` run as standalone GJS processes — version specifiers in `gi://` imports are correct and necessary for these, but flagged as unnecessary.

3. **Compiled GResource inspection**: The extension ships `org.gnome.Shell.Extensions.GSConnect.gresource` — ego-lint doesn't inspect compiled GResource bundles for embedded UI files.

4. **Plugin architecture lifecycle**: GSConnect's plugin system (`service/plugins/`) manages lifecycle differently from extension enable/disable — plugins have `connected()`/`disconnected()` lifecycle, not `enable()`/`disable()`.

### General gaps (also in MEMORY.md)

- Module-scope Map/Set detection (mutable state)
- `.disable()` as cleanup method recognition (would reduce resource-tracking FP WARNs)

## Comparison with Previous Field Tests

| Metric | Hara-hachi-bu | AppIndicator | Clipboard Ind. | Blur my Shell | GSConnect |
|--------|--------------|--------------|----------------|---------------|-----------|
| JS files | 17 | 17 | 6 | 49 | 65 |
| Total lines | ~3,000 | ~5,000 | ~2,000 | 7,743 | 24,680 |
| PASS | 204 | 178 | 190 | 186 | 165 |
| FAIL (final) | 0 | 11 | 2 | 7 | 13 |
| WARN | 8 | 69 | 27 | 120 | 411 |
| SKIP | 23 | 14 | 17 | 17 | 17 |
| FPs fixed | 0 | — | — | 14 | 6 |
| Provenance | 3 | — | — | — | 4 |

## Priority Improvements

### P0 (Done)
- [x] R-WEB-03: Guard-pattern for `.fetch()` method calls and `async fetch()` definitions
- [x] schema/gnome-trademark: Case-insensitive prefix stripping

### P1 (Done)
- [x] R-VER46-04: Guard-pattern for GioUnix fallback pattern
- [x] init/shell-modification: VALUE_TYPES exemption for GLib.Bytes, Variant, DateTime, etc.

### P2 (Future consideration)
- [ ] R-SLOP-01/02 noise: Consider suppressing for projects with high provenance score (>3)
- [ ] R-SLOP-24 in `service/` directory: Service daemon files use `new Gio.Settings()` legitimately
- [ ] R-QUAL-32 in standalone scripts: Version specifiers are correct for standalone GJS
- [ ] Architectural awareness: Distinguish daemon/service files from extension shell code

## Verdict

GSConnect v71 has **13 real blocking issues** (all TPs): missing LICENSE, Python script, 6 Tweener usages, deprecated imports.format, and Main.panel at module scope. The 411 WARNs are dominated by R-SLOP-01/02 JSDoc noise (222 hits) from legitimate documentation — a systemic noise issue for well-documented, human-written extensions. Resource tracking and lifecycle warnings are generally accurate. Provenance score of 4 correctly identifies this as strong hand-written code.

**Post-fix signal-to-noise ratio**: Acceptable for FAILs (13 FAILs, all TP or borderline). WARN noise is high due to JSDoc — would benefit from provenance-aware suppression in future.
