# Phase 13: Batch 8 — P2 import segregation enhancement
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- shared-import-violation ---
echo "=== shared-import-violation ==="
run_lint "shared-import-violation@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on shared module Shell import" "\[FAIL\].*imports/shared-module-shell"
echo ""

# --- import-guarded: importInShellOnly/importInPrefsOnly guard pattern ---
echo "=== import-guarded ==="
run_lint "import-guarded@test"
assert_output_not_contains "no false positive for importInShellOnly string arg" "imports/shared-module-shell"
assert_output_not_contains "no false positive for importInPrefsOnly Gtk string arg" "imports/no-gtk-in-extension"
echo ""
