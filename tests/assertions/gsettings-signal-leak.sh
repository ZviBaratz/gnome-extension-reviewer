# R-LIFE-21: GSettings signal leak detection
# Sourced by run-tests.sh

echo "=== gsettings-bare-connect ==="
run_lint "gsettings-bare-connect@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on bare GSettings connect" "\[FAIL\].*lifecycle/gsettings-signal-leak"
echo ""
