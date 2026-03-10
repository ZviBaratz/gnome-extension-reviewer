# Dash to Panel field test — FP fixes
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_exit_code, etc.

# --- gpl-license-header (R-SEC-03 guard for GPL boilerplate URLs) ---
echo "=== gpl-license-header ==="
run_lint "gpl-license-header@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_not_contains "R-SEC-03 suppressed for GPL license URL" "\[WARN\].*R-SEC-03.*gnu\.org"
assert_output_not_contains "R-SEC-03 suppressed for HTTP URL in block comment" "\[WARN\].*R-SEC-03.*frippery"
assert_output_contains "R-SEC-03 still fires on real HTTP URL in code" "\[WARN\].*R-SEC-03"
echo ""

# --- version-guard-pkgver (R-VER48-02 guard for PACKAGE_VERSION) ---
echo "=== version-guard-pkgver ==="
run_lint "version-guard-pkgver@test"
assert_exit_code "exits with 0 (version guard suppresses R-VER48-02)" 0
assert_output_not_contains "no FAIL for R-VER48-02 with PACKAGE_VERSION guard" "\[FAIL\].*R-VER48-02"
echo ""

# --- version-guard-distant (R-VER48-02 guard-window with distant guard) ---
echo "=== version-guard-distant ==="
run_lint "version-guard-distant@test"
assert_exit_code "exits with 0 (distant version guard suppresses R-VER48-02)" 0
assert_output_not_contains "no FAIL for R-VER48-02 with distant PACKAGE_VERSION guard" "\[FAIL\].*R-VER48-02"
echo ""

# --- deprecated-in-comments (skip-comments for R-DEPR-05/06) ---
echo "=== deprecated-in-comments ==="
run_lint "deprecated-in-comments@test"
assert_exit_code "exits with 0 (comments skipped)" 0
assert_output_not_contains "R-DEPR-06 not fired in comment" "\[FAIL\].*R-DEPR-06"
assert_output_not_contains "R-DEPR-05 not fired in comment" "\[FAIL\].*R-DEPR-05"
echo ""

# --- system-gsettings-multiline (R-SLOP-24 guard-window-forward) ---
echo "=== system-gsettings-multiline ==="
run_lint "system-gsettings-multiline@test"
assert_output_not_contains "R-SLOP-24 suppressed for multiline system schema" "\[WARN\].*R-SLOP-24"
echo ""
