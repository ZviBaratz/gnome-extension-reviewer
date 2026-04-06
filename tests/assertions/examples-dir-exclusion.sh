# Examples directory exclusion tests
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_output_not_contains, assert_exit_code, etc.

# --- examples-exclusion (examples/ directory code should skip pattern rule checks) ---
echo "=== examples-exclusion ==="
run_lint "examples-exclusion@test"
assert_exit_code "exits with 0 (examples dir code not flagged)" 0
# R-DEPR-04 must NOT fire on legacy imports.* in examples/winprops.js
assert_output_not_contains "R-DEPR-04 skipped in examples/" "\[FAIL\].*R-DEPR-04.*examples/"
assert_output_not_contains "R-DEPR-04 skipped in examples/ (warn variant)" "\[WARN\].*R-DEPR-04.*examples/"
echo ""
