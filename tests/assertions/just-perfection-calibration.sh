# Field test #10: Just Perfection calibration fixes

# --- src-license-fallback (LICENSE in parent dir of src/) ---
echo "=== src-license-fallback ==="
run_lint "src-license-fallback@test/src"
assert_exit_code "exits with 0 (license found in parent dir)" 0
assert_output_contains "license found via parent fallback" "\[PASS\].*license"
assert_output_contains "UUID-dir skipped for src/ layout" "\[PASS\].*metadata/uuid-matches-dir.*src/ layout"
echo ""

# --- islocked-guard (sessionMode.isLocked as guard, not lock screen) ---
echo "=== islocked-guard ==="
run_lint "islocked-guard@test"
assert_exit_code "exits with 0" 0
assert_output_not_contains "no impossible-state for isLocked guard" "\[WARN\].*quality/impossible-state"
assert_output_not_contains "no session-modes-consistency for isLocked" "\[WARN\].*session-modes-consistency"
echo ""

# --- proto-override-dedup (each prototype warned only once) ---
echo "=== proto-override-dedup ==="
run_lint "proto-override-dedup@test"
assert_output_contains "prototype override detected" "\[WARN\].*lifecycle/prototype-override.*BackgroundMenu.prototype.open"
assert_output_contains "search prototype override detected" "\[WARN\].*lifecycle/prototype-override.*SearchController.prototype.startSearch"
echo ""
