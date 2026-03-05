# Batch 5: Widget lifecycle and settings cleanup checks
# Sourced by run-tests.sh

echo "=== widget-no-destroy ==="
run_lint "widget-no-destroy@test"
assert_output_contains "widget not destroyed in disable()" "\[WARN\].*lifecycle/widget-destroy"

echo "=== settings-no-null ==="
run_lint "settings-no-null@test"
assert_output_contains "settings not nulled in disable()" "\[WARN\].*lifecycle/settings-cleanup"
assert_output_not_contains "no gsettings-signal-leak FP (stored ID)" "\[FAIL\].*lifecycle/gsettings-signal-leak"
