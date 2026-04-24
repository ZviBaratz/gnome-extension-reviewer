# AI defense and provenance assertion tests

# --- ai-defense-legit: legitimate code with provenance indicators ---
echo "=== ai-defense-legit ==="
run_lint "ai-defense-legit@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_contains "provenance score >= 3" "quality/code-provenance.*provenance-score=[3-9]"
assert_output_contains "domain vocabulary detected" "quality/code-provenance.*domain-vocabulary"
assert_output_contains "consistent naming detected" "quality/code-provenance.*consistent-naming-style"
echo ""

# --- spdx-provenance: SPDX headers project-wide carry weight-2 signal (issue #223) ---
echo "=== spdx-provenance ==="
run_lint "spdx-provenance@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_contains "SPDX signal detected" "quality/code-provenance.*spdx-headers-project-wide"
assert_output_contains "weighted score reaches 3 via SPDX+naming" "quality/code-provenance.*provenance-score=[3-9]"
assert_output_contains "JSDoc warnings suppressed" "provenance/jsdoc-suppressed"
echo ""
