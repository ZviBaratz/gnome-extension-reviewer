# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin for GNOME Shell extension EGO (extensions.gnome.org) review compliance. It provides six skills (`ego-lint`, `ego-review`, `ego-scaffold`, `ego-simulate`, `ego-submit`, `ego-field-test`). This is **not** a GNOME extension itself — it's a set of tools that validate GNOME extensions against EGO submission requirements. Load it with `claude --plugin-dir <path-to-this-repo>`.

## Running ego-lint

```bash
./ego-lint /path/to/extension@username        # FAIL + WARN + report (default)
./ego-lint --show all /path/to/extension      # show all severity levels
./ego-lint --no-report /path/to/extension     # suppress grouped report
./ego-lint --help                              # check categories, exit codes
```

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

- `ego-lint` — Top-level CLI wrapper (runs `skills/ego-lint/scripts/ego-lint.sh`)
- `.claude-plugin/plugin.json` — Plugin manifest (minimal: `name`, `description`, `version`)
- `skills/` — Five skills, each with a `SKILL.md` (skill definition + instructions for Claude) and supporting files. Auto-discovered by Claude Code.
- `docs/ci-integration.md` — GitHub Actions and GitLab CI examples

### Key reference files

- `skills/ego-simulate/references/reviewer-persona.md` — Reviewer persona for simulation
- `skills/ego-simulate/references/rejection-taxonomy.md` — 23-reason rejection taxonomy (weight-based)
- `skills/ego-lint/references/rules-reference.md` — Canonical rule docs (R-XXXX-NN format)
- `docs/research/` — Requirements reference, gap analysis, approved patterns, real review findings
- `docs/internal/` — Field test reports, false-positive analysis, pipeline reviews
- `tests/fixtures/regressions/` — Regression test fixtures

### Skill hierarchy

`ego-submit` is the top-level orchestrator: it invokes `ego-lint` (automated checks) then `ego-review` (manual code review) then validates packaging. `ego-simulate` is an optional pre-flight that simulates the reviewer's triage process using a 23-reason rejection taxonomy with weight-based scoring; it integrates ego-lint FAIL results into its verdict. `ego-scaffold` is independent (creates new extensions).

### ego-lint internals

`ego-lint.sh` is the main orchestrator. It uses a three-tier rule system (pattern → structural → semantic) and delegates to sub-scripts via `run_subscript`:

- `rules/patterns.yaml` — Tier 1 pattern rules (124 regex-based, declarative rules). Note: at project root, not under `skills/ego-lint/`
- `apply-patterns.py` — Tier 1 pattern engine (inline YAML parser, no PyYAML dependency). Supports `guard-pattern` + `guard-window` (sliding `deque` lookback) + `guard-window-forward` (forward peeking), `replacement-pattern`, `exclude-dirs`, version-gating, `fix-min-version` (suppresses fix text when extension min shell-version is below threshold), `skip-comments` (skips matches inside `//` and `/* */` comments)
- `check-quality.py` — Tier 2 heuristic AI slop detection (try-catch density, impossible states, pendulum patterns, empty catches, _destroyed density, mock detection, constructor resources, run_dispose comment, clipboard disclosure, network disclosure, excessive null checks, repeated getSettings, obfuscated names, mixed indentation, excessive logging, code provenance)
- `check-metadata.py` — JSON validity, required fields, UUID format/match, shell-version (with VALID_GNOME_VERSIONS allowlist), session-modes, settings-schema, version-name, donations, gettext-domain consistency
- `check-init.py` — Init-time Shell modification (module-scope + extension.js constructors only; arrow function definitions exempt), GObject constructor detection (extension.js only; all GI namespaces, GObject.registerClass exempt, GLib value types exempt), Gio._promisify placement
- `check-lifecycle.py` — enable/disable symmetry, signal cleanup (connectSmart/SignalTracker-aware), timeout removal verification, InjectionManager, lock screen signals, selective disable detection, unlock-dialog comment, clipboard+keybinding cross-ref, prototype override detection, pkexec target validation, Soup.Session abort, D-Bus export/unexport, bus name own/unown lifecycle, timeout reassignment, subprocess cancellation, clipboard+network cross-ref, widget lifecycle, D-Bus connectSignal leak detection, settings cleanup, module-scope mutable state detection, module-scope prototype mutation detection
- `check-prefs.py` — Preferences file validation (ExtensionPreferences base class, GTK4/Adwaita patterns, memory leak detection, supports `src/` layout)
- `check-gobject.py` — GObject.registerClass patterns and GTypeName validation
- `check-async.py` — Async/await safety (_destroyed guards, cancellable usage, per-line _async() cancellable detection)
- `check-css.py` — Stylesheet validation, shell class override detection (supports `src/` layout)
- `check-resources.py` — Cross-file resource orphan detection (reads resource graph)
- `build-resource-graph.py` — Cross-file resource graph builder (signals, timeouts, widgets, D-Bus, file monitors, GSettings). Parent-child cleanup recognizes both `.destroy()` and `.disable()` calls.
- `check-imports.sh` — Import segregation (no GTK in extension.js via BFS from extension.js, no Shell libs in prefs.js via BFS from prefs.js, resource path case validation)
- `check-schema.sh` — GSettings schema ID/path validation, GNOME trademark in schema IDs (case-insensitive prefix strip), glib-compile-schemas dry-run
- `check-package.sh` — Zip contents validation (forbidden files, required files, compiled schemas for GNOME 45+)

Sub-scripts output pipe-delimited lines (`STATUS|check-name|detail`) which `ego-lint.sh` parses and reformats.

Additional tooling:
- `rules/README.md` — 5-minute contributor guide for adding pattern rules
- `scripts/validate-rule.sh` — Helper for rule authors to test individual rules against fixtures

### Three-tier rule system

- **Tier 1 (patterns.yaml)**: 124 regex rules in YAML, processed by `apply-patterns.py`. Covers web APIs, deprecated APIs, security (telemetry, curl/gsettings spawn, base64), logging, import segregation, AI slop signals, subprocess safety, i18n, GSettings bind flags, GNOME 44-50 migration, code quality advisories. Add new rules by editing `rules/patterns.yaml`. Advanced fields: `min-version`/`max-version` (version-gating), `guard-pattern` + `guard-window` (line-level suppression with configurable lookback) + `guard-window-forward` (forward peeking), `replacement-pattern` (file-level suppression), `exclude-dirs`, `skip-comments` (comment-aware matching).
- **Tier 2 (scripts)**: 17 structural heuristic check scripts in Python/bash. `check-quality.py` (AI slop heuristics), `check-init.py` (init-time safety), `check-lifecycle.py` (enable/disable symmetry + timeout verification), `check-resources.py` + `build-resource-graph.py` (cross-file resource tracking), `check-disclosures.py` (clipboard/network disclosure), `check-polkit.py` (polkit policy validation), `check-schema-usage.py` (unused/undefined schema keys), `check-accessibility.py` (a11y checks), plus metadata, prefs, GObject, async, CSS, imports, schema, and package checks. `ego-lint.sh` also has an inline minified JS check, code metrics, and a provenance-gated post-filter that suppresses R-SLOP-01/02 JSDoc warnings when `quality/code-provenance` score >= 3.
- **Tier 3 (checklists)**: 6 semantic review checklists in `skills/ego-review/references/`: lifecycle, security, code-quality (with 10 additional quality items), ai-slop (46-item scoring model), licensing, accessibility (7 items). Applied by Claude during `ego-review` phases.

### ego-review internals

Purely prompt-driven (no scripts). `SKILL.md` defines a multi-phase review process (Phase 0: automated baseline, 1: discovery, 1b: licensing, 2: lifecycle audit with resource graph, 3: signal/resource audit, 4: security, 4b: accessibility, 5: code quality, 5a: AI pattern analysis). Uses 6 checklists in `references/` (lifecycle, security, code-quality, ai-slop, licensing, accessibility). Claude reads extension source code and applies the checklists.

### ego-scaffold internals

Prompt-driven with templates in `assets/` using `${PLACEHOLDER}` syntax. Claude reads templates, substitutes variables, and writes the scaffolded extension.

## Conventions

### Check output format

All automated checks use: `STATUS|check-name|detail` where STATUS is PASS/FAIL/WARN/SKIP.

### Severity changes

Upgrading advisory→blocking changes `[WARN]` to `[FAIL]` and exit code 0→1. Always grep for existing test assertions on the rule ID before changing severity. Changing `CURRENT_STABLE` in `ego-lint.sh` shifts version arithmetic — update fixtures that depend on version boundaries.

### Adding a new lint rule

Choose the appropriate tier:

- **Tier 1 (regex pattern)**: Add an entry to `rules/patterns.yaml` — no code changes needed
- **Tier 2 (structural heuristic)**: Add logic to `check-quality.py` or a new sub-script in `skills/ego-lint/scripts/`
- **Tier 3 (semantic checklist)**: Add items to checklists in `skills/ego-review/references/`

Then for Tier 1 and 2:

1. Document it in `skills/ego-lint/references/rules-reference.md` using the `R-XXXX-NN` format with severity, rationale, and fix
2. Add a test fixture in `tests/fixtures/` with minimal files to trigger the check
3. Add assertions to `tests/run-tests.sh`

### Test fixture conventions

- Directory name must exactly match the `uuid` in `metadata.json`
- UUID/name must not contain "gnome" (trademark check will FAIL)
- Include a `LICENSE` file (single line `SPDX-License-Identifier: GPL-2.0-or-later`) or the license check will WARN
- Avoid `.sh` files in fixtures (non-GJS script check flags them)
- See `rules/README.md` for required files, metadata template, and troubleshooting

### Commit messages

Conventional commits, lowercase, scoped to skill name when applicable:
```
feat(ego-lint): add check for unscoped CSS classes
fix(ego-scaffold): correct schema path in template
test(ego-lint): add fixture for deprecated ByteArray usage
```

### Known gotchas

- **Guard pattern comment gotcha**: Comments mentioning deprecated API (e.g., `// use Clutter.Color`) trigger the pattern but NOT the guard — use `skip-comments: true` for rules where comment FPs are common
- **Import graph BFS direction**: `check-imports.sh` uses BFS from extension.js/prefs.js (not glob) to find runtime-reachable files. Helper functions must be defined before both BFS blocks
- **`src/` layout fallback**: check-css.py, check-prefs.py, ego-lint.sh all check `src/` as fallback for extension.js, stylesheet.css, prefs.js
- **Schema trademark case-insensitive**: check-schema.sh lowercases schema ID before stripping `org.gnome.shell.extensions.` prefix
- **Obfuscation regex pitfalls**: `[a-z]\d+` catches unicode escapes (`\u2013`); `re.IGNORECASE` on guard patterns catches `console.debug` when matching `DEBUG`
- **Git history rewritten 2026-02-27**: `git filter-repo` removed internal files. All SHAs before that date are invalid

## Repository Workflow

- **Squash merge only** — merge commits and rebase merges are disabled. Every PR becomes a single commit on main with the PR title (conventional commit) and PR body as the commit message
- **Required status check**: `test` must pass before merging (enforced by `main-protection` ruleset). Admin can bypass for hotfixes
- **Auto-merge**: Enabled — can be activated per-PR to merge automatically when CI passes
- **Branch protection**: `main` is protected against deletion and force push via repository ruleset (not classic branch protection)
- **Labels**: `false-positive`, `new-rule`, `severity-change`, `ego-lint`, `ego-review`, `ego-simulate`, `ego-field-test`, `ego-scaffold`, `ego-submit` (plus GitHub defaults)

## Development Workflow

- **Issue first**: Create a GitHub issue describing the problem or improvement before starting work. Label with `false-positive`, `new-rule`, or `severity-change` as appropriate
- **Branch per issue**: Create a branch from `main` named `fix/<short-description>`, `feat/<short-description>`, or `docs/<short-description>`
- **One concern per PR**: Each PR should address a single logical concern (one fix, one feature, one doc update). Split multi-concern work into separate PRs
- **PR closes issue**: Include `Closes #N` in the PR description to auto-close the issue on merge
- **Tests before PR**: Run `bash tests/run-tests.sh` and verify all assertions pass before pushing

## Field Testing

Batch ego-lint runner for regression testing across 10 real-world GNOME extensions.

### Running field tests

```bash
bash scripts/field-test-runner.sh                    # lint all extensions
bash scripts/field-test-runner.sh --extension NAME   # lint single extension
bash scripts/field-test-runner.sh --update-baselines # save current as golden
bash scripts/field-test-runner.sh --no-fetch         # skip git clones, use cache
bash scripts/field-test-runner.sh --review --no-fetch          # lint + review all
bash scripts/field-test-runner.sh --review --review-exclude X  # review all except X
bash scripts/field-test-runner.sh --review-dry-run             # print prompts only
```

### Pipeline structure

- `field-tests/manifest.yaml` — Extension source manifest (local paths, GitHub repos)
- `field-tests/baselines/` — Golden JSON snapshots (committed)
- `field-tests/annotations/` — Per-extension finding classifications: tp, fp, borderline, expected (committed)
- `field-tests/history.jsonl` — Append-only trend data (committed)
- `field-tests/cache/` — Downloaded extensions (gitignored)
- `field-tests/results/` — Timestamped run output (gitignored), includes `.review.md` reports
- `field-tests/reports/` — Regression/synthesis reports (committed)
- `scripts/field-test-runner.sh` — Bash orchestrator (lint + optional review phase)
- `scripts/parse-manifest.py` — Manifest YAML → JSON (inline parser, no PyYAML)
- `scripts/parse-lint-results.py` — ego-lint stdout → structured JSON
- `scripts/diff-baselines.py` — Baseline comparison + annotation-aware filtering
- `scripts/review-prompt.md` — Review prompt template (incremental Write strategy)
- `scripts/hydrate-review-prompt.py` — Template hydration with lint/diff/annotation data
- `skills/ego-field-test/SKILL.md` — Claude Code skill for full pipeline (classification, synthesis, issue creation)

### Calibration cycle

1. Make a code change (guard pattern, threshold tweak, new rule)
2. Run `bash scripts/field-test-runner.sh --no-fetch` — see impact across all extensions
3. Classify new unannotated findings in `field-tests/annotations/`
4. If FPs found, create issues and fix
5. Run with `--update-baselines` to snapshot improved state

### Review phase

The `--review` flag runs headless `claude -p` sessions after lint. Each session uses `scripts/review-prompt.md` (hydrated with lint results, diff, and annotations). Key flags:

- `--review` — review all extensions; `--review-changed` — only changed ones
- `--review-exclude NAME` — skip specific extensions from review (repeatable); `--exclude` skips from both lint and review
- `--budget AMOUNT` — max USD per review session (default: 4.00)
- `--timeout SECONDS` — max seconds per review session (default: 900)
- `--parallel N` — max concurrent sessions (default: 3)
- `--review-dry-run` — write hydrated prompts without invoking claude

Reports are written incrementally (section-by-section) to survive budget exhaustion. Review findings use `review/` prefix in annotation files to distinguish from lint findings.

## Releasing

release-please automates versioning, CHANGELOG updates, git tags, and GitHub Releases:

- Conventional commit messages on `main` drive version bumps (`feat:` = patch pre-1.0, `feat!:` = minor pre-1.0)
- PR titles are validated in CI — must follow conventional commit format (e.g., `feat(ego-lint): add check`)
- To cut a release: merge the release-please PR that appears on GitHub after `feat:`/`fix:` commits land on `main`
- `release-please-config.json` defines changelog sections and syncs version to `.claude-plugin/plugin.json`
- `.release-please-manifest.json` tracks the current version

## Requirements

- **Required**: bash, python3
- **Optional**: npm/node (ESLint checks), glib-compile-schemas (schema validation), zipinfo/unzip (package checks)
