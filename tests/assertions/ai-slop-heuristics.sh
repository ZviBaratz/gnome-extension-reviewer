# Phase 2: AI slop assertions
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- ai-slop-comments ---
echo "=== ai-slop-comments ==="
run_lint "ai-slop-comments@test"
assert_output_contains "detects LLM prompt comments" "\[WARN\].*R-SLOP-18"
echo ""

# --- ai-slop-rethrow ---
echo "=== ai-slop-rethrow ==="
run_lint "ai-slop-rethrow@test"
assert_output_contains "detects catch-log-rethrow" "\[WARN\].*R-SLOP-22"
echo ""

# --- ai-slop-cleanup ---
echo "=== ai-slop-cleanup ==="
run_lint "ai-slop-cleanup@test"
assert_output_contains "detects redundant cleanup" "\[WARN\].*quality/redundant-cleanup"
echo ""

# --- regression-001-ai-slop ---
echo "=== regression-001-ai-slop ==="
run_lint "regressions/regression-001-ai-slop@test"
assert_output_contains "detects JSDoc @param" "\[WARN\].*R-SLOP-01"
assert_output_contains "detects JSDoc @returns" "\[WARN\].*R-SLOP-02"
assert_output_contains "detects LLM prompt comments" "\[WARN\].*R-SLOP-18"
assert_output_contains "detects catch-log-rethrow" "\[WARN\].*R-SLOP-22"
echo ""
