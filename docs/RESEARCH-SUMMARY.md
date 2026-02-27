# Research Summary

This document summarizes the research behind gnome-extension-reviewer's rules and checks. For full details, see the individual research documents in [docs/research/](research/).

## Methodology

| Source | Approach | Yield |
|--------|----------|-------|
| [gjs.guide](https://gjs.guide) review guidelines | Deep-read, requirement extraction | 109 requirements |
| EGO reviews on extensions.gnome.org | Analysis of 9 real EGO reviews by active reviewers | 26 findings, 8 unwritten rules |
| GNOME Shell GitLab | Guideline evolution tracking across GNOME 44–50 | Version-gated rule parameters |
| Popular approved extensions | Reverse-engineering of 5 extensions | 15 cross-extension patterns |
| hara-hachi-bu (real 11-module extension) | Regression baseline testing | 4 false positives found and fixed |

## Top Rejection Reasons (from real reviews)

1. **Lifecycle cleanup** — `destroy()` without `null` assignment, missing signal disconnection, timeouts not removed in `disable()`
2. **Import segregation** — GTK imports in extension.js, Shell runtime imports in prefs.js (including transitive dependencies)
3. **Shell-version format** — Minor versions (e.g., "45.1") rejected for GNOME 40+; must be major-only
4. **AI-generated patterns** — Unnecessary try-catch wrapping, `typeof super.method` checks, dead code after throw, TypeScript-style JSDoc
5. **Development artifacts** — `env.d.ts`, `jsconfig.json`, `.old`/`.bak` files included in submission
6. **Metadata errors** — Redundant `session-modes: ["user"]`, missing `url` field, UUID without `@`
7. **Deprecated APIs** — `ExtensionUtils`, `imports.*` syntax, `Lang.Class`, `Mainloop`
8. **Missing GPL license** — No LICENSE/COPYING file, or non-GPL-compatible license

## Unwritten Rules

These rules are consistently enforced by reviewers but not documented in official guidelines:

1. **GNOME trademark** — No "GNOME" in UUID, extension name, or schema ID
2. **Major-only shell-version** — `"shell-version": ["48"]`, not `"48.1"` (GNOME 40+)
3. **D-Bus unexport** — `export_action_group()`/`export_menu_model()` must have matching `unexport` in `disable()`
4. **destroy-then-null** — `this._widget.destroy(); this._widget = null;` — reviewers look for both
5. **No compiled schemas** — `gschemas.compiled` forbidden in zip for GNOME 45+ (auto-compiled at install)
6. **Timeout removal before reassignment** — `this._timeoutId = GLib.timeout_add(...)` without prior `Source.remove()` leaks the old timeout
7. **Subprocess cancellation** — Long-running subprocesses must have a cancellation path in `disable()`
8. **No convenience.js** — Legacy pattern from pre-ESM era; use Extension base class methods instead

## Coverage Summary

| Tier | Type | Count | Description |
|------|------|-------|-------------|
| 1 | Pattern rules (YAML) | 114 | Regex-based, declarative, version-gated |
| 2 | Structural scripts | 13 | Python/bash heuristic analysis |
| 3 | Semantic checklists | 6 | Applied by Claude during ego-review |

### Pattern rule categories
Web APIs (12), deprecated APIs (8), security (23), AI slop (18), version compatibility (GNOME 44–50), i18n (2), code quality (11), preferences (3), imports (1), logging (2)

### Structural script coverage
Metadata validation, code quality heuristics, init-time safety, lifecycle symmetry, preferences validation, GObject patterns, async safety, CSS validation, cross-file resource tracking, import segregation, schema validation, package validation

### Known gaps (3 remaining)
1. Polkit action ID validation (verify `.policy` file if `pkexec` used)
2. Schema filename validation (`.gschema.xml` filename should match schema ID)
3. Module-scope mutable state detection (Map/Set at module level)

## Cross-Source Validation

Seven findings were independently confirmed across multiple research sources:

| Finding | Sources |
|---------|---------|
| destroy-then-null pattern | gjs.guide, Discourse reviews, gold standard extensions |
| Import segregation strictness | gjs.guide, real rejections, GitLab guidelines |
| Shell-version major-only | Discourse reviews, EGO metadata validation, GitLab history |
| GNOME trademark in UUID | Discourse reviews, EGO submission form, gold standards |
| Compiled schemas prohibition (45+) | gjs.guide, Discourse reviews, GNOME Shell changelog |
| AI slop try-catch wrapping | Discourse reviews, gold standard comparison, code quality research |
| Convenience.js prohibition | Discourse reviews, gjs.guide migration guide, gold standards |

## Research Documents

- [`phase1-guidelines-deep-read.md`](research/phase1-guidelines-deep-read.md) — gjs.guide requirement extraction (109 requirements)
- [`phase1-discourse-findings.md`](research/phase1-discourse-findings.md) — Real EGO review analysis (26 findings)
- [`phase1-gitlab-guideline-evolution.md`](research/phase1-gitlab-guideline-evolution.md) — Guideline version tracking
- [`phase1-gold-standards.md`](research/phase1-gold-standards.md) — Popular extension analysis
- [`ego-review-guidelines-research.md`](research/ego-review-guidelines-research.md) — Initial guidelines research
- [`gap-analysis.md`](research/gap-analysis.md) — Current coverage gaps
