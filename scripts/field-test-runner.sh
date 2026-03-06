#!/usr/bin/env bash
# field-test-runner.sh — Batch ego-lint runner for field test extensions.
#
# Usage:
#   field-test-runner.sh [OPTIONS]
#     --lint-only         Only run ego-lint (default)
#     --update-baselines  Save current results as new baselines
#     --extension NAME    Run for a single extension
#     --exclude NAME      Exclude extension from lint+review (repeatable)
#     --review-exclude N  Exclude extension from review only (repeatable)
#     --fetch-only        Only fetch/update extension sources
#     --no-fetch          Skip fetching, use existing cache/paths
#     --json              Output summary as JSON instead of table
#     --review            Run ego-review on all extensions after lint
#     --review-changed    Run ego-review only on extensions with changed lint results
#     --parallel N        Max concurrent claude -p sessions (default: 3)
#     --review-dry-run    Print hydrated prompts without invoking claude -p
#     --budget AMOUNT     Max USD per review session (default: 4.00)

set -euo pipefail
trap 'echo "Error: script failed at line $LINENO (exit code $?): $BASH_COMMAND" >&2' ERR

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MANIFEST="$ROOT_DIR/field-tests/manifest.yaml"
CACHE_DIR="$ROOT_DIR/field-tests/cache"
BASELINES_DIR="$ROOT_DIR/field-tests/baselines"
ANNOTATIONS_DIR="$ROOT_DIR/field-tests/annotations"
HISTORY_FILE="$ROOT_DIR/field-tests/history.jsonl"

# Helper: run python3 -c with JSON error handling.
# Usage: json_extract "context label" 'python expression' [< input]
# Wraps the expression in try/except for clear error messages.
json_extract() {
    local context="$1"; shift
    local expr="$1"; shift
    python3 -c "
import json, sys
try:
    $expr
except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
    print(f'Error ($context): {type(e).__name__}: {e}', file=sys.stderr)
    sys.exit(1)
" "$@"
}

EGO_LINT="$ROOT_DIR/ego-lint"
PARSE_MANIFEST="$SCRIPT_DIR/parse-manifest.py"
PARSE_RESULTS="$SCRIPT_DIR/parse-lint-results.py"
DIFF_BASELINES="$SCRIPT_DIR/diff-baselines.py"
HYDRATE_PROMPT="$SCRIPT_DIR/hydrate-review-prompt.py"
REVIEW_TEMPLATE="$SCRIPT_DIR/review-prompt.md"
PLUGIN_DIR="$ROOT_DIR"

# Validate required scripts exist before processing
for _req_script in "$EGO_LINT" "$PARSE_MANIFEST" "$PARSE_RESULTS" "$DIFF_BASELINES"; do
    if [[ ! -f "$_req_script" ]]; then
        echo "Error: required script not found: $_req_script" >&2
        exit 1
    fi
done

if [[ ! -f "$MANIFEST" ]]; then
    echo "Error: manifest not found: $MANIFEST" >&2
    exit 1
fi

# Options
OPT_UPDATE_BASELINES=false
OPT_SINGLE_EXT=""
OPT_EXCLUDE_EXTS=()
OPT_REVIEW_EXCLUDE_EXTS=()
OPT_FETCH_ONLY=false
OPT_NO_FETCH=false
OPT_JSON=false
OPT_REVIEW=false
OPT_REVIEW_CHANGED=false
OPT_PARALLEL=3
OPT_REVIEW_DRY_RUN=false
OPT_BUDGET="4.00"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --update-baselines) OPT_UPDATE_BASELINES=true; shift ;;
        --extension)        OPT_SINGLE_EXT="$2"; shift 2 ;;
        --exclude)          OPT_EXCLUDE_EXTS+=("$2"); shift 2 ;;
        --review-exclude)   OPT_REVIEW_EXCLUDE_EXTS+=("$2"); shift 2 ;;
        --fetch-only)       OPT_FETCH_ONLY=true; shift ;;
        --no-fetch)         OPT_NO_FETCH=true; shift ;;
        --json)             OPT_JSON=true; shift ;;
        --lint-only)        shift ;;  # default behavior
        --review)           OPT_REVIEW=true; shift ;;
        --review-changed)   OPT_REVIEW_CHANGED=true; shift ;;
        --parallel)
            if ! [[ "$2" =~ ^[1-9][0-9]*$ ]]; then
                echo "Error: --parallel requires a positive integer, got: $2" >&2
                exit 1
            fi
            OPT_PARALLEL="$2"; shift 2 ;;
        --review-dry-run)   OPT_REVIEW_DRY_RUN=true; shift ;;
        --budget)
            if ! [[ "$2" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
                echo "Error: --budget requires a numeric amount, got: $2" >&2
                exit 1
            fi
            OPT_BUDGET="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: field-test-runner.sh [OPTIONS]"
            echo "  --lint-only         Only run ego-lint (default)"
            echo "  --update-baselines  Save current results as new baselines"
            echo "  --extension NAME    Run for a single extension"
            echo "  --exclude NAME      Exclude extension from lint+review (repeatable)"
            echo "  --review-exclude N  Exclude extension from review only (repeatable)"
            echo "  --fetch-only        Only fetch/update extension sources"
            echo "  --no-fetch          Skip fetching, use existing cache/paths"
            echo "  --json              Output summary as JSON instead of table"
            echo "  --review            Run ego-review on all extensions after lint"
            echo "  --review-changed    Run ego-review only on changed extensions"
            echo "  --parallel N        Max concurrent claude -p sessions (default: 3)"
            echo "  --review-dry-run    Print hydrated prompts without invoking claude"
            echo "  --budget AMOUNT     Max USD per review session (default: 4.00)"
            exit 0
            ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# --review-dry-run implies --review if neither --review nor --review-changed is set
if [[ "$OPT_REVIEW_DRY_RUN" == true && "$OPT_REVIEW" != true && "$OPT_REVIEW_CHANGED" != true ]]; then
    OPT_REVIEW=true
fi

# Validate review flags
if [[ "$OPT_REVIEW" == true || "$OPT_REVIEW_CHANGED" == true ]] && [[ "$OPT_REVIEW_DRY_RUN" != true ]]; then
    if ! command -v claude &>/dev/null; then
        echo "Error: 'claude' CLI not found. Required for --review/--review-changed." >&2
        exit 1
    fi
    if ! command -v timeout &>/dev/null; then
        echo "Error: 'timeout' command not found. Required for --review/--review-changed." >&2
        exit 1
    fi
fi

# Ensure baselines directory exists when updating
if [[ "$OPT_UPDATE_BASELINES" == true ]]; then
    mkdir -p "$BASELINES_DIR"
fi

# Get ego-lint version
EGO_LINT_VERSION="$(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")"

# Timestamp for this run
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
RESULTS_DIR="$ROOT_DIR/field-tests/results/$(echo "$TIMESTAMP" | tr ':' '-')"
mkdir -p "$RESULTS_DIR"

# Parse manifest
MANIFEST_JSON="$(python3 "$PARSE_MANIFEST" "$MANIFEST")"
EXT_COUNT="$(echo "$MANIFEST_JSON" | json_extract "manifest count" "print(len(json.load(sys.stdin)))")"

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

# Associative arrays for review phase (name → path, name → changed, name → review status)
declare -A EXT_PATHS
declare -A EXT_CHANGED
declare -A REVIEW_STATUS

# Resolve extension path from manifest entry JSON.
# Sets RESOLVED_PATH on success, returns 1 on failure.
resolve_ext_path() {
    local ext_json="$1"
    local name="$2"
    local source_type source_path source_repo source_ref _src_line
    _src_line="$(echo "$ext_json" | json_extract "$name source" "
s = json.load(sys.stdin).get('source', {})
print(s.get('type',''), s.get('path',''), s.get('repo',''), s.get('ref', s.get('tag','')), sep='\t')
")"
    IFS=$'\t' read -r source_type source_path source_repo source_ref <<< "$_src_line"

    RESOLVED_PATH=""
    case "$source_type" in
        local)
            RESOLVED_PATH="$source_path"
            if [[ ! -d "$RESOLVED_PATH" ]]; then
                echo "  SKIP: local path not found: $RESOLVED_PATH"
                return 1
            fi
            ;;
        github)
            RESOLVED_PATH="$CACHE_DIR/$name"

            if [[ "$OPT_NO_FETCH" != true ]] && [[ ! -d "$RESOLVED_PATH" ]]; then
                echo "  Fetching from github: $source_repo..."
                clone_err="$(git clone --depth 1 "https://github.com/$source_repo.git" "$RESOLVED_PATH" 2>&1)" || {
                    echo "  SKIP: failed to clone $source_repo"
                    echo "  ${clone_err%%$'\n'*}" >&2
                    return 1
                }
                if [[ -n "$source_ref" ]]; then
                    fetch_err="$(git -C "$RESOLVED_PATH" fetch --depth 1 origin "$source_ref" 2>&1)" || {
                        echo "  SKIP: failed to fetch ref $source_ref from $source_repo"
                        echo "  ${fetch_err%%$'\n'*}" >&2
                        rm -rf "$RESOLVED_PATH"
                        return 1
                    }
                    checkout_err="$(git -C "$RESOLVED_PATH" checkout FETCH_HEAD 2>&1)" || {
                        echo "  SKIP: failed to checkout ref $source_ref"
                        echo "  ${checkout_err%%$'\n'*}" >&2
                        rm -rf "$RESOLVED_PATH"
                        return 1
                    }
                fi
            fi
            if [[ ! -d "$RESOLVED_PATH" ]]; then
                echo "  SKIP: cache not found (run without --no-fetch)"
                return 1
            fi
            ;;
        github-release)
            RESOLVED_PATH="$CACHE_DIR/$name"

            if [[ "$OPT_NO_FETCH" != true ]] && [[ ! -d "$RESOLVED_PATH" ]]; then
                echo "  Fetching from github release: $source_repo@$source_ref..."
                clone_err="$(git clone --depth 1 --branch "$source_ref" "https://github.com/$source_repo.git" "$RESOLVED_PATH" 2>&1)" || {
                    echo "  SKIP: failed to clone $source_repo@$source_ref"
                    echo "  ${clone_err%%$'\n'*}" >&2
                    return 1
                }
            fi
            if [[ ! -d "$RESOLVED_PATH" ]]; then
                echo "  SKIP: cache not found (run without --no-fetch)"
                return 1
            fi
            ;;
        *)
            echo "  SKIP: unknown source type: $source_type"
            return 1
            ;;
    esac
    return 0
}

process_extension() {
    local idx="$1"
    local ext_json
    if ! ext_json="$(echo "$MANIFEST_JSON" | json_extract "manifest[$idx]" "
exts = json.load(sys.stdin)
print(json.dumps(exts[$idx]))
")"; then
        echo "  ERROR: failed to extract manifest entry $idx" >&2
        return 1
    fi

    local name uuid ego_approved _ext_line
    if ! _ext_line="$(echo "$ext_json" | json_extract "extension[$idx] metadata" "
d = json.load(sys.stdin)
print(d['name'], d['uuid'], 'true' if d.get('ego_approved', False) else 'false', sep='\t')
")"; then
        echo "  ERROR: failed to extract extension metadata for entry $idx" >&2
        return 1
    fi
    IFS=$'\t' read -r name uuid ego_approved <<< "$_ext_line"

    # Filter by --extension / --exclude if specified
    if [[ -n "$OPT_SINGLE_EXT" && "$name" != "$OPT_SINGLE_EXT" ]]; then
        return 2  # signal: silently filtered out
    fi
    for excl in "${OPT_EXCLUDE_EXTS[@]+"${OPT_EXCLUDE_EXTS[@]}"}"; do
        if [[ "$name" == "$excl" ]]; then
            return 2
        fi
    done

    echo "--- $name ($uuid) ---"

    # Resolve extension path
    if ! resolve_ext_path "$ext_json" "$name"; then
        return 1
    fi
    local ext_path="$RESOLVED_PATH"

    if [[ "$OPT_FETCH_ONLY" == true ]]; then
        echo "  OK: source available at $ext_path"
        return 0
    fi

    # Run ego-lint
    local lint_output exit_code
    lint_output="$("$EGO_LINT" --verbose "$ext_path" 2>&1)" || exit_code=$?
    exit_code="${exit_code:-0}"

    # Parse results to JSON
    local parse_args=(--name "$name" --uuid "$uuid")
    [[ "$ego_approved" == "true" ]] && parse_args+=(--ego-approved)
    parse_args+=(--exit-code "$exit_code" --version "$EGO_LINT_VERSION")

    # NOTE: process_extension is called with || rc=$?, which disables set -e
    # for the entire function body. Guard critical commands explicitly.
    local result_file="$RESULTS_DIR/$name.lint.json"
    if ! echo "$lint_output" | python3 "$PARSE_RESULTS" \
        "${parse_args[@]}" > "$result_file"; then
        echo "  ERROR: failed to parse lint results for $name" >&2
        return 1
    fi

    # Extract counts
    local pass fail warn skip _counts_line
    if ! _counts_line="$(json_extract "$name counts" "
d = json.load(sys.stdin)
c = d['counts']
print(c['pass'], c['fail'], c['warn'], c['skip'], sep='\t')
" < "$result_file")"; then
        echo "  ERROR: failed to extract counts from $result_file" >&2
        return 1
    fi
    IFS=$'\t' read -r pass fail warn skip <<< "$_counts_line"

    # Sanity check: nonzero exit + zero results likely means ego-lint crashed
    local total=$((pass + fail + warn + skip))
    if [[ "$exit_code" -ne 0 && "$total" -eq 0 ]]; then
        echo "  ⚠ WARNING: ego-lint exited $exit_code but produced 0 check results (possible crash)"
    fi

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
        local diff_args=("$result_file" "$baseline_file")
        [[ -f "$annotation_file" ]] && diff_args+=("$annotation_file")
        if ! python3 "$DIFF_BASELINES" "${diff_args[@]}" > "$diff_file"; then
            echo "  WARNING: baseline diff failed for $name" >&2
        elif [[ -s "$diff_file" ]]; then
            local _diff_line
            if _diff_line="$(json_extract "$name diff" "
d = json.load(sys.stdin)
print(str(d['changed']).lower(), len(d['new_findings']), len(d['resolved_findings']), len(d['unannotated_findings']), sep='\t')
" < "$diff_file")"; then
                IFS=$'\t' read -r changed new_count resolved_count unannotated_count <<< "$_diff_line"
            else
                echo "  WARNING: failed to parse diff results for $name" >&2
            fi
        fi
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
        if ! cp "$result_file" "$baseline_file"; then
            echo "  ERROR: failed to update baseline: $baseline_file" >&2
            return 1
        fi
        echo "  → baseline updated"
    fi

    # Append to history (write to temp file first to prevent partial JSON
    # lines if json_extract crashes mid-output)
    local history_tmp
    history_tmp="$(mktemp)"
    if ! json_extract "$name history" "
date, name, version, exit_code, p, f, w, s, changed = sys.argv[1:]
entry = {
    'date': date, 'name': name, 'ego_lint_version': version,
    'exit_code': int(exit_code),
    'counts': {'pass': int(p), 'fail': int(f), 'warn': int(w), 'skip': int(s)},
    'changed': changed == 'true',
}
print(json.dumps(entry))
" "$TIMESTAMP" "$name" "$EGO_LINT_VERSION" "$exit_code" \
  "$pass" "$fail" "$warn" "$skip" "$changed" > "$history_tmp"; then
        echo "  WARNING: failed to build history entry for $name" >&2
        rm -f "$history_tmp"
    elif ! cat "$history_tmp" >> "$HISTORY_FILE"; then
        echo "  WARNING: failed to append history for $name" >&2
        rm -f "$history_tmp"
    else
        rm -f "$history_tmp"
    fi

    # Store summary entry
    SUMMARY_ENTRIES+=("$name|$pass|$fail|$warn|$skip|$changed|$new_count|$resolved_count|$unannotated_count")

    # Track for review phase
    EXT_PATHS["$name"]="$ext_path"
    EXT_CHANGED["$name"]="$changed"

    return 0
}

# Main loop
for idx in $(seq 0 $((EXT_COUNT - 1))); do
    rc=0
    process_extension "$idx" || rc=$?
    if [[ $rc -eq 1 ]]; then
        SKIPPED=$((SKIPPED + 1))
        echo ""
    elif [[ $rc -eq 0 ]]; then
        echo ""
    fi
    # rc==2: silently filtered, no output
done

# ── Review Phase ──────────────────────────────────────────────────────

if [[ "$OPT_REVIEW" == true || "$OPT_REVIEW_CHANGED" == true ]]; then
    echo "================================================================"
    echo "  Review Phase"
    echo "  Mode: $( [[ "$OPT_REVIEW" == true ]] && echo "all" || echo "changed-only" )"
    echo "  Parallel: $OPT_PARALLEL"
    [[ "$OPT_REVIEW_DRY_RUN" == true ]] && echo "  *** DRY RUN — no claude invocations ***"
    echo "================================================================"
    echo ""

    # Collect a finished review process and update its status
    collect_review_result() {
        local pid="$1" rname="$2"
        local rc=0 rfile
        # 2>/dev/null: suppress "not a child" warnings when PID was already
        # reaped between kill -0 check and wait (expected race condition)
        wait "$pid" 2>/dev/null || rc=$?
        if [[ $rc -eq 0 ]]; then
            REVIEW_STATUS["$rname"]="ok"
            echo "  ✓ Review complete: $rname"
        elif [[ $rc -eq 124 ]]; then
            REVIEW_STATUS["$rname"]="timeout"
            echo "  ✗ Review timeout: $rname"
        else
            REVIEW_STATUS["$rname"]="error"
            echo "  ✗ Review error (exit $rc): $rname"
        fi
        # Validate report file exists and is non-empty
        rfile="$RESULTS_DIR/$rname.review.md"
        if [[ ! -s "$rfile" ]]; then
            REVIEW_STATUS["$rname"]="no-report"
            echo "  ⚠ No report written: $rname (exit code: $rc)"
        fi
    }

    REVIEW_PIDS=()
    REVIEW_NAMES=()

    # Kill orphaned background claude sessions on interrupt/exit
    cleanup_reviews() {
        for pid in "${REVIEW_PIDS[@]+"${REVIEW_PIDS[@]}"}"; do
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null || echo "  ⚠ Failed to kill review process $pid" >&2
            fi
        done
        wait 2>/dev/null || true
    }
    trap cleanup_reviews EXIT INT TERM

    for name in "${!EXT_PATHS[@]}"; do
        ext_path="${EXT_PATHS[$name]}"
        changed="${EXT_CHANGED[$name]}"

        # Filter: --review-exclude skips specific extensions from review
        review_excluded=false
        for excl in "${OPT_REVIEW_EXCLUDE_EXTS[@]+"${OPT_REVIEW_EXCLUDE_EXTS[@]}"}"; do
            if [[ "$name" == "$excl" ]]; then
                review_excluded=true
                break
            fi
        done
        if [[ "$review_excluded" == true ]]; then
            REVIEW_STATUS["$name"]="excluded"
            echo "  SKIP (review-excluded): $name"
            continue
        fi

        # Filter: --review-changed skips unchanged extensions
        if [[ "$OPT_REVIEW_CHANGED" == true && "$changed" != "true" ]]; then
            REVIEW_STATUS["$name"]="skipped"
            echo "  SKIP (unchanged): $name"
            continue
        fi

        local_lint="$RESULTS_DIR/$name.lint.json"
        local_diff="$RESULTS_DIR/$name.diff.json"
        local_ann="$ANNOTATIONS_DIR/$name.yaml"
        review_file="$RESULTS_DIR/$name.review.md"
        err_file="$RESULTS_DIR/$name.review.err"

        # Build hydration args
        hydrate_args=(
            --name "$name"
            --ext-path "$ext_path"
            --lint-json "$local_lint"
            --template "$REVIEW_TEMPLATE"
            --review-output "$review_file"
        )
        [[ -f "$local_diff" ]] && hydrate_args+=(--diff-json "$local_diff")
        [[ -f "$local_ann" ]] && hydrate_args+=(--annotations "$local_ann")

        if ! prompt="$(python3 "$HYDRATE_PROMPT" "${hydrate_args[@]}")"; then
            echo "  ERROR: prompt hydration failed for $name" >&2
            REVIEW_STATUS["$name"]="hydration-error"
            continue
        fi

        if [[ "$OPT_REVIEW_DRY_RUN" == true ]]; then
            echo "  DRY RUN: $name"
            echo "$prompt" > "$RESULTS_DIR/$name.review-prompt.md"
            REVIEW_STATUS["$name"]="dry-run"
            continue
        fi

        echo "  Launching review: $name"

        # Launch claude -p in background subshell
        # Claude writes the report to $review_file via Write tool (instructed in prompt).
        # Stdout goes to .review.out for debugging; stderr to .review.err.
        (
            timeout 600 claude -p \
                --plugin-dir "$PLUGIN_DIR" \
                --add-dir "$ext_path" \
                --dangerously-skip-permissions \
                --max-budget-usd "$OPT_BUDGET" \
                "$prompt" > "$RESULTS_DIR/$name.review.out" 2>"$err_file"
        ) &
        REVIEW_PIDS+=($!)
        REVIEW_NAMES+=("$name")

        # Throttle at concurrency cap — poll for completion instead of wait -n
        # to avoid reaping PIDs before collect_review_result can read exit codes
        while [[ ${#REVIEW_PIDS[@]} -ge $OPT_PARALLEL ]]; do
            new_pids=()
            new_names=()
            collected=false
            for i in "${!REVIEW_PIDS[@]}"; do
                if kill -0 "${REVIEW_PIDS[$i]}" 2>/dev/null; then
                    new_pids+=("${REVIEW_PIDS[$i]}")
                    new_names+=("${REVIEW_NAMES[$i]}")
                else
                    collect_review_result "${REVIEW_PIDS[$i]}" "${REVIEW_NAMES[$i]}"
                    collected=true
                fi
            done
            REVIEW_PIDS=("${new_pids[@]+"${new_pids[@]}"}")
            REVIEW_NAMES=("${new_names[@]+"${new_names[@]}"}")
            if [[ "$collected" != true ]]; then
                sleep 1
            fi
        done
    done

    # Wait for remaining review processes
    for i in "${!REVIEW_PIDS[@]}"; do
        collect_review_result "${REVIEW_PIDS[$i]}" "${REVIEW_NAMES[$i]}"
    done

    # Parse review reports into structured JSON
    for rname in "${!REVIEW_STATUS[@]}"; do
        [[ "${REVIEW_STATUS[$rname]}" != "ok" ]] && continue
        review_md="$RESULTS_DIR/$rname.review.md"
        review_json="$RESULTS_DIR/$rname.review.json"
        local_ann="$ANNOTATIONS_DIR/$rname.yaml"
        parse_args=(--name "$rname")
        [[ -f "$local_ann" ]] && parse_args+=(--annotations "$local_ann")
        if python3 "$SCRIPT_DIR/parse-review-results.py" "$review_md" \
                "${parse_args[@]}" > "$review_json" 2>/dev/null; then
            echo "  → Parsed review: $rname ($(python3 -c "import json; d=json.load(open('$review_json')); print(f\"{d['counts']['total']} findings\")"))"
        else
            echo "  ⚠ Failed to parse review: $rname" >&2
        fi
    done

    echo ""
fi

# Build summary JSON (used for both file output and --json flag)
# Build review status JSON for merging into summary
REVIEW_STATUS_LINES=""
for k in "${!REVIEW_STATUS[@]}"; do
    REVIEW_STATUS_LINES+="$k|${REVIEW_STATUS[$k]}"$'\n'
done
if [[ -n "$REVIEW_STATUS_LINES" ]]; then
    REVIEW_STATUS_JSON="$(json_extract "review status" "
status = {}
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    k, v = line.split('|', 1)
    status[k] = v
print(json.dumps(status))
" <<< "$REVIEW_STATUS_LINES")"
else
    REVIEW_STATUS_JSON="{}"
fi

ENTRIES_JSON="$(json_extract "summary entries" "
review_status = json.loads(sys.argv[1])
entries = []
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('|')
    name = parts[0]
    entry = {
        'name': name,
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
        'review_status': review_status.get(name, 'none'),
    }
    entries.append(entry)
print(json.dumps(entries))
" "$REVIEW_STATUS_JSON" <<< "$(printf '%s\n' "${SUMMARY_ENTRIES[@]+"${SUMMARY_ENTRIES[@]}"}")")"

SUMMARY_JSON="$(json_extract "summary" "
extensions = json.loads(sys.argv[1])
ts, version, processed, skipped, changed = sys.argv[2:7]
tp, tf, tw, tsk, results_dir = sys.argv[7:]
summary = {
    'timestamp': ts, 'ego_lint_version': version,
    'processed': int(processed), 'skipped': int(skipped), 'changed': int(changed),
    'totals': {'pass': int(tp), 'fail': int(tf), 'warn': int(tw), 'skip': int(tsk)},
    'extensions': extensions, 'results_dir': results_dir,
}
print(json.dumps(summary, indent=2))
" "$ENTRIES_JSON" "$TIMESTAMP" "$EGO_LINT_VERSION" "$PROCESSED" "$SKIPPED" "$CHANGED" \
  "$TOTAL_PASS" "$TOTAL_FAIL" "$TOTAL_WARN" "$TOTAL_SKIP" "$RESULTS_DIR")"

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
