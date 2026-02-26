# Batch 3: Version compatibility gaps and new rules
# Sourced by run-tests.sh

echo "=== ver49-dnd-switch ==="
run_lint "ver49-dnd-switch@test"
assert_exit_code "exits with failure (DoNotDisturbSwitch)" 1
assert_output_contains "R-VER49-10 fires on DoNotDisturbSwitch" "\[FAIL\].*R-VER49-10"

echo "=== ver49-unmaximize-flags ==="
run_lint "ver49-unmaximize-flags@test"
assert_exit_code "exits with failure (MaximizeFlags in unmaximize)" 1
assert_output_contains "R-VER49-11 fires on unmaximize MaximizeFlags" "\[FAIL\].*R-VER49-11"

echo "=== base64-usage ==="
run_lint "base64-usage@test"
assert_output_contains "R-SEC-23 fires on atob/btoa" "\[WARN\].*R-SEC-23"
