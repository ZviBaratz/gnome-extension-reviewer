# Phase 12: Batch 7 — P2 script enhancements
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- repeated-settings ---
echo "=== repeated-settings ==="
run_lint "repeated-settings@test"
assert_output_contains "warns on repeated getSettings" "\[WARN\].*quality/repeated-settings"
echo ""

# --- async-no-cancellable ---
echo "=== async-no-cancellable ==="
run_lint "async-no-cancellable@test"
assert_output_contains "warns on async without cancellable" "\[WARN\].*async/missing-cancellable"
echo ""

# --- clipboard-network ---
echo "=== clipboard-network ==="
run_lint "clipboard-network@test"
assert_output_contains "warns on clipboard + network" "\[WARN\].*lifecycle/clipboard-network"
echo ""
