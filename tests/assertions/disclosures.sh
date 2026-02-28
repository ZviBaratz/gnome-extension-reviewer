# Disclosure matrix assertions

# --- disclosure-pkexec ---
echo "=== disclosure-pkexec ==="
run_lint "disclosure-pkexec@test"
assert_output_contains "detects undisclosed pkexec" "\[WARN\].*disclosure/pkexec"
echo ""

# --- disclosure-private-api ---
echo "=== disclosure-private-api ==="
run_lint "disclosure-private-api@test"
assert_output_contains "detects undisclosed private API" "\[WARN\].*disclosure/private-api"
echo ""
