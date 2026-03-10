# GdkPixbuf in transitive dependency: should not trigger no-gtk-in-extension

echo "=== gdkpixbuf-transitive ==="
run_lint "gdkpixbuf-transitive@test"
assert_exit_code "exits with 0 (GdkPixbuf is allowed in transitive deps)" 0
assert_output_not_contains "no GTK violation for transitive GdkPixbuf" "\[FAIL\].*imports/no-gtk-in-extension"
assert_output_contains "import segregation passes" "\[PASS\].*imports/segregation"
echo ""
