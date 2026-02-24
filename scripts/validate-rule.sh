#!/usr/bin/env bash
# validate-rule.sh — Validate a single pattern rule against a test fixture
#
# Usage: validate-rule.sh RULE_ID FIXTURE_DIR
#   Example: validate-rule.sh R-SEC-01 tests/fixtures/security-patterns@test

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: validate-rule.sh RULE_ID FIXTURE_DIR"
    echo "  Example: validate-rule.sh R-SEC-01 tests/fixtures/security-patterns@test"
    exit 1
fi

RULE_ID="$1"
FIXTURE_DIR="$2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RULES_FILE="$SCRIPT_DIR/rules/patterns.yaml"
APPLY_SCRIPT="$SCRIPT_DIR/skills/ego-lint/scripts/apply-patterns.py"

# Check rule exists in patterns.yaml
if ! grep -q "id: $RULE_ID" "$RULES_FILE"; then
    echo "ERROR: Rule $RULE_ID not found in $RULES_FILE"
    exit 1
fi

# Check fixture exists
if [[ ! -d "$FIXTURE_DIR" ]]; then
    echo "ERROR: Fixture directory $FIXTURE_DIR not found"
    exit 1
fi

echo "Validating rule $RULE_ID against $FIXTURE_DIR"
echo ""

# Run pattern engine
output="$(python3 "$APPLY_SCRIPT" "$RULES_FILE" "$FIXTURE_DIR" 2>&1)" || true

# Filter to just this rule
rule_output="$(echo "$output" | grep "$RULE_ID" || true)"

if [[ -n "$rule_output" ]]; then
    echo "$rule_output" | while IFS='|' read -r status check detail; do
        status="${status#"${status%%[![:space:]]*}"}"
        printf "[%-4s] %-30s %s\n" "$status" "$check" "$detail"
    done
    echo ""
    echo "Rule $RULE_ID matched in fixture."
else
    echo "Rule $RULE_ID did NOT match in fixture."
    echo ""
    echo "Full output from apply-patterns.py:"
    echo "$output"
    exit 1
fi
