# gnome-extension-reviewer

EGO review compliance tools for GNOME Shell extensions — catch rejection reasons before submission.

## The Problem

Extensions submitted to [extensions.gnome.org](https://extensions.gnome.org) (EGO) are manually reviewed, and many are rejected for avoidable reasons: missing lifecycle cleanup, import segregation violations, deprecated APIs, or incorrect metadata formats. Some rejection criteria are documented in official guidelines; others are unwritten rules consistently enforced by reviewers but not published anywhere. Meanwhile, AI-generated extensions are increasingly common and often fail review due to patterns that look correct but violate GNOME Shell conventions (unnecessary try-catch wrapping, TypeScript-style JSDoc, dead code after throw).

This project provides automated checks to catch these issues before submission.

## ego-lint: Standalone Compliance Checker

ego-lint is a standalone bash/python tool with **zero AI dependency**. It runs locally, produces deterministic output, and checks your extension against 114 pattern rules and 13 structural analysis scripts.

### Quick Start

```bash
./lint.sh /path/to/your-extension@username
```

Or directly:

```bash
bash skills/ego-lint/scripts/ego-lint.sh /path/to/your-extension@username
```

Exit code 0 = no blocking issues found. Exit code 1 = blocking issues that will likely cause rejection.

### What Gets Checked

| Category | Checks |
|----------|--------|
| **Metadata** | UUID format/match, required fields, shell-version format, session-modes, GNOME trademark, donations |
| **Imports** | GTK/Gdk/Adw banned in extension.js; Clutter/Meta/St/Shell banned in prefs.js; transitive dependency analysis |
| **Schema** | Schema ID matches metadata, path format, `glib-compile-schemas` dry-run |
| **Lifecycle** | enable/disable symmetry, signal cleanup, timeout removal, InjectionManager, D-Bus unexport, widget destroy, settings null, subprocess cancellation |
| **Async** | `_destroyed` guards, cancellable usage, per-call cancellable verification |
| **GObject** | `GObject.registerClass` patterns, GTypeName validation |
| **Resources** | Cross-file resource graph (signals, timeouts, widgets, D-Bus, file monitors, GSettings), orphan detection |
| **Security** | Subprocess validation, pkexec targets, clipboard/network disclosure, `/tmp` writes, telemetry, curl/gsettings spawn |
| **Deprecated** | Mainloop, Lang, ByteArray, ExtensionUtils, Tweener, legacy `imports.*` syntax |
| **Web APIs** | setTimeout, setInterval, fetch, XMLHttpRequest, WebSocket, localStorage |
| **Version Compat** | GNOME 44–50 migration rules (version-gated, only fire for declared shell-versions) |
| **CSS** | Unscoped class names, `!important` usage, GNOME Shell theme class overrides |
| **Code Quality** | AI slop detection (try-catch density, impossible states, empty catches, obfuscation, code provenance scoring) |
| **Package** | Forbidden files in zip, required files, compiled schemas for GNOME 45+ |
| **Preferences** | ExtensionPreferences base class, GTK4/Adwaita patterns, memory leak detection |

### Sample Output

```
================================================================
  ego-lint — GNOME Shell Extension Compliance Checker
================================================================

Extension: /path/to/my-extension@username

[PASS] file-structure/extension.js            extension.js exists
[PASS] file-structure/metadata.json           metadata.json exists
[PASS] license                                License file found (appears GPL-compatible)
[FAIL] R-DEPR-04                              extension.js:4: Legacy imports.* syntax; use ESM imports for GNOME 45+
[FAIL] R-DEPR-05                              extension.js:2: ExtensionUtils removed in GNOME 45+; use Extension base class
[WARN] R-SEC-17                               lib/controller.js:10: Writing to /tmp is insecure; use GLib.get_tmp_dir()
[PASS] metadata/required-fields               All required fields present
[FAIL] metadata/session-modes                 session-modes ["user"] is redundant and MUST be dropped
[WARN] metadata/shell-version-current         shell-version does not include GNOME 49
[PASS] lifecycle/enable-disable               enable() and disable() both defined
[WARN] lifecycle/file-monitor-cleanup         File monitor created but no .cancel() found
[WARN] resource-tracking/orphan-signal        lib/manager.js:9 — this._handlerId not cleaned up in destroy()
[PASS] quality/code-provenance                provenance-score=1; signals=[consistent-naming-style]
...

----------------------------------------------------------------
  Results: 196 checks — 167 passed, 3 failed, 4 warnings, 22 skipped
----------------------------------------------------------------
```

### Rules Format

Pattern rules are declared in [`rules/patterns.yaml`](rules/patterns.yaml) — adding a new check is 4 lines of YAML:

```yaml
- id: R-DEPR-08
  pattern: "\\bnew\\s+Lang\\.Class\\b"
  scope: ["*.js"]
  severity: blocking
  message: "Lang.Class is deprecated; use standard ES6 classes"
  category: deprecated
```

## Research Background

The rules and checks in this project are grounded in analysis of real EGO review behavior — not just the official documentation.

- Analyzed **9 real EGO reviews** on extensions.gnome.org by active reviewers
- Identified **26 real-world findings** including **8 unwritten rules** not in official docs
- Cross-referenced [gjs.guide](https://gjs.guide) guidelines (109 extracted requirements) with actual reviewer behavior
- Traced GNOME Shell guideline evolution across versions 44–50 via GitLab history
- Reverse-engineered patterns from 5 popular approved extensions
- Regression-tested all checks against a real 11-module extension as baseline

Key unwritten rules discovered:
1. No "GNOME" in UUID, extension name, or schema ID (trademark)
2. `shell-version` must be major-only for GNOME 40+ (no minor versions like "45.1")
3. D-Bus interfaces must be unexported in `disable()`
4. `destroy()` must be followed by `null` assignment
5. No compiled schemas in package for GNOME 45+
6. Timeout IDs must be removed before reassignment
7. Subprocesses must have cancellation path in `disable()`
8. No `convenience.js` patterns

Full research: [docs/RESEARCH-SUMMARY.md](docs/RESEARCH-SUMMARY.md) | Detailed findings: [docs/research/](docs/research/)

## Optional: Claude Code Integration

This project is also a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin that provides AI-assisted review skills. These are **optional** — ego-lint works standalone without them.

| Skill | Description |
|-------|-------------|
| `ego-review` | Multi-phase code review applying 6 semantic checklists (lifecycle, security, code quality, AI slop, licensing, accessibility) |
| `ego-simulate` | Predicts reviewer verdict using rejection taxonomy and reviewer persona model |
| `ego-scaffold` | Generates EGO-compliant extension boilerplate from templates |
| `ego-submit` | Full pipeline: lint → review → package validation → readiness report |

### Installation

```bash
claude plugins add github:ZviBaratz/gnome-extension-reviewer
```

### AI Transparency

ego-lint is **fully deterministic** — bash and python only, no AI calls. The four skills above (`ego-review`, `ego-simulate`, `ego-scaffold`, `ego-submit`) use Claude to read and analyze extension source code via Anthropic's API.

## Known Limitations

- **Does not guarantee EGO approval** — use as guidance, not certification
- Rules are based primarily on JustPerfection's review patterns; other reviewers may have different preferences
- Some checks are heuristic (AI slop detection, code quality scoring) and may produce false positives
- Per-line `_async()` cancellable check is a heuristic — some `null` cancellable calls are valid
- Three known gaps remain: polkit action ID validation, schema filename validation, module-scope mutable state detection
- Full gap list: [docs/research/gap-analysis.md](docs/research/gap-analysis.md)

## How This Was Built

This tool was built using [Claude Code](https://docs.anthropic.com/en/docs/claude-code). The research — Discourse mining, guideline analysis, gold standard extension review — was AI-assisted. The rules and checklists were validated against real rejection data and regression-tested against a real extension. The AI slop detection rules exist precisely because the author understands how LLMs generate GNOME extension code — and where they get it wrong.

## Requirements

- **Required**: bash, python3
- **Optional**: npm/node (ESLint checks), glib-compile-schemas (schema validation), zipinfo/unzip (package checks)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding rules, reporting false positives, and the rule lifecycle.

## License

[GPL-2.0-or-later](LICENSE)
