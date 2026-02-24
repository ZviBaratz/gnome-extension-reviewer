# Contributing

## Quick Contribution: Adding a Rule

To add a new lint rule, append it to `skills/ego-lint/references/rules-reference.md` using this format:

```markdown
### R-XXXX-NN: Rule title
- **Severity**: blocking | advisory | info
- **Checked by**: script name or "manual review"
- **Rule**: What the rule checks
- **Rationale**: Why this matters
- **Fix**: How to fix it
```

Choose the appropriate category prefix for the rule ID (e.g., `R-META` for metadata, `R-IMPORT` for imports, `R-SCHEMA` for schema).

## Adding an Automated Check

1. Modify the appropriate script in `skills/ego-lint/scripts/` (or create a new one if the check doesn't fit an existing script).
2. Use the standard output format for each check result:
   ```
   STATUS|check-name|detail
   ```
   Where `STATUS` is one of `PASS`, `FAIL`, `WARN`, or `SKIP`.
3. Add a test fixture in `tests/fixtures/` with the minimal files needed to trigger the check.
4. Update `tests/run-tests.sh` with assertions for the new check.

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
