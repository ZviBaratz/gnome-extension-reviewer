# Phase 14: Batch 9 — P3 low-priority items
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- donations-overflow ---
echo "=== donations-overflow ==="
run_lint "donations-overflow@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on donations array length" "\[FAIL\].*metadata/donations-array-length"
echo ""
