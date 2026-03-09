# Output filtering: --show and --no-report flags
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_output_not_contains, etc.

# --- default (no flags) shows FAIL + WARN + report ---
echo "=== output-filtering: default ==="
output=""
exit_code=0
output="$(bash "$LINT" "$FIXTURES/valid-extension@test" 2>&1)" || exit_code=$?
assert_output_not_contains "default hides PASS lines" "\[PASS\]"
assert_output_not_contains "default hides SKIP lines" "\[SKIP\]"
assert_output_not_contains "default hides header" "ego-lint — GNOME Shell Extension"
assert_output_not_contains "default hides metrics" "\[METRIC\]"
assert_output_contains "default keeps summary" "Results:"
assert_output_contains "default shows report" "REPORT"
assert_output_contains "default shows verdict" "VERDICT"
assert_output_contains "default shows hint" "run with --show all"
echo ""

# --- --show all shows everything ---
echo "=== output-filtering: --show all ==="
output=""
exit_code=0
output="$(bash "$LINT" --show all "$FIXTURES/valid-extension@test" 2>&1)" || exit_code=$?
assert_output_contains "show=all shows PASS lines" "\[PASS\]"
assert_output_contains "show=all shows header" "ego-lint — GNOME Shell Extension"
assert_output_contains "show=all keeps summary" "Results:"
assert_output_contains "show=all shows report" "REPORT"
echo ""

# --- --show fail only ---
echo "=== output-filtering: --show fail ==="
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

# --- --show pass,skip ---
echo "=== output-filtering: --show pass,skip ==="
output=""
exit_code=0
output="$(bash "$LINT" --show pass,skip "$FIXTURES/valid-extension@test" 2>&1)" || exit_code=$?
assert_output_contains "show=pass,skip shows PASS lines" "\[PASS\]"
assert_output_not_contains "show=pass,skip hides FAIL lines" "\[FAIL\]"
assert_output_not_contains "show=pass,skip hides header" "ego-lint — GNOME Shell Extension"
assert_output_contains "show=pass,skip keeps summary" "Results:"
echo ""

# --- --no-report hides grouped report ---
echo "=== output-filtering: --no-report ==="
output=""
exit_code=0
output="$(bash "$LINT" --no-report "$FIXTURES/valid-extension@test" 2>&1)" || exit_code=$?
assert_output_not_contains "no-report hides grouped report" "REPORT"
assert_output_not_contains "no-report hides verdict" "VERDICT"
assert_output_contains "no-report keeps summary" "Results:"
echo ""

# --- --show all --no-report ---
echo "=== output-filtering: --show all --no-report ==="
output=""
exit_code=0
output="$(bash "$LINT" --show all --no-report "$FIXTURES/valid-extension@test" 2>&1)" || exit_code=$?
assert_output_contains "show=all+no-report shows PASS lines" "\[PASS\]"
assert_output_not_contains "show=all+no-report hides report" "REPORT"
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

# --- --show=LEVELS equals syntax ---
echo "=== output-filtering: --show=fail (equals syntax) ==="
output=""
exit_code=0
output="$(bash "$LINT" --show=fail "$FIXTURES/console-log" 2>&1)" || exit_code=$?
assert_output_contains "show=fail (equals) shows FAIL lines" "\[FAIL\]"
assert_output_not_contains "show=fail (equals) hides PASS lines" "\[PASS\]"
assert_output_not_contains "show=fail (equals) hides WARN lines" "\[WARN\]"
echo ""
