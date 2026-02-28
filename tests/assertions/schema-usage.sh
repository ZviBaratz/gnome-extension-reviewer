# Schema key usage validation assertions

# --- schema-unused-key ---
echo "=== schema-unused-key ==="
run_lint "schema-unused-key@test"
assert_exit_code "exits with 0 (unused is advisory)" 0
assert_output_contains "detects unused schema key" "\[WARN\].*schema-usage/unused-key"
echo ""

# --- schema-undefined-key ---
echo "=== schema-undefined-key ==="
run_lint "schema-undefined-key@test"
assert_exit_code "exits with 1 (undefined key is blocking)" 1
assert_output_contains "detects undefined schema key" "\[FAIL\].*schema-usage/undefined-key"
echo ""

# --- schema-keys-clean ---
echo "=== schema-keys-clean ==="
run_lint "schema-keys-clean@test"
assert_output_contains "all schema keys used" "\[PASS\].*schema-usage/all-keys-used"
assert_output_contains "all referenced keys defined" "\[PASS\].*schema-usage/undefined-key"
echo ""
