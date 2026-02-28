# Internal Development Artifacts

Development history and analysis artifacts. These are kept for transparency but are not part of the project's external documentation.

## Field Tests

Run the full ego-submit pipeline against real extensions to surface false positives, coverage gaps, and calibration issues. See `field-test-template.md` for the process.

| Extension | Date | ego-lint FAILs (before→after) | ego-simulate Score | Key Fixes |
|-----------|------|-------------------------------|-------------------|-----------|
| [Clipboard Indicator](field-test-clipboard-indicator.md) | 2026-02-28 | 27→1 | 10 (threshold) | R-WEB version gating, license variants, uuid-matches-dir severity |

### Cumulative Calibration Lessons

Patterns discovered across field tests — encode here so future rules avoid repeating mistakes:

1. **GJS polyfills shift rule applicability**: When GJS adopts a browser API (e.g., `setTimeout` in GNOME 45), any rule flagging that API needs `max-version` gating. Audit all R-WEB rules when a new GNOME version adds polyfills.
2. **Cloned repos break directory-name checks**: Any check comparing directory name to UUID must be advisory, not blocking — developers clone repos with repo names, not UUIDs.
3. **License file extensions vary**: Real extensions use `.rst`, `.md`, `.txt` — not just bare `LICENSE`/`COPYING`.
4. **Fixture gotcha — "GNOME" in names**: The trademark check catches "gnome" in UUIDs and names. Use abbreviations like `g45` in fixture identifiers.

## Other Artifacts

- `false-positive-analysis-v0.1.0.md` — False positives found and fixed in v0.1.0 (all resolved)
- `improvements-v0.2.0.md` — Post-fix analysis and improvement suggestions from v0.2.0 cycle
