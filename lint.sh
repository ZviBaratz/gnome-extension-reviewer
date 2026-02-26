#!/usr/bin/env bash
# lint.sh — convenience wrapper for ego-lint
exec "$(dirname "$0")/skills/ego-lint/scripts/ego-lint.sh" "$@"
