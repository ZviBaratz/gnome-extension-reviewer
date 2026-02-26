# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin for GNOME Shell extension EGO (extensions.gnome.org) review compliance. It provides five skills (`ego-lint`, `ego-review`, `ego-scaffold`, `ego-simulate`, `ego-submit`). This is **not** a GNOME extension itself — it's a set of tools that validate GNOME extensions against EGO submission requirements. Load it with `claude --plugin-dir <path-to-this-repo>`.

## Testing

```bash
bash tests/run-tests.sh
```

There is no separate "run single test" command — the test runner runs ego-lint against each fixture in `tests/fixtures/` and asserts on output patterns and exit codes. To test a specific fixture in isolation:

```bash
bash skills/ego-lint/scripts/ego-lint.sh tests/fixtures/<fixture-name>
```

## Architecture

### Plugin structure

- `.claude-plugin/plugin.json` — Plugin manifest (minimal: `name`, `description`, `version`)
- `skills/` — Five skills, each with a `SKILL.md` (skill definition + instructions for Claude) and supporting files. Auto-discovered by Claude Code.

### Skill hierarchy

`ego-submit` is the top-level orchestrator: it invokes `ego-lint` (automated checks) then `ego-review` (manual code review) then validates packaging. `ego-simulate` is an optional pre-flight that simulates the reviewer's triage process. `ego-scaffold` is independent (creates new extensions).

### ego-lint internals

`ego-lint.sh` is the main orchestrator. It uses a three-tier rule system (pattern → structural → semantic) and delegates to sub-scripts via `run_subscript`:

- `rules/patterns.yaml` — Tier 1 pattern rules (106 regex-based, declarative rules)
- `apply-patterns.py` — Tier 1 pattern engine (inline YAML parser, no PyYAML dependency)
- `check-quality.py` — Tier 2 heuristic AI slop detection (try-catch density, impossible states, pendulum patterns, empty catches, _destroyed density, mock detection, constructor resources, run_dispose comment, clipboard disclosure, network disclosure, excessive null checks, repeated getSettings)
- `check-metadata.py` — JSON validity, required fields, UUID format/match, shell-version, session-modes, settings-schema, version-name, donations
- `check-init.py` — Init-time Shell modification, GObject constructor detection (all GI namespaces), Gio._promisify placement
- `check-lifecycle.py` — enable/disable symmetry, signal cleanup, timeout removal verification, InjectionManager, lock screen signals, selective disable detection, unlock-dialog comment, clipboard+keybinding cross-ref, prototype override detection, pkexec target validation, Soup.Session abort, D-Bus export/unexport, timeout reassignment, subprocess cancellation, clipboard+network cross-ref
- `check-prefs.py` — Preferences file validation (ExtensionPreferences base class, GTK4/Adwaita patterns, memory leak detection)
- `check-gobject.py` — GObject.registerClass patterns and GTypeName validation
- `check-async.py` — Async/await safety (_destroyed guards, cancellable usage, per-line _async() cancellable detection)
- `check-css.py` — Stylesheet validation, shell class override detection
- `check-resources.py` — Cross-file resource orphan detection (reads resource graph)
- `build-resource-graph.py` — Cross-file resource graph builder (signals, timeouts, widgets, D-Bus, file monitors, GSettings)
- `check-imports.sh` — Import segregation (no GTK in extension.js, no Shell libs in prefs.js, transitive BFS from prefs.js, resource path case validation)
- `check-schema.sh` — GSettings schema ID/path validation, glib-compile-schemas dry-run
- `check-package.sh` — Zip contents validation (forbidden files, required files, compiled schemas for GNOME 45+)

Sub-scripts output pipe-delimited lines (`STATUS|check-name|detail`) which `ego-lint.sh` parses and reformats.

Additional tooling:
- `rules/README.md` — 5-minute contributor guide for adding pattern rules
- `scripts/validate-rule.sh` — Helper for rule authors to test individual rules against fixtures

### Three-tier rule system

- **Tier 1 (patterns.yaml)**: 106 regex rules in YAML, processed by `apply-patterns.py`. Covers web APIs, deprecated APIs, security, logging, import segregation, AI slop signals, subprocess safety, i18n, GSettings bind flags, GNOME 44-50 migration. Add new rules by editing `rules/patterns.yaml`. Supports version-gating via `min-version`/`max-version` fields.
- **Tier 2 (scripts)**: 13 structural heuristic check scripts in Python/bash. `check-quality.py` (AI slop heuristics), `check-init.py` (init-time safety), `check-lifecycle.py` (enable/disable symmetry + timeout verification), `check-resources.py` + `build-resource-graph.py` (cross-file resource tracking), plus metadata, prefs, GObject, async, CSS, imports, schema, and package checks. `ego-lint.sh` also has an inline minified JS check.
- **Tier 3 (checklists)**: 6 semantic review checklists in `skills/ego-review/references/`: lifecycle, security, code-quality (with 10 additional quality items), ai-slop (46-item scoring model), licensing, accessibility (7 items). Applied by Claude during `ego-review` phases.

### ego-review internals

Purely prompt-driven (no scripts). `SKILL.md` defines a multi-phase review process (Phase 0: automated baseline, 1: discovery, 1b: licensing, 2: lifecycle audit with resource graph, 3: signal/resource audit, 4: security, 4b: accessibility, 5: code quality, 5a: AI pattern analysis). Uses 6 checklists in `references/` (lifecycle, security, code-quality, ai-slop, licensing, accessibility). Claude reads extension source code and applies the checklists.

### ego-scaffold internals

Prompt-driven with templates in `assets/` using `${PLACEHOLDER}` syntax. Claude reads templates, substitutes variables, and writes the scaffolded extension.

## Conventions

### Check output format

All automated checks use: `STATUS|check-name|detail` where STATUS is PASS/FAIL/WARN/SKIP.

### Adding a new lint rule

Choose the appropriate tier:

- **Tier 1 (regex pattern)**: Add an entry to `rules/patterns.yaml` — no code changes needed
- **Tier 2 (structural heuristic)**: Add logic to `check-quality.py` or a new sub-script in `skills/ego-lint/scripts/`
- **Tier 3 (semantic checklist)**: Add items to checklists in `skills/ego-review/references/`

Then for Tier 1 and 2:

1. Document it in `skills/ego-lint/references/rules-reference.md` using the `R-XXXX-NN` format with severity, rationale, and fix
2. Add a test fixture in `tests/fixtures/` with minimal files to trigger the check
3. Add assertions to `tests/run-tests.sh`

### Commit messages

Conventional commits, lowercase, scoped to skill name when applicable:
```
feat(ego-lint): add check for unscoped CSS classes
fix(ego-scaffold): correct schema path in template
test(ego-lint): add fixture for deprecated ByteArray usage
```

## Requirements

- **Required**: bash, python3
- **Optional**: npm/node (ESLint checks), glib-compile-schemas (schema validation), zipinfo/unzip (package checks)
