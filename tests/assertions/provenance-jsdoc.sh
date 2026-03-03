# Provenance-gated JSDoc suppression assertions
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- high-provenance-jsdoc ---
echo "=== high-provenance-jsdoc ==="
run_lint "high-provenance-jsdoc@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_contains "provenance suppresses JSDoc" "provenance/jsdoc-suppressed"
assert_output_contains "provenance score 4+" "provenance-score=[4-9]"
assert_output_not_contains "JSDoc WARNs suppressed from output" "\[WARN\].*R-SLOP-0[12]"
echo ""
