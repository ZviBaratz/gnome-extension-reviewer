# --- destroy-all-cleanup (destroy_all recognized as cleanup method) ---
echo "=== destroy-all-cleanup ==="
run_lint "destroy-all-cleanup@test"
assert_exit_code "exits with 0 (no blocking issues)" 0
assert_output_not_contains "no no-destroy-method for class with destroy_all" "\[WARN\].*resource-tracking/no-destroy-method.*effects_manager"
assert_output_contains "resource tracking ran" "(PASS|WARN|FAIL).*resource-tracking"
echo ""

# --- multi-parent-ownership (child with multiple parents, one calls cleanup) ---
echo "=== multi-parent-ownership ==="
run_lint "multi-parent-ownership@test"
assert_exit_code "exits with 0 (no blocking issues)" 0
assert_output_not_contains "no destroy-not-called for multi-parent child" "\[WARN\].*resource-tracking/destroy-not-called.*shared_helper"
assert_output_contains "resource tracking ran" "(PASS|WARN|FAIL).*resource-tracking"
echo ""

# --- prefs-src-constructor (src/preferences excluded from constructor-resources) ---
echo "=== prefs-src-constructor ==="
run_lint "prefs-src-constructor@test"
assert_exit_code "exits with 0 (no blocking issues)" 0
assert_output_not_contains "no constructor-resources for src/preferences" "\[WARN\].*quality/constructor-resources.*preferences"
assert_output_contains "quality checks ran" "(PASS|WARN|FAIL).*quality"
echo ""
