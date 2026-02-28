---
description: Simulate an EGO review submission with pass/fail verdict
allowed-tools: Bash(bash *ego-lint.sh*), Read, Glob, Grep
---

Simulate how an EGO reviewer would evaluate this extension submission.

## Target

Extension directory: $ARGUMENTS (if empty, use the current working directory).

## Instructions

Read and follow the simulation process in this plugin's `skills/ego-simulate/SKILL.md`. It runs ego-lint first, then applies a 23-reason rejection taxonomy with weighted scoring from `skills/ego-simulate/references/rejection-taxonomy.md`, and produces a structured readiness report.
