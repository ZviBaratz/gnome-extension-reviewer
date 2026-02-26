# Phase 3: Gap closure assertions (WS1 checks)
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- selective-disable ---
echo "=== selective-disable ==="
run_lint "selective-disable@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "detects selective disable" "\[FAIL\].*lifecycle/selective-disable"
echo ""

# --- conditional-null-guard (negative test) ---
echo "=== conditional-null-guard ==="
run_lint "conditional-null-guard@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_not_contains "no selective-disable false positive" "\[FAIL\].*lifecycle/selective-disable"
assert_output_contains "passes selective-disable check" "\[PASS\].*lifecycle/selective-disable"
echo ""

# --- unlock-no-comment ---
echo "=== unlock-no-comment ==="
run_lint "unlock-no-comment@test"
assert_output_contains "warns on missing unlock-dialog comment" "\[WARN\].*lifecycle/unlock-dialog-comment"
echo ""

# --- unlock-with-comment (negative test) ---
echo "=== unlock-with-comment ==="
run_lint "unlock-with-comment@test"
assert_output_not_contains "no unlock-dialog-comment false positive" "\[WARN\].*lifecycle/unlock-dialog-comment"
assert_output_contains "passes unlock-dialog comment check" "\[PASS\].*lifecycle/unlock-dialog-comment"
echo ""

# --- clipboard-keybinding ---
echo "=== clipboard-keybinding ==="
run_lint "clipboard-keybinding@test"
assert_output_contains "warns on clipboard + keybinding" "\[WARN\].*lifecycle/clipboard-keybinding"
echo ""

# --- manual-prototype-override ---
echo "=== manual-prototype-override ==="
run_lint "manual-prototype-override@test"
assert_output_contains "warns on prototype override" "\[WARN\].*lifecycle/prototype-override"
echo ""

# --- prefs-no-method ---
echo "=== prefs-no-method ==="
run_lint "prefs-no-method@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on missing prefs method" "\[FAIL\].*prefs/missing-prefs-method"
echo ""
