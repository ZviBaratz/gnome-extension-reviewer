# Meson installed-tests/ exclusion tests
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.
#
# Verifies that installed-tests/ (Meson standard test infrastructure) is excluded
# from pattern checks when meson.build is present at the extension root.
# installed-tests/ is never shipped in an EGO package.

echo "=== meson-installed-tests ==="
run_lint "meson-installed-tests@test"
assert_exit_code "exits with 0 (installed-tests/ content not flagged)" 0
# eval() inside installed-tests/jasmine.js must not trip R-SEC-01
assert_output_not_contains "no R-SEC-01 (eval) from installed-tests/ jasmine" "[WARN].*R-SEC-01.*jasmine"
assert_output_not_contains "no R-SEC-01 (eval) from installed-tests/ jasmine (FAIL)" "[FAIL].*R-SEC-01.*jasmine"
# SKIP notice for dev-tooling-dir-exclusion must be emitted
assert_output_contains "dev-tooling-dir-exclusion SKIP emitted" "[SKIP].*dev-tooling-dir-exclusion"
echo ""
