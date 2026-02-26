# Phase 6: AI slop hardening assertions
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- excessive-null-checks ---
echo "=== excessive-null-checks ==="
run_lint "excessive-null-checks@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on excessive null checks" "\[WARN\].*quality/excessive-null-checks"
echo ""

# --- slop-spread-copy ---
echo "=== slop-spread-copy ==="
run_lint "slop-spread-copy@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on defensive spread copy" "\[WARN\].*R-SLOP-27"
echo ""

# --- slop-error-instanceof ---
echo "=== slop-error-instanceof ==="
run_lint "slop-error-instanceof@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on instanceof Error" "\[WARN\].*R-SLOP-28"
echo ""

# --- pkexec-user-writable ---
echo "=== pkexec-user-writable ==="
run_lint "pkexec-user-writable@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "detects pkexec user-writable target" "\[FAIL\].*lifecycle/pkexec-user-writable"
echo ""

# --- non-executable-script ---
echo "=== non-executable-script ==="
run_lint "non-executable-script@test"
assert_output_contains "warns on non-executable shell script" "\[WARN\].*script-permissions"
assert_output_contains "keeps non-gjs as WARN with pkexec" "\[WARN\].*non-gjs-scripts"
echo ""
