# Phase 8: Reviewer-grade understanding assertions (Batch 2)
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- shell-version-minor ---
echo "=== shell-version-minor ==="
run_lint "shell-version-minor@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on GNOME 40+ minor version" "\[FAIL\].*metadata/shell-version-minor"
echo ""

# --- destroy-no-null ---
echo "=== destroy-no-null ==="
run_lint "destroy-no-null@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on destroy without null" "\[WARN\].*lifecycle/destroy-no-null"
echo ""

# --- typeof-super-method ---
echo "=== typeof-super-method ==="
run_lint "typeof-super-method@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on typeof super.method (R-SLOP-30)" "\[FAIL\].*R-SLOP-30"
echo ""
