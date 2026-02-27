# Architecture

## Three-Tier Rule System

```
                          ego-lint.sh (orchestrator)
                                  |
                 +----------------+----------------+
                 |                |                |
           Tier 1: Regex    Tier 2: Scripts   Tier 3: Checklists
                 |                |                |
         patterns.yaml      check-*.py/sh     ego-review refs/
              |                   |                |
       apply-patterns.py    13 sub-scripts    6 checklists
       (114 rules, YAML)    (structural)      (semantic, AI)
                 |                |                |
                 +--- PASS/FAIL/WARN/SKIP --------+
                      (pipe-delimited output)
```

## How ego-lint.sh Orchestrates

`ego-lint.sh` is a bash script that runs all automated checks (Tiers 1 and 2)
against an extension directory. It first invokes `run_pattern_rules()`, which
calls `apply-patterns.py` with `rules/patterns.yaml` to evaluate 114 regex
rules against every JS file. Then it calls `run_subscript()` for each of the 13
Tier 2 scripts -- Python and bash programs that perform structural analysis
(metadata validation, lifecycle symmetry, resource tracking, etc.). Each
sub-script is passed the extension directory and runs independently.

Every sub-script outputs pipe-delimited lines in the format
`STATUS|check-name|detail`, where STATUS is one of PASS, FAIL, WARN, or SKIP.
`ego-lint.sh` parses these lines, counts results by status, and reformats them
into a fixed-width report. Exit code 0 means no blocking issues (no FAILs);
exit code 1 means at least one FAIL was found. The `--verbose` flag adds
grouped output and a verdict summary.

## When to Use Each Tier

**Tier 1** is for rules expressible as a single regex per file. Add a YAML entry
to `rules/patterns.yaml` -- no code changes needed. Supports version-gating
(`min-version`/`max-version`) and a fix suggestion field. Best for: deprecated
API usage, banned imports, security anti-patterns, simple code-smell detection.

**Tier 2** is for checks that need multi-line analysis, cross-file reasoning, or
structured data (JSON, XML). Examples: metadata.json field validation,
enable/disable symmetry detection, resource graph construction. Each check is a
standalone script in `skills/ego-lint/scripts/`.

**Tier 3** is for nuanced judgment that requires reading and understanding code
intent. The 6 checklists in `skills/ego-review/references/` (lifecycle,
security, code-quality, ai-slop, licensing, accessibility) are applied by Claude
during `ego-review`. This tier catches things regex and heuristics cannot --
logical errors, incomplete cleanup, architectural issues.

## Resource Graph

`build-resource-graph.py` scans all JS files and builds a JSON graph of resource
lifecycle events: signal connections, timeout registrations, widget creation,
D-Bus exports, file monitors, and GSettings bindings. Each entry records the
resource type, creation site (file + line), and any corresponding destroy site.
`check-resources.py` then reads this graph and reports orphaned resources --
creates without matching destroys -- as FAIL or WARN depending on resource type.

## File Map

```
ego-lint                        CLI wrapper (top-level entry point)
rules/
  patterns.yaml                 Tier 1: 114 regex rules (18 sections)
skills/
  ego-lint/
    SKILL.md                    Skill definition for Claude
    scripts/
      ego-lint.sh               Main orchestrator
      apply-patterns.py         Tier 1 pattern engine
      build-resource-graph.py   Resource graph builder
      check-resources.py        Resource orphan detector
      check-metadata.py         metadata.json validation
      check-lifecycle.py        enable/disable symmetry
      check-init.py             Init-time safety
      check-quality.py          AI slop / code provenance
      check-async.py            Async/await safety
      check-gobject.py          GObject.registerClass
      check-prefs.py            Preferences validation
      check-css.py              Stylesheet checks
      check-imports.sh          Import segregation
      check-schema.sh           GSettings schema validation
      check-package.sh          Zip contents validation
    references/
      rules-reference.md        Rule ID catalog (R-XXXX-NN)
  ego-review/
    SKILL.md                    Multi-phase review process
    references/                 Tier 3: 6 semantic checklists
  ego-scaffold/                 Extension scaffolding templates
  ego-simulate/                 Reviewer simulation
  ego-submit/                   Submission orchestrator
tests/
  run-tests.sh                  Test runner
  assertions/                   Assertion files (sourced by runner)
  fixtures/                     138 test fixtures
docs/
  ci-integration.md             GitHub Actions / GitLab CI examples
  ARCHITECTURE.md               This file
```
