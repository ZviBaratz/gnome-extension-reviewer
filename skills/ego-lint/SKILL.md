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
| Deprecated | Mainloop, Lang, ByteArray imports | FAIL |
| Web APIs | setTimeout, setInterval, fetch | FAIL |
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

## Fallback

If the scripts cannot run (e.g., no bash available), perform manual checks by reading
the extension files and applying the rules in [rules-reference.md](references/rules-reference.md).

## Reference

For the complete rules catalog with severity, rationale, and examples, see
[rules-reference.md](references/rules-reference.md).
