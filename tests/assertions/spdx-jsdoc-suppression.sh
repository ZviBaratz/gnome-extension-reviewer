# SPDX license header JSDoc suppression assertions
# When >= 70% of JS files have SPDX headers, R-SLOP-01/02 are suppressed at the pattern level.
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, etc.

echo "=== spdx-jsdoc (SPDX headers suppress R-SLOP-01/02) ==="
run_lint "spdx-jsdoc@test"
assert_exit_code "exits with 0 (no blocking issues)" 0
assert_output_not_contains "R-SLOP-01 suppressed for SPDX project" "\[WARN\].*R-SLOP-01"
assert_output_not_contains "R-SLOP-02 suppressed for SPDX project" "\[WARN\].*R-SLOP-02"
assert_output_contains "R-SLOP-01 shows as SKIP" "\[SKIP\].*R-SLOP-01.*SPDX"
assert_output_contains "R-SLOP-02 shows as SKIP" "\[SKIP\].*R-SLOP-02.*SPDX"
echo ""
