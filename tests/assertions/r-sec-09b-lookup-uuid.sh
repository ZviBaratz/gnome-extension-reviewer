#!/usr/bin/env bash
# Assertion: R-SEC-09b — UUID-aware lookupByUUID detection
#
# Self-lookup (extension calls lookupByUUID with its own UUID) must not
# produce a warning. Cross-extension lookup must produce R-SEC-09b advisory.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CHECK="$REPO_ROOT/skills/ego-lint/scripts/check-security.py"
FIXTURES="$REPO_ROOT/tests/fixtures"

pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; exit 1; }

# --- Test 1: self-lookup must not be flagged ---
out=$(python3 "$CHECK" "$FIXTURES/lookup-self@test" 2>&1)
if echo "$out" | grep -q "R-SEC-09b.*extension.js"; then
    fail "Self-lookup was flagged as R-SEC-09b (false positive)"
fi
if echo "$out" | grep -q "^PASS|R-SEC-09b"; then
    pass "Self-lookup correctly produces no warning"
else
    fail "Unexpected output for self-lookup fixture: $out"
fi

# --- Test 2: cross-extension lookup must be flagged ---
out=$(python3 "$CHECK" "$FIXTURES/lookup-other@test" 2>&1)
if echo "$out" | grep -q "WARN|R-SEC-09b"; then
    pass "Cross-extension lookup correctly flagged as R-SEC-09b"
else
    fail "Cross-extension lookup was not flagged: $out"
fi
if echo "$out" | grep -q "other-extension@example.com"; then
    pass "Warning includes the cross-extension UUID for context"
else
    fail "Warning does not include the target UUID: $out"
fi

echo "All R-SEC-09b assertions passed."
