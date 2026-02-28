---
description: Complete pre-submission validation for extensions.gnome.org
allowed-tools: Bash(bash *ego-lint.sh*), Read, Glob, Grep
---

Run the full pre-submission validation pipeline for extensions.gnome.org.

## Target

Extension directory: $ARGUMENTS (if empty, use the current working directory).

## Instructions

Read and follow the submission pipeline in this plugin's `skills/ego-submit/SKILL.md`. It orchestrates: ego-lint (automated checks) → ego-review (manual code review) → packaging validation, producing a final submission readiness report.
