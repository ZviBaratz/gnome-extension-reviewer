# Subprocess directory exclusion tests
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_output_not_contains, etc.
#
# Verifies that top-level directories containing a GJS subprocess entry point
# (#!/usr/bin/env gjs shebang) are auto-detected and excluded from ALL lint checks:
# pattern rules (apply-patterns), init checks (check-init), lifecycle checks
# (check-lifecycle), and quality checks (check-quality).
# Covers the DING (Desktop Icons NG) architecture where app/ bundles a standalone GJS process.

echo "=== subprocess-dir-exclusion ==="
run_lint "subprocess-dir-exclusion@test"
assert_exit_code "exits with 0 (subprocess dir not flagged)" 0
# Legacy imports in app/ subprocess must not produce R-DEPR-04 FAILs
assert_output_not_contains "no R-DEPR-04 from subprocess dir" "\[FAIL\].*R-DEPR-04.*app"
# var declarations in app/ subprocess must not produce R-DEPR-09 WARNs
assert_output_not_contains "no R-DEPR-09 from subprocess dir" "\[WARN\].*R-DEPR-09.*app"
# GSettings.connect() in subprocess must not produce gsettings-signal-leak FAILs
assert_output_not_contains "no gsettings-signal-leak from subprocess dir" "\[FAIL\].*gsettings-signal-leak.*app"
# Quality checks must not fire on subprocess files
assert_output_not_contains "no quality checks from subprocess dir" "\[FAIL\].*quality/.*app"
# console.log() in subprocess must not produce no-console-log FAILs
assert_output_not_contains "no no-console-log FAIL from subprocess dir" "\[FAIL\].*no-console-log"
# SKIP notice must be emitted
assert_output_contains "subprocess-dir-exclusion SKIP emitted" "\[SKIP\].*subprocess-dir-exclusion"
echo ""
