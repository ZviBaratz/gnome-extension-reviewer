# Field Tests

Batch ego-lint runner for regression testing across 10 real-world GNOME Shell extensions. Used to calibrate rules, catch false positives, and track lint accuracy over time.

## Extension Catalog

| Extension | Version | Shell Versions | EGO |
|---|---|---|---|
| [hara-hachi-bu](https://github.com/ZviBaratz/hara-hachi-bu) | dev | 46–48 | No |
| [tiling-shell](https://github.com/domferr/tilingshell) | 17.3 | 42–49 | Yes |
| [v-shell](https://github.com/G-dH/vertical-workspaces) | 49.13 | 45–49 | Yes |
| [gsconnect](https://github.com/GSConnect/gnome-shell-extension-gsconnect) | 71 | 46–49 | Yes |
| [appindicator](https://github.com/ubuntu/gnome-shell-extension-appindicator) | `be68add` | 45–50 | Yes |
| [clipboard-indicator](https://github.com/Tudmotu/gnome-shell-extension-clipboard-indicator) | `13ba8b1` | 46–49 | Yes |
| [blur-my-shell](https://github.com/aunetx/blur-my-shell) | 70 | 46–49 | Yes |
| [dash-to-panel](https://github.com/home-sweet-gnome/dash-to-panel) | `ebf64ab` | 46–49 | Yes |
| [media-controls](https://github.com/cliffniff/Media-Controls) | 2.4.4 | 46–49 | Yes |
| [just-perfection](https://github.com/jrahmatzadeh/just-perfection) | 36 | 45–50 | Yes |

> **Version pinning**: Some extensions lack a version field in metadata.json — for those, the git short ref is shown instead. See `manifest.yaml` for full source details.

## Code Metrics

| Extension | JS Files | Total Lines | Largest File | CSS Lines | Schema Keys |
|---|---|---|---|---|---|
| hara-hachi-bu | 18 | 8,898 | prefs.js (1,973) | 126 | 26 |
| tiling-shell | 1 | 14 | monitorDescription.js (14) | 0 | 61 |
| v-shell | 28 | 19,201 | prefs.js (2,507) | 396 | 152 |
| gsconnect | 65 | 24,680 | messaging.js (1,325) | 127 | 48 |
| appindicator | 17 | 5,655 | appIndicator.js (1,604) | 0 | 10 |
| clipboard-indicator | 6 | 2,486 | extension.js (1,430) | 75 | 31 |
| blur-my-shell | 49 | 7,743 | extension.js (602) | 572 | 95 |
| dash-to-panel | 18 | 16,583 | prefs.js (4,052) | 251 | 247 |
| media-controls | 17 | 5,064 | PanelButton.js (1,236) | 100 | 29 |
| just-perfection | 7 | 7,490 | API.js (3,663) | 732 | 73 |

> **Note**: tiling-shell metrics reflect the compiled release zip — the TypeScript source is much larger. The high SKIP count (51) is due to checks that don't apply to bundled output.

## Latest Lint Results (2026-03-08)

ego-lint version: `05523f9`

| Extension | Exit | PASS | FAIL | WARN | SKIP | Verdict |
|---|---|---|---|---|---|---|
| hara-hachi-bu | 0 | 208 | 0 | 9 | 23 | Pass |
| tiling-shell | 1 | 139 | 3 | 5 | 51 | Fail |
| v-shell | 1 | 188 | 2 | 91 | 17 | Fail |
| gsconnect | 1 | 172 | 11 | 134 | 17 | Fail |
| appindicator | 1 | 187 | 10 | 59 | 14 | Fail |
| clipboard-indicator | 1 | 197 | 3 | 24 | 17 | Fail |
| blur-my-shell | 1 | 193 | 4 | 40 | 17 | Fail |
| dash-to-panel | 1 | 173 | 9 | 64 | 17 | Fail |
| media-controls | 1 | 188 | 4 | 28 | 17 | Fail |
| just-perfection | 1 | 204 | 1 | 13 | 12 | Fail |
| **Totals** | — | **1,849** | **47** | **467** | **202** | — |

## Annotation Coverage

Each extension has a classification file in `annotations/` where findings are labeled as true positive (tp), false positive (fp), borderline, expected, or resolved (finding no longer emitted).

| Extension | TP | FP | Borderline | Expected | Resolved | Classified | Unannotated |
|---|---|---|---|---|---|---|---|
| hara-hachi-bu | 7 | 9 | 0 | 1 | 0 | 17 | 32 |
| tiling-shell | 10 | 9 | 2 | 0 | 0 | 21 | 59 |
| v-shell | 10 | 6 | 0 | 0 | 0 | 16 | 49 |
| gsconnect | 11 | 6 | 7 | 0 | 2 | 26 | 69 |
| appindicator | 17 | 10 | 4 | 0 | 0 | 31 | 52 |
| clipboard-indicator | 20 | 6 | 0 | 0 | 0 | 26 | 42 |
| blur-my-shell | 17 | 7 | 3 | 0 | 2 | 29 | 47 |
| dash-to-panel | 22 | 8 | 2 | 1 | 3 | 36 | 65 |
| media-controls | 14 | 5 | 2 | 0 | 1 | 22 | 38 |
| just-perfection | 2 | 0 | 0 | 0 | 1 | 3 | 26 |
| **Totals** | **130** | **66** | **20** | **2** | **9** | **227** | **479** |

## Directory Structure

```
field-tests/
  manifest.yaml          # Extension source manifest
  baselines/             # Golden JSON snapshots (committed)
  annotations/           # Per-extension finding classifications (committed)
  history.jsonl          # Append-only trend data (committed)
  reports/               # Regression/synthesis reports (committed)
  cache/                 # Downloaded extensions (gitignored)
  results/               # Timestamped run output (gitignored)
```

## Quick Start

```bash
# Run lint on all extensions
bash scripts/field-test-runner.sh

# Run lint on a single extension
bash scripts/field-test-runner.sh --extension blur-my-shell

# Skip git fetches, use cached copies
bash scripts/field-test-runner.sh --no-fetch

# Update baselines after confirming results
bash scripts/field-test-runner.sh --update-baselines

# Run lint + ego-review on all extensions
bash scripts/field-test-runner.sh --review --no-fetch

# Review with exclusions and custom budget
bash scripts/field-test-runner.sh --review --review-exclude gsconnect --budget 6.00
```

See the [calibration cycle](../CLAUDE.md#calibration-cycle) in CLAUDE.md for the full workflow.
