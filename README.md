# gnome-extension-reviewer

Automated pre-submission checks for GNOME Shell extensions, built from analysis of real EGO review decisions. ego-lint catches the mechanical issues that cause the most common rejections — so extensions arrive cleaner and reviewers spend less time on round-trips.

ego-lint is fully deterministic: bash + python + YAML rules. No AI at runtime, no network access, no dependencies beyond coreutils.

### For EGO Reviewers

This tool encodes the mechanical checks you already do by hand — import segregation, lifecycle symmetry, metadata validation, resource cleanup — into automated, reproducible rules. The rules are grounded in [real EGO review analysis](docs/research/) and designed to be co-owned: adding a new check is [4 lines of YAML](CONTRIBUTING.md). You are invited to shape the rules, adjust severity, and add checks for rejection patterns you see often.

## Quick Start

```bash
git clone https://github.com/ZviBaratz/gnome-extension-reviewer.git
cd gnome-extension-reviewer
./ego-lint /path/to/your-extension@username
```

Exit code 0 = no blocking issues. Exit code 1 = blocking issues that will likely cause rejection.

Run `./ego-lint --help` for the full check list and options.

Try it on a bundled test fixture:

    ./ego-lint tests/fixtures/lifecycle-imbalance@test --verbose

## How This Helps the Review Queue

ego-lint automates the mechanical checks that cause the most common rejections. When developers run it before submitting, it catches issues that would otherwise require reviewer round-trips:

- **Transitive import analysis** — BFS from `prefs.js` through relative imports to catch indirect Shell runtime dependencies (`gi://St`, `gi://Clutter`, etc.)
- **Cross-file resource tracking** — builds a resource graph (signals, timeouts, widgets, D-Bus, file monitors, GSettings) and detects orphans that aren't cleaned up
- **AI pattern detection** — code provenance scoring, try-catch density, impossible state guards, `typeof super.method` checks, and 40+ other heuristic signals for AI-generated code (patterns identified as common in AI-generated submissions per the [December 2025 GNOME blog post](https://blogs.gnome.org/shell-dev/2025/12/18/extensions-and-ai/))
- **Version-gated rules** — GNOME 44–50 migration rules that only fire when the extension's declared `shell-version` includes the relevant version

ego-lint does **not**:

- Make approval/rejection decisions
- Use AI inference or network access at runtime
- Check logic correctness or functionality
- Replace human review judgment

**CI integration**: Pure bash + python, exits 0/1, no network access, no dependencies beyond coreutils. Tested against 142 fixtures with 373 assertions. See [docs/ci-integration.md](docs/ci-integration.md) for GitHub Actions and GitLab CI examples.

## How This Was Built

- **Claude Code wrote the code** — scripts, rules, tests, and docs were produced under human direction using [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (Anthropic's AI coding tool). Every design decision was human-reviewed. The AI slop detection rules are based on patterns observed in real EGO rejections of AI-generated submissions.
- **Research was AI-assisted** — Discourse mining, guideline extraction, cross-source synthesis, and gap analysis were performed with Claude Code and verified against real EGO reviews on extensions.gnome.org, [gjs.guide](https://gjs.guide) requirements, and GNOME Shell GitLab history. Regression-tested against a real 11-module extension as baseline.
- **ego-lint itself is AI-free** — The output artifact is deterministic bash + python + YAML. No API calls. No network access. No model inference. AI was the development tool, not the runtime tool.

## What Gets Checked

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

Of the 113 pattern rules, 64 are blocking (FAIL) and 49 are advisory (WARN). Structural checks add further findings. See [`rules/patterns.yaml`](rules/patterns.yaml) for the full list with rationale.

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

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide, including a 5-minute workflow for reviewers.

## Research Background

The rules and checks are grounded in analysis of real EGO review behavior — not just the official documentation.

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

## Known Limitations

- **Does not guarantee EGO approval** — use as guidance, not certification
- Rules are based primarily on active EGO reviewer patterns; individual reviewers may have different preferences
- Some checks are heuristic (AI slop detection, code quality scoring) and may produce false positives
- Per-line `_async()` cancellable check is a heuristic — some `null` cancellable calls are valid
- Full gap list: [docs/research/gap-analysis.md](docs/research/gap-analysis.md)

## Reporting Issues

Found a false positive? Rule missing a common rejection reason? [Open an issue](https://github.com/ZviBaratz/gnome-extension-reviewer/issues) with the rule ID and a code sample. False positives in blocking rules are treated as high priority.

## Advanced: Claude Code Plugin (Optional)

ego-lint is the primary offering — it works standalone without Claude Code or any AI. The skills below are experimental extras for developers who use [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

| Skill | Description |
|-------|-------------|
| `ego-review` | Multi-phase code review applying 6 semantic checklists (lifecycle, security, code quality, AI slop, licensing, accessibility) |
| `ego-simulate` | Estimates review readiness using rejection taxonomy and published review criteria |
| `ego-scaffold` | Generates EGO-compliant extension boilerplate from templates |
| `ego-submit` | Full pipeline: lint → review → package validation → readiness report |

```bash
claude plugins add github:ZviBaratz/gnome-extension-reviewer
```

The four skills above use Claude to analyze extension source code via Anthropic's API. ego-lint itself makes no API calls — it's the same deterministic tool whether or not you use the plugin.

## Community

This project is looking for community co-maintainers among EGO reviewers. If you'd like to help shape the rules — add checks for rejection patterns you see often, adjust severity, or improve heuristics — open an issue or PR. See [GOVERNANCE.md](GOVERNANCE.md) for how rule decisions are made.

### Help Wanted

Self-contained improvements where reviewer expertise would be especially valuable:

- **Polkit action ID validation** — verify `.policy` file exists with `org.gnome.shell.extensions.*` ID when `pkexec` is used
- **Schema filename validation** — ensure `.gschema.xml` filename matches the schema ID inside
- **Module-scope mutable state** — detect `Map`/`Set` at module level (mutable state outside `enable()`/`disable()`)
- **New rejection patterns** — if you see a common rejection reason not covered by ego-lint, [open an issue](https://github.com/ZviBaratz/gnome-extension-reviewer/issues) with the pattern

## Roadmap

- [ ] Polkit action ID validation (verify `.policy` file when `pkexec` is used)
- [ ] Schema filename validation (ensure `.gschema.xml` filename matches schema ID)
- [ ] Module-scope mutable state detection (`Map`/`Set` at module level)
- [ ] Per-extension configuration (`.ego-lint.yml` for rule overrides)

Full gap list: [docs/research/gap-analysis.md](docs/research/gap-analysis.md)

## Author

Built by [Zvi Baratz](https://github.com/ZviBaratz), author of [hara-hachi-bu](https://github.com/ZviBaratz/hara-hachi-bu) (a GNOME Shell extension for power management, submitted to EGO). Motivated by review round-trip friction — the mechanical checks that delay approval shouldn't require human time on either side. Built entirely with [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Requirements

- **Required**: bash, python3
- **Optional**: npm/node (ESLint checks), glib-compile-schemas (schema validation), zipinfo/unzip (package checks)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding rules, reporting false positives, and the rule lifecycle.

## License

[GPL-2.0-or-later](LICENSE)
