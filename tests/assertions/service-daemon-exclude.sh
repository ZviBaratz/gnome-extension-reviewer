# Service daemon directory exclusion tests
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- service-daemon (service/ directory code should skip extension-specific checks) ---
echo "=== service-daemon ==="
run_lint "service-daemon@test"
assert_exit_code "exits with 0 (service daemon code not flagged)" 0
# Pattern rules with exclude-dirs: ["service"]
assert_output_not_contains "R-LOG-02 skipped in service/" "\[WARN\].*R-LOG-02.*service/"
assert_output_not_contains "R-LOG-03 skipped in service/" "\[WARN\].*R-LOG-03.*service/"
assert_output_not_contains "R-SLOP-43 skipped in service/" "\[WARN\].*R-SLOP-43.*service/"
assert_output_not_contains "R-QUAL-32 skipped in service/" "\[WARN\].*R-QUAL-32.*service/"
assert_output_not_contains "R-QUAL-34 skipped in service/" "\[WARN\].*R-QUAL-34.*service/"
assert_output_not_contains "R-QUAL-35 skipped in service/" "\[WARN\].*R-QUAL-35.*service/"
# Tier 2 checks with service/ exclusion
assert_output_not_contains "quality/module-state skipped in service/" "\[WARN\].*quality/module-state.*service/"
assert_output_not_contains "lifecycle/untracked-timeout skipped in service/" "\[WARN\].*lifecycle/untracked-timeout.*service/"
echo ""
