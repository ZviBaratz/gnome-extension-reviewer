# Pattern Rules

This directory lives at the project root (not under `skills/ego-lint/`) because
pattern rules are shared across skills — `ego-lint` applies them, `ego-review`
references them, and `ego-submit` orchestrates both. See [CONTRIBUTING.md](../CONTRIBUTING.md) for
the full three-tier rule system.

`patterns.yaml` contains the Tier 1 rules for ego-lint.
Pattern rules are simple regex checks — the easiest way to add a new lint rule.

## Adding a Pattern Rule (5 minutes)

### 1. Add the rule to patterns.yaml

Append an entry:

```yaml
- id: R-XXXX-NN
  pattern: "\\byourPattern\\s*\\("
  scope: ["*.js"]
  severity: blocking
  message: "What is wrong and what to do instead"
  category: category-name
  fix: "Concrete replacement code or approach"
```

**Fields:**
- `id` — Unique ID: `R-` + category prefix + `-` + number (e.g., `R-WEB-12`)
- `pattern` — Python `re` regex (double-escape `\b` for word boundaries)
- `scope` — File globs: `["*.js"]`, `["metadata.json"]`, `["*.css"]`, `["prefs.js"]`
- `severity` — `blocking` (FAIL, must fix) or `advisory` (WARN, should fix)
- `message` — Shown to the user. Say what's wrong AND what to use instead.
- `category` — One of: `web-apis`, `deprecated`, `security`, `imports`, `logging`, `ai-slop`
- `fix` — Concrete replacement. Show code, not just "don't do this."

### 2. Create a test fixture

```
tests/fixtures/<fixture-name>@test/
├── metadata.json    # Minimal valid metadata
└── extension.js     # Contains the pattern you want to catch
```

Minimal `metadata.json`:
```json
{
    "uuid": "<fixture-name>@test",
    "name": "Test",
    "description": "Test",
    "shell-version": ["48"],
    "url": "https://example.com"
}
```

### 3. Add test assertions

In `tests/run-tests.sh`, add before `# --- Summary ---`:

```bash
echo "=== <fixture-name> ==="
run_lint "<fixture-name>@test"
assert_exit_code "exits with <0 or 1>" <0_or_1>
assert_output_contains "description" "\[FAIL\].*R-XXXX-NN"
echo ""
```

### 4. Run tests

```bash
bash tests/run-tests.sh
```

### 5. Validate a single rule (optional)

```bash
bash scripts/validate-rule.sh R-XXXX-NN tests/fixtures/<fixture-name>@test
```

## Advanced Fields

Beyond the basic fields, pattern rules support version-gating and conditional suppression.

### Version-Gating (`min-version` / `max-version`)

Rules can target specific GNOME versions using `min-version` and/or `max-version`. The rule only fires when the extension's `shell-version` in `metadata.json` includes a version within range.

```yaml
- id: R-VER48-01
  pattern: "\\bMeta\\.DisplayDirection\\b"
  scope: ["*.js"]
  severity: blocking
  message: "Meta.DisplayDirection removed in GNOME 48; use Meta.Direction instead"
  category: gnome-48
  fix: "Replace Meta.DisplayDirection with Meta.Direction"
  min-version: 48
```

This rule only fires for extensions that declare `shell-version` including `48` or later. An extension targeting only `["47"]` won't see this check.

Use `max-version` for rules about APIs that were deprecated but not yet removed:

```yaml
- id: R-VER49-01
  pattern: "\\bClutter\\.ClickAction\\b"
  scope: ["*.js"]
  severity: advisory
  message: "Clutter.ClickAction deprecated; will be removed in GNOME 50"
  category: gnome-49
  min-version: 49
  max-version: 49
```

### Conditional Suppression (`replacement-pattern`)

A rule can be suppressed when a replacement pattern also exists in the same file. This prevents false positives when extensions maintain backward compatibility by supporting both old and new patterns.

```yaml
- id: R-VER48-07
  pattern: "\\.panel-button\\b"
  scope: ["*.css"]
  severity: advisory
  message: ".panel-button renamed to .panel-icon in GNOME 48"
  category: gnome-48
  fix: "Use .panel-icon instead of .panel-button"
  min-version: 48
  replacement-pattern: "\\.panel-icon\\b"
```

If a CSS file contains both `.panel-button` and `.panel-icon` (dual selectors for backward compatibility), the rule is suppressed for that file. The replacement check is file-level — if the replacement pattern appears anywhere in the file, the match is skipped.

## Inline Suppression

Add `ego-lint-ignore` comments to suppress specific findings on a per-line basis.
This works for both Tier 1 (pattern rules) and Tier 2 (heuristic checks).

```js
// Suppress a specific rule on the next line
// ego-lint-ignore-next-line: R-WEB-01
setTimeout(() => {}, 1000);

// Suppress a specific rule on the same line
clearTimeout(this._id); // ego-lint-ignore: R-WEB-10

// Blanket suppress (any rule) — use sparingly
doSomething(); // ego-lint-ignore

// Suppress a Tier 2 check
Main.panel._delegate; // ego-lint-ignore: quality/private-api
```

Use suppression for intentional deviations that would otherwise be false positives.
Always prefer fixing the issue over suppressing it.

## Category Prefixes

| Prefix | Category | Severity | Source |
|--------|----------|----------|--------|
| R-WEB | Browser/web APIs | blocking | patterns.yaml |
| R-DEPR | Deprecated GNOME APIs | blocking or advisory | patterns.yaml |
| R-SEC | Security concerns | blocking or advisory | patterns.yaml |
| R-IMPORT | Import segregation | blocking | patterns.yaml + check-imports.sh |
| R-LOG | Logging patterns | advisory | patterns.yaml |
| R-SLOP | AI-generated code signals | advisory | patterns.yaml |
| R-META | Metadata fields | varies | check-metadata.py |
| R-QUAL | Code quality | advisory | patterns.yaml + check-quality.py |
| R-PREFS | Preferences validation | blocking or advisory | patterns.yaml + check-prefs.py |
| R-INIT | Init-time safety | blocking | check-init.py |
| R-LIFE | Lifecycle (enable/disable) | blocking or advisory | check-lifecycle.py |
| R-PKG | Package contents | blocking | check-package.sh |
| R-I18N | Internationalization | advisory | patterns.yaml |
| R-VER44–R-VER50 | GNOME version migration | blocking or advisory | patterns.yaml (version-gated) |

## Troubleshooting

### Pattern doesn't match

- **YAML escaping**: Word boundaries need double-escaping: `\\b` not `\b`. In YAML double-quoted strings, `\b` is a backspace character.
- **Scope mismatch**: Check that your `scope` includes the file type you're testing. `["*.js"]` won't match `metadata.json`.
- **Regex syntax**: Test your pattern inline: `python3 -c "import re; print(re.search(r'your_pattern', 'test string'))"`

### Rule fires but test assertion fails

- **UUID mismatch**: The fixture directory name must exactly match the `uuid` in `metadata.json` and must contain `@`.
- **Missing required files**: Every fixture needs a `LICENSE` file with `SPDX-License-Identifier: GPL-2.0-or-later` and a `url` field in `metadata.json`.
- **Validate your fixture**: Run `bash scripts/validate-fixture.sh tests/fixtures/your-fixture@test`

### Multi-line patterns don't work

Tier 1 pattern rules are **per-line only** — each line is tested independently against the regex. For patterns spanning multiple lines, use a Tier 2 structural check script (Python/bash) instead. See [CONTRIBUTING.md](../CONTRIBUTING.md) for the Tier 2 guide.

### Quick regex test

```bash
python3 -c "
import re
pattern = r'\\byourPattern\\b'
test = 'code containing yourPattern here'
m = re.search(pattern, test)
print('Match!' if m else 'No match')
"
```

## Common Pattern Recipes

Quick-reference for the most common regex patterns used in existing rules. Copy, adapt, and test.

| What to match | Pattern | Matches | Doesn't match |
|---------------|---------|---------|----------------|
| Exact function call | `\\bfunctionName\\s*\\(` | `functionName(x)` | `myFunctionName(x)` |
| Property access | `\\bobject\\.property\\b` | `object.property` | `myobject.property` |
| String literal | `['"]string['"]` | `"string"`, `'string'` | `substring` |
| Either-or | `\\b(oldApi\|newApi)\\b` | `oldApi`, `newApi` | `oldApis` |
| Method chain | `\\.method\\s*\\(` | `obj.method()` | `method()` |
| Constructor | `\\bnew\\s+ClassName\\b` | `new ClassName()` | `ClassName()` |
| Import statement | `from\\s+['"]gi://Lib['"]` | `from 'gi://Lib'` | `from 'gi://LibExtra'` |
| Start-of-line declaration | `^\\s*(let\|var)\\s+` | `let x = 1` | `const x = 1` |

**Tips:**
- `\\b` = word boundary — prevents partial matches (e.g., `\\bLog\\b` matches `Log` but not `Login`)
- `\\s*` = optional whitespace — handles `func()` and `func ()` both
- Always double-escape in YAML: write `\\b` not `\b` (YAML interprets `\b` as backspace)
- Test inline: `python3 -c "import re; print(re.search(r'\\byourPattern\\b', 'test string'))"`
