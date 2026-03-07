# Field Tests

Batch ego-lint runner for regression testing across 10 real-world GNOME Shell extensions. Used to calibrate rules, catch false positives, and track lint accuracy over time.

## Extension Catalog

| Extension | Description | Source | EGO Approved |
|---|---|---|---|
| [hara-hachi-bu](https://github.com/ZviBaratz/hara-hachi-bu) | Mindful eating timer with pomodoro-style reminders | local | No |
| [tiling-shell](https://github.com/domferr/tilingshell) | Tiling window manager (compiled TypeScript) | github-release (v17.3) | Yes |
| [v-shell](https://github.com/G-dH/vertical-workspaces) | Vertical workspaces and Shell UI customization | local | Yes |
| [gsconnect](https://github.com/GSConnect/gnome-shell-extension-gsconnect) | KDE Connect implementation for GNOME (D-Bus daemon) | local | Yes |
| [appindicator](https://github.com/ubuntu/gnome-shell-extension-appindicator) | System tray / StatusNotifierItem support | github | Yes |
| [clipboard-indicator](https://github.com/Tudmotu/gnome-shell-extension-clipboard-indicator) | Clipboard manager with history | github | Yes |
| [blur-my-shell](https://github.com/aunetx/blur-my-shell) | Blur effects for Shell UI elements | github | Yes |
| [dash-to-panel](https://github.com/home-sweet-gnome/dash-to-panel) | Moves the dash into a Windows-style taskbar panel | github | Yes |
| [media-controls](https://github.com/cliffniff/Media-Controls) | Media player controls in the top panel | github | Yes |
| [just-perfection](https://github.com/jrahmatzadeh/just-perfection) | GNOME Shell UI tweaks and customization | github | Yes |

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

## Latest Lint Results (2026-03-07)

ego-lint version: `ae650be`

| Extension | Exit | PASS | FAIL | WARN | SKIP | Verdict |
|---|---|---|---|---|---|---|
| hara-hachi-bu | 0 | 207 | 0 | 9 | 23 | Pass |
| tiling-shell | 1 | 138 | 4 | 4 | 51 | Fail |
| v-shell | 1 | 188 | 1 | 91 | 17 | Fail |
| gsconnect | 1 | 171 | 12 | 144 | 17 | Fail |
| appindicator | 1 | 187 | 11 | 57 | 14 | Fail |
| clipboard-indicator | 1 | 196 | 3 | 24 | 17 | Fail |
| blur-my-shell | 1 | 190 | 4 | 43 | 17 | Fail |
| dash-to-panel | 1 | 171 | 11 | 66 | 17 | Fail |
| media-controls | 1 | 188 | 6 | 28 | 17 | Fail |
| just-perfection | 1 | 198 | 4 | 10 | 12 | Fail |
| **Totals** | — | **1,834** | **56** | **476** | **202** | — |

## Annotation Coverage

Each extension has a classification file in `annotations/` where findings are labeled as true positive (tp), false positive (fp), borderline, or expected.

| Extension | TP | FP | Borderline | Expected | Classified | Unannotated |
|---|---|---|---|---|---|---|
| hara-hachi-bu | 7 | 10 | 0 | 1 | 18 | 32 |
| tiling-shell | 13 | 7 | 4 | 0 | 24 | 59 |
| v-shell | 8 | 5 | 1 | 0 | 14 | 48 |
| gsconnect | 12 | 8 | 8 | 0 | 28 | 76 |
| appindicator | 23 | 12 | 3 | 0 | 38 | 51 |
| clipboard-indicator | 28 | 8 | 0 | 0 | 36 | 42 |
| blur-my-shell | 23 | 11 | 4 | 0 | 38 | 50 |
| dash-to-panel | 18 | 10 | 3 | 0 | 31 | 68 |
| media-controls | 16 | 3 | 2 | 0 | 21 | 37 |
| just-perfection | 2 | 0 | 0 | 0 | 2 | 26 |
| **Totals** | **150** | **74** | **25** | **1** | **250** | **489** |

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
