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

### Line-Level Suppression (`guard-pattern`)

A rule can be suppressed when a guard pattern matches the same line or the previous line. This handles runtime feature detection, polymorphic dispatch, and other cases where the flagged pattern is used safely.

```yaml
- id: R-VER46-01
  pattern: "\\.add_actor\\s*\\("
  scope: ["*.js"]
  severity: blocking
  message: "Clutter.Container.add_actor() removed in GNOME 46; use add_child()"
  min-version: 46
  guard-pattern: "\\bif\\s*\\(.*\\.add_actor\\b"
```

If a line calls `.add_actor(` but the same line (or previous line) has `if (obj.add_actor)` — a runtime capability check — the match is suppressed. The guard check is line-level: it checks both the current matched line and the immediately preceding line.

**Use cases**:
- Runtime feature detection: `if (obj.method)` before calling `obj.method()`
- Polymorphic dispatch: `!(this instanceof Foo)` (negated instanceof is a type guard, not AI slop)
- Enum constants: `const X = Object.freeze({` (const assignment + freeze is standard JS enum pattern)
- Signal handler conventions: `.connect('destroy', ...this._onDestroy)` (handler, not method to rename)

### Extended Guard Lookback (`guard-window`)

By default, `guard-pattern` checks only the current line and the immediately preceding line. For version-compat if/else blocks where the guard and the deprecated call are separated by several lines, use `guard-window` to extend the lookback:

```yaml
- id: R-VER44-02
  pattern: "\\bMeta\\.later_remove\\b"
  guard-pattern: "if\\s*\\(\\s*global\\.compositor\\s*\\)"
  guard-window: 7
```

This checks the current line plus the 7 preceding lines for the guard pattern. The typical case is an if/else block:

```js
if (global.compositor) {
    global.compositor.get_laters().removeLater(id);
} else {
    Meta.later_remove(id);  // 6 lines after guard — suppressed with guard-window: 7
}
```

**Guidelines:**
- Set `guard-window` to the maximum expected distance between the guard and the flagged pattern, plus 1
- Only use when the default 1-line lookback is insufficient — most guards are on the same or previous line
- Keep the window as small as practical to avoid false suppressions

### Forward Guard Lookback (`guard-window-forward`)

When the guard evidence appears _after_ the flagged pattern (e.g., in a multi-line constructor), use `guard-window-forward` to look ahead:

```yaml
- id: R-SLOP-24
  pattern: "\\bnew\\s+Gio\\.Settings\\s*\\("
  guard-pattern: "schema.*org\\.gnome\\.(?!shell\\.extensions\\.)|KEYBINDINGS_SCHEMA"
  guard-window-forward: 2
```

This checks the next 2 lines after the matched line for the guard pattern. The typical case is a multi-line constructor:

```js
this._mutter = new Gio.Settings({           // ← pattern fires here
    schema_id: 'org.gnome.mutter'            // ← guard matches here (forward +1)
});
```

**Guidelines:**
- Set `guard-window-forward` to the maximum expected distance between the flagged pattern and the guard evidence
- Can be combined with `guard-window` for bidirectional lookback
- Keep the window as small as practical to avoid false suppressions

### Comment Skipping (`skip-comments`)

When a rule should not match inside comments (e.g., deprecated API names mentioned in code comments), use `skip-comments: true`:

```yaml
- id: R-DEPR-06
  pattern: "\\bTweener\\b"
  skip-comments: true
```

This skips matches inside `//` single-line comments and `/* */` block comments (including multi-line). Code on the same line as a comment is still checked — only the portion after `//` or between `/* */` is skipped.

**Use cases:**
- Deprecated API names mentioned in migration comments
- Commented-out legacy code that hasn't been removed

### Fix Version Gating (`fix-min-version`)

When a deprecation rule suggests a fix that only works on newer GNOME versions, use `fix-min-version` to suppress the fix text for extensions whose minimum shell-version is below the threshold. The warning still fires (developers should know about deprecations), but the fix suggestion is omitted when applying it would break backward compatibility.

```yaml
- id: R-VER48-04
  pattern: "\\.vertical\\s*="
  scope: ["*.js"]
  severity: advisory
  message: "St.Widget.vertical deprecated in GNOME 48; use orientation (available since GNOME 47; keep vertical for GNOME <=46 compat)"
  fix: "Use {orientation: Clutter.Orientation.VERTICAL} instead of {vertical: true}"
  min-version: 48
  fix-min-version: 47
```

For an extension with `shell-version: ["46", "47", "48"]` (min_shell=46), the fix text is suppressed because 46 < 47. For an extension targeting only `["48"]` (min_shell=48), the fix text is shown because 48 >= 47.

**Guidelines:**
- Set `fix-min-version` to the GNOME version where the replacement API was introduced
- Only use when the fix would break older versions in the extension's declared range
- The warning message should include the compat note inline (e.g., "keep vertical for GNOME <=46 compat")

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
