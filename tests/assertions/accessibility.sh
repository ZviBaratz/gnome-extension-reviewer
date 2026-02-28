# Accessibility check assertions

# --- a11y-missing-name ---
echo "=== a11y-missing-name ==="
run_lint "a11y-missing-name@test"
assert_exit_code "exits with 0 (accessibility is advisory)" 0
assert_output_contains "detects icon-only button without accessible_name" "\[WARN\].*accessibility/accessible-name"
assert_output_contains "detects widget without accessible_role" "\[WARN\].*accessibility/widget-role"
echo ""
