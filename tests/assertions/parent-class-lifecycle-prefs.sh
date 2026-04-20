# Parent class enable/disable and prefs method inheritance assertions
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- lifecycle-parent-class-enable-disable ---
echo "=== lifecycle-parent-class-enable-disable ==="
run_lint "lifecycle-parent-class-enable-disable@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_contains "passes when enable/disable in parent class" "\[PASS\].*lifecycle/enable-disable"
assert_output_not_contains "no enable-method FP" "\[FAIL\].*lifecycle/enable-method"
assert_output_not_contains "no disable-method FP" "\[FAIL\].*lifecycle/disable-method"
echo ""

# --- prefs-parent-class-method ---
echo "=== prefs-parent-class-method ==="
run_lint "prefs-parent-class-method@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_contains "passes when fillPreferencesWindow in parent class" "\[PASS\].*prefs/prefs-method"
assert_output_not_contains "no missing-prefs-method FP" "\[FAIL\].*prefs/missing-prefs-method"
echo ""
