# Field test improvements — assertions for rules added from ego-submit field testing
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- slop-object-freeze (R-SLOP-35) ---
echo "=== slop-object-freeze ==="
run_lint "slop-object-freeze@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on Object.freeze" "\[WARN\].*R-SLOP-35"
echo ""

# --- slop-long-params (R-SLOP-38) ---
echo "=== slop-long-params ==="
run_lint "slop-long-params@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on over-long parameter name" "\[WARN\].*R-SLOP-38"
echo ""

# --- slop-promise-wrapper (R-SLOP-40) ---
echo "=== slop-promise-wrapper ==="
run_lint "slop-promise-wrapper@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on manual Promise wrapper" "\[WARN\].*R-SLOP-40"
echo ""

# --- slop-underscore-export (R-SLOP-43) ---
echo "=== slop-underscore-export ==="
run_lint "slop-underscore-export@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on underscore-prefixed export" "\[WARN\].*R-SLOP-43"
echo ""

# --- promisify-module-scope (R-QUAL-33) ---
echo "=== promisify-module-scope ==="
run_lint "promisify-module-scope@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on Gio._promisify at module scope" "\[WARN\].*R-QUAL-33"
echo ""
