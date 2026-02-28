# Changelog

## v0.1.0 — Initial Release

### What's Included

- **113 pattern rules** in `rules/patterns.yaml` covering web APIs, deprecated APIs, security, import segregation, AI slop detection, GNOME 44–50 migration, and more
- **13 structural check scripts** (Python/bash) for metadata validation, lifecycle symmetry, resource graph construction, async safety, GObject patterns, preferences validation, schema checks, and package validation
- **Cross-file resource tracking** — builds a resource graph (signals, timeouts, widgets, D-Bus, file monitors, GSettings) and detects orphaned resources
- **Version-gated rules** — GNOME 44–50 migration rules that only fire when the extension's declared `shell-version` includes the relevant version
- **Contributor tooling** — `scripts/new-rule.sh` for scaffolding rules, `scripts/validate-fixture.sh` for fixture validation, `scripts/validate-rule.sh` for rule testing
- **142 test fixtures** with 372 assertions
- **CI integration** — GitHub Actions and GitLab CI examples in `docs/ci-integration.md`

### Research Basis

Rules are grounded in analysis of 9 real EGO reviews, 109 extracted requirements from gjs.guide, GNOME Shell GitLab guideline evolution across versions 44–50, and reverse-engineered patterns from 5 popular approved extensions. 8 unwritten reviewer rules were identified and encoded. Full research: [docs/research/](docs/research/).

### Known Limitations

- Polkit action ID validation not yet implemented (if `pkexec` used, `.policy` file not verified)
- Schema filename validation partial (warns but doesn't block on filename mismatch)
- Module-scope mutable state detection not yet implemented (`Map`/`Set` at module level)
- Full gap list: [docs/research/gap-analysis.md](docs/research/gap-analysis.md)
