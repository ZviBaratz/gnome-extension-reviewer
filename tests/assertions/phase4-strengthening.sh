# Phase 4: Strengthening assertions (WS2 checks)
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- promisify-in-enable ---
echo "=== promisify-in-enable ==="
run_lint "promisify-in-enable@test"
assert_output_contains "warns on promisify in enable" "\[WARN\].*init/promisify-in-enable"
echo ""

# --- run-dispose-no-comment ---
echo "=== run-dispose-no-comment ==="
run_lint "run-dispose-no-comment@test"
assert_output_contains "warns on run_dispose without comment" "\[WARN\].*quality/run-dispose-no-comment"
echo ""

# --- shell-class-override ---
echo "=== shell-class-override ==="
run_lint "shell-class-override@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on shell class override" "\[FAIL\].*css/shell-class-override"
echo ""
