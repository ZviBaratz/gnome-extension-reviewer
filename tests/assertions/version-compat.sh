# Phase 5: Version-gated rule assertions
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- gnome48-css-compat ---
echo "=== gnome48-css-compat ==="
run_lint "gnome48-css-compat@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "detects quick-menu-toggle CSS rename" "\[FAIL\].*R-VER48-07"
echo ""

# --- gnome49-maximize ---
echo "=== gnome49-maximize ==="
run_lint "gnome49-maximize@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "detects maximize() signature change" "\[FAIL\].*R-VER49-08"
echo ""

# --- gnome49-appmenu ---
echo "=== gnome49-appmenu ==="
run_lint "gnome49-appmenu@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "detects AppMenuButton removal" "\[FAIL\].*R-VER49-09"
echo ""

# --- bad-url ---
echo "=== bad-url ==="
run_lint "bad-url@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on non-repo URL" "\[WARN\].*metadata/url-format"
echo ""

# --- css-dual-selector ---
echo "=== css-dual-selector ==="
run_lint "css-dual-selector@test"
assert_exit_code "exits with 0 (dual selector is backward-compatible)" 0
assert_output_not_contains "dual-selector passes R-VER48-07" "\[FAIL\].*R-VER48-07"
echo ""

# --- gsettings-bind-flags ---
echo "=== gsettings-bind-flags ==="
run_lint "gsettings-bind-flags@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on GObject.BindingFlags" "\[WARN\].*R-QUAL-23"
echo ""
