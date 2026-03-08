# R-SLOP-38 guard for domain-specific identifier suffixes
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- slop-long-id-guard (R-SLOP-38 suffix guards) ---
echo "=== slop-long-id-guard ==="
run_lint "slop-long-id-guard@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on AI-style verbose name" "\[WARN\].*R-SLOP-38"
assert_output_count "only 1 R-SLOP-38 warning (guarded cases suppressed)" "\[WARN\].*R-SLOP-38" 1
echo ""
