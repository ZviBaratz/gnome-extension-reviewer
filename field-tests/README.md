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

> **Note**: tiling-shell metrics reflect the compiled release zip — the TypeScript source is much larger. The high SKIP count (16) is due to checks that don't apply to bundled output.

## Latest Lint Results (2026-03-10)

ego-lint version: `a441201`

| Extension | Exit | PASS | FAIL | WARN | SKIP | Verdict |
|---|---|---|---|---|---|---|
| hara-hachi-bu | 0 | 209 | 0 | 9 | 23 | Pass |
| tiling-shell | 1 | 193 | 2 | 7 | 16 | Fail |
| v-shell | 1 | 190 | 1 | 90 | 17 | Fail |
| gsconnect | 1 | 174 | 4 | 131 | 17 | Fail |
| appindicator | 1 | 189 | 6 | 60 | 14 | Fail |
| clipboard-indicator | 1 | 198 | 2 | 25 | 17 | Fail |
| blur-my-shell | 1 | 194 | 3 | 35 | 17 | Fail |
| dash-to-panel | 1 | 176 | 8 | 62 | 17 | Fail |
| media-controls | 1 | 189 | 3 | 29 | 17 | Fail |
| just-perfection | 1 | 205 | 1 | 13 | 12 | Fail |
| **Totals** | — | **1,917** | **30** | **461** | **167** | — |

## Annotation Coverage

Each extension has a classification file in `annotations/` where findings are labeled as true positive (tp), false positive (fp), borderline, expected, or resolved (finding no longer emitted).

| Extension | TP | FP | Borderline | Expected | Resolved | Total |
|---|---|---|---|---|---|---|
| hara-hachi-bu | 14 | 9 | 0 | 26 | 0 | 49 |
| tiling-shell | 4 | 1 | 2 | 20 | 55 | 82 |
| v-shell | 40 | 6 | 1 | 17 | 0 | 64 |
| gsconnect | 52 | 7 | 16 | 18 | 2 | 95 |
| appindicator | 45 | 10 | 10 | 15 | 2 | 82 |
| clipboard-indicator | 44 | 6 | 0 | 18 | 0 | 68 |
| blur-my-shell | 38 | 9 | 6 | 18 | 9 | 80 |
| dash-to-panel | 63 | 6 | 5 | 19 | 7 | 100 |
| media-controls | 18 | 0 | 4 | 18 | 20 | 60 |
| just-perfection | 14 | 0 | 1 | 13 | 1 | 29 |
| **Totals** | **332** | **54** | **45** | **182** | **96** | **709** |

**100% annotation coverage** — all 709 annotations across 10 extensions are classified (613 active findings + 96 resolved).

## Precision Metrics

| Metric | Value |
|---|---|
| Strict precision (TP / (TP + FP)) | **86.0%** (332 / 386) |
| Lenient precision ((TP + BL) / (TP + FP + BL)) | **87.5%** (377 / 431) |
| False positive rate | 8.8% (54 / 613) |
| Expected / not-applicable | 29.7% (182 / 613) |
| Resolved (no longer emitted) | 96 findings across 6 PRs |

### Top FP-generating rules

| Rule | FP | TP | Precision |
|---|---|---|---|
| init/shell-modification | 5 | 5 | 50.0% |
| R-SLOP-38 | 3 | 0 | 0.0% |
| R-SLOP-35 | 1 | 0 | 0.0% |
| R-SLOP-24 | 2 | 0 | 0.0% |
| R-SLOP-13 | 2 | 0 | 0.0% |
| resource-tracking/no-destroy-method | 2 | 2 | 50.0% |
| resource-tracking/destroy-not-called | 2 | 2 | 50.0% |
| quality/gettext-pattern | 2 | 0 | 0.0% |
| R-VER48-02 | 2 | 0 | 0.0% |

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
