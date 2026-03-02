# Managed constructor-resources suppression tests
# Sourced by run-tests.sh

echo "=== managed-constructor ==="
run_lint "managed-constructor@test"
assert_exit_code "exits with 0 (managed constructors suppressed)" 0
assert_output_not_contains "no WARN for managed constructor-resources" "\[WARN\].*constructor-resources"
assert_output_contains "constructor-resources passes" "\[PASS\].*constructor-resources"
echo ""
