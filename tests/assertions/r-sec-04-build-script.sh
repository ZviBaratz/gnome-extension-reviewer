# R-SEC-04: sudo in build scripts should not fire
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- build-script-sudo (sudo in scripts/ dir is excluded from R-SEC-04) ---
echo "=== build-script-sudo ==="
run_lint "build-script-sudo@test"
assert_output_not_contains "R-SEC-04 not fired on build scripts" "\[FAIL\].*R-SEC-04"
echo ""
