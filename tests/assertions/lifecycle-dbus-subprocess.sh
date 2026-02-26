# Phase 10: Batch 4 — P1 lifecycle checks
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- dbus-export-leak ---
echo "=== dbus-export-leak ==="
run_lint "dbus-export-leak@test"
assert_output_contains "fails on DBus export without unexport" "\[FAIL\].*lifecycle/dbus-export-leak"
echo ""

# --- timeout-reassign ---
echo "=== timeout-reassign ==="
run_lint "timeout-reassign@test"
assert_output_contains "warns on timeout reassignment without removal" "\[WARN\].*lifecycle/timeout-reassignment"
echo ""

# --- subprocess-no-cancel ---
echo "=== subprocess-no-cancel ==="
run_lint "subprocess-no-cancel@test"
assert_output_contains "warns on subprocess without cancellation" "\[WARN\].*lifecycle/subprocess-no-cancel"
echo ""

# --- resource-path-case ---
echo "=== resource-path-case ==="
run_lint "resource-path-case@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on wrong resource path case in prefs.js" "\[FAIL\].*imports/resource-path-case"
echo ""

# --- legacy-imports-pre45 ---
echo "=== legacy-imports-pre45 ==="
run_lint "legacy-imports-pre45@test"
assert_output_contains "warns on legacy imports for pre-45" "\[WARN\].*R-DEPR-04-legacy"
assert_output_not_contains "no blocking R-DEPR-04 for pre-45" "\[FAIL\].*R-DEPR-04[^-]"
echo ""
