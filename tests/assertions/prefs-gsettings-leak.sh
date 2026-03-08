# Preferences directory: gsettings-signal-leak should be excluded

echo "=== prefs-gsettings-leak ==="
run_lint "prefs-gsettings-leak@test"
assert_exit_code "exits with 0 (no blocking issues)" 0
assert_output_not_contains "no gsettings-signal-leak FAIL from preferences/ dir" "\[FAIL\].*gsettings-signal-leak"
assert_output_not_contains "no gsettings-signal-leak WARN from preferences/ dir" "\[WARN\].*gsettings-signal-leak"
echo ""
