# Contributing

## Contributing a Rule

There are three ways to contribute a new rule, depending on complexity:

### Option 1: Pattern Rule (Easiest — 4 lines of YAML)

For simple regex-based checks (e.g., "flag usage of X API"), add a rule to `rules/patterns.yaml`:

```yaml
- id: R-XXXX-NN
  pattern: "\\bsomeAPI\\s*\\("
  scope: ["*.js"]
  severity: blocking
  message: "someAPI is not available in GJS; use alternative instead"
  category: category-name
```

Fields:
- `id`: Unique rule ID following the `R-CATEGORY-NN` convention (e.g., R-WEB-10, R-DEPR-08)
- `pattern`: Python `re` regex syntax (double-escape backslashes in YAML)
- `scope`: Glob patterns for which files to check (e.g., `["*.js"]`, `["metadata.json"]`)
- `severity`: `blocking` (FAIL) or `advisory` (WARN)
- `message`: Human-readable explanation shown to the user
- `category`: Group name for the rule (web-apis, deprecated, ai-slop)
- `fix`: Optional — how to fix the issue

Then add a test fixture and assertion (see Testing below).

### Option 2: Structural Check (Python/Bash Script)

For checks that need code structure analysis (e.g., "flag excessive try-catch density"), modify the appropriate script in `skills/ego-lint/scripts/`:

- `check-metadata.py` — metadata.json validation
- `check-quality.py` — code quality heuristics (Tier 2)
- `check-imports.sh` — import segregation
- `check-schema.sh` — GSettings schema validation
- `check-package.sh` — zip package validation

Use the standard output format:
```
STATUS|check-name|detail
```
Where `STATUS` is one of `PASS`, `FAIL`, `WARN`, or `SKIP`.

### Option 3: Semantic Checklist Item (Markdown — No Code)

For checks that require human judgment (e.g., "does the error handling make sense in context?"), add an item to the appropriate checklist in `skills/ego-review/references/`:

- `ai-slop-checklist.md` — AI-generated code patterns
- `lifecycle-checklist.md` — enable/disable lifecycle correctness
- `security-checklist.md` — security concerns
- `code-quality-checklist.md` — code quality patterns

Use the existing format in each file (Ask / Red flag / Acceptable).

## Adding an Automated Check

This process applies to Option 1 (pattern rules) and Option 2 (structural checks) above. Test fixtures are expected for all automated checks.

1. Add or modify the check in the appropriate location (see Options 1 and 2).
2. Add a test fixture in `tests/fixtures/` with the minimal files needed to trigger the check.
3. Update `tests/run-tests.sh` with assertions for the new check.

## Testing

Run the full test suite:

```bash
bash tests/run-tests.sh
```

All assertions must pass before submitting a pull request.

## Skill Content Changes

- Skill files are in `skills/*/SKILL.md`
- Reference files are in `skills/*/references/`
- Changes to skill descriptions should be reviewed for accuracy against the current EGO review guidelines

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - new feature or check
- `fix:` - bug fix
- `docs:` - documentation only
- `test:` - adding or updating tests
- `chore:` - build, tooling, dependencies

Scope to the skill name when applicable:

```
feat(ego-lint): add check for unscoped CSS classes
fix(ego-scaffold): correct schema path in template
docs(ego-review): update lifecycle checklist for GNOME 48
test(ego-lint): add fixture for deprecated ByteArray usage
```
