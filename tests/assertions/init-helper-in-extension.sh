# Tests that helper class constructors in extension.js are not flagged
# while Extension class constructors still are
# Sourced by run-tests.sh

echo "=== init-helper-in-extension ==="
run_lint "init-helper-in-extension@test"
assert_exit_code "exits with 1 (Extension constructor violation)" 1
assert_output_contains "flags Extension constructor Shell global" "\[FAIL\].*init/shell-modification.*extension.js:20"
assert_output_not_contains "no FP on helper class constructor" "init/shell-modification.*extension.js:8"
echo ""
