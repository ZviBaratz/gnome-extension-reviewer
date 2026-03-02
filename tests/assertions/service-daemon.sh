# Service daemon directory awareness tests
# Sourced by run-tests.sh

echo "=== service-daemon ==="
run_lint "service-daemon@test"
assert_exit_code "exits with 0 (service dir checks suppressed)" 0
assert_output_not_contains "no FAIL for init/shell-modification in service/" "\[FAIL\].*init/shell-modification"
assert_output_not_contains "no WARN for R-SLOP-24 in service/" "\[WARN\].*R-SLOP-24"
assert_output_not_contains "no WARN for constructor-resources in service/" "\[WARN\].*constructor-resources"
echo ""
