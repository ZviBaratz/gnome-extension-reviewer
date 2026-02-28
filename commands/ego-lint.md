---
description: Run automated EGO compliance checks on a GNOME Shell extension
allowed-tools: Bash(bash *ego-lint.sh*), Read, Glob, Grep
---

Run the ego-lint automated compliance checker on the target extension.

## Target

Extension directory: $ARGUMENTS (if empty, use the current working directory).

## Instructions

1. Locate `ego-lint.sh` in this plugin's `skills/ego-lint/scripts/` directory and run it:

```bash
bash <plugin-path>/skills/ego-lint/scripts/ego-lint.sh <extension-directory>
```

2. Present the results grouped by severity (FAIL first, then WARN, then SKIP, then PASS).
3. If any FAILs exist, summarize the blocking issues and suggest fixes using the table in `skills/ego-lint/SKILL.md` under "Common Fixes".
4. For `--verbose` output, add the flag to the command.
