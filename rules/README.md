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

| Prefix | Category | Severity |
|--------|----------|----------|
| R-WEB | Browser/web APIs | blocking |
| R-DEPR | Deprecated GNOME APIs | blocking or advisory |
| R-SEC | Security concerns | blocking |
| R-IMPORT | Import segregation | blocking |
| R-LOG | Logging patterns | advisory |
| R-SLOP | AI-generated code signals | advisory |
| R-META | Metadata fields | see rules-reference.md |
