# R-QUAL-36: CRITICAL notification urgency
# Sourced by run-tests.sh

echo "=== urgency-critical ==="
run_lint "urgency-critical@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on CRITICAL urgency" "\[WARN\].*R-QUAL-36"
echo ""
