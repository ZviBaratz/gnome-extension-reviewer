# Field test #10: src/ layout license fallback and UUID-dir skip (closes #26)

# --- src-license-fallback (LICENSE in parent dir of src/) ---
echo "=== src-license-fallback ==="
run_lint "src-license-fallback@test/src"
assert_exit_code "exits with 0 (license found in parent dir)" 0
assert_output_contains "license found via parent fallback" "\[PASS\].*license"
assert_output_contains "UUID-dir skipped for src/ layout" "\[PASS\].*metadata/uuid-matches-dir.*src/ layout"
echo ""
