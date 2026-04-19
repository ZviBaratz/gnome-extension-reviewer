# Tests that helper class constructors in extension.js are not flagged
# while Extension class constructors still are.
# Note: Extension constructor Shell global reads are downgraded to WARN
# (Option 4) — reads are advisory, not blocking.
# Sourced by run-tests.sh

echo "=== init-helper-in-extension ==="
run_lint "init-helper-in-extension@test"
assert_exit_code "exits with 0 (WARN only, reads are advisory)" 0
assert_output_contains "warns on Extension constructor Shell global read" "\[WARN\].*init/shell-modification.*extension.js:20"
assert_output_not_contains "no FAIL on Shell global read" "\[FAIL\].*init/shell-modification"
assert_output_not_contains "no FP on helper class constructor" "init/shell-modification.*extension.js:8"
echo ""
