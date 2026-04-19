# Field test: GSConnect — FP fixes
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- fetch-method-name (method calls/definitions named fetch are not browser API) ---
echo "=== fetch-method-name ==="
run_lint "fetch-method-name@test"
assert_exit_code "exits with 0 (fetch method name OK)" 0
assert_output_not_contains "R-WEB-03 not triggered for .fetch()" "\[FAIL\].*R-WEB-03"
echo ""

# --- gio-unix-fallback (Gio.UnixInputStream in try-catch fallback is OK) ---
echo "=== gio-unix-fallback ==="
run_lint "gio-unix-fallback@test"
assert_exit_code "exits with 0 (GioUnix fallback OK)" 0
assert_output_not_contains "R-VER46-04 suppressed for GioUnix fallback" "\[FAIL\].*R-VER46-04"
echo ""

# --- glib-bytes-init (GLib.Bytes at module scope is a data container, not a resource) ---
echo "=== glib-bytes-init ==="
run_lint "glib-bytes-init@test"
assert_exit_code "exits with 0 (GLib.Bytes at module scope OK)" 0
assert_output_contains "no init-time modification" "\[PASS\].*init/shell-modification"
echo ""

# --- gio-subprocesslauncher-init (Gio.SubprocessLauncher at module scope is a config container) ---
echo "=== gio-subprocesslauncher-init ==="
run_lint "gio-subprocesslauncher-init@test"
assert_exit_code "exits with 0 (Gio.SubprocessLauncher at module scope OK)" 0
assert_output_contains "no init-time modification" "\[PASS\].*init/shell-modification"
echo ""
