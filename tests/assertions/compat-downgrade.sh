# compat-downgrade: version-aware deprecated API gating

# Wide version range (42-48): R-VER44-01 should be downgraded to WARN
echo "=== compat-downgrade-wide ==="
run_lint "compat-downgrade-wide@test"
assert_exit_code "exits with 0 (compat-downgrade to WARN)" 0
assert_output_contains "R-VER44-01 downgraded to WARN" "\[WARN\].*R-VER44-01"
assert_output_not_contains "no R-VER44-01 FAIL" "\[FAIL\].*R-VER44-01"
echo ""

# Narrow version range (45-48): R-VER44-01 should stay FAIL
echo "=== compat-downgrade-narrow ==="
run_lint "compat-downgrade-narrow@test"
assert_exit_code "exits with 1 (no compat excuse)" 1
assert_output_contains "R-VER44-01 stays FAIL" "\[FAIL\].*R-VER44-01"
echo ""
