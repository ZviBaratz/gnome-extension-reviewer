# ego-lint False Positives and Improvement Opportunities

> **All items resolved in v0.1.0 (commit 7ecc386).** Archived for transparency.

Discovered during a full EGO submission pipeline run on the
[hara-hachi-bu](https://github.com/ZviBaratz/hara-hachi-bu) extension
(18 JS files, 7,662 non-blank lines). The ego-simulate score was **0**
(likely to pass without comments), yet ego-lint's verdict was
**"LIKELY REJECTED: 14 warnings suggest quality concerns"**.

---

## Bug 1: R-SEC-07 fires even when disclosure is present

**Files**: `rules/patterns.yaml:243`, `skills/ego-lint/scripts/check-quality.py:775`

**Problem**: Two checks cover clipboard disclosure, but they don't
cross-reference:

1. `R-SEC-07` (patterns.yaml) — fires WARN for any `St.Clipboard` match,
   message: "Clipboard access must be disclosed in metadata.json description"
2. `quality/clipboard-disclosure` (check-quality.py) — reads metadata.json,
   checks if "clipboard" appears in description, PASSes if it does

When an extension correctly discloses clipboard usage, the result is:
```
[WARN] R-SEC-07         Clipboard access must be disclosed...
[PASS] quality/clipboard-disclosure  St.Clipboard usage disclosed in metadata description
```

The WARN is a false positive — the disclosure requirement is satisfied.
It inflates the warning count and contributes to the misleading verdict.

**Fix options** (pick one):
- Remove R-SEC-07 entirely — `quality/clipboard-disclosure` is a strict
  superset (it checks for the pattern AND verifies disclosure)
- Suppress R-SEC-07 when `quality/clipboard-disclosure` passes (requires
  cross-check coordination between Tier 1 patterns and Tier 2 heuristics)
- Change R-SEC-07 to `severity: info` so it doesn't count toward WARN_COUNT

**Recommendation**: Remove R-SEC-07. The `quality/clipboard-disclosure` check
already handles both the detection and the disclosure verification.

---

## Bug 2: Verdict "LIKELY REJECTED" threshold is too aggressive

**File**: `skills/ego-lint/scripts/ego-lint.sh:563-564`

```bash
elif [[ $WARN_COUNT -gt 5 ]]; then
    echo "  LIKELY REJECTED: $WARN_COUNT warnings suggest quality concerns"
```

**Problem**: A flat threshold of >5 warnings triggers "LIKELY REJECTED"
regardless of warning severity or nature. In the test case, 14 warnings
included:

| Warning | Nature |
|---------|--------|
| polkit-files | Informational — polkit files exist, needs security review |
| R-SEC-07 | False positive (see Bug 1) |
| R-SEC-20 | Informational — pkexec will get scrutiny |
| R-PREFS-04b | Advisory — GTK containers that may be legitimate |
| metadata/shell-version-current | Informational — not including GNOME 49 |
| quality/module-state | Informational — already properly managed |
| quality/private-api ×6 | One concern emitted as 6 WARN lines |
| quality/gettext-pattern | Advisory — style preference |
| async/missing-cancellable | Advisory |

None of these are quality problems that would cause rejection. The
ego-simulate rejection taxonomy scored 0 for the same extension.

**Root causes**:
1. Informational/scrutiny warnings count the same as quality concerns
2. `quality/private-api` emits up to 6 WARN lines for one check (see
   Improvement 2 below), heavily skewing the count
3. The R-SEC-07 false positive adds another

**Fix options**:
- Count unique check IDs instead of WARN lines (private-api = 1, not 6)
- Raise the threshold (e.g., >10 unique checks)
- Categorize warnings: only count `quality/*` and `lifecycle/*` toward
  the rejection verdict, not `security scrutiny` or `metadata informational`
- Weight by severity: `advisory` × 1, `scrutiny` × 0

**Recommendation**: Count unique check IDs. This alone would have reduced
the 14 warnings to ~9 unique checks, which is still above 5 but closer to
reality. Combined with removing the R-SEC-07 false positive, it would be 8.
A threshold of >8 unique checks would produce a more accurate verdict.

---

## Bug 3: `quality/gettext-pattern` fix message is inaccurate

**File**: `skills/ego-lint/scripts/check-quality.py:639-642`

```python
result("WARN", "quality/gettext-pattern",
       f"Uses Gettext.dgettext() directly ({locs}) — "
       f"hardcoded gettext domain creates maintenance burden if domain changes; "
       f"use this.gettext() from the Extension base class")
```

**Problem**: The fix says "use `this.gettext()` from the Extension base
class," but `this.gettext()` is an instance method — it can't be used at
module scope for `const _ = this.gettext()`. The idiomatic pattern is a
module-level import:

```javascript
// extension.js
import {Extension, gettext as _} from 'resource:///org/gnome/shell/extensions/extension.js';

// prefs.js
import {ExtensionPreferences, gettext as _} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';
```

**Fix**: Update the message to:

```python
result("WARN", "quality/gettext-pattern",
       f"Uses Gettext.dgettext() directly ({locs}) — "
       f"hardcoded gettext domain creates maintenance burden if domain changes; "
       f"use `import {{gettext as _}} from` the Extension/ExtensionPreferences module")
```

---

## Improvement 1: R-SEC-20 scope is too broad

**File**: `rules/patterns.yaml:283-287`

```yaml
- id: R-SEC-20
  pattern: "\\bpkexec\\b"
  scope: ["*.js", "*.sh"]
  severity: advisory
  message: "pkexec usage will receive extra reviewer scrutiny..."
```

**Problem**: Matches `\bpkexec\b` in all JS and shell files, catching
files that merely reference pkexec in string literals or comments:

- `package.sh` — echoes a message mentioning pkexec
- `prefs.js` — displays install instructions containing "pkexec"
- `install-helper.sh` — installs the helper (doesn't execute pkexec itself)

Only `lib/helper.js` actually calls pkexec via `Gio.Subprocess`. The
report says "5 files" but only 1 is a true usage.

**Fix options**:
- Scope to `["*.js"]` only (shell scripts aren't extension code)
- Use `deduplicate: true` so it fires once, not per-file
- Add comment/string-literal exclusion to the pattern engine

---

## Improvement 2: `quality/private-api` inflates warning count

**File**: `skills/ego-lint/scripts/check-quality.py:601-609`

```python
if matches:
    for rel, lineno, desc in matches[:5]:
        result("WARN", "quality/private-api",
               f"{rel}:{lineno}: {desc} — requires reviewer justification "
               f"and version pinning")
    remaining = len(matches) - 5
    if remaining > 0:
        result("WARN", "quality/private-api",
               f"...and {remaining} more private API access(es)")
```

**Problem**: Each location emits a separate `result("WARN", ...)` call,
so one check can contribute up to 6 WARN lines (5 locations + 1 overflow).
This extension had 11 `_indicators` accesses across 2 methods — one concern,
6 warning lines. This heavily skews `WARN_COUNT` in the verdict.

**Fix**: Emit one WARN with all locations in the detail text:

```python
if matches:
    locs = ', '.join(f"{rel}:{lineno}" for rel, lineno, _ in matches[:5])
    overflow = f" (+{len(matches) - 5} more)" if len(matches) > 5 else ""
    result("WARN", "quality/private-api",
           f"{locs}{overflow}: {matches[0][2]} — requires reviewer "
           f"justification and version pinning")
```

This changes `quality/private-api` from 6 warnings to 1, matching how
other checks (like `quality/gettext-pattern`) report multiple locations
in a single warning.

---

## Summary

| # | Type | Impact | Effort |
|---|------|--------|--------|
| Bug 1 | R-SEC-07 false positive | Inflates WARN_COUNT | Low — remove rule |
| Bug 2 | Verdict threshold | Misleading "LIKELY REJECTED" | Medium — count unique IDs |
| Bug 3 | gettext fix message | Incorrect advice | Low — update string |
| Imp 1 | R-SEC-20 scope | Inflates file count | Low — add deduplicate |
| Imp 2 | private-api WARN count | Inflates WARN_COUNT | Low — consolidate output |

Fixing Bugs 1-2 and Improvement 2 together would have changed the test
case from "LIKELY REJECTED: 14 warnings" to approximately "MAY PASS WITH
COMMENTS: 5 advisory warnings" — which aligns with the ego-simulate
score of 0.
