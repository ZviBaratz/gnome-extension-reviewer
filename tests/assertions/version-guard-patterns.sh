# Version guard pattern suppression tests
# Sourced by run-tests.sh

echo "=== version-guard-fallback ==="
run_lint "version-guard-fallback@test"
assert_exit_code "exits with 0 (all version guards suppressed)" 0
assert_output_not_contains "no FAIL for R-VER49-02 with fallback guard" "\[FAIL\].*R-VER49-02"
assert_output_not_contains "no FAIL for R-VER47-01 with ternary guard" "\[FAIL\].*R-VER47-01"
echo ""

echo "=== version-guard-boolean ==="
run_lint "version-guard-boolean@test"
assert_exit_code "exits with 0 (all version guards suppressed)" 0
assert_output_not_contains "no FAIL for R-VER46-07 with boolean guard" "\[FAIL\].*R-VER46-07"
assert_output_not_contains "no FAIL for R-VER44-02 with compositor guard" "\[FAIL\].*R-VER44-02"
assert_output_not_contains "no FAIL for R-VER48-02 with feature detection guard" "\[FAIL\].*R-VER48-02"
echo ""
