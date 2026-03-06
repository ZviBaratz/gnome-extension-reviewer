# Compiled TypeScript detection assertions
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- compiled-ts-extension (with esbuild markers) ---
echo "=== compiled-ts-extension ==="
run_lint "compiled-ts-extension@test"
assert_exit_code "exits with 0 (no blocking issues)" 0
assert_output_contains "detects compiled TypeScript" "\[WARN\].*compiled-typescript.*compiled from TypeScript"
assert_output_contains "R-DEPR-09 skipped for compiled TS" "\[SKIP\].*R-DEPR-09.*compiled TypeScript"
assert_output_contains "R-SLOP-38 skipped for compiled TS" "\[SKIP\].*R-SLOP-38.*compiled TypeScript"
assert_output_not_contains "no-destroy-method suppressed" "resource-tracking/no-destroy-method"
assert_output_contains "resource tracking still runs" "resource-tracking/ownership"
echo ""
