# EGO Rejection Taxonomy

23 common rejection reasons weighted by severity. Use these weights to compute
a simulation score.

## Weight 10 — Hard Blockers (automatic rejection)

| # | Reason | Description |
|---|--------|-------------|
| 1 | Missing enable/disable | Extension class lacks `enable()` or `disable()` method |
| 2 | Missing metadata fields | `uuid`, `name`, `description`, or `shell-version` absent |
| 3 | UUID mismatch | UUID doesn't match directory name |
| 4 | Browser APIs | `setTimeout`, `setInterval`, `fetch`, `document.*`, `window.*` |
| 5 | Deprecated modules | `Mainloop`, `Lang`, `ByteArray`, `ExtensionUtils`, `Tweener` in GNOME 45+ |
| 6 | console.log in production | Must use `console.debug`/`warn`/`error` instead |

## Weight 8 — AI Slop Signals (strong rejection signal since Dec 2025)

| # | Reason | Description |
|---|--------|-------------|
| 7 | Systematic JSDoc @param/@returns | TypeScript-style annotations throughout |
| 8 | typeof super.method guard | Checking if `super.destroy` is a function |
| 9 | Catch-log-rethrow | `catch(e) { log(e); throw e; }` |
| 10 | Verbose template errors | `console.error(\`Failed to ${verb}: ${e}\`)` |
| 11 | Redundant destroy guards | 5+ if/destroy/null blocks instead of `?.destroy()` |
| 12 | LLM prompt comments | "Important: Make sure...", "Note: Ensure..." |

## Weight 5 — Structural Issues

| # | Reason | Description |
|---|--------|-------------|
| 13 | Signal leak | `.connect()` without matching `.disconnect()` in disable |
| 14 | Timeout leak | `timeout_add` without stored ID and removal in disable |
| 15 | Import segregation | GTK in `extension.js` or Shell modules in `prefs.js` |
| 16 | InjectionManager leak | `new InjectionManager()` without `.clear()` in disable |
| 17 | Mock/test code shipped | `MockDevice.js`, test files in production package |
| 23 | ESLint errors | Code that fails ESLint with errors (undefined references, syntax errors, missing imports) |

## Weight 3 — Style/Quality

| # | Reason | Description |
|---|--------|-------------|
| 18 | Excessive try-catch | >50% of functions wrapped in try-catch |
| 19 | Empty catch blocks | `catch {}` without logging or comment |
| 20 | Excessive code volume | >8000 non-blank lines |

## Weight 1 — Advisory

| # | Reason | Description |
|---|--------|-------------|
| 21 | Missing LICENSE file | Should include GPL-compatible license |
| 22 | Excessive notifications | >3 `Main.notify()` call sites |

## Verdict Thresholds

| Score | Verdict |
|-------|---------|
| 0 | Likely to pass without comments |
| 1-4 | Likely to pass with minor comments |
| 5-9 | May pass, but expect revision requests |
| 10+ | Will be rejected |

## Scoring Rules

- Each triggered reason contributes its weight ONCE (not per occurrence)
- Multiple occurrences of the same reason still count as one trigger
- AI slop signals are cumulative — 3+ signals at weight 8 push score well past
  the rejection threshold
- Hard blockers are independently sufficient for rejection
- When multiple reasons in the same weight class trigger, sum all their weights
- ego-lint runs ESLint as part of its automated checks. If ESLint reports
  errors (not warnings), reason #23 is triggered with weight 5.
