# tsconfig.json JSDoc suppression assertions
# When tsconfig.json is present, R-SLOP-01/02 are suppressed at the pattern level.
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, etc.

echo "=== tsconfig-jsdoc (tsconfig.json suppresses R-SLOP-01/02) ==="
run_lint "tsconfig-jsdoc@test"
assert_exit_code "exits with 0 (no blocking issues)" 0
assert_output_not_contains "R-SLOP-01 suppressed for TS project" "\[WARN\].*R-SLOP-01"
assert_output_not_contains "R-SLOP-02 suppressed for TS project" "\[WARN\].*R-SLOP-02"
assert_output_contains "R-SLOP-01 shows as SKIP" "\[SKIP\].*R-SLOP-01.*tsconfig"
assert_output_contains "R-SLOP-02 shows as SKIP" "\[SKIP\].*R-SLOP-02.*tsconfig"
echo ""
