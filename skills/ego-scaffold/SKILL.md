---
name: ego-scaffold
description: >-
  Create a new GNOME Shell extension project with correct structure, lifecycle
  boilerplate, eslint-config-gnome, and EGO-compliant metadata. Generates
  extension.js, prefs.js, metadata.json, schema, stylesheet, and tooling.
  Use when creating a new extension, scaffolding a project, or starting fresh.
---

# ego-scaffold

Scaffold a new GNOME Shell extension with EGO-compliant structure.

## Information Needed

Before scaffolding, gather from the user:

1. **Extension name** — Human-readable name (e.g., "My Extension")
2. **UUID** — Format: `name@username` (e.g., `my-extension@JohnDoe`)
3. **Description** — What the extension does
4. **Target GNOME versions** — Array like ["48", "49"] (must include current stable)
5. **Author name** — For LICENSE copyright
6. **Repository URL** — GitHub/GitLab URL
7. **Needs preferences?** — Whether to generate prefs.js (default: yes)
8. **Needs GSettings schema?** — Whether to generate schema (default: yes, if prefs)

## Generated Structure

```
<uuid>/
├── extension.js          # Main extension with lifecycle boilerplate
├── prefs.js              # Preferences UI (if requested)
├── metadata.json         # EGO-compliant metadata
├── stylesheet.css        # Empty stylesheet with scoped example
├── schemas/
│   └── <schema-id>.gschema.xml  # GSettings schema (if requested)
├── eslint.config.mjs     # ESLint with eslint-config-gnome
├── package.json          # For ESLint dependency
├── LICENSE               # GPL-2.0-or-later
└── .gitignore
```

## Template Variables

Templates in the `assets/` directory use `${PLACEHOLDER}` syntax:

| Variable | Description | Example |
|----------|-------------|---------|
| `${UUID}` | Extension UUID | `my-extension@JohnDoe` |
| `${NAME}` | Human-readable name | `My Extension` |
| `${DESCRIPTION}` | Extension description | `Does something useful` |
| `${SHELL_VERSIONS}` | JSON array of versions | `["47", "48"]` |
| `${SCHEMA_ID}` | Full schema ID | `org.gnome.shell.extensions.my-extension` |
| `${SCHEMA_SUFFIX}` | Schema path suffix | `my-extension` |
| `${CLASS_NAME}` | PascalCase class name | `MyExtension` |
| `${YEAR}` | Current year | `2026` |
| `${AUTHOR}` | Author name | `John Doe` |

## Steps

1. Ask user for required information
2. Create extension directory at the appropriate location
3. For each template in `assets/`, read it, replace placeholders, write to target
4. Generate `stylesheet.css` with a scoped class example: `.${SCHEMA_SUFFIX}-label { }`
5. Generate `package.json` with eslint + eslint-config-gnome devDependencies
6. Generate `.gitignore` (node_modules/, *.zip, .claude/, CLAUDE.md)
7. Generate `LICENSE` with GPL-2.0-or-later boilerplate
8. Run `glib-compile-schemas schemas/` if glib-compile-schemas is available
9. Optionally run `npm install` if npm is available
10. Initialize git repo
11. Suggest running `ego-lint` to verify: "Run ego-lint to verify your new extension is EGO-compliant"

## After Scaffolding

Tell the user:
- Edit `extension.js` to add extension functionality in `enable()`
- Edit `prefs.js` to add preference controls
- Run `glib-compile-schemas schemas/` after schema changes
- Test with `gnome-extensions enable <uuid>`
