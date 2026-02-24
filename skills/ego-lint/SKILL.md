---
name: ego-lint
description: >-
  Run automated EGO (extensions.gnome.org) compliance checks on a GNOME Shell
  extension. Validates metadata.json, GSettings schema, import segregation,
  console.log usage, deprecated modules, web APIs, binary files, CSS scoping,
  ESLint with gnome config, and package contents. Use when checking extension
  code quality, preparing for EGO submission, or when linting, validation, or
  GNOME extension compliance is mentioned.
---

# ego-lint

Automated EGO compliance checker for GNOME Shell extensions.

## What It Checks

| Category | Checks | Severity |
|----------|--------|----------|
| Metadata | UUID format, required fields, shell-version, session-modes | FAIL/WARN |
| Schema | ID matches metadata, path format, compilation | FAIL |
| Imports | GTK in extension.js, Shell libs in prefs.js | FAIL |
| Logging | console.log() usage (console.debug is OK) | FAIL |
| Deprecated | Mainloop, Lang, ByteArray, ExtensionUtils, Tweener imports | FAIL |
| Web APIs | setTimeout, setInterval, fetch, XMLHttpRequest, DOM APIs, require() | FAIL |
| Pattern Rules | Additional checks from `rules/patterns.yaml` (web APIs, deprecated APIs, AI slop signals) | FAIL/WARN |
| Quality | Heuristic code quality checks (try-catch density, empty catches, mutable state) | WARN |
| Files | extension.js/metadata.json exist, LICENSE present | FAIL/WARN |
| CSS | Unscoped class names in stylesheet.css | WARN |
| ESLint | eslint-config-gnome violations | FAIL/WARN |
| Package | Forbidden files in zip, required files present | FAIL |

## How to Run

```bash
bash <path-to-this-skill>/scripts/ego-lint.sh [extension-directory]
```

If `extension-directory` is omitted, uses the current working directory.

The script path is relative to this skill's location. In practice, Claude will resolve the absolute path.

## Interpreting Results

Each check outputs one line:

- `[PASS]` — Check passed
- `[FAIL]` — Blocking issue that must be fixed before EGO submission
- `[WARN]` — Advisory issue that may cause reviewer questions
- `[SKIP]` — Check could not run (missing tool or not applicable)

The script exits with code 0 if no FAILs, 1 if any FAIL.

## Common Fixes

| Failure | Fix |
|---------|-----|
| `console.log` found | Replace with `console.debug()` for operational messages |
| GTK import in extension.js | Move GTK code to prefs.js |
| Shell import in prefs.js | Move Shell code to extension.js or lib/ |
| Deprecated Mainloop | Use `GLib.timeout_add()` / `GLib.Source.remove()` |
| setTimeout/setInterval | Use `GLib.timeout_add()` / `GLib.timeout_add_seconds()` |
| fetch() | Use `Soup.Session` or `Gio.File` for network/file I/O |
| UUID mismatch | Ensure metadata.json `uuid` matches directory name exactly |
| Missing shell-version 48 | Add `"48"` to the `shell-version` array |
| session-modes ["user"] | Remove the key entirely (it is the EGO default) |

## Check Tiers

### Tier 1: Pattern Rules

Additional lint rules are defined declaratively in `rules/patterns.yaml` and processed
by `scripts/apply-patterns.py`. Each pattern rule specifies a regex, the file globs to
match against, a severity level, and a human-readable message. This makes it easy to
add new checks without writing shell or Python code.

Pattern rules currently cover:
- **Extended Web API detection** — XMLHttpRequest, requestAnimationFrame, DOM APIs
  (`document.*`), `window` object usage, localStorage, and `require()` (Node.js)
- **Extended deprecated API detection** — `ExtensionUtils` (removed in GNOME 45+),
  `Tweener` (removed), and `imports.misc.convenience` (removed in GNOME 45+)
- **AI slop signals** — TypeScript-style JSDoc annotations (`@param {Type}`,
  `@returns {Type}`), deprecated `version` field in metadata, and non-standard
  metadata fields (`version-name`, `homepage`, `bug-report-url`) that often appear
  in AI-generated extensions

### Tier 2: Quality Heuristics

`scripts/check-quality.py` runs heuristic code quality checks that detect patterns
commonly seen in AI-generated or over-engineered extensions. These are advisory-only
(WARN severity) and do not block submission, but they flag code that EGO reviewers
are likely to question:

- Excessive try-catch density (wrapping every few lines in try/catch)
- Impossible state checks (`isLocked` without `unlock-dialog` session-mode)
- Over-engineered async coordination patterns (`_pendingDestroy`, `_initializing`)
- Module-level mutable state (variables outside class scope)
- Empty catch blocks (silencing errors without handling them)

## Fallback

If the scripts cannot run (e.g., no bash available), perform manual checks by reading
the extension files and applying the rules in [rules-reference.md](references/rules-reference.md).

## Reference

For the complete rules catalog with severity, rationale, and examples, see
[rules-reference.md](references/rules-reference.md).
