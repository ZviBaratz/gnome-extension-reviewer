#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LINT="$SCRIPT_DIR/skills/ego-lint/scripts/ego-lint.sh"
FIXTURES="$SCRIPT_DIR/tests/fixtures"
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

assert_exit_code() {
    local label="$1" expected="$2"
    if [[ "$exit_code" -eq "$expected" ]]; then
        echo -e "  ${GREEN}✓${NC} $label (exit code: $exit_code)"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo -e "  ${RED}✗${NC} $label (expected exit code $expected, got $exit_code)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

run_lint() {
    local fixture="$1"
    output=""
    exit_code=0
    output="$(bash "$LINT" "$FIXTURES/$fixture" 2>&1)" || exit_code=$?
}

echo "============================================"
echo "  ego-lint Test Runner"
echo "============================================"
echo ""

# --- valid-extension ---
echo "=== valid-extension ==="
run_lint "valid-extension@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_not_contains "no FAIL results" "\[FAIL\]"
assert_output_contains "metadata passes" "\[PASS\].*metadata/valid-json"
assert_output_contains "no console.log" "\[PASS\].*no-console-log"
assert_output_contains "no deprecated modules" "\[PASS\].*no-deprecated-modules"
assert_output_contains "no web APIs" "\[PASS\].*R-WEB-01"
assert_output_contains "no binary files" "\[PASS\].*no-binary-files"
assert_output_contains "license exists" "\[PASS\].*license"
assert_output_contains "schema checks pass" "\[PASS\].*schema/exists"
assert_output_contains "import checks pass" "\[PASS\].*imports/segregation"
echo ""

# --- bad-metadata ---
echo "=== bad-metadata ==="
run_lint "bad-metadata"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on missing uuid" "\[FAIL\].*metadata/required-fields.*uuid"
assert_output_contains "fails on shell-version type" "\[FAIL\].*metadata/shell-version-array"
echo ""

# --- import-violation ---
echo "=== import-violation ==="
run_lint "import-violation"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on GTK import" "\[FAIL\].*imports/no-gtk-in-extension"
echo ""

# --- console-log ---
echo "=== console-log ==="
run_lint "console-log"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on console.log" "\[FAIL\].*no-console-log"
echo ""

# --- deprecated-modules ---
echo "=== deprecated-modules ==="
run_lint "deprecated-modules"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on deprecated module" "\[FAIL\].*no-deprecated-modules"
echo ""

# --- web-apis ---
echo "=== web-apis ==="
run_lint "web-apis"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on setTimeout" "\[FAIL\].*R-WEB-01"
assert_output_contains "fails on XMLHttpRequest" "\[FAIL\].*R-WEB-04"
assert_output_contains "fails on document.*" "\[FAIL\].*R-WEB-06"
echo ""

# --- deprecated-imports ---
echo "=== deprecated-imports ==="
run_lint "deprecated-imports"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on ExtensionUtils" "\[FAIL\].*R-DEPR-05"
assert_output_contains "fails on Tweener" "\[FAIL\].*R-DEPR-06"
echo ""

# --- non-standard-metadata ---
echo "=== non-standard-metadata ==="
run_lint "non-standard-metadata"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on UUID missing @" "\[FAIL\].*metadata/uuid-at-sign"
assert_output_contains "warns on non-standard fields" "\[WARN\].*metadata/non-standard-field"
assert_output_contains "warns on deprecated version" "\[WARN\].*metadata/deprecated-version"
echo ""

# --- bad-package ---
echo "=== bad-package ==="
run_lint "bad-package"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on nested structure" "\[FAIL\].*package/nested-structure"
assert_output_contains "fails on missing compiled schemas" "\[FAIL\].*package/compiled-schemas"
echo ""

# --- ai-slop ---
echo "=== ai-slop ==="
run_lint "ai-slop@test"
assert_exit_code "exits with 0 (warnings only, no failures)" 0
assert_output_contains "warns on try-catch density" "\[WARN\].*quality.*try-catch"
assert_output_contains "warns on impossible state" "\[WARN\].*quality/impossible-state"
assert_output_contains "warns on pendulum pattern" "\[WARN\].*quality/pendulum-pattern"
assert_output_contains "warns on module state" "\[WARN\].*quality/module-state"
assert_output_contains "warns on empty catch" "\[WARN\].*quality/empty-catch"
assert_output_contains "warns on JSDoc" "\[WARN\].*R-SLOP-01"
echo ""

# --- Summary ---
echo "============================================"
echo "  Results: $PASS_COUNT passed, $FAIL_COUNT failed"
echo "============================================"

if [[ "$FAIL_COUNT" -gt 0 ]]; then
    echo -e "${RED}SOME TESTS FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}ALL TESTS PASSED${NC}"
    exit 0
fi
