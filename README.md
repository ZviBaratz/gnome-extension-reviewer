# gnome-extension-reviewer

Claude Code plugin for GNOME Shell extension EGO (extensions.gnome.org) review compliance.

## Installation

```bash
claude plugins add github:ZviBaratz/gnome-extension-reviewer
```

## Skills

| Skill | Description |
|-------|-------------|
| `ego-lint` | Automated compliance checks (metadata, imports, logging, deprecated APIs, schema, packaging) |
| `ego-review` | Manual code review simulating an EGO reviewer (lifecycle, signals, security, quality) |
| `ego-scaffold` | Scaffold a new GNOME Shell extension with EGO-compliant structure |
| `ego-submit` | Full pre-submission validation pipeline (lint + review + package + readiness report) |

## Quick Start

In your extension directory, ask Claude to lint your extension:

> "Run ego-lint on this extension"

Or use the command directly:

> `/ego-submit`

## What Gets Checked

| Category | Checks |
|----------|--------|
| Metadata | UUID format/match, required fields, shell-version, session-modes |
| Schema | ID matches metadata, path format, compilation |
| Imports | GTK/Gdk/Adw banned in extension.js; Clutter/Meta/St/Shell banned in prefs.js |
| Logging | console.log() banned (use console.debug) |
| Deprecated | Mainloop, Lang, ByteArray |
| Web APIs | setTimeout, setInterval, fetch |
| Files | extension.js/metadata.json required, LICENSE recommended |
| CSS | Unscoped class names |
| ESLint | eslint-config-gnome violations |
| Package | Forbidden files in zip (node_modules, .git, .claude, etc.) |
| Lifecycle | Enable/disable symmetry, resource cleanup, async safety |
| Security | Subprocess validation, pkexec, clipboard/network disclosure |

## Requirements

- **Required**: bash, python3
- **Optional**: npm/node (for ESLint checks), glib-compile-schemas (for schema validation)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

GPL-2.0-or-later
