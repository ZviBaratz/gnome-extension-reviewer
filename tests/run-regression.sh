#!/usr/bin/env bash
set -euo pipefail

# Standalone regression runner for hara-hachi-bu baseline.
# Run locally to verify no new false positives from newly added checks.
# Not part of CI (depends on locally installed extension).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LINT="$SCRIPT_DIR/skills/ego-lint/scripts/ego-lint.sh"
PASS_COUNT=0
FAIL_COUNT=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

assert_output_contains() {
    local label="$1" pattern="$2"
    if echo "$output" | grep -qE "$pattern"; then
        echo -e "  ${GREEN}✓${NC} $label"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo -e "  ${RED}✗${NC} $label (expected pattern: $pattern)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

assert_output_not_contains() {
    local label="$1" pattern="$2"
    if ! echo "$output" | grep -qE "$pattern"; then
        echo -e "  ${GREEN}✓${NC} $label"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo -e "  ${RED}✗${NC} $label (should NOT match: $pattern)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

echo "============================================"
echo "  ego-lint Regression Runner"
echo "============================================"
echo ""

# Source the regression assertions
ASSERTIONS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/assertions"
if [[ -f "$ASSERTIONS_DIR/hara-hachi-bu-regression.sh" ]]; then
    source "$ASSERTIONS_DIR/hara-hachi-bu-regression.sh"
else
    echo "Assertion file not found: $ASSERTIONS_DIR/hara-hachi-bu-regression.sh"
    exit 1
fi

# --- Summary ---
echo "============================================"
echo "  Results: $PASS_COUNT passed, $FAIL_COUNT failed"
echo "============================================"

if [[ "$FAIL_COUNT" -gt 0 ]]; then
    echo -e "${RED}REGRESSION FAILURES DETECTED${NC}"
    exit 1
else
    echo -e "${GREEN}ALL REGRESSION CHECKS PASSED${NC}"
    exit 0
fi
