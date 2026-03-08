# Parent-managed custom cleanup assertions
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- parent-managed-cleanup (custom cleanup method recognized) ---
echo "=== parent-managed-cleanup ==="
run_lint "parent-managed-cleanup@test"
assert_exit_code "exits with 0 (no blocking issues)" 0
assert_output_not_contains "no no-destroy-method for parent-managed child" "\[WARN\].*resource-tracking/no-destroy-method"
assert_output_not_contains "no destroy-not-called for parent-managed child" "\[WARN\].*resource-tracking/destroy-not-called"
assert_output_contains "resource tracking ran" "(PASS|WARN|FAIL).*resource-tracking"
echo ""
