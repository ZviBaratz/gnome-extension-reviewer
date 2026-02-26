# Batch 6: Remaining quick wins
# Sourced by run-tests.sh

echo "=== gettext-mismatch ==="
run_lint "gettext-mismatch@test"
assert_output_contains "gettext domain mismatch detected" "\[WARN\].*gettext-domain-mismatch"

echo "=== excessive-logging ==="
run_lint "excessive-logging@test"
assert_output_contains "excessive logging flagged" "\[WARN\].*quality/excessive-logging"
