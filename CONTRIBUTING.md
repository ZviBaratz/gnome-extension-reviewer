# Contributing

Thank you for your interest in improving GNOME extension review tooling.

## For Reviewers: Add a Check in 5 Minutes

You just rejected an extension because it uses `navigator.clipboard` (a browser API that doesn't exist in GJS). Here's how to encode that rejection so ego-lint catches it automatically next time.

### Step 1: Add the rule to `rules/patterns.yaml`

Append 4 lines of YAML:

```yaml
- id: R-WEB-12
  pattern: "\\bnavigator\\.clipboard\\b"
  scope: ["*.js"]
  severity: blocking
  message: "navigator.clipboard is a browser API; use St.Clipboard instead"
  category: web-apis
  fix: "Import St from 'gi://St' and use St.Clipboard.get_default()"
```

### Step 2: Create a test fixture

Every rule needs a minimal extension that triggers it. Create a directory in `tests/fixtures/`:

```
tests/fixtures/navigator-clipboard@test/
  metadata.json
  extension.js
  LICENSE
```

**UUID conventions:**
- The directory name **must contain `@`** -- use `<rule-name>@test`
- The `uuid` in `metadata.json` **must match the directory name exactly**

`metadata.json`:
```json
{
    "uuid": "navigator-clipboard@test",
    "name": "Navigator Clipboard Test",
    "description": "Tests R-WEB-12",
    "shell-version": ["48"],
    "url": "https://example.com"
}
```

`extension.js`:
```js
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
export default class TestExtension extends Extension {
    enable() { navigator.clipboard.writeText('test'); }
    disable() {}
}
```

`LICENSE`:
```
SPDX-License-Identifier: GPL-2.0-or-later
```

### Step 3: Add a test assertion

Create a new file `tests/assertions/your-category.sh` (or add to an existing one):

```bash
# Navigator clipboard browser API detection
echo "=== navigator-clipboard ==="
run_lint "navigator-clipboard@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on navigator.clipboard" "\[FAIL\].*R-WEB-12"
echo ""
```

If you created a new assertion file, source it in `tests/run-tests.sh` by adding before the summary section:

```bash
if [[ -f "$ASSERTIONS_DIR/your-category.sh" ]]; then
    source "$ASSERTIONS_DIR/your-category.sh"
fi
```

### Step 4: Run tests

```bash
bash tests/run-tests.sh
```

All existing tests must still pass alongside your new assertion.

**Shortcut:** Use `scripts/new-rule.sh` to scaffold all of the above interactively, or `scripts/validate-fixture.sh` to check that your fixtures meet the structural requirements.

---

## How Rules Are Sourced

Rules come from three sources:

1. **Official guidelines** — [gjs.guide](https://gjs.guide) review guidelines and GNOME Shell documentation
2. **Real reviewer behavior** — Analysis of actual EGO reviews on extensions.gnome.org (documented in [docs/research/](docs/research/))
3. **Observed patterns** — Common mistakes found in approved and rejected extensions

When proposing a new rule, cite the source (guideline section, review URL, or observed pattern) in the rule's rationale. Rules grounded in real rejection data are prioritized.

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

See [`rules/README.md`](rules/README.md) for the full field reference, category prefixes, advanced fields (version-gating, conditional suppression), and inline suppression syntax.

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

## Worked Examples

### Example 1: Adding a Pattern Rule

Suppose you notice that many AI-generated extensions use `Object.freeze()` unnecessarily.

**1. Add the rule:**

```yaml
# In rules/patterns.yaml
- id: R-SLOP-08
  pattern: "Object\\.freeze\\s*\\("
  scope: ["*.js"]
  severity: advisory
  message: "Object.freeze() is unusual in GNOME extensions; may signal over-engineering"
  category: ai-slop
  fix: "Remove Object.freeze() — GNOME extensions don't need runtime immutability guards."
```

**2. Create fixture:** `tests/fixtures/object-freeze@test/extension.js`
```js
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
const CONFIG = Object.freeze({TIMEOUT: 5});
export default class FreezeExtension extends Extension {
    enable() {}
    disable() {}
}
```

**3. Add assertion** in `tests/run-tests.sh`:
```bash
echo "=== object-freeze ==="
run_lint "object-freeze@test"
assert_output_contains "warns on Object.freeze" "\[WARN\].*R-SLOP-08"
```

**4. Test:** `bash tests/run-tests.sh`

### Example 2: Adding a Structural Check

See `skills/ego-lint/scripts/check-quality.py` for the pattern. Each check is a
function that takes `(ext_dir, js_files)` and calls `result(status, check, detail)`.

### Example 3: Adding a Semantic Checklist Item

In `skills/ego-review/references/ai-slop-checklist.md`, add:

```markdown
### CS-5: Excessive constant objects

**Ask**: Are there `Object.freeze()` calls or large constant objects that could be
simple variables?

**Red flag**: `const CONFIG = Object.freeze({...})` with 20+ properties defined at
module level.

**Acceptable**: Small frozen objects used as enums across multiple files.
```

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

## Reporting False Positives

If ego-lint flags something incorrectly:

1. Open an issue with the rule ID (e.g., `R-SLOP-08`), the flagged code, and why it's a false positive
2. If possible, include the extension UUID or a minimal reproduction
3. We validate all reports against our regression baseline (a real 11-module extension with known-good findings)

False positives in blocking rules (FAIL) are treated as high priority. False positives in advisory rules (WARN) are tracked and addressed in batches.

## Rule Lifecycle

- New rules start as **advisory** (WARN) unless they correspond to a documented MUST requirement in the official guidelines
- Rules are upgraded to **blocking** (FAIL) after validation against real extensions confirms no false positives
- Rules are **deprecated** (not removed) when the GNOME versions they apply to are no longer supported
- Version-gated rules use `min-version`/`max-version` fields in `rules/patterns.yaml` — they only fire when the extension's declared `shell-version` falls within range

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
