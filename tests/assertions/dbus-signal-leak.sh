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
assert_exit_code "exits with 1 (bare connect always fails)" 1
assert_output_contains "fails on bare connectSignal despite other cleanup" "\[FAIL\].*lifecycle/dbus-signal-leak"
assert_output_not_contains "no WARN when file has disconnectSignal" "\[WARN\].*lifecycle/dbus-signal-leak"
echo ""

echo "=== dbus-signal-array-storage ==="
run_lint "dbus-signal-array-storage@test"
assert_exit_code "exits with 0 (array storage is not bare connect)" 0
assert_output_not_contains "no dbus-signal-leak FP on array storage" "\[FAIL\].*lifecycle/dbus-signal-leak"
assert_output_not_contains "no WARN when file has disconnectSignal" "\[WARN\].*lifecycle/dbus-signal-leak"
echo ""

echo "=== dbus-signal-mixed-cleanup ==="
run_lint "dbus-signal-mixed-cleanup@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails despite GObject cleanup" "\[FAIL\].*lifecycle/dbus-signal-leak"
echo ""

echo "=== dbus-signal-stored-no-disconnect ==="
run_lint "dbus-signal-stored-no-disconnect@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on stored connect without disconnect" "\[WARN\].*lifecycle/dbus-signal-leak"
assert_output_not_contains "no FAIL for stored connect" "\[FAIL\].*lifecycle/dbus-signal-leak"
echo ""

echo "=== dbus-signal-bind-cleanup ==="
run_lint "dbus-signal-bind-cleanup@test"
assert_exit_code "exits with 0 (bind cleanup recognized)" 0
assert_output_not_contains "no FAIL with bind cleanup" "\[FAIL\].*lifecycle/dbus-signal-leak"
assert_output_not_contains "no WARN with bind cleanup" "\[WARN\].*lifecycle/dbus-signal-leak"
echo ""
