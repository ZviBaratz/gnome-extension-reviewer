# Field test: Blur my Shell — FP fixes
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- registerclass-module-scope (GObject.registerClass at module scope is OK) ---
echo "=== registerclass-module-scope ==="
run_lint "registerclass-module-scope@test"
assert_exit_code "exits with 0 (registerClass at module scope is OK)" 0
assert_output_contains "init check passes" "\[PASS\].*init/shell-modification"
assert_output_not_contains "no FAIL for registerClass" "\[FAIL\].*init/shell-modification"
echo ""

# --- src-layout (extension.js/prefs.js/stylesheet.css in src/) ---
echo "=== src-layout ==="
run_lint "src-layout@test"
assert_exit_code "exits with 0 (src/ layout recognized)" 0
assert_output_contains "extension.js found in src/" "\[PASS\].*file-structure/extension.js.*src/"
assert_output_contains "CSS scoping check runs" "\[PASS\].*css/scoping"
assert_output_contains "prefs check runs" "\[PASS\].*prefs/prefs-method"
assert_output_not_contains "no CSS SKIP" "\[SKIP\].*css/scoping"
assert_output_not_contains "no prefs SKIP" "\[SKIP\].*prefs/exists"
echo ""

# --- system-gsettings (non-extension schema OK) ---
echo "=== system-gsettings ==="
run_lint "system-gsettings@test"
assert_output_not_contains "R-SLOP-24 suppressed for system schema" "\[WARN\].*R-SLOP-24"
echo ""

# --- long-param-default (parameter with default value OK) ---
echo "=== long-param-default ==="
run_lint "long-param-default@test"
assert_output_not_contains "R-SLOP-38 suppressed for default param" "\[WARN\].*R-SLOP-38"
echo ""
