# Guard-window multi-line lookback tests
# Sourced by run-tests.sh

echo "=== guard-window-multiline ==="
run_lint "guard-window-multiline@test"
assert_exit_code "exits with 0 (multi-line guard suppresses R-VER44-02)" 0
assert_output_not_contains "no FAIL for R-VER44-02 with 7-line guard window" "\[FAIL\].*R-VER44-02"
echo ""
