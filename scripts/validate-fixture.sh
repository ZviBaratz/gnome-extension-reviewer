#!/usr/bin/env bash
# validate-fixture.sh — Validate all test fixtures in tests/fixtures/
#
# Checks:
#   - Directory name contains @
#   - metadata.json exists and its uuid matches the directory name
#   - LICENSE file exists
#   - metadata.json has a url field
#
# Usage: scripts/validate-fixture.sh
# Exit: 0 if all valid, 1 if any violations found

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES_DIR="$SCRIPT_DIR/tests/fixtures"
violations=0

for fixture_dir in "$FIXTURES_DIR"/*/; do
    dir_name="$(basename "$fixture_dir")"

    # Skip regressions/ subdirectory (contains nested fixtures)
    if [[ "$dir_name" == "regressions" ]]; then
        continue
    fi

    # Check: directory name contains @
    if [[ "$dir_name" != *@* ]]; then
        echo "FAIL: $dir_name — directory name missing @ (expected name@domain format)"
        violations=$((violations + 1))
    fi

    # Check: metadata.json exists
    if [[ ! -f "$fixture_dir/metadata.json" ]]; then
        echo "FAIL: $dir_name — missing metadata.json"
        violations=$((violations + 1))
        continue  # Can't check uuid/url without metadata.json
    fi

    # Check: uuid matches directory name
    uuid="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['uuid'])" "$fixture_dir/metadata.json" 2>/dev/null || echo "")"
    if [[ "$uuid" != "$dir_name" ]]; then
        echo "FAIL: $dir_name — uuid mismatch (metadata.json uuid='$uuid', expected '$dir_name')"
        violations=$((violations + 1))
    fi

    # Check: url field exists
    has_url="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print('yes' if 'url' in d and d['url'] else 'no')" "$fixture_dir/metadata.json" 2>/dev/null || echo "no")"
    if [[ "$has_url" != "yes" ]]; then
        echo "FAIL: $dir_name — metadata.json missing url field"
        violations=$((violations + 1))
    fi

    # Check: LICENSE file exists
    if [[ ! -f "$fixture_dir/LICENSE" ]]; then
        echo "FAIL: $dir_name — missing LICENSE file"
        violations=$((violations + 1))
    fi
done

# Also validate fixtures under regressions/
if [[ -d "$FIXTURES_DIR/regressions" ]]; then
    for fixture_dir in "$FIXTURES_DIR"/regressions/*/; do
        [[ -d "$fixture_dir" ]] || continue
        dir_name="$(basename "$fixture_dir")"

        if [[ "$dir_name" != *@* ]]; then
            echo "FAIL: regressions/$dir_name — directory name missing @"
            violations=$((violations + 1))
        fi

        if [[ ! -f "$fixture_dir/metadata.json" ]]; then
            echo "FAIL: regressions/$dir_name — missing metadata.json"
            violations=$((violations + 1))
            continue
        fi

        uuid="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['uuid'])" "$fixture_dir/metadata.json" 2>/dev/null || echo "")"
        if [[ "$uuid" != "$dir_name" ]]; then
            echo "FAIL: regressions/$dir_name — uuid mismatch (uuid='$uuid', expected '$dir_name')"
            violations=$((violations + 1))
        fi

        has_url="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print('yes' if 'url' in d and d['url'] else 'no')" "$fixture_dir/metadata.json" 2>/dev/null || echo "no")"
        if [[ "$has_url" != "yes" ]]; then
            echo "FAIL: regressions/$dir_name — metadata.json missing url field"
            violations=$((violations + 1))
        fi

        if [[ ! -f "$fixture_dir/LICENSE" ]]; then
            echo "FAIL: regressions/$dir_name — missing LICENSE file"
            violations=$((violations + 1))
        fi
    done
fi

if [[ "$violations" -gt 0 ]]; then
    echo ""
    echo "$violations violation(s) found."
    exit 1
else
    echo "All fixtures valid."
    exit 0
fi
