# Internal Development Artifacts

Development history and analysis artifacts. These are kept for transparency but are not part of the project's external documentation.

## Field Test Suite

Run the full ego-submit pipeline against real extensions to surface false positives, coverage gaps, and calibration issues. Results are iterative — re-run after tool improvements to track accuracy over time. See `field-test-template.md` for the process.

| Extension | First Tested | JS Files | Lines | FAILs (first → latest) | TPs | FPs | Key Patterns |
|-----------|-------------|----------|-------|------------------------|-----|-----|--------------|
| [hara-hachi-bu](field-test-hara-hachi-bu.md) (baseline) | 2026-02-25 | 18 | ~8,894 | 0 | — | — | Regression baseline; 29 findings |
| [Clipboard Indicator](field-test-clipboard-indicator.md) | 2026-02-28 | 6 | ~2,000 | 27→1 | — | — | R-WEB version gating, license variants |
| [AppIndicator](field-test-appindicator.md) | 2026-03-01 | 17 | ~5,655 | 14→11 | 6 | 8 | D-Bus, connectSmart, compat shims |
| [Blur my Shell](field-test-blur-my-shell.md) | 2026-03-01 | 49 | 7,743 | 21→7 | 7 | 14 | GObject.registerClass, src/ layout |
| [GSConnect](field-test-gsconnect.md) | 2026-03-02 | 65 | 24,680 | 19→13 | 10 | 6 | Service daemon context, JSDoc noise |
| [V-Shell](field-test-v-shell.md) | 2026-03-02 | 28 | 19,201 | 23→3 | 3 | 0 | Multi-version compat guards; all initial FPs resolved |
| [Dash to Panel](field-test-dash-to-panel.md) | 2026-03-03 | 17 | 16,583 | 19→16† | 10 | 9 | Comment FPs, version-compat guards |
| [Tiling Shell](field-test-tiling-shell.md) | 2026-03-03 | 64 | 11,371 | 21→4 | 4 | 0 | Compiled TS, keybindings, constructors-from-enable |
| [Media Controls](field-test-media-controls.md) | 2026-03-04 | 17 | ~5,000 | 246W/3F→31W/6F | 6 | 0 | MPRIS D-Bus, onDestroy, src/ layout, provenance |

† Tiling Shell session #29 fixes (constructor-only-in-extension.js) resolve 4 of Dash to Panel's init/shell-modification FP FAILs; re-run pending.

### Cumulative Calibration Lessons

Patterns discovered across field tests — encode here so future rules avoid repeating mistakes:

*Threshold and gating:*

1. **GJS polyfills shift rule applicability**: When GJS adopts a browser API (e.g., `setTimeout` in GNOME 45), any rule flagging that API needs `max-version` gating. Audit all R-WEB rules when a new GNOME version adds polyfills.
2. **Cloned repos break directory-name checks**: Any check comparing directory name to UUID must be advisory, not blocking — developers clone repos with repo names, not UUIDs.
3. **License file extensions vary**: Real extensions use `.rst`, `.md`, `.txt` — not just bare `LICENSE`/`COPYING`.
4. **Fixture gotcha — "GNOME" in names**: The trademark check catches "gnome" in UUIDs and names. Use abbreviations like `g45` in fixture identifiers.
5. **Thresholds don't scale with extension size**: Fixed-count thresholds (logging volume, warning count) produce false positives on large extensions. Use density-based thresholds (per 100 lines) with a minimum floor.

*Pattern rule limitations:*

6. **Comment matches are a systemic FP source**: Rules matching API names (e.g., `R-DEPR-06` Tweener) fire on comments mentioning the API. Use `skip-comments: true` for rules where comment FPs are common.
7. **Version-compat guard idioms are extension-specific**: Feature detection (`if (Meta.disable_unredirect`), boolean flags (`! Clutter.Container`), version comparison (`PACKAGE_VERSION >= '48'`) — no single guard pattern covers all extensions.
8. **Multi-version extensions produce systemic FPs invisible to static analysis**: V-Shell (GNOME 45–49) had 23 FAILs, all FPs from version-compat code. Guard patterns and import-graph BFS reduced this to 3 TPs.

*Structural analysis limitations:*

9. **`GObject.registerClass` is class registration, not resource allocation**: Blur my Shell had 13 FPs from init/constructor-resources flagging `GObject.registerClass` at module scope. Now exempt.
10. **Service daemon code (`service/`) follows different patterns than extension code**: GSConnect's service daemon legitimately uses deprecated APIs, standalone GJS imports, and module-scope resources. `service/` is now excluded from init-time and constructor-resources checks.
11. **Import segregation needs import-graph awareness for shared `lib/` modules**: V-Shell's `optionsFactory` is imported by both `prefs.js` and `extension.js` — BFS from each entry point is needed to determine which rules apply to shared code.

*WARN noise:*

12. **License header URLs are the largest single source of false R-SEC-03 WARNs**: GPL boilerplate with `gnu.org/licenses` URLs triggered the external-URL rule. Now suppressed by guard pattern.
13. **JSDoc documentation creates massive R-SLOP-01/02 WARN noise on mature projects**: GSConnect (222 WARNs) and Dash to Panel both showed that real JSDoc on mature code triggers AI slop heuristics. Provenance scoring (`quality/code-provenance >= 3`) now gates R-SLOP-01/02 post-filter.

*Compiled TypeScript patterns:*

14. **Helper file constructors called from enable() are not init-time violations**: Tiling Shell had 13 FP FAILs from Shell globals in class constructors that are only ever instantiated from `enable()`. Constructor checks are now restricted to `extension.js` only — matching the existing `GOBJECT_CONSTRUCTORS` guard.
15. **Arrow function definitions at module scope are lazy**: `const fn = () => Main.layoutManager.monitors` doesn't execute at module load time. The function body is deferred until the first call.
16. **Same-line ternary guards need `guard-window: 0`**: Version compat patterns like `api.exists ? old(args) : new()` have the guard and deprecated API on the same line. `guard-window: 0` (match on current line only) handles this.
17. **Single long lines ≠ minification**: Compiled TypeScript may have one or two very long lines (keyboard constant chains, export lists) in otherwise readable files. The minified-js check now requires 3+ lines > 500 chars.
18. **Compiled TypeScript (esbuild) generates systematic WARN noise**: `var` declarations from `__defProp`/`__publicField` helpers (R-DEPR-09), verbose parameter names (R-SLOP-38), and many small classes without `destroy()` methods (resource-tracking/no-destroy-method). These are build artifacts, not author issues.

## Other Artifacts

- `false-positive-analysis-2026-02-27.md` — Detailed root-cause analysis for initial false positives (archived; see field-test-hara-hachi-bu.md F-001–F-005)
- `pipeline-improvements-2026-02-28.md` — Detailed analysis and code snippets for pipeline improvements (archived; see field-test-hara-hachi-bu.md F-006–F-011)
- `review-feedback-2026-02-28.md` — Full pipeline improvement proposals from ego-submit run (see field-test-hara-hachi-bu.md F-012–F-021)
- `pipeline-review-2026-03-03.md` — Pipeline efficiency review (see field-test-hara-hachi-bu.md F-022–F-029)
