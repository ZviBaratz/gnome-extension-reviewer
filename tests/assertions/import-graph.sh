# Import graph traversal tests
# Sourced by run-tests.sh

echo "=== import-graph ==="
run_lint "import-graph@test"
assert_exit_code "exits with 1 (shared module has GTK in extension path)" 1
assert_output_contains "shared module FAIL" "\[FAIL\].*imports/no-gtk-in-extension.*lib/shared.js"
assert_output_not_contains "prefs-only module not flagged" "\[FAIL\].*imports/no-gtk-in-extension.*lib/prefsHelper.js"
echo ""
