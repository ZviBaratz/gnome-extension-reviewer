# R-LIFE-25: D-Bus proxy signal leak detection
# Sourced by run-tests.sh

echo "=== dbus-signal-leak ==="
run_lint "dbus-signal-leak@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on bare connectSignal" "\[FAIL\].*lifecycle/dbus-signal-leak"
assert_output_contains "mentions connectSignal" "connectSignal"
echo ""

echo "=== dbus-signal-auto-cleanup ==="
run_lint "dbus-signal-auto-cleanup@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_contains "passes with auto-cleanup" "\[PASS\].*lifecycle/dbus-signal-leak"
assert_output_not_contains "no dbus-signal-leak FP" "\[FAIL\].*lifecycle/dbus-signal-leak"
echo ""
