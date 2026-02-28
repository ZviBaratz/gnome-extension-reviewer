#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LINT="$SCRIPT_DIR/skills/ego-lint/scripts/ego-lint.sh"
FIXTURES="$SCRIPT_DIR/tests/fixtures"
PASS_COUNT=0
FAIL_COUNT=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

assert_output_contains() {
    local label="$1" pattern="$2"
    if echo "$output" | grep -qE "$pattern"; then
        echo -e "  ${GREEN}✓${NC} $label"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo -e "  ${RED}✗${NC} $label (expected pattern: $pattern)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

assert_output_not_contains() {
    local label="$1" pattern="$2"
    if ! echo "$output" | grep -qE "$pattern"; then
        echo -e "  ${GREEN}✓${NC} $label"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo -e "  ${RED}✗${NC} $label (should NOT match: $pattern)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

assert_exit_code() {
    local label="$1" expected="$2"
    if [[ "$exit_code" -eq "$expected" ]]; then
        echo -e "  ${GREEN}✓${NC} $label (exit code: $exit_code)"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo -e "  ${RED}✗${NC} $label (expected exit code $expected, got $exit_code)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

run_lint() {
    local fixture="$1"
    output=""
    exit_code=0
    output="$(bash "$LINT" "$FIXTURES/$fixture" 2>&1)" || exit_code=$?
}

echo "============================================"
echo "  ego-lint Test Runner"
echo "============================================"
echo ""

# --- valid-extension ---
echo "=== valid-extension ==="
run_lint "valid-extension@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_not_contains "no FAIL results" "\[FAIL\]"
assert_output_contains "metadata passes" "\[PASS\].*metadata/valid-json"
assert_output_contains "no console.log" "\[PASS\].*no-console-log"
assert_output_contains "no deprecated modules" "\[PASS\].*no-deprecated-modules"
assert_output_contains "no web APIs" "\[PASS\].*R-WEB-01"
assert_output_contains "no binary files" "\[PASS\].*no-binary-files"
assert_output_contains "license exists" "\[PASS\].*license"
assert_output_contains "schema checks pass" "\[PASS\].*schema/exists"
assert_output_contains "import checks pass" "\[PASS\].*imports/segregation"
echo ""

# --- bad-metadata ---
echo "=== bad-metadata ==="
run_lint "bad-metadata"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on missing uuid" "\[FAIL\].*metadata/required-fields.*uuid"
assert_output_contains "fails on shell-version type" "\[FAIL\].*metadata/shell-version-array"
echo ""

# --- import-violation ---
echo "=== import-violation ==="
run_lint "import-violation"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on GTK import" "\[FAIL\].*imports/no-gtk-in-extension"
echo ""

# --- console-log ---
echo "=== console-log ==="
run_lint "console-log"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on console.log" "\[FAIL\].*no-console-log"
echo ""

# --- deprecated-modules ---
echo "=== deprecated-modules ==="
run_lint "deprecated-modules"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on deprecated module" "\[FAIL\].*no-deprecated-modules"
echo ""

# --- web-apis ---
echo "=== web-apis ==="
run_lint "web-apis"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on setTimeout" "\[FAIL\].*R-WEB-01"
assert_output_contains "fails on XMLHttpRequest" "\[FAIL\].*R-WEB-04"
assert_output_contains "fails on document.*" "\[FAIL\].*R-WEB-06"
assert_output_contains "fails on clearTimeout" "\[FAIL\].*R-WEB-10"
assert_output_contains "fails on clearInterval" "\[FAIL\].*R-WEB-11"
echo ""

# --- deprecated-imports ---
echo "=== deprecated-imports ==="
run_lint "deprecated-imports"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on ExtensionUtils" "\[FAIL\].*R-DEPR-05"
assert_output_contains "fails on Tweener" "\[FAIL\].*R-DEPR-06"
assert_output_contains "fails on legacy imports" "\[FAIL\].*R-DEPR-04"
echo ""

# --- non-standard-metadata ---
echo "=== non-standard-metadata ==="
run_lint "non-standard-metadata"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on UUID missing @" "\[FAIL\].*metadata/uuid-at-sign"
assert_output_contains "warns on non-standard fields" "\[WARN\].*metadata/non-standard-field"
assert_output_contains "warns on deprecated version" "\[WARN\].*metadata/deprecated-version"
echo ""

# --- bad-package ---
echo "=== bad-package ==="
run_lint "bad-package"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on nested structure" "\[FAIL\].*package/nested-structure"
assert_output_contains "passes on no compiled schemas (GNOME 44+)" "\[PASS\].*package/compiled-schemas"
echo ""

# --- ai-slop ---
echo "=== ai-slop ==="
run_lint "ai-slop@test"
assert_exit_code "exits with 0 (warnings only, no failures)" 0
assert_output_contains "warns on try-catch density" "\[WARN\].*quality.*try-catch"
assert_output_contains "warns on impossible state" "\[WARN\].*quality/impossible-state"
assert_output_contains "warns on pendulum pattern" "\[WARN\].*quality/pendulum-pattern"
assert_output_contains "warns on module state" "\[WARN\].*quality/module-state"
assert_output_contains "warns on empty catch" "\[WARN\].*quality/empty-catch"
assert_output_contains "warns on JSDoc" "\[WARN\].*R-SLOP-01"
echo ""

# --- security-patterns ---
echo "=== security-patterns ==="
run_lint "security-patterns@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on eval()" "\[FAIL\].*R-SEC-01"
assert_output_contains "fails on new Function()" "\[FAIL\].*R-SEC-02"
assert_output_contains "warns on http://" "\[WARN\].*R-SEC-03"
assert_output_contains "fails on shell -c" "\[FAIL\].*R-SEC-05"
echo ""

# --- logging-patterns ---
echo "=== logging-patterns ==="
run_lint "logging-patterns@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on log()" "\[WARN\].*R-LOG-02"
assert_output_contains "warns on print()" "\[WARN\].*R-LOG-03"
echo ""

# --- destroyed-density ---
echo "=== destroyed-density ==="
run_lint "destroyed-density@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on _destroyed density" "\[WARN\].*quality/destroyed-density"
echo ""

# --- mock-in-production ---
echo "=== mock-in-production ==="
run_lint "mock-in-production@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on MockDevice.js" "\[WARN\].*quality/mock-in-production"
echo ""

# --- minified-js ---
echo "=== minified-js ==="
run_lint "minified-js@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on minified JS" "\[FAIL\].*minified-js"
echo ""

# --- lifecycle-imbalance ---
echo "=== lifecycle-imbalance ==="
run_lint "lifecycle-imbalance@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on signal imbalance" "\[WARN\].*lifecycle/signal-balance"
assert_output_contains "warns on untracked timeout" "\[WARN\].*lifecycle/untracked-timeout"
echo ""

# --- missing-disable ---
echo "=== missing-disable ==="
run_lint "missing-disable@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on missing disable" "\[FAIL\].*lifecycle/disable-method"
echo ""

# --- lifecycle-clean ---
echo "=== lifecycle-clean ==="
run_lint "lifecycle-clean@test"
assert_exit_code "exits with 0 (no failures)" 0
assert_output_contains "lifecycle checks pass" "\[PASS\].*lifecycle/enable-disable"
assert_output_contains "signal balance OK" "\[PASS\].*lifecycle/signal-balance"
echo ""

# --- hallucinated-apis ---
echo "=== hallucinated-apis ==="
run_lint "hallucinated-apis@test"
assert_exit_code "exits with 1 (has failures from R-SLOP-30)" 1
assert_output_contains "warns on Meta.Screen" "\[WARN\].*R-SLOP-08"
assert_output_contains "warns on St setter" "\[WARN\].*R-SLOP-09"
assert_output_contains "warns on Clutter.Actor.show_all" "\[WARN\].*R-SLOP-10"
assert_output_contains "warns on GLib.source_remove" "\[WARN\].*R-SLOP-11"
assert_output_contains "warns on typeof super.destroy" "\[WARN\].*R-SLOP-17"
assert_output_contains "fails on typeof super.method" "\[FAIL\].*R-SLOP-30"
assert_output_contains "warns on this instanceof" "\[WARN\].*R-SLOP-13"
echo ""

# --- run-dispose ---
echo "=== run-dispose ==="
run_lint "run-dispose@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on run_dispose" "\[WARN\].*R-SEC-06"
echo ""

# --- structural-issues ---
echo "=== structural-issues ==="
run_lint "structural-issues@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "warns on missing default export" "\[WARN\].*lifecycle/default-export"
assert_output_contains "fails on console.log in prefs.js" "\[FAIL\].*no-console-log"
echo ""

# --- quality-signals ---
echo "=== quality-signals ==="
run_lint "quality-signals@test"
assert_exit_code "exits with 1 (has failures from R-SLOP-30)" 1
assert_output_contains "warns on typeof super.destroy" "\[WARN\].*R-SLOP-17"
assert_output_contains "fails on typeof super.method" "\[FAIL\].*R-SLOP-30"
assert_output_contains "warns on this instanceof" "\[WARN\].*R-SLOP-13"
echo ""

# --- metadata-polish ---
echo "=== metadata-polish ==="
run_lint "metadata-polish@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "warns on missing gettext-domain" "\[WARN\].*metadata/missing-gettext-domain"
assert_output_contains "fails on future shell-version" "\[FAIL\].*metadata/future-shell-version"
echo ""

# --- clipboard-access ---
echo "=== clipboard-access ==="
run_lint "clipboard-access@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on clipboard non-disclosure" "\[WARN\].*quality/clipboard-disclosure"
assert_output_not_contains "R-SEC-07 removed" "\[WARN\].*R-SEC-07"
echo ""

# --- telemetry-patterns ---
echo "=== telemetry-patterns ==="
run_lint "telemetry-patterns@test"
assert_exit_code "exits with failure (telemetry is blocking)" 1
assert_output_contains "blocks on telemetry" "\[FAIL\].*R-SEC-08"
echo ""

# --- extension-interference ---
echo "=== extension-interference ==="
run_lint "extension-interference@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on extensionManager" "\[WARN\].*R-SEC-09"
echo ""

# --- var-declarations ---
echo "=== var-declarations ==="
run_lint "var-declarations@test"
assert_exit_code "exits with 0 (advisory only)" 0
assert_output_contains "warns on var" "\[WARN\].*R-DEPR-09"
echo ""

# --- donations-invalid ---
echo "=== donations-invalid ==="
run_lint "donations-invalid@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on invalid donations key" "\[FAIL\].*metadata/donations-invalid-key"
echo ""

# --- session-modes-invalid ---
echo "=== session-modes-invalid ==="
run_lint "session-modes-invalid@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on invalid session-modes" "\[FAIL\].*metadata/session-modes-invalid"
echo ""

# --- version-name-invalid ---
echo "=== version-name-invalid ==="
run_lint "version-name-invalid@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on version-name format" "\[FAIL\].*metadata/version-name-format"
echo ""

# --- shell-version-garbage ---
echo "=== shell-version-garbage ==="
run_lint "shell-version-garbage@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on invalid shell-version entry" "\[FAIL\].*metadata/shell-version-entry"
echo ""

# --- prefs-issues ---
echo "=== prefs-issues ==="
run_lint "prefs-issues@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on dual prefs pattern" "\[FAIL\].*prefs/dual-prefs-pattern"
assert_output_contains "warns on missing prefs default export" "\[WARN\].*prefs/default-export"
echo ""

# --- async-no-destroyed ---
echo "=== async-no-destroyed ==="
run_lint "async-no-destroyed@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on missing destroyed guard" "\[WARN\].*lifecycle/async-destroyed-guard"
echo ""

# --- timeout-no-return ---
echo "=== timeout-no-return ==="
run_lint "timeout-no-return@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on missing timeout return" "\[WARN\].*lifecycle/timeout-return-value"
echo ""

# --- keybinding-leak ---
echo "=== keybinding-leak ==="
run_lint "keybinding-leak@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on missing removeKeybinding" "\[FAIL\].*lifecycle/keybinding-cleanup"
echo ""

# --- auto-install ---
echo "=== auto-install ==="
run_lint "auto-install@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on pip install" "\[FAIL\].*R-SEC-10"
assert_output_contains "fails on npm install" "\[FAIL\].*R-SEC-11"
assert_output_contains "fails on apt install" "\[FAIL\].*R-SEC-12"
echo ""

# --- missing-url ---
echo "=== missing-url ==="
run_lint "missing-url@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on missing url" "\[FAIL\].*metadata/missing-url"
echo ""

# --- multi-dev-version ---
echo "=== multi-dev-version ==="
run_lint "multi-dev-version@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on multiple dev releases" "\[FAIL\].*metadata/shell-version-dev-limit"
echo ""

# --- donations-empty ---
echo "=== donations-empty ==="
run_lint "donations-empty@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on empty donations" "\[FAIL\].*metadata/donations-empty"
echo ""

# --- esm-version-floor ---
echo "=== esm-version-floor ==="
run_lint "esm-version-floor@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on pre-ESM shell-version" "\[FAIL\].*metadata/shell-version-esm-floor"
echo ""

# --- schema-filename ---
echo "=== schema-filename ==="
run_lint "schema-filename@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on schema filename" "\[FAIL\].*schema/filename-convention"
echo ""

# --- gnome46-compat ---
echo "=== gnome46-compat ==="
run_lint "gnome46-compat@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on add_actor" "\[FAIL\].*R-VER46-01"
assert_output_contains "fails on remove_actor" "\[FAIL\].*R-VER46-02"
echo ""

# --- gnome47-compat ---
echo "=== gnome47-compat ==="
run_lint "gnome47-compat@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on Clutter.Color" "\[FAIL\].*R-VER47-01"
echo ""

# --- gnome48-compat ---
echo "=== gnome48-compat ==="
run_lint "gnome48-compat@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on Clutter.Image" "\[FAIL\].*R-VER48-01"
assert_output_contains "fails on Meta.disable_unredirect" "\[FAIL\].*R-VER48-02"
echo ""

# --- gnome49-compat ---
echo "=== gnome49-compat ==="
run_lint "gnome49-compat@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on Meta.Rectangle" "\[FAIL\].*R-VER49-01"
assert_output_contains "fails on Clutter.ClickAction" "\[FAIL\].*R-VER49-02"
assert_output_contains "fails on Clutter.TapAction" "\[FAIL\].*R-VER49-03"
echo ""

# --- gnome46-extras ---
echo "=== gnome46-extras ==="
run_lint "gnome46-extras@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on BlurEffect sigma" "\[FAIL\].*R-VER46-06"
assert_output_contains "fails on Clutter.Container" "\[FAIL\].*R-VER46-07"
echo ""

# --- gnome45-only ---
echo "=== gnome45-only ==="
run_lint "gnome45-only@test"
assert_output_not_contains "no GNOME 46 rule failures" "\[FAIL\].*R-VER46"
assert_output_not_contains "no GNOME 47 rule failures" "\[FAIL\].*R-VER47"
assert_output_not_contains "no GNOME 48 rule failures" "\[FAIL\].*R-VER48"
assert_output_not_contains "no GNOME 49 rule failures" "\[FAIL\].*R-VER49"
echo ""

# --- large-file ---
echo "=== large-file ==="
run_lint "large-file@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on per-file complexity" "\[WARN\].*quality/file-complexity"
echo ""

# --- debug-volume ---
echo "=== debug-volume ==="
run_lint "debug-volume@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on console.debug volume" "\[WARN\].*quality/debug-volume"
assert_output_contains "warns on notification volume" "\[WARN\].*quality/notification-volume"
echo ""

# --- private-api ---
echo "=== private-api ==="
run_lint "private-api@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on private API access" "\[WARN\].*quality/private-api"
echo ""

# --- session-modes-inconsistent ---
echo "=== session-modes-inconsistent ==="
run_lint "session-modes-inconsistent@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "warns on session-modes inconsistency" "\[WARN\].*metadata/session-modes-consistency"
assert_output_contains "fails on selective disable" "\[FAIL\].*lifecycle/selective-disable"
echo ""

# --- gettext-direct ---
echo "=== gettext-direct ==="
run_lint "gettext-direct@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on direct dgettext" "\[WARN\].*quality/gettext-pattern"
echo ""

# --- polkit-files ---
echo "=== polkit-files ==="
run_lint "polkit-files@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on polkit files" "\[WARN\].*polkit-files"
echo ""

# --- binary-files ---
echo "=== binary-files ==="
run_lint "binary-files@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on binary files" "\[FAIL\].*no-binary-files"
echo ""

# --- non-gjs-scripts ---
echo "=== non-gjs-scripts ==="
run_lint "non-gjs-scripts@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on non-GJS scripts (no pkexec)" "\[FAIL\].*non-gjs-scripts"
echo ""

# --- logging-volume ---
echo "=== logging-volume ==="
run_lint "logging-volume@test"
assert_exit_code "exits with 0 (warnings only)" 0
assert_output_contains "warns on total logging volume" "\[WARN\].*quality/logging-volume"
echo ""

# --- forbidden-pkg-files ---
echo "=== forbidden-pkg-files ==="
run_lint "forbidden-pkg-files@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "fails on .po in zip" "\[FAIL\].*package/no-forbidden.*\.po"
assert_output_contains "fails on Makefile in zip" "\[FAIL\].*package/no-forbidden.*Makefile"
assert_output_contains "fails on tsconfig.json in zip" "\[FAIL\].*package/no-forbidden.*tsconfig\.json"
echo ""

# --- gnome48-extras ---
echo "=== gnome48-extras ==="
run_lint "gnome48-extras@test"
assert_output_contains "Should detect Shell.SnippetHook" "\[FAIL\].*R-VER48-05"
assert_output_contains "Should detect get_key_focus" "\[WARN\].*R-VER48-06"
assert_exit_code "exits with 1 (has failures)" 1
echo ""

# --- typeof-super ---
echo "=== typeof-super ==="
run_lint "typeof-super@test"
assert_output_contains "Should detect typeof super method check" "\[WARN\].*R-SLOP-17"
echo ""

# --- shell-concat ---
echo "=== shell-concat ==="
run_lint "shell-concat@test"
assert_output_contains "Should detect subprocess string concatenation" "\[FAIL\].*R-SEC-13"
echo ""

# --- sync-subprocess ---
echo "=== sync-subprocess ==="
run_lint "sync-subprocess@test"
assert_exit_code "exits with 1 (has failures)" 1
assert_output_contains "detects GLib.spawn_sync" "\[FAIL\].*R-SEC-14"
echo ""

# --- async-no-cancel ---
echo "=== async-no-cancel ==="
run_lint "async-no-cancel@test"
assert_output_contains "detects missing Gio.Cancellable" "async/no-cancellable"
assert_output_contains "detects disable without cancel" "async/disable-no-cancel"
echo ""

# --- gobject-patterns ---
echo "=== gobject-patterns ==="
run_lint "gobject-patterns@test"
assert_output_contains "detects missing GTypeName" "gobject/missing-gtypename"
assert_output_contains "detects missing super._init" "gobject/missing-super-init"
assert_output_contains "detects missing cr.\$dispose" "gobject/cairo-dispose"
echo ""

# --- css-unscoped ---
echo "=== css-unscoped ==="
run_lint "css-unscoped@test"
assert_output_contains "detects unscoped CSS classes" "css/unscoped-class"
assert_output_contains "detects !important usage" "css/important"
echo ""

# --- ego-lint-ignore ---
echo "=== ego-lint-ignore ==="
run_lint "ego-lint-ignore@test"
assert_exit_code "exits with 0 (suppressed rules)" 0
assert_output_not_contains "R-WEB-01 suppressed by next-line" "\[FAIL\].*R-WEB-01"
assert_output_not_contains "R-WEB-10 suppressed by inline" "\[FAIL\].*R-WEB-10"
echo ""

# Extended assertion files (auto-sourced from assertions/ directory)
ASSERTIONS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/assertions"
for assertion_file in "$ASSERTIONS_DIR"/*.sh; do
    [[ -f "$assertion_file" ]] || continue
    source "$assertion_file"
done

# --- Summary ---
echo "============================================"
echo "  Results: $PASS_COUNT passed, $FAIL_COUNT failed"
echo "============================================"

if [[ "$FAIL_COUNT" -gt 0 ]]; then
    echo -e "${RED}SOME TESTS FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}ALL TESTS PASSED${NC}"
    exit 0
fi
