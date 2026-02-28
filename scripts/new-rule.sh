#!/usr/bin/env bash
# new-rule.sh — Interactive scaffolder for new ego-lint pattern rules.
#
# Creates:
#   1. A rule entry appended to rules/patterns.yaml
#   2. A test fixture directory in tests/fixtures/
#   3. Prints assertion lines to paste into your test file
#
# Usage: scripts/new-rule.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RULES_FILE="$SCRIPT_DIR/rules/patterns.yaml"
FIXTURES_DIR="$SCRIPT_DIR/tests/fixtures"

# --- Prompts ---

read -rp "Category prefix (e.g. SEC, SLOP, QUAL, WEB, DEPR): " category_prefix
if [[ -n "$category_prefix" ]]; then
    category_prefix_upper="$(echo "$category_prefix" | tr '[:lower:]' '[:upper:]')"
    highest=$(grep -oP "id: R-${category_prefix_upper}-\\K\\d+" "$RULES_FILE" 2>/dev/null | sort -n | tail -1)
    if [[ -n "$highest" ]]; then
        next=$((highest + 1))
        printf "  Suggestion: R-%s-%02d (highest existing: R-%s-%02d)\n" "$category_prefix_upper" "$next" "$category_prefix_upper" "$highest"
    else
        printf "  No existing R-%s-* rules found. Starting at 01.\n" "$category_prefix_upper"
        printf "  Suggestion: R-%s-01\n" "$category_prefix_upper"
    fi
fi

read -rp "Rule ID (e.g. R-SEC-24): " rule_id
if [[ -z "$rule_id" ]]; then
    echo "ERROR: Rule ID is required." >&2
    exit 1
fi

# Check for duplicate rule ID
if grep -q "id: $rule_id" "$RULES_FILE" 2>/dev/null; then
    echo "ERROR: Rule $rule_id already exists in $RULES_FILE" >&2
    exit 1
fi

read -rp "Regex pattern (Python re syntax): " pattern
if [[ -z "$pattern" ]]; then
    echo "ERROR: Pattern is required." >&2
    exit 1
fi

read -rp "Scope glob [*.js]: " scope
scope="${scope:-*.js}"

read -rp "Severity (blocking/advisory) [blocking]: " severity
severity="${severity:-blocking}"
if [[ "$severity" != "blocking" && "$severity" != "advisory" ]]; then
    echo "ERROR: Severity must be 'blocking' or 'advisory'." >&2
    exit 1
fi

read -rp "Message (human-readable explanation): " message
if [[ -z "$message" ]]; then
    echo "ERROR: Message is required." >&2
    exit 1
fi

read -rp "Fix suggestion (optional): " fix

read -rp "Category (e.g. web-apis, security, ai-slop): " category
if [[ -z "$category" ]]; then
    echo "ERROR: Category is required." >&2
    exit 1
fi

read -rp "Trigger code for test fixture (JS expression that matches the pattern): " trigger_code
if [[ -z "$trigger_code" ]]; then
    echo "ERROR: Trigger code is required to generate the test fixture." >&2
    exit 1
fi

# --- Derived values ---

rule_id_lower="$(echo "$rule_id" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"
fixture_name="${rule_id_lower}@test"
fixture_dir="$FIXTURES_DIR/$fixture_name"

if [[ -d "$fixture_dir" ]]; then
    echo "ERROR: Fixture directory $fixture_dir already exists." >&2
    exit 1
fi

# --- 1. Append rule to patterns.yaml ---

{
    echo ""
    echo "- id: $rule_id"
    echo "  pattern: \"$pattern\""
    echo "  scope: [\"$scope\"]"
    echo "  severity: $severity"
    echo "  message: \"$message\""
    echo "  category: $category"
    if [[ -n "$fix" ]]; then
        echo "  fix: \"$fix\""
    fi
} >> "$RULES_FILE"

echo "Added rule $rule_id to $RULES_FILE"

# --- 2. Create test fixture ---

mkdir -p "$fixture_dir"

cat > "$fixture_dir/metadata.json" <<EOF
{
    "uuid": "$fixture_name",
    "name": "$rule_id Test",
    "description": "Tests $rule_id",
    "shell-version": ["48"],
    "url": "https://example.com"
}
EOF

cat > "$fixture_dir/extension.js" <<EOF
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
export default class TestExtension extends Extension {
    enable() { $trigger_code; }
    disable() {}
}
EOF

cat > "$fixture_dir/LICENSE" <<'EOF'
SPDX-License-Identifier: GPL-2.0-or-later
EOF

echo "Created fixture at $fixture_dir/"

# --- 3. Append assertions to test file ---

if [[ "$severity" == "blocking" ]]; then
    status_tag="FAIL"
    exit_label="exits with 1 (has failures)"
    exit_val=1
else
    status_tag="WARN"
    exit_label="exits with 0 (advisory only)"
    exit_val=0
fi

ASSERTIONS_DIR="$SCRIPT_DIR/tests/assertions"

# Build assertion block
assertion_block="# --- $fixture_name ---
echo \"=== $fixture_name ===\"
run_lint \"$fixture_name\"
assert_exit_code \"$exit_label\" $exit_val
assert_output_contains \"detects $rule_id\" \"\\[${status_tag}\\].*${rule_id}\"
echo \"\""

echo ""
echo "Assertion lines to append:"
echo ""
echo "$assertion_block"
echo ""

# List existing assertion files
mapfile -t files < <(ls "$ASSERTIONS_DIR"/*.sh 2>/dev/null | grep -v local-regression.sh | sort)
if [[ ${#files[@]} -eq 0 ]]; then
    echo "No existing assertion files found."
else
    echo "Existing assertion files:"
    for i in "${!files[@]}"; do
        printf "  %2d) %s\n" "$((i + 1))" "$(basename "${files[$i]}")"
    done
fi
echo ""

read -rp "Append to which file? (number, or 'new' to create one, or 'skip' to print only): " choice

if [[ "$choice" == "skip" ]]; then
    echo "Skipped — copy the assertion lines above into your test file manually."
elif [[ "$choice" == "new" ]]; then
    suggested_name="$(echo "$category" | tr '[:upper:]' '[:lower:]' | tr ' ' '-').sh"
    read -rp "Filename [$suggested_name]: " new_name
    new_name="${new_name:-$suggested_name}"
    [[ "$new_name" == *.sh ]] || new_name="${new_name}.sh"
    target="$ASSERTIONS_DIR/$new_name"
    echo "" >> "$target"
    echo "$assertion_block" >> "$target"
    echo "Assertions appended to tests/assertions/$new_name"
elif [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#files[@]} )); then
    target="${files[$((choice - 1))]}"
    echo "" >> "$target"
    echo "$assertion_block" >> "$target"
    echo "Assertions appended to tests/assertions/$(basename "$target")"
else
    echo "Invalid choice — printing assertion lines for manual copy-paste."
fi

echo ""
echo "--- Done! Run 'bash tests/run-tests.sh' to verify. ---"
