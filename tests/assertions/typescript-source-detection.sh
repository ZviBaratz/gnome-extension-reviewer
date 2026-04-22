# TypeScript source repo detection assertions
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- typescript-source-repo (unbuilt .ts files, no extension.js) ---
echo "=== typescript-source-repo ==="
run_lint "typescript-source-repo@test"
assert_exit_code "exits with 1 (blocking issue: missing extension.js)" 1
assert_output_contains "FAIL with TypeScript hint" "\[FAIL\].*file-structure/extension\.js.*TypeScript source detected"
assert_output_not_contains "no bare 'extension.js is missing'" "extension\.js is missing$"
echo ""
