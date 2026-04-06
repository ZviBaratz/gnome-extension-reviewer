# constructor-resources: no FP on inner/callback object connects
# Sourced by run-tests.sh

echo "=== constructor-inner-object ==="
run_lint "constructor-inner-object@test"
assert_exit_code "exits with 0 (inner object connects not flagged)" 0
assert_output_not_contains "no WARN for shader/callback-param .connect()" "\[WARN\].*constructor-resources"
assert_output_contains "constructor-resources passes" "\[PASS\].*constructor-resources"
echo ""
