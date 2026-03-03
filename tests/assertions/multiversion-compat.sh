# fix-min-version gating tests (R-VER48-04/04b with multi-version extensions)
# Sourced by run-tests.sh

echo "=== multiversion-vertical ==="
run_lint "multiversion-vertical@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on vertical assignment" "\[WARN\].*R-VER48-04 "
assert_output_contains "warns on vertical constructor" "\[WARN\].*R-VER48-04b"
assert_output_contains "message mentions compat" "keep vertical for GNOME"
assert_output_not_contains "no fix text when min-shell below fix-min-version" "fix:.*orientation"
echo ""
