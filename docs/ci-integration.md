# CI Integration

ego-lint exits 0 (pass) or 1 (blocking issues found). It needs only `bash` and `python3` — no network access, no API keys, no extra dependencies.

## GitHub Actions

```yaml
name: ego-lint
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/checkout@v4
        with:
          repository: ZviBaratz/gnome-extension-reviewer
          path: .ego-lint
      - run: .ego-lint/ego-lint .
```

## GitLab CI

```yaml
ego-lint:
  image: python:3-slim
  before_script:
    - git clone --depth 1 https://github.com/ZviBaratz/gnome-extension-reviewer.git /tmp/ego-lint
  script:
    - /tmp/ego-lint/ego-lint .
```

## Notes

- Both examples assume the extension source is at the repo root. Adjust the path if your extension is in a subdirectory.
- `glib-compile-schemas` is optional — the schema dry-run check will be skipped if it's not installed. Install `libglib2.0-dev-bin` (Debian/Ubuntu) or `glib2-devel` (Fedora) if you want schema validation in CI.
- The `--verbose` flag adds a grouped report and verdict summary, useful for CI logs.
