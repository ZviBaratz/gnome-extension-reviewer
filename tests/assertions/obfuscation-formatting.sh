# Batch 4: Obfuscation and formatting detection
# Sourced by run-tests.sh

echo "=== obfuscated-code ==="
run_lint "obfuscated-code@test"
assert_exit_code "exits with failure (obfuscated names)" 1
assert_output_contains "obfuscated names detected" "\[FAIL\].*quality/obfuscated-names"

echo "=== mixed-indent ==="
run_lint "mixed-indent@test"
assert_output_contains "mixed indentation flagged" "\[WARN\].*quality/mixed-indentation"
