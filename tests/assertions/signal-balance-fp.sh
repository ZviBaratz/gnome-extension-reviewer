# --- signal-non-gobject (Sub-issue A: non-signal .connect() not counted) ---
echo "=== signal-non-gobject ==="
run_lint "signal-non-gobject@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_contains "signal balance OK" "\[PASS\].*lifecycle/signal-balance"
assert_output_not_contains "no signal imbalance warning" "\[WARN\].*lifecycle/signal-balance"
echo ""

# --- signal-destroy-connect (Sub-issue B: destroy signal not counted) ---
echo "=== signal-destroy-connect ==="
run_lint "signal-destroy-connect@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_contains "signal balance OK" "\[PASS\].*lifecycle/signal-balance"
assert_output_not_contains "no signal imbalance warning" "\[WARN\].*lifecycle/signal-balance"
echo ""

# --- signal-local-variable (Sub-issue C: local-variable signal not counted) ---
echo "=== signal-local-variable ==="
run_lint "signal-local-variable@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_contains "signal balance OK" "\[PASS\].*lifecycle/signal-balance"
assert_output_not_contains "no signal imbalance warning" "\[WARN\].*lifecycle/signal-balance"
echo ""
