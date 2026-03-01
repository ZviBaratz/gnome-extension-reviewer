# Field test improvements — assertions for rules added from ego-submit field testing
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- slop-object-freeze (R-SLOP-35) ---
echo "=== slop-object-freeze ==="
run_lint "slop-object-freeze@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on Object.freeze" "\[WARN\].*R-SLOP-35"
echo ""

# --- slop-long-params (R-SLOP-38) ---
echo "=== slop-long-params ==="
run_lint "slop-long-params@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on over-long parameter name" "\[WARN\].*R-SLOP-38"
echo ""

# --- slop-promise-wrapper (R-SLOP-40) ---
echo "=== slop-promise-wrapper ==="
run_lint "slop-promise-wrapper@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on manual Promise wrapper" "\[WARN\].*R-SLOP-40"
echo ""

# --- slop-underscore-export (R-SLOP-43) ---
echo "=== slop-underscore-export ==="
run_lint "slop-underscore-export@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on underscore-prefixed export" "\[WARN\].*R-SLOP-43"
echo ""

# --- promisify-module-scope (R-QUAL-33) ---
echo "=== promisify-module-scope ==="
run_lint "promisify-module-scope@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on Gio._promisify at module scope" "\[WARN\].*R-QUAL-33"
echo ""

# --- prefs-constructor-clean (FP fix) ---
echo "=== prefs-constructor-clean ==="
run_lint "prefs-constructor-clean@test"
assert_exit_code "exits with 0 (no FAIL)" 0
assert_output_not_contains "no constructor-resources WARN for prefs.js" "\[WARN\].*quality/constructor-resources"
echo ""

# --- stage-add-child (R-LIFE-19) ---
echo "=== stage-add-child ==="
run_lint "stage-add-child@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on global.stage.add_child" "\[WARN\].*R-LIFE-19"
echo ""

# --- shell-keybinding-mode (R-DEPR-11) ---
echo "=== shell-keybinding-mode ==="
run_lint "shell-keybinding-mode@test"
assert_exit_code "exits with 1 (blocking)" 1
assert_output_contains "fails on Shell.KeyBindingMode" "\[FAIL\].*R-DEPR-11"
echo ""

# --- sync-file-io (R-QUAL-34) ---
echo "=== sync-file-io ==="
run_lint "sync-file-io@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on synchronous enumerate_children" "\[WARN\].*R-QUAL-34"
echo ""

# --- native-timer-untracked (lifecycle native timer) ---
echo "=== native-timer-untracked ==="
run_lint "native-timer-untracked@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on untracked setTimeout" "\[WARN\].*lifecycle/untracked-timeout"
echo ""
