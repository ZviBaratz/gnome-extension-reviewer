# R-LIFE-27: Module-scope prototype mutation detection

echo "=== prototype-mutation ==="
run_lint "prototype-mutation@test"
assert_exit_code "exits with 0 (advisory)" 0
assert_output_contains "warns on module-scope prototype assignment" "\[WARN\].*lifecycle/module-scope-prototype.*Button\.prototype\.customMethod"
assert_output_contains "warns on module-scope Object.assign" "\[WARN\].*lifecycle/module-scope-prototype.*Object\.assign.*Button\.prototype"
assert_output_count "exactly 2 module-scope-prototype warnings" "\[WARN\].*lifecycle/module-scope-prototype" 2
assert_output_not_contains "=== comparison does not trigger warning" "\[WARN\].*lifecycle/module-scope-prototype.*isOriginal"
assert_output_not_contains "module-scope findings not in prototype-override" "\[WARN\].*lifecycle/prototype-override.*customMethod"
echo ""
