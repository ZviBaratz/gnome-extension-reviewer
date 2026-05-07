# Subprocess directory exclusion tests
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_output_not_contains, etc.
#
# Verifies that top-level directories containing a GJS subprocess entry point
# (#!/usr/bin/env gjs shebang) are auto-detected and excluded from pattern rules.
# Covers the DING (Desktop Icons NG) architecture where app/ bundles a standalone GJS process.

echo "=== subprocess-dir-exclusion ==="
run_lint "subprocess-dir-exclusion@test"
assert_exit_code "exits with 0 (subprocess dir not flagged)" 0
# Legacy imports in app/ subprocess must not produce R-DEPR-04 FAILs
assert_output_not_contains "no R-DEPR-04 from subprocess dir" "\[FAIL\].*R-DEPR-04.*app"
# var declarations in app/ subprocess must not produce R-DEPR-09 WARNs
assert_output_not_contains "no R-DEPR-09 from subprocess dir" "\[WARN\].*R-DEPR-09.*app"
# SKIP notice must be emitted
assert_output_contains "subprocess-dir-exclusion SKIP emitted" "\[SKIP\].*subprocess-dir-exclusion"
echo ""
