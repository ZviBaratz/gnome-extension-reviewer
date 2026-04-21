# Vendored file exclusion tests
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.
#
# Verifies that files with third-party attribution headers (@license, Credits:, etc.)
# are auto-detected as vendored and excluded from pattern rules and quality checks.

echo "=== vendored-exclusion ==="
run_lint "vendored-exclusion@test"
assert_exit_code "exits with 0 (vendored file not flagged)" 0
# Pattern rules must skip vendored file (Credits: header)
assert_output_not_contains "no R-DEPR-09 (var) from vendored file" "\[WARN\].*R-DEPR-09.*css-parser"
# Quality module-state must skip vendored file (Credits: header)
assert_output_not_contains "no quality/module-state from vendored file" "\[WARN\].*quality/module-state.*css-parser"
# Pattern rules must skip "downloaded from" vendored file (sql-downloaded.js)
assert_output_not_contains "no R-WEB-03 (fetch) from downloaded-from vendored file" "\[WARN\].*R-WEB-03.*sql-downloaded"
assert_output_not_contains "no R-WEB-07 (window) from downloaded-from vendored file" "\[WARN\].*R-WEB-07.*sql-downloaded"
assert_output_not_contains "no prototype-override from downloaded-from vendored file" "\[WARN\].*prototype-override.*sql-downloaded"
# SKIP notice must be emitted
assert_output_contains "vendored-file-exclusion SKIP emitted" "\[SKIP\].*vendored-file-exclusion"
echo ""
