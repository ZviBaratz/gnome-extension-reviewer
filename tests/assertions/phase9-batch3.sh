# Phase 9: Batch 3 — P1 metadata, package, and prefs checks
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- gnome-trademark ---
echo "=== gnome-trademark ==="
run_lint "gnome-trademark@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on GNOME trademark in UUID" "\[FAIL\].*metadata/gnome-trademark"
assert_output_contains "fails on GNOME trademark in name" "\[FAIL\].*metadata/gnome-trademark.*name"
assert_output_contains "fails on GNOME trademark in schema ID" "\[FAIL\].*schema/gnome-trademark"
echo ""

# --- prefs-gtk-legitimate ---
echo "=== prefs-gtk-legitimate ==="
run_lint "prefs-gtk-legitimate@test"
assert_output_contains "fails on replaceable Gtk widget (R-PREFS-04)" "\[FAIL\].*R-PREFS-04[^b]"
assert_output_contains "warns on legitimate Gtk widget (R-PREFS-04b)" "\[WARN\].*R-PREFS-04b"
echo ""
