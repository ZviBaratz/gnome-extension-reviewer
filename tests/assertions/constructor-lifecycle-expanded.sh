# Expanded constructor lifecycle and value type exemption tests
# Sourced by run-tests.sh

echo "=== constructor-lifecycle-expanded ==="
run_lint "constructor-lifecycle-expanded@test"
assert_exit_code "exits with 0 (no blocking violations)" 0
assert_output_not_contains "no FP on Cogl.Color value type" "init/shell-modification.*extension.js"
assert_output_not_contains "no FP on _destroy lifecycle class" "constructor-resources.*helper.js.*PrivateDestroy"
assert_output_not_contains "no FP on onDestroy lifecycle class" "constructor-resources.*helper.js.*OnDestroy"
assert_output_not_contains "no FP on ShaderEffect widget base" "constructor-resources.*helper.js.*CustomEffect"
echo ""
