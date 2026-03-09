# R-LIFE-21: GSettings signal leak detection
# Sourced by run-tests.sh

echo "=== gsettings-bare-connect ==="
run_lint "gsettings-bare-connect@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on bare GSettings connect" "\[FAIL\].*lifecycle/gsettings-signal-leak"
echo ""

echo "=== gsettings-auto-cleanup ==="
run_lint "gsettings-auto-cleanup@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_contains "passes with auto-cleanup" "\[PASS\].*lifecycle/gsettings-signal-leak"
assert_output_not_contains "no gsettings-signal-leak FP" "\[FAIL\].*lifecycle/gsettings-signal-leak"
echo ""

echo "=== gsettings-array-storage ==="
run_lint "gsettings-array-storage@test"
assert_exit_code "exits with 0 (array storage is not bare connect)" 0
assert_output_not_contains "no gsettings-signal-leak FP on array storage" "\[FAIL\].*lifecycle/gsettings-signal-leak"
echo ""

echo "=== gsettings-array-literal ==="
run_lint "gsettings-array-literal@test"
assert_exit_code "exits with 0 (array literal is not bare connect)" 0
assert_output_not_contains "no gsettings-signal-leak FP on array literal" "\[FAIL\].*lifecycle/gsettings-signal-leak"
echo ""

echo "=== gsettings-cross-file-leak ==="
run_lint "gsettings-cross-file-leak@test"
assert_exit_code "exits with 1 (cross-file leak detected)" 1
assert_output_contains "fails on cross-file bare GSettings connect" "\[FAIL\].*lifecycle/gsettings-signal-leak"
echo ""
