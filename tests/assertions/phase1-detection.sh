# Phase 1: Detection completeness assertions
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- injection-leak ---
echo "=== injection-leak ==="
run_lint "injection-leak@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "detects missing InjectionManager.clear()" "\[FAIL\].*lifecycle/injection-cleanup"
echo ""

# --- lockscreen-signals ---
echo "=== lockscreen-signals ==="
run_lint "lockscreen-signals@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "detects unguarded keyboard signals" "\[FAIL\].*lifecycle/lockscreen-signals"
echo ""

# --- init-modification ---
echo "=== init-modification ==="
run_lint "init-modification@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "detects init-time Shell modification" "\[FAIL\].*init/shell-modification.*extension.js"
assert_output_contains "detects init-time GObject constructor" "\[FAIL\].*init/shell-modification.*helper.js"
echo ""

# --- constructor-gobject ---
echo "=== constructor-gobject ==="
run_lint "constructor-gobject@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "detects Gio.File in constructor" "\[FAIL\].*init/shell-modification"
echo ""

# --- gtk3-prefs ---
echo "=== gtk3-prefs ==="
run_lint "gtk3-prefs@test"
assert_output_contains "detects GTK3 widgets in prefs.js" "\[WARN\].*R-PREFS-04"
echo ""

# --- timeout-no-remove ---
echo "=== timeout-no-remove ==="
run_lint "timeout-no-remove@test"
assert_output_contains "detects missing Source.remove" "\[WARN\].*lifecycle/timeout-not-removed"
echo ""
