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
assert_output_contains "fails on clearTimeout" "\[FAIL\].*R-WEB-10"
assert_output_contains "fails on clearInterval" "\[FAIL\].*R-WEB-11"
echo ""

# --- deprecated-imports ---
echo "=== deprecated-imports ==="
run_lint "deprecated-imports"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on ExtensionUtils" "\[FAIL\].*R-DEPR-05"
assert_output_contains "fails on Tweener" "\[FAIL\].*R-DEPR-06"
assert_output_contains "warns on legacy imports.*" "\[WARN\].*R-DEPR-04"
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

# --- security-patterns ---
echo "=== security-patterns ==="
run_lint "security-patterns@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on eval()" "\[FAIL\].*R-SEC-01"
assert_output_contains "fails on new Function()" "\[FAIL\].*R-SEC-02"
assert_output_contains "warns on http://" "\[WARN\].*R-SEC-03"
assert_output_contains "warns on shell -c" "\[WARN\].*R-SEC-05"
echo ""

# --- logging-patterns ---
echo "=== logging-patterns ==="
run_lint "logging-patterns@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on log()" "\[WARN\].*R-LOG-02"
assert_output_contains "warns on print()" "\[WARN\].*R-LOG-03"
echo ""

# --- destroyed-density ---
echo "=== destroyed-density ==="
run_lint "destroyed-density@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on _destroyed density" "\[WARN\].*quality/destroyed-density"
echo ""

# --- mock-in-production ---
echo "=== mock-in-production ==="
run_lint "mock-in-production@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on MockDevice.js" "\[WARN\].*quality/mock-in-production"
echo ""

# --- minified-js ---
echo "=== minified-js ==="
run_lint "minified-js@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on minified JS" "\[FAIL\].*minified-js"
echo ""

# --- lifecycle-imbalance ---
echo "=== lifecycle-imbalance ==="
run_lint "lifecycle-imbalance@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on signal imbalance" "\[WARN\].*lifecycle/signal-balance"
assert_output_contains "warns on untracked timeout" "\[WARN\].*lifecycle/untracked-timeout"
echo ""

# --- missing-disable ---
echo "=== missing-disable ==="
run_lint "missing-disable@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on missing disable" "\[FAIL\].*lifecycle/disable-method"
echo ""

# --- lifecycle-clean ---
echo "=== lifecycle-clean ==="
run_lint "lifecycle-clean@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_contains "lifecycle checks pass" "\[PASS\].*lifecycle/enable-disable"
assert_output_contains "signal balance OK" "\[PASS\].*lifecycle/signal-balance"
echo ""

# --- hallucinated-apis ---
echo "=== hallucinated-apis ==="
run_lint "hallucinated-apis@test"
assert_exit_code "exits with 0 (advisories only)" 0
assert_output_contains "warns on Meta.Screen" "\[WARN\].*R-SLOP-08"
assert_output_contains "warns on St setter" "\[WARN\].*R-SLOP-09"
assert_output_contains "warns on Clutter.Actor.show_all" "\[WARN\].*R-SLOP-10"
assert_output_contains "warns on GLib.source_remove" "\[WARN\].*R-SLOP-11"
assert_output_contains "warns on typeof super.destroy" "\[WARN\].*R-SLOP-12"
assert_output_contains "warns on this instanceof" "\[WARN\].*R-SLOP-13"
echo ""

# --- run-dispose ---
echo "=== run-dispose ==="
run_lint "run-dispose@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on run_dispose" "\[WARN\].*R-SEC-06"
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
