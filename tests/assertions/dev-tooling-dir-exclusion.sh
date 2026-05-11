# Dev-tooling directory exclusion tests
# Sourced by run-tests.sh — uses run_lint, assert_output_contains, assert_output_not_contains, etc.
#
# Verifies that top-level directories containing Vagrant/Gulp development infrastructure
# are auto-detected (via Vagrantfile trigger) and excluded from pattern rules and
# non-gjs-scripts / script-permissions checks.
# Covers the rounded-window-corners pattern where gulp/ and conf/ hold dev tooling
# that is never shipped in an EGO package.

echo "=== dev-tooling-exclusion ==="
run_lint "dev-tooling-exclusion@test"
assert_exit_code "exits with 0 (dev-tooling dirs not flagged)" 0
# R-SEC-04 (sudo) must not fire from gulp/vagrant.js
assert_output_not_contains "no R-SEC-04 from gulp/ dir" "\[WARN\].*R-SEC-04.*gulp"
# R-SEC-22 (gsettings) must not fire from gulp/vagrant.js
assert_output_not_contains "no R-SEC-22 from gulp/ dir" "\[WARN\].*R-SEC-22.*gulp"
# non-gjs-scripts must not flag conf/init_vm.sh
assert_output_not_contains "no non-gjs-scripts WARN" "\[WARN\].*non-gjs-scripts"
# script-permissions must not flag conf/init_vm.sh
assert_output_not_contains "no script-permissions WARN" "\[WARN\].*script-permissions"
# SKIP notice must be emitted for dev-tooling dirs
assert_output_contains "dev-tooling-dir-exclusion SKIP emitted" "\[SKIP\].*dev-tooling-dir-exclusion"
echo ""
