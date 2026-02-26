# Batch 2: Severity corrections — new rules and metadata checks
# Sourced by run-tests.sh

echo "=== curl-spawn ==="
run_lint "curl-spawn@test"
assert_exit_code "exits with failure (curl/gsettings spawn)" 1
assert_output_contains "R-SEC-21 fires on curl spawn" "\[FAIL\].*R-SEC-21"
assert_output_contains "R-SEC-22 fires on gsettings spawn" "\[FAIL\].*R-SEC-22"

echo "=== version-unknown ==="
run_lint "version-unknown@test"
assert_output_contains "unknown version 37 flagged" "\[WARN\].*shell-version-unknown.*37"

echo "=== gi-version-import ==="
run_lint "gi-version-import@test"
assert_output_contains "R-QUAL-32 fires on unnecessary version specifier" "\[WARN\].*R-QUAL-32"
