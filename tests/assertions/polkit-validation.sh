# Polkit action ID cross-reference assertions

# --- polkit-mismatch ---
echo "=== polkit-mismatch ==="
run_lint "polkit-mismatch@test"
assert_output_contains "detects action ID mismatch" "\[FAIL\].*polkit/action-id-match"
assert_output_contains "detects wrong action ID prefix" "\[WARN\].*polkit/action-id-prefix"
echo ""
