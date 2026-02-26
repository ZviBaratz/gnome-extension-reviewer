# Hara-hachi-bu regression assertions
# Sourced by run-tests.sh — only runs if the extension exists locally.
# Verifies known findings remain stable and no new FAILs from newly added checks.

HHB_DIR="$HOME/.local/share/gnome-shell/extensions/hara-hachi-bu@ZviBaratz"

if [[ ! -d "$HHB_DIR" ]]; then
    echo "=== hara-hachi-bu regression (SKIPPED — extension not installed) ==="
    echo ""
    return 0 2>/dev/null || true
fi

echo "=== hara-hachi-bu regression ==="
output=""
exit_code=0
output="$(bash "$LINT" "$HHB_DIR" 2>&1)" || exit_code=$?

# Known legitimate findings that MUST remain
assert_output_contains "known: R-SEC-20 (pkexec advisory)" "\[WARN\].*R-SEC-20"
assert_output_contains "known: R-PREFS-04 (GTK widgets)" "\[WARN\].*R-PREFS-04"
assert_output_contains "known: R-SEC-07 (clipboard)" "\[WARN\].*R-SEC-07"

# New checks MUST NOT produce false positives
assert_output_not_contains "no init-safety false positive on registerClass" "\[FAIL\].*init/shell-modification"
assert_output_not_contains "no R-SLOP-04 false positive on version-name" "\[WARN\].*R-SLOP-04"
assert_output_not_contains "no selective-disable false positive" "\[FAIL\].*lifecycle/selective-disable"
assert_output_not_contains "no clipboard-keybinding false positive" "\[WARN\].*lifecycle/clipboard-keybinding"
assert_output_not_contains "no prototype-override false positive" "\[WARN\].*lifecycle/prototype-override"
assert_output_not_contains "no promisify-in-enable false positive" "\[WARN\].*init/promisify-in-enable"
assert_output_not_contains "no shell-class-override false positive" "\[FAIL\].*css/shell-class-override"
assert_output_not_contains "no pkexec-user-writable false positive" "\[FAIL\].*lifecycle/pkexec-user-writable"
assert_output_not_contains "no excessive-null-checks false positive" "\[WARN\].*quality/excessive-null-checks"
assert_output_not_contains "no R-SLOP-27 false positive" "\[WARN\].*R-SLOP-27"
assert_output_not_contains "no R-SLOP-28 false positive" "\[WARN\].*R-SLOP-28"
assert_output_not_contains "no R-QUAL-23 false positive" "\[WARN\].*R-QUAL-23"
assert_output_not_contains "no R-SLOP-29 false positive" "\[WARN\].*R-SLOP-29"
assert_output_not_contains "no R-QUAL-25 false positive" "\[WARN\].*R-QUAL-25"
assert_output_not_contains "no R-QUAL-26 false positive" "\[WARN\].*R-QUAL-26"
assert_output_not_contains "no prefs-memory-leak false positive" "\[WARN\].*prefs/memory-leak"
assert_output_not_contains "no soup-session-abort false positive" "\[WARN\].*lifecycle/soup-session-abort"
assert_output_not_contains "no network-disclosure false positive" "\[WARN\].*quality/network-disclosure"
assert_output_not_contains "no destroy-no-null false positive" "\[WARN\].*lifecycle/destroy-no-null"
assert_output_not_contains "no shell-version-minor false positive" "\[FAIL\].*metadata/shell-version-minor"
echo ""
