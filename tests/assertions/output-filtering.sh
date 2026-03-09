# Output filtering: --quiet and --show flags
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_output_not_contains, etc.

# --- quiet mode ---
echo "=== output-filtering: --quiet ==="
output=""
exit_code=0
output="$(bash "$LINT" --quiet "$FIXTURES/valid-extension@test" 2>&1)" || exit_code=$?
assert_output_not_contains "quiet hides PASS lines" "\[PASS\]"
assert_output_not_contains "quiet hides SKIP lines" "\[SKIP\]"
assert_output_not_contains "quiet hides header" "ego-lint — GNOME Shell Extension"
assert_output_not_contains "quiet hides metrics" "\[METRIC\]"
assert_output_not_contains "quiet hides verbose hint" "run with --verbose"
assert_output_contains "quiet keeps summary" "Results:"
echo ""

# --- show=fail only ---
echo "=== output-filtering: --show=fail ==="
output=""
exit_code=0
output="$(bash "$LINT" --show fail "$FIXTURES/console-log" 2>&1)" || exit_code=$?
assert_output_contains "show=fail shows FAIL lines" "\[FAIL\]"
assert_output_not_contains "show=fail hides PASS lines" "\[PASS\]"
assert_output_not_contains "show=fail hides WARN lines" "\[WARN\]"
assert_output_not_contains "show=fail hides SKIP lines" "\[SKIP\]"
assert_output_not_contains "show=fail hides header" "ego-lint — GNOME Shell Extension"
assert_output_not_contains "show=fail hides metrics" "\[METRIC\]"
assert_output_contains "show=fail keeps summary" "Results:"
assert_exit_code "show=fail preserves exit code" 1
echo ""

# --- show=pass,skip ---
echo "=== output-filtering: --show=pass,skip ==="
output=""
exit_code=0
output="$(bash "$LINT" --show pass,skip "$FIXTURES/valid-extension@test" 2>&1)" || exit_code=$?
assert_output_contains "show=pass,skip shows PASS lines" "\[PASS\]"
assert_output_not_contains "show=pass,skip hides FAIL lines" "\[FAIL\]"
assert_output_not_contains "show=pass,skip hides header" "ego-lint — GNOME Shell Extension"
assert_output_contains "show=pass,skip keeps summary" "Results:"
echo ""

# --- quiet + verbose ---
echo "=== output-filtering: --quiet --verbose ==="
output=""
exit_code=0
output="$(bash "$LINT" --quiet --verbose "$FIXTURES/valid-extension@test" 2>&1)" || exit_code=$?
assert_output_not_contains "quiet+verbose hides PASS lines" "\[PASS\]"
assert_output_contains "quiet+verbose still shows verbose report" "VERBOSE REPORT"
echo ""

# --- invalid --show value ---
echo "=== output-filtering: --show=invalid ==="
output=""
exit_code=0
output="$(bash "$LINT" --show bogus "$FIXTURES/valid-extension@test" 2>&1)" || exit_code=$?
assert_exit_code "invalid --show exits with 2" 2
assert_output_contains "invalid --show shows error" "unknown severity level"
echo ""

# --- --show with uppercase levels ---
echo "=== output-filtering: --show=FAIL (uppercase) ==="
output=""
exit_code=0
output="$(bash "$LINT" --show FAIL "$FIXTURES/console-log" 2>&1)" || exit_code=$?
assert_output_contains "show=FAIL (uppercase) shows FAIL lines" "\[FAIL\]"
assert_output_not_contains "show=FAIL (uppercase) hides PASS lines" "\[PASS\]"
assert_exit_code "show=FAIL preserves exit code" 1
echo ""
