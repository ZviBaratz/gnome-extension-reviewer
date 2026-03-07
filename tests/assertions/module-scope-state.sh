# R-LIFE-26: Module-scope mutable state detection
# Sourced by run-tests.sh

echo "=== module-scope-state ==="
run_lint "module-scope-state@test"
assert_exit_code "exits with 0 (advisory)" 0
assert_output_contains "warns uncleared Map" "\[WARN\].*lifecycle/module-scope-state.*Map.*cache.*not cleared"
assert_output_contains "warns uncleared Set" "\[WARN\].*lifecycle/module-scope-state.*Set.*seen.*not cleared"
echo ""

echo "=== module-scope-state-cleared ==="
run_lint "module-scope-state-cleared@test"
assert_exit_code "exits with 0 (no issues)" 0
assert_output_not_contains "no module-scope-state warning for cleared state" "\[WARN\].*lifecycle/module-scope-state"
assert_output_not_contains "no WeakMap warning" "lifecycle/module-scope-state.*WeakMap"
echo ""
