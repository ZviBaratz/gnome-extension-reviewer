# Cross-file resource tracking assertions
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- cross-file-leak ---
echo "=== cross-file-leak ==="
run_lint "cross-file-leak@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "detects orphan signal in manager.js" "resource-tracking/orphan-signal.*manager"
assert_output_contains "detects orphan filemonitor in controller.js" "resource-tracking/orphan-filemonitor.*controller"
assert_output_contains "reports ownership tracking" "resource-tracking/ownership"
echo ""

# --- cross-file-clean ---
echo "=== cross-file-clean ==="
run_lint "cross-file-clean@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_contains "passes resource tracking" "\[PASS\].*resource-tracking/ownership"
assert_output_not_contains "no orphan warnings" "resource-tracking/orphan"
echo ""
