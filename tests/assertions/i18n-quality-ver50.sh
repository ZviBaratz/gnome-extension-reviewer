# Phase 11: Batch 6 — P2 pattern rules
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- version-string-compare ---
echo "=== version-string-compare ==="
run_lint "version-string-compare@test"
assert_output_contains "warns on string version comparison" "\[WARN\].*R-QUAL-27"
echo ""

# --- gettext-concat ---
echo "=== gettext-concat ==="
run_lint "gettext-concat@test"
assert_output_contains "warns on gettext concatenation" "\[WARN\].*R-I18N-02"
echo ""

# --- module-scope-gobject ---
echo "=== module-scope-gobject ==="
run_lint "module-scope-gobject@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on module-scope GObject construction" "\[FAIL\].*R-QUAL-04b"
echo ""

# --- gnome50-oneshot ---
echo "=== gnome50-oneshot ==="
run_lint "gnome50-oneshot@test"
assert_output_contains "warns on one-shot timeout without _destroyed guard" "\[WARN\].*R-VER50-05"
echo ""
