# Field test #10: isLocked guard exemption (closes #27)

# --- islocked-guard (sessionMode.isLocked as guard, not lock screen) ---
echo "=== islocked-guard ==="
run_lint "islocked-guard@test"
assert_exit_code "exits with 0" 0
assert_output_not_contains "no impossible-state for isLocked guard" "\[WARN\].*quality/impossible-state"
assert_output_not_contains "no session-modes-consistency for isLocked" "\[WARN\].*session-modes-consistency"
echo ""
