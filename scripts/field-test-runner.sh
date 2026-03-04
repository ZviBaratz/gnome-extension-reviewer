#!/usr/bin/env bash
# field-test-runner.sh — Batch ego-lint runner for field test extensions.
#
# Usage:
#   field-test-runner.sh [OPTIONS]
#     --lint-only         Only run ego-lint (default)
#     --update-baselines  Save current results as new baselines
#     --extension NAME    Run for a single extension
#     --fetch-only        Only fetch/update extension sources
#     --no-fetch          Skip fetching, use existing cache/paths
#     --json              Output summary as JSON instead of table

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MANIFEST="$ROOT_DIR/field-tests/manifest.yaml"
CACHE_DIR="$ROOT_DIR/field-tests/cache"
BASELINES_DIR="$ROOT_DIR/field-tests/baselines"
ANNOTATIONS_DIR="$ROOT_DIR/field-tests/annotations"
HISTORY_FILE="$ROOT_DIR/field-tests/history.jsonl"

EGO_LINT="$ROOT_DIR/ego-lint"
PARSE_MANIFEST="$SCRIPT_DIR/parse-manifest.py"
PARSE_RESULTS="$SCRIPT_DIR/parse-lint-results.py"
DIFF_BASELINES="$SCRIPT_DIR/diff-baselines.py"

# Options
OPT_UPDATE_BASELINES=false
OPT_SINGLE_EXT=""
OPT_FETCH_ONLY=false
OPT_NO_FETCH=false
OPT_JSON=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --update-baselines) OPT_UPDATE_BASELINES=true; shift ;;
        --extension)        OPT_SINGLE_EXT="$2"; shift 2 ;;
        --fetch-only)       OPT_FETCH_ONLY=true; shift ;;
        --no-fetch)         OPT_NO_FETCH=true; shift ;;
        --json)             OPT_JSON=true; shift ;;
        --lint-only)        shift ;;  # default behavior
        -h|--help)
            echo "Usage: field-test-runner.sh [OPTIONS]"
            echo "  --lint-only         Only run ego-lint (default)"
            echo "  --update-baselines  Save current results as new baselines"
            echo "  --extension NAME    Run for a single extension"
            echo "  --fetch-only        Only fetch/update extension sources"
            echo "  --no-fetch          Skip fetching, use existing cache/paths"
            echo "  --json              Output summary as JSON instead of table"
            exit 0
            ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# Get ego-lint version
EGO_LINT_VERSION="$(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")"

# Timestamp for this run
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
RESULTS_DIR="$ROOT_DIR/field-tests/results/$(echo "$TIMESTAMP" | tr ':' '-')"
mkdir -p "$RESULTS_DIR"

# Parse manifest
MANIFEST_JSON="$(python3 "$PARSE_MANIFEST" "$MANIFEST")"
EXT_COUNT="$(echo "$MANIFEST_JSON" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")"

# When --json, redirect progress output to stderr so stdout is clean JSON
if [[ "$OPT_JSON" == true ]]; then
    exec 3>&1 1>&2
fi

echo "================================================================"
echo "  Field Test Runner — $EXT_COUNT extensions"
echo "  ego-lint version: $EGO_LINT_VERSION"
echo "  Timestamp: $TIMESTAMP"
echo "================================================================"
echo ""

# Process each extension
SUMMARY_ENTRIES=()
TOTAL_PASS=0
TOTAL_FAIL=0
TOTAL_WARN=0
TOTAL_SKIP=0
PROCESSED=0
SKIPPED=0
CHANGED=0

process_extension() {
    local idx="$1"
    local ext_json
    ext_json="$(echo "$MANIFEST_JSON" | python3 -c "
import json, sys
exts = json.load(sys.stdin)
print(json.dumps(exts[$idx]))
")"

    local name uuid source_type ego_approved
    name="$(echo "$ext_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['name'])")"
    uuid="$(echo "$ext_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['uuid'])")"
    source_type="$(echo "$ext_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['source']['type'])")"
    ego_approved="$(echo "$ext_json" | python3 -c "import json,sys; print('true' if json.load(sys.stdin).get('ego_approved', False) else 'false')")"

    # Filter by --extension if specified
    if [[ -n "$OPT_SINGLE_EXT" && "$name" != "$OPT_SINGLE_EXT" ]]; then
        return 1  # signal: skipped by filter
    fi

    echo "--- $name ($uuid) ---"

    # Resolve extension path
    local ext_path=""
    case "$source_type" in
        local)
            ext_path="$(echo "$ext_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['source']['path'])")"
            if [[ ! -d "$ext_path" ]]; then
                echo "  SKIP: local path not found: $ext_path"
                return 1
            fi
            ;;
        github)
            local repo ref
            repo="$(echo "$ext_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['source']['repo'])")"
            ref="$(echo "$ext_json" | python3 -c "import json,sys; s=json.load(sys.stdin)['source']; print(s.get('ref', ''))")"
            ext_path="$CACHE_DIR/$name"

            if [[ "$OPT_NO_FETCH" != true ]] && [[ ! -d "$ext_path" ]]; then
                echo "  Fetching from github: $repo..."
                if ! git clone --depth 1 "https://github.com/$repo.git" "$ext_path" 2>/dev/null; then
                    echo "  SKIP: failed to clone $repo"
                    return 1
                fi
                if [[ -n "$ref" ]]; then
                    git -C "$ext_path" fetch --depth 1 origin "$ref" 2>/dev/null
                    git -C "$ext_path" checkout "$ref" 2>/dev/null || true
                fi
            fi
            if [[ ! -d "$ext_path" ]]; then
                echo "  SKIP: cache not found (run without --no-fetch)"
                return 1
            fi
            ;;
        github-release)
            local repo tag
            repo="$(echo "$ext_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['source']['repo'])")"
            tag="$(echo "$ext_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['source']['tag'])")"
            ext_path="$CACHE_DIR/$name"

            if [[ "$OPT_NO_FETCH" != true ]] && [[ ! -d "$ext_path" ]]; then
                echo "  Fetching from github release: $repo@$tag..."
                if ! git clone --depth 1 --branch "$tag" "https://github.com/$repo.git" "$ext_path" 2>/dev/null; then
                    echo "  SKIP: failed to clone $repo@$tag"
                    return 1
                fi
            fi
            if [[ ! -d "$ext_path" ]]; then
                echo "  SKIP: cache not found (run without --no-fetch)"
                return 1
            fi
            ;;
        *)
            echo "  SKIP: unknown source type: $source_type"
            return 1
            ;;
    esac

    if [[ "$OPT_FETCH_ONLY" == true ]]; then
        echo "  OK: source available at $ext_path"
        return 0
    fi

    # Run ego-lint
    local lint_output exit_code
    lint_output="$("$EGO_LINT" --verbose "$ext_path" 2>&1)" || exit_code=$?
    exit_code="${exit_code:-0}"

    # Parse results to JSON
    local approved_flag=""
    if [[ "$ego_approved" == "true" ]]; then
        approved_flag="--ego-approved"
    fi

    local result_file="$RESULTS_DIR/$name.lint.json"
    echo "$lint_output" | python3 "$PARSE_RESULTS" \
        --name "$name" \
        --uuid "$uuid" \
        $approved_flag \
        --exit-code "$exit_code" \
        --version "$EGO_LINT_VERSION" \
        > "$result_file"

    # Extract counts
    local pass fail warn skip
    pass="$(python3 -c "import json; d=json.load(open('$result_file')); print(d['counts']['pass'])")"
    fail="$(python3 -c "import json; d=json.load(open('$result_file')); print(d['counts']['fail'])")"
    warn="$(python3 -c "import json; d=json.load(open('$result_file')); print(d['counts']['warn'])")"
    skip="$(python3 -c "import json; d=json.load(open('$result_file')); print(d['counts']['skip'])")"

    TOTAL_PASS=$((TOTAL_PASS + pass))
    TOTAL_FAIL=$((TOTAL_FAIL + fail))
    TOTAL_WARN=$((TOTAL_WARN + warn))
    TOTAL_SKIP=$((TOTAL_SKIP + skip))
    PROCESSED=$((PROCESSED + 1))

    # Diff against baseline if available
    local baseline_file="$BASELINES_DIR/$name.json"
    local annotation_file="$ANNOTATIONS_DIR/$name.yaml"
    local diff_file="$RESULTS_DIR/$name.diff.json"
    local changed="false"
    local new_count=0 resolved_count=0 unannotated_count=0

    if [[ -f "$baseline_file" ]]; then
        local ann_arg=""
        [[ -f "$annotation_file" ]] && ann_arg="$annotation_file"
        python3 "$DIFF_BASELINES" "$result_file" "$baseline_file" $ann_arg > "$diff_file"
        changed="$(python3 -c "import json; print(str(json.load(open('$diff_file'))['changed']).lower())")"
        new_count="$(python3 -c "import json; print(len(json.load(open('$diff_file'))['new_findings']))")"
        resolved_count="$(python3 -c "import json; print(len(json.load(open('$diff_file'))['resolved_findings']))")"
        unannotated_count="$(python3 -c "import json; print(len(json.load(open('$diff_file'))['unannotated_findings']))")"
    fi

    if [[ "$changed" == "true" ]]; then
        CHANGED=$((CHANGED + 1))
    fi

    # Print status
    local status_icon="✓"
    [[ "$fail" -gt 0 ]] && status_icon="✗"
    [[ "$changed" == "true" ]] && status_icon="△"

    printf "  %s  P:%-4s F:%-4s W:%-4s S:%-4s" "$status_icon" "$pass" "$fail" "$warn" "$skip"
    if [[ -f "$baseline_file" ]]; then
        printf "  (new:%s resolved:%s unannotated:%s)" "$new_count" "$resolved_count" "$unannotated_count"
    else
        printf "  (no baseline)"
    fi
    echo ""

    # Update baselines if requested
    if [[ "$OPT_UPDATE_BASELINES" == true ]]; then
        cp "$result_file" "$baseline_file"
        echo "  → baseline updated"
    fi

    # Append to history
    python3 -c "
import json
entry = {
    'date': '$TIMESTAMP',
    'name': '$name',
    'ego_lint_version': '$EGO_LINT_VERSION',
    'exit_code': $exit_code,
    'counts': {'pass': $pass, 'fail': $fail, 'warn': $warn, 'skip': $skip},
    'changed': $([[ "$changed" == "true" ]] && echo "True" || echo "False"),
}
print(json.dumps(entry))
" >> "$HISTORY_FILE"

    # Store summary entry
    SUMMARY_ENTRIES+=("$name|$pass|$fail|$warn|$skip|$changed|$new_count|$resolved_count|$unannotated_count")

    return 0
}

# Main loop
for idx in $(seq 0 $((EXT_COUNT - 1))); do
    if ! process_extension "$idx"; then
        SKIPPED=$((SKIPPED + 1))
    fi
    echo ""
done

# Build summary JSON (used for both file output and --json flag)
ENTRIES_JSON="$(python3 -c "
import json, sys
entries = []
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('|')
    entries.append({
        'name': parts[0],
        'counts': {
            'pass': int(parts[1]),
            'fail': int(parts[2]),
            'warn': int(parts[3]),
            'skip': int(parts[4]),
        },
        'changed': parts[5] == 'true',
        'new': int(parts[6]),
        'resolved': int(parts[7]),
        'unannotated': int(parts[8]),
    })
print(json.dumps(entries))
" <<< "$(printf '%s\n' "${SUMMARY_ENTRIES[@]}")")"

SUMMARY_JSON="$(python3 -c "
import json, sys
extensions = json.loads(sys.argv[1])
summary = {
    'timestamp': '$TIMESTAMP',
    'ego_lint_version': '$EGO_LINT_VERSION',
    'processed': $PROCESSED,
    'skipped': $SKIPPED,
    'changed': $CHANGED,
    'totals': {
        'pass': $TOTAL_PASS,
        'fail': $TOTAL_FAIL,
        'warn': $TOTAL_WARN,
        'skip': $TOTAL_SKIP,
    },
    'extensions': extensions,
    'results_dir': '$RESULTS_DIR',
}
print(json.dumps(summary, indent=2))
" "$ENTRIES_JSON")"

echo "$SUMMARY_JSON" > "$RESULTS_DIR/summary.json"

if [[ "$OPT_JSON" == true ]]; then
    echo "$SUMMARY_JSON" >&3
else
    # Print human-readable summary
    echo "================================================================"
    echo "  Summary: $PROCESSED processed, $SKIPPED skipped, $CHANGED changed"
    echo "  Totals: P:$TOTAL_PASS F:$TOTAL_FAIL W:$TOTAL_WARN S:$TOTAL_SKIP"
    echo "================================================================"
    echo ""
    echo "Results saved to: $RESULTS_DIR/"

    if [[ "$OPT_UPDATE_BASELINES" == true ]]; then
        echo "Baselines updated in: $BASELINES_DIR/"
    fi
fi
