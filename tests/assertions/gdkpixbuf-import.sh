# GdkPixbuf import: should not trigger no-gtk-in-extension

echo "=== gdkpixbuf-import ==="
run_lint "gdkpixbuf-import@test"
assert_exit_code "exits with 0 (GdkPixbuf is allowed in extension)" 0
assert_output_not_contains "no GTK import violation for GdkPixbuf" "\[FAIL\].*imports/no-gtk-in-extension"
assert_output_contains "import segregation passes" "\[PASS\].*imports/segregation"
echo ""
