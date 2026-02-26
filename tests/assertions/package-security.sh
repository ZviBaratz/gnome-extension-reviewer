# Phase 7: Review quality optimization assertions

# --- compiled-schemas-45plus ---
echo "=== compiled-schemas-45plus ==="
run_lint "compiled-schemas-45plus@test"
assert_output_contains "detects compiled schemas forbidden for 45+" "\[FAIL\].*package/compiled-schemas"
echo ""

# --- soup-session-no-abort ---
echo "=== soup-session-no-abort ==="
run_lint "soup-session-no-abort@test"
assert_output_contains "detects missing soup session abort" "\[WARN\].*lifecycle/soup-session-abort"
echo ""

# --- network-undisclosed ---
echo "=== network-undisclosed ==="
run_lint "network-undisclosed@test"
assert_output_contains "detects undisclosed network usage" "\[WARN\].*quality/network-disclosure"
echo ""

# --- gnome50-compat ---
echo "=== gnome50-compat ==="
run_lint "gnome50-compat@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "detects releaseKeyboard() removal" "\[FAIL\].*R-VER50-01"
assert_output_contains "detects holdKeyboard() removal" "\[FAIL\].*R-VER50-02"
assert_output_contains "detects show-restart-message signal removal" "\[FAIL\].*R-VER50-03"
assert_output_contains "detects restart signal removal" "\[FAIL\].*R-VER50-04"
echo ""

# --- prefs-memory-leak ---
echo "=== prefs-memory-leak ==="
run_lint "prefs-memory-leak@test"
assert_output_contains "detects prefs memory leak" "\[WARN\].*prefs/memory-leak"
echo ""

# --- empty-destroy-override ---
echo "=== empty-destroy-override ==="
run_lint "empty-destroy-override@test"
assert_output_contains "detects empty destroy override" "\[WARN\].*R-SLOP-29"
echo ""

# --- dir-get-path ---
echo "=== dir-get-path ==="
run_lint "dir-get-path@test"
assert_output_contains "detects dir.get_path() anti-pattern" "\[WARN\].*R-QUAL-25"
echo ""

# --- custom-logger ---
echo "=== custom-logger ==="
run_lint "custom-logger@test"
assert_output_contains "detects custom logger class" "\[WARN\].*R-QUAL-26"
echo ""
