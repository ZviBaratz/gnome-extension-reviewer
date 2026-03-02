# Field Test: GSConnect v71

**Date**: 2026-03-02 (updated 2026-03-02 with ego-review + ego-simulate)
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

## ego-lint Verdict

GSConnect v71 has **13 real blocking issues** (all TPs): missing LICENSE, Python script, 6 Tweener usages, deprecated imports.format, and Main.panel at module scope. The 411 WARNs are dominated by R-SLOP-01/02 JSDoc noise (222 hits) from legitimate documentation — a systemic noise issue for well-documented, human-written extensions. Resource tracking and lifecycle warnings are generally accurate. Provenance score of 4 correctly identifies this as strong hand-written code.

**Post-fix signal-to-noise ratio**: Acceptable for FAILs (13 FAILs, all TP or borderline). WARN noise is high due to JSDoc — would benefit from provenance-aware suppression in future.

---

## ego-review Results

Ran the full ego-submit pipeline (ego-lint → ego-review → package validation → metadata review → readiness report) using parallel 3-agent execution:
- **Agent 1**: ego-lint + package validation
- **Agent 2**: ego-review lifecycle + signals + security (Phases 2-4)
- **Agent 3**: ego-review quality + AI patterns + metadata + disclosure (Phases 5-5a, Phase 4)

Wall-clock time: ~4 minutes (parallel), vs ~10 minutes estimated sequential.

### Verdict

**NEEDS FIXES** | **Rejection Risk: MEDIUM** (2 blocking from lint, 10 advisory from review)

### Blocking Issues (from ego-lint, confirmed by review)

| # | Issue | File:Line | Category |
|---|-------|-----------|----------|
| B1 | Missing LICENSE file | — | packaging |
| B2 | Deprecated `imports.tweener` | service/components/pulseaudio.js:11, service/ui/messaging.js:18 | deprecated API |

### Advisory Issues (from manual review)

| # | Issue | File:Line | Category |
|---|-------|-----------|----------|
| A1 | Constructor patches never reversed | extension.js constructor | lifecycle |
| A2 | `unpatchGtkNotificationDaemon()` dead code | shell/notification.js:402 | lifecycle |
| A3 | `unwatchService()` dead code | shell/clipboard.js:374 | lifecycle |
| A4 | `_sessionExpiryId` timer not removed in destroy() | service/components/input.js | resource leak |
| A5 | `_serviceMonitor` file monitor not cancelled | service/daemon.js:283 | resource leak |
| A6 | Gtk import in shell-process code | shell/utils.js:6 | import segregation |
| A7 | `gschemas.compiled` missing from schemas/ | schemas/ | packaging |
| A8 | GNOME 49 in shell-version (unreleased) | metadata.json | metadata |
| A9 | `run_dispose()` usage (6 instances) | extension.js:317, service/daemon.js:389, etc. | lifecycle |
| A10 | `.claude/` directory must be excluded from zip | .claude/ | packaging |

### Issues ego-lint Could Not Detect

1. **A1-A3: Constructor patches not reversed** — `patchGSConnectNotificationSource()`, `patchGtkNotificationDaemon()`, and `Clipboard.watchService()` are called in the extension constructor but never reversed in `disable()`. Corresponding unpatch/unwatch functions exist as dead code. This requires semantic analysis of constructor vs enable/disable lifecycle — ego-lint's `init/shell-modification` check catches module-scope issues but not constructor-time persistent state.

2. **A4: Timer leak in service component** — `_sessionExpiryId` in `service/components/input.js` is set at lines 292/367 but not cleaned in `destroy()` (lines 468-485). Requires cross-method analysis within a class — ego-lint's `lifecycle/untracked-timeout` only checks enable/disable scope.

3. **A5: File monitor not cancelled** — `_serviceMonitor` in `service/daemon.js:283` is never cancelled in `vfunc_shutdown()`. ego-lint's resource graph would need GApplication lifecycle awareness (vfunc_startup/vfunc_shutdown) in addition to enable/disable.

4. **Signal balance across 130+ connections** — ego-review confirmed all signals in the shell process are properly balanced (~125+ balanced, 5 advisory in widget-lifecycle or separate-process contexts). ego-lint's `lifecycle/signal-balance` provides a coarse count but can't verify per-signal correctness.

5. **Disclosure matrix gaps** — 5 of 6 capability categories (clipboard, network, subprocess, private API, file I/O) are present in code but undisclosed in the metadata description. ego-lint's `disclosure/clipboard` and `disclosure/network` checks only catch the most obvious patterns; the comprehensive cross-reference requires reading actual code semantics.

### Resource Summary

- Signal connections: ~130+ total, ~125+ balanced / 5 advisory
- Timers: All critical timers tracked; 1 leak (`_sessionExpiryId`)
- File monitors: 1 found, not cancelled in shutdown
- D-Bus proxies: All properly disconnected and nulled
- Empty catch blocks: ~38 instances (mostly justified — graceful degradation)

### AI Pattern Analysis

- **Score**: 0/46 — **PASS**
- **Provenance score**: 5/5 (strongly hand-written)
- **Assessment**: Zero AI-generation indicators. Deep domain expertise (KDE Connect protocol, GNOME internals), protocol version negotiation (v7→v8), multi-fallback implementations (GSound→libcanberra→Gdk.beep, Mutter RemoteDesktop→Atspi→ydotool), references to upstream bug reports. Community contributions from named developers (JingMatrix for wl_clipboard/ydotool).

### Disclosure Matrix

| Capability | Found in Code | Disclosed in Description | Status |
|-----------|---------------|--------------------------|--------|
| Clipboard | Yes — `shell/clipboard.js`, `service/components/clipboard.js`, `wl_clipboard.js` | No | **WARN** |
| Network | Yes — `service/backends/lan.js` (TCP/UDP 1716-1764, TLS) | Partial ("share content") | **WARN** |
| Subprocess | Yes — openssl, ssh-add/keygen, dconf, canberra, ydotool/wtype, wl-paste/copy | No | **WARN** |
| pkexec | No | N/A | OK |
| Private API | Yes — `Main.notificationDaemon._gtkNotificationDaemon`, `RemoteAccessController.inhibit_remote_access` | No | **WARN** |
| File I/O | Yes — `~/.config/gsconnect/`, `~/.cache/gsconnect/`, TLS certs, file transfers | No | **WARN** |
| D-Bus | Yes — exports clipboard portal + object manager; monitors notifications | No | **WARN** |

### Package Validation

- Zip exists: No
- Required files: All present except LICENSE and gschemas.compiled
- Forbidden files: `.claude/` present (must be excluded)
- Secrets scan: Clean
- Estimated size: ~1-2 MB

### Review Process Assessment

1. **Parallel execution worked well** — 3-agent split had clean separation with no overlapping findings to deduplicate
2. **Agent 2 (lifecycle/signals)** produced the most valuable findings — constructor patches (A1-A3) and signal balance verification are the kind of semantic analysis that ego-lint cannot perform
3. **Agent 3 (quality/metadata)** correctly identified the disclosure matrix as the biggest strategic concern — 5 of 6 undisclosed capabilities
4. **Provenance scoring divergence**: ego-lint scored 4/5, ego-review scored 5/5. The difference is minor and both correctly classify as strongly hand-written

---

## ego-simulate Results

### Score

| Taxonomy Reason | Weight | Evidence |
|-----------------|--------|----------|
| #5 Deprecated modules | 10 | Tweener in pulseaudio.js:11, messaging.js:18; imports.format in setup.js:18 |
| #7 Systematic JSDoc @param/@returns | 8 | 170+ R-SLOP-01 instances across service/ (discounted — see note) |
| #15 Import segregation | 5 | Gtk in shell/utils.js:6 (shell-process code) |
| ego-lint: non-gjs-scripts (unmapped) | 5 | nautilus-gsconnect.py |
| ego-lint: init/shell-modification (unmapped) | 5 | extension.js:28 + 3 daemon-process instances |
| #19 Empty catch blocks | 3 | ~38 instances across codebase |
| #20 Excessive code volume | 3 | ~17K lines (>8K threshold) |
| #21 Missing LICENSE | 1 | No standalone license file |
| **Mechanical total** | **40** | |

### Verdict

**Mechanical score: 40** — Will be rejected (10+ threshold)

The mechanical score is inflated by context the taxonomy cannot account for:

- **#7 JSDoc (8 pts)**: GSConnect's extensive JSDoc predates the AI era by years. The `url` field points to an active GitHub repo with thousands of commits. A real reviewer would verify provenance and discount this as a deliberate documentation style, not AI slop. This is a single AI slop signal — per the EGO AI policy, single signals are "noted but not blocking."
- **non-gjs-scripts (5 pts)**: `nautilus-gsconnect.py` is a Nautilus file manager integration — a standard pattern for file-sharing extensions, not a helper script.
- **init/shell-modification (5 pts)**: 3 of 4 instances are in the service daemon process (not the shell). Only `extension.js:28` runs in the GNOME Shell process.
- **#20 Code volume (3 pts)**: GSConnect is one of the most complex extensions on EGO. Reviewers are familiar with it and expect the volume.

**Realistic score: ~16** — Still a rejection, driven by the deprecated Tweener (10 pts). The Tweener usage alone exceeds the rejection threshold.

### Calibration Assessment

GSConnect v71 is **approved on EGO** (version 71 with 46-49 support). The mechanical score of 40 significantly overestimates rejection risk. Even the realistic score of 16 is high for an approved extension. Key calibration observations:

1. **Taxonomy #5 (deprecated modules) is correctly blocking** — Tweener removal is a hard requirement for GNOME 45+. However, GSConnect may have been approved before the deprecation check was enforced, or the review may have been lenient for such a well-known project with years of history.

2. **#7 (JSDoc) creates significant noise** — a single AI slop reason adds 8 points regardless of provenance. For known projects with repo URLs, the weight should be reduced or gated behind a provenance check. This confirms the P2 improvement identified in the ego-lint section.

3. **Unmapped ego-lint FAILs add 10 points** — `non-gjs-scripts` and `init/shell-modification` each add 5 points but are borderline/contextual FPs for GSConnect. The +5 penalty for unmapped FAILs may be too aggressive when the FAIL itself is a false positive.

4. **#20 (code volume) penalizes complex but legitimate extensions** — the 8K threshold is reasonable for detecting AI-generated boilerplate but inappropriate for mature projects like GSConnect. Consider gating behind provenance score.

### Suggested Taxonomy Improvements

- **Provenance-gated scoring for #7**: When provenance score is ≥4 and a repo URL exists, reduce #7 weight from 8 to 1 (advisory)
- **Unmapped FAIL weight reduction**: Consider weight 3 (not 5) for ego-lint FAILs that don't map to taxonomy reasons, as they tend to be edge cases
- **Architecture-aware init/shell-modification**: Reduce to WARN for files in `service/` subdirectories (daemon process code)

---

## Overall Verdict

GSConnect v71 is a well-engineered, mature extension with strong provenance (5/5). The codebase demonstrates deep domain expertise in both GNOME Shell internals and the KDE Connect protocol. Signal management across 130+ connections is thorough and balanced.

**Blocking fixes required**: Replace deprecated Tweener (2 files) and `imports.format` (1 file), add LICENSE file, compile GSettings schemas.

**Strategic concern**: 5 of 6 capability categories are undisclosed in the metadata description. The extension uses network sockets, clipboard access, subprocess execution, private Shell APIs, and D-Bus services extensively — all should be disclosed.

**Tool calibration value**: GSConnect is the most architecturally complex extension tested and exposed key limitations:
- ego-lint cannot distinguish daemon-process code from shell-process code (causes FPs)
- ego-lint cannot detect constructor-time persistent state (only module-scope)
- ego-simulate's mechanical scoring overestimates rejection risk for known, provenance-verified projects
- The JSDoc noise problem (222 of 411 WARNs = 54%) confirms provenance-aware suppression should be prioritized
