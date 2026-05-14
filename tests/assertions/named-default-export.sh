# Named default export false-positive regression tests (issue #283)
# Verifies that `export { X as default }` is accepted as a valid default export
# for both R-FILE-07 (extension.js) and R-PREFS-02 (prefs.js).
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

echo "=== named-default-export ==="
run_lint "named-default-export@test"
assert_exit_code "exits with 0 (no blocking issues)" 0
assert_output_not_contains "no R-FILE-07 false positive for extension.js named export" "lifecycle/default-export.*missing"
assert_output_contains "extension.js default export passes" "\[PASS\].*lifecycle/default-export"
assert_output_not_contains "no R-PREFS-02 false positive for prefs.js named export" "prefs/default-export.*missing"
assert_output_contains "prefs.js default export passes" "\[PASS\].*prefs/default-export"
assert_output_contains "prefs.js extends check runs and passes" "\[PASS\].*prefs/extends-base"
echo ""
