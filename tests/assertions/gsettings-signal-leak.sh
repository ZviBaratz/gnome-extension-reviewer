# R-LIFE-21: GSettings signal leak detection
# Sourced by run-tests.sh

echo "=== gsettings-bare-connect ==="
run_lint "gsettings-bare-connect@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on bare GSettings connect" "\[FAIL\].*lifecycle/gsettings-signal-leak"
echo ""

echo "=== gsettings-auto-cleanup ==="
run_lint "gsettings-auto-cleanup@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_contains "passes with auto-cleanup" "\[PASS\].*lifecycle/gsettings-signal-leak"
assert_output_not_contains "no gsettings-signal-leak FP" "\[FAIL\].*lifecycle/gsettings-signal-leak"
echo ""
