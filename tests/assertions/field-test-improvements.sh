# Field test improvements — assertions for rules added from ego-submit field testing
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- slop-object-freeze (R-SLOP-35) ---
echo "=== slop-object-freeze ==="
run_lint "slop-object-freeze@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on Object.freeze with inline object" "\[WARN\].*R-SLOP-35"
assert_output_not_contains "R-SLOP-35 suppressed for Object.freeze(identifier)" "\[WARN\].*R-SLOP-35.*extension\.js:13"
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
assert_output_not_contains "Gio._promisify does not trigger R-LIFE-27" "\[WARN\].*lifecycle/module-scope-prototype"
echo ""

# --- prefs-constructor-clean (FP fix) ---
echo "=== prefs-constructor-clean ==="
run_lint "prefs-constructor-clean@test"
assert_exit_code "exits with 0 (no FAIL)" 0
assert_output_not_contains "no constructor-resources WARN for prefs.js" "\[WARN\].*quality/constructor-resources"
echo ""

# --- stage-add-child (R-LIFE-22) ---
echo "=== stage-add-child ==="
run_lint "stage-add-child@test"
assert_exit_code "exits with 1 (FAIL — stage actor leak)" 1
assert_output_contains "fails on stage actor leak" "\[FAIL\].*lifecycle/stage-actor-leak"
echo ""

# --- messagetray-source-leak (R-LIFE-24) ---
echo "=== messagetray-source-leak ==="
run_lint "messagetray-source-leak@test"
assert_exit_code "exits with 0 (WARN only)" 0
assert_output_contains "warns on messageTray source leak" "\[WARN\].*lifecycle/messagetray-source-leak"
echo ""

# --- stage-add-child-clean (R-LIFE-22 negative) ---
echo "=== stage-add-child-clean ==="
run_lint "stage-add-child-clean@test"
assert_exit_code "exits with 0 (clean)" 0
assert_output_not_contains "no stage actor leak" "lifecycle/stage-actor-leak.*FAIL"
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

# --- constructor-smart-cleanup (connectSmart constructor skip) ---
echo "=== constructor-smart-cleanup ==="
run_lint "constructor-smart-cleanup@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_not_contains "no constructor-resources WARN for connectSmart class" "\[WARN\].*quality/constructor-resources"
echo ""

# --- native-timer-untracked (lifecycle native timer) ---
echo "=== native-timer-untracked ==="
run_lint "native-timer-untracked@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on untracked setTimeout" "\[WARN\].*lifecycle/untracked-timeout"
echo ""

# --- instanceof-dispatch (R-SLOP-13 guard for polymorphic dispatch) ---
echo "=== instanceof-dispatch ==="
run_lint "instanceof-dispatch@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on always-true instanceof in class method" "\[WARN\].*R-SLOP-13"
assert_output_not_contains "R-SLOP-13 suppressed for variable-assigned instanceof" "\[WARN\].*R-SLOP-13.*extension\.js:6"
echo ""
