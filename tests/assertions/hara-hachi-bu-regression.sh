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
assert_output_contains "known: R-SEC-04 (pkexec)" "\[FAIL\].*R-SEC-04"
assert_output_contains "known: R-PREFS-04 (GTK widgets)" "\[WARN\].*R-PREFS-04"
assert_output_contains "known: R-SEC-07 (clipboard)" "\[WARN\].*R-SEC-07"

# New checks MUST NOT produce false positives
assert_output_not_contains "no selective-disable false positive" "\[FAIL\].*lifecycle/selective-disable"
assert_output_not_contains "no clipboard-keybinding false positive" "\[WARN\].*lifecycle/clipboard-keybinding"
assert_output_not_contains "no prototype-override false positive" "\[WARN\].*lifecycle/prototype-override"
assert_output_not_contains "no promisify-in-enable false positive" "\[WARN\].*init/promisify-in-enable"
assert_output_not_contains "no shell-class-override false positive" "\[WARN\].*css/shell-class-override"
echo ""
