#!/usr/bin/env bash
# ego-lint.sh — Orchestrator for GNOME Shell extension EGO compliance checks
#
# Usage: ego-lint.sh [EXTENSION_DIR]
#   EXTENSION_DIR defaults to the current working directory.
#
# Runs all checks and outputs structured results. Exit code 0 if no FAILs, 1 otherwise.

set -euo pipefail

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    cat <<'HELPEOF'
Usage: ego-lint [OPTIONS] [EXTENSION_DIR]

GNOME Shell extension compliance checker for EGO (extensions.gnome.org)
submission. Runs deterministic checks — bash + python only, no AI, no
network access.

Options:
  -h, --help       Show this help message and exit
  --show LEVELS    Comma-separated severity filter: fail,warn,pass,skip,all (default: fail,warn)
  --no-report      Hide grouped report, fix suggestions, and verdict

Checks (124 pattern rules + 13 structural scripts):
  metadata         UUID, required fields, shell-version, session-modes, GNOME trademark
  imports          GTK/Shell import segregation, transitive dependency analysis
  schema           Schema ID, path format, glib-compile-schemas dry-run
  lifecycle        enable/disable symmetry, signals, timeouts, D-Bus, widgets
  async            _destroyed guards, cancellable usage
  gobject          GObject.registerClass patterns, GTypeName validation
  resources        Cross-file resource graph, orphan detection
  security         Subprocess validation, pkexec, clipboard/network disclosure
  deprecated       Mainloop, Lang, ByteArray, ExtensionUtils, legacy imports
  version-compat   GNOME 44-50 migration rules (version-gated)
  css              Unscoped classes, !important, Shell theme overrides
  quality          AI slop detection, code provenance scoring, obfuscation
  package          Forbidden/required files, compiled schemas
  preferences      ExtensionPreferences base class, GTK4/Adwaita, memory leaks

Exit codes:
  0  No blocking issues found
  1  Blocking issues found (likely rejection)
  2  Invalid arguments
HELPEOF
    exit 0
}

REPORT=true
SHOW_LEVELS="fail,warn"   # comma-separated: fail,warn,pass,skip,all
EXT_DIR=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            show_help
            ;;
        --no-report)
            REPORT=false
            shift
            ;;
        --show)
            if [[ $# -lt 2 ]]; then
                echo "ego-lint: --show requires an argument" >&2
                exit 2
            fi
            SHOW_LEVELS="$2"
            shift 2
            ;;
        --show=*)
            SHOW_LEVELS="${1#--show=}"
            shift
            ;;
        *)
            EXT_DIR="$1"
            shift
            ;;
    esac
done
EXT_DIR="${EXT_DIR:-.}"
EXT_DIR="$(cd "$EXT_DIR" && pwd)"

SHOW_LEVELS="$(echo "$SHOW_LEVELS" | tr '[:upper:]' '[:lower:]')"

# Expand "all" to all four levels
if [[ ",$SHOW_LEVELS," == *",all,"* ]]; then
    SHOW_LEVELS="fail,warn,pass,skip"
fi

IFS=',' read -ra _levels <<< "$SHOW_LEVELS"
for _level in "${_levels[@]}"; do
    case "$_level" in
        fail|warn|pass|skip) ;;
        *) echo "ego-lint: unknown severity level '$_level' (valid: fail,warn,pass,skip,all)" >&2; exit 2 ;;
    esac
done

# Show header/metrics/chrome when all four levels are present
SHOW_ALL=false
if [[ ",$SHOW_LEVELS," == *",fail,"* && ",$SHOW_LEVELS," == *",warn,"* && \
      ",$SHOW_LEVELS," == *",pass,"* && ",$SHOW_LEVELS," == *",skip,"* ]]; then
    SHOW_ALL=true
fi

RESULTS_FILE="$(mktemp)"
trap 'rm -f "$RESULTS_FILE"' EXIT

FAIL_COUNT=0
WARN_COUNT=0
PASS_COUNT=0
SKIP_COUNT=0
DEFERRED_SLOP_JSDOC=()  # R-SLOP-01/02 WARNs deferred until provenance score is known

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

should_show() {
    local status="$1"
    [[ ",$SHOW_LEVELS," == *",${status,,},"* ]]
}

print_result() {
    local status="$1"
    local check="$2"
    local detail="$3"
    local display_detail="${detail%%|fix:*}"

    # Fixed-width formatting: [STATUS] check-name  detail (fix text stripped)
    if should_show "$status"; then
        printf "[%-4s] %-38s %s\n" "$status" "$check" "$display_detail"
    fi
    # Results file preserves fix text for --report
    echo "${status}|${check}|${detail}" >> "$RESULTS_FILE"

    case "$status" in
        FAIL) FAIL_COUNT=$((FAIL_COUNT + 1)) ;;
        WARN) WARN_COUNT=$((WARN_COUNT + 1)) ;;
        PASS) PASS_COUNT=$((PASS_COUNT + 1)) ;;
        SKIP) SKIP_COUNT=$((SKIP_COUNT + 1)) ;;
    esac
}

# Parse output from sub-scripts (PIPE-delimited: STATUS|check-name|detail)
run_subscript() {
    local script="$1"
    local output

    if [[ ! -x "$script" ]]; then
        print_result "SKIP" "$(basename "$script" .sh)" "Script not found or not executable"
        return
    fi

    # Run sub-script; capture output, allow non-zero exit
    output="$("$script" "$EXT_DIR" 2>&1)" || true

    while IFS='|' read -r status check detail; do
        # Skip empty lines
        [[ -z "$status" ]] && continue
        # Trim whitespace without xargs (which mangles quotes)
        status="${status#"${status%%[![:space:]]*}"}"
        status="${status%"${status##*[![:space:]]}"}"
        check="${check#"${check%%[![:space:]]*}"}"
        check="${check%"${check##*[![:space:]]}"}"
        detail="${detail#"${detail%%[![:space:]]*}"}"
        detail="${detail%"${detail##*[![:space:]]}"}"
        print_result "$status" "$check" "$detail"
    done <<< "$output"
}

# Run Tier 1 pattern rules from rules/patterns.yaml
run_pattern_rules() {
    local rules_file="$SCRIPT_DIR/../../../rules/patterns.yaml"
    local helper="$SCRIPT_DIR/apply-patterns.py"

    if [[ ! -f "$rules_file" ]]; then
        print_result "SKIP" "pattern-rules" "rules/patterns.yaml not found"
        return
    fi

    if ! command -v python3 > /dev/null 2>&1; then
        print_result "SKIP" "pattern-rules" "python3 not available"
        return
    fi

    local output
    output="$(python3 "$helper" "$rules_file" "$EXT_DIR" 2>&1)" || true

    while IFS='|' read -r status check detail; do
        [[ -z "$status" ]] && continue
        status="${status#"${status%%[![:space:]]*}"}"
        status="${status%"${status##*[![:space:]]}"}"
        check="${check#"${check%%[![:space:]]*}"}"
        check="${check%"${check##*[![:space:]]}"}"
        detail="${detail#"${detail%%[![:space:]]*}"}"
        detail="${detail%"${detail##*[![:space:]]}"}"
        # Defer R-SLOP-01/02 WARNs until provenance score is known
        if [[ "$status" == "WARN" && "$check" =~ ^R-SLOP-0[12]$ ]]; then
            DEFERRED_SLOP_JSDOC+=("${status}|${check}|${detail}")
            WARN_COUNT=$((WARN_COUNT + 1))
        else
            print_result "$status" "$check" "$detail"
        fi
    done <<< "$output"
}

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

if [[ "$SHOW_ALL" == true ]]; then
    echo "================================================================"
    echo "  ego-lint — GNOME Shell Extension Compliance Checker"
    echo "================================================================"
    echo ""
    echo "Extension: $EXT_DIR"
    echo ""
fi

# ---------------------------------------------------------------------------
# Compiled TypeScript detection (must run before file-structure checks)
# ---------------------------------------------------------------------------
# esbuild emits helper functions (var __defProp, __decorateClass, etc.)
# that are definitive markers of transpiled output. When detected, noisy rules
# that flag transpiler artifacts (var declarations, verbose identifiers) are
# suppressed, resource-tracking/no-destroy-method is skipped, and
# file-structure checks are relaxed (bundled output has non-standard layout).

COMPILED_TS=false
while IFS= read -r -d '' f; do
    if grep -qE 'var __defProp|__decorateClass|__publicField' "$f" 2>/dev/null; then
        COMPILED_TS=true
        break
    fi
done < <(find "$EXT_DIR" -name '*.js' -not -path '*/node_modules/*' -not -path '*/.git/*' -print0 2>/dev/null)

if [[ "$COMPILED_TS" == true ]]; then
    export EGO_LINT_COMPILED_TS=1
    print_result "WARN" "compiled-typescript" "Extension appears compiled from TypeScript — some lint checks adjusted; lifecycle checks have reduced accuracy for bundled output (manually verify enable()/disable() cleanup)"
else
    print_result "PASS" "compiled-typescript" "No transpiler artifacts detected"
fi

# TypeScript project detection (tsconfig.json at root or src/)
# Built TS extensions emit @param {Type} / @returns {Type} annotations from tsc;
# flagging them as AI slop is noise for maintainers who chose TypeScript.
if [[ -f "$EXT_DIR/tsconfig.json" || -f "$EXT_DIR/src/tsconfig.json" ]]; then
    export EGO_LINT_HAS_TSCONFIG=1
fi

# SPDX license header detection
# Hand-authored projects with deliberate licensing use SPDX per-file headers.
# AI-generated code almost never includes SPDX-FileCopyrightText / SPDX-License-Identifier.
# Threshold: >= 70% of JS files have SPDX headers → suppress R-SLOP-01/02 (intentional JSDoc).
_spdx_js_total=0
_spdx_count=0
while IFS= read -r -d '' _f; do
    _spdx_js_total=$((_spdx_js_total + 1))
    if head -n 10 "$_f" 2>/dev/null | grep -qE 'SPDX-(License-Identifier|FileCopyrightText)'; then
        _spdx_count=$((_spdx_count + 1))
    fi
done < <(find "$EXT_DIR" -name "*.js" -not -path "*/node_modules/*" -print0 2>/dev/null)
if [[ $_spdx_js_total -gt 0 && $((_spdx_count * 100 / _spdx_js_total)) -ge 70 ]]; then
    export EGO_LINT_HAS_SPDX=1
fi

# ---------------------------------------------------------------------------
# Subprocess directory detection
# ---------------------------------------------------------------------------
# Top-level dirs containing a GJS subprocess entry point (#!/usr/bin/env gjs)
# run outside GNOME Shell and must not be checked for Shell-specific patterns.
# Mirrors the _discover_subprocess_dirs() logic in the Python checks.

_SUBPROCESS_DIRS=()
while IFS= read -r -d '' f; do
    rel="${f#"$EXT_DIR/"}"
    top_dir="${rel%%/*}"
    [[ "$top_dir" == "$rel" ]] && continue  # root-level file, no subdir
    if head -n 2 "$f" 2>/dev/null | grep -q '#!/usr/bin/env.*gjs'; then
        _SUBPROCESS_DIRS+=("$EXT_DIR/$top_dir")
    fi
done < <(find "$EXT_DIR" -name '*.js' \
    -not -path '*/node_modules/*' -not -path '*/.git/*' -print0 2>/dev/null)

# Build find exclusion args for use in per-check file discovery
_SUBPROCESS_EXCL=()
for _sd in "${_SUBPROCESS_DIRS[@]}"; do
    _SUBPROCESS_EXCL+=("-not" "-path" "${_sd}/*")
done

if [[ ${#_SUBPROCESS_DIRS[@]} -gt 0 ]]; then
    _sd_names=()
    for _sd in "${_SUBPROCESS_DIRS[@]}"; do _sd_names+=("$(basename "$_sd")/"); done
    print_result "SKIP" "subprocess-dir-exclusion" "Detected GJS subprocess dir(s): ${_sd_names[*]} — excluded from Shell extension checks"
fi

# ---------------------------------------------------------------------------
# File structure checks
# ---------------------------------------------------------------------------

# Skip file-structure checks for compiled TypeScript (bundled output has
# non-standard layout; the compiled-typescript WARN already flags this)
if [[ "$COMPILED_TS" == true ]]; then
    print_result "SKIP" "file-structure/extension.js" "Skipped for compiled TypeScript"
    print_result "SKIP" "file-structure/metadata.json" "Skipped for compiled TypeScript"
elif [[ -f "$EXT_DIR/extension.js" ]]; then
    print_result "PASS" "file-structure/extension.js" "extension.js exists"
    if [[ -f "$EXT_DIR/metadata.json" ]]; then
        print_result "PASS" "file-structure/metadata.json" "metadata.json exists"
    elif [[ -f "$EXT_DIR/src/metadata.json" ]]; then
        print_result "PASS" "file-structure/metadata.json" "metadata.json exists (in src/)"
    else
        print_result "FAIL" "file-structure/metadata.json" "metadata.json is missing"
    fi
elif [[ -f "$EXT_DIR/src/extension.js" ]]; then
    print_result "PASS" "file-structure/extension.js" "extension.js exists (in src/)"
    if [[ -f "$EXT_DIR/metadata.json" ]]; then
        print_result "PASS" "file-structure/metadata.json" "metadata.json exists"
    elif [[ -f "$EXT_DIR/src/metadata.json" ]]; then
        print_result "PASS" "file-structure/metadata.json" "metadata.json exists (in src/)"
    else
        print_result "FAIL" "file-structure/metadata.json" "metadata.json is missing"
    fi
else
    # Detect unbuilt TypeScript source repos: .ts files present but no compiled .js
    _ts_source=false
    if compgen -G "$EXT_DIR/src/*.ts" > /dev/null 2>&1 || \
       compgen -G "$EXT_DIR/*.ts" > /dev/null 2>&1; then
        _ts_source=true
    fi

    if [[ "$_ts_source" == true ]]; then
        print_result "FAIL" "file-structure/extension.js" "extension.js is missing — TypeScript source detected; build the extension first (e.g. 'make' or 'npm run build') before running ego-lint|fix: Compile TypeScript source to extension.js before running ego-lint"
    else
        print_result "FAIL" "file-structure/extension.js" "extension.js is missing"
    fi
    if [[ -f "$EXT_DIR/metadata.json" ]]; then
        print_result "PASS" "file-structure/metadata.json" "metadata.json exists"
    elif [[ -f "$EXT_DIR/src/metadata.json" ]]; then
        print_result "PASS" "file-structure/metadata.json" "metadata.json exists (in src/)"
    else
        print_result "FAIL" "file-structure/metadata.json" "metadata.json is missing"
    fi
fi

# ---------------------------------------------------------------------------
# License check
# ---------------------------------------------------------------------------

license_file=""
for candidate in LICENSE COPYING LICENSE.rst LICENSE.md LICENSE.txt COPYING.rst COPYING.md COPYING.txt; do
    if [[ -f "$EXT_DIR/$candidate" ]]; then
        license_file="$EXT_DIR/$candidate"
        break
    fi
done

# src/ layout fallback: check parent directory for license
if [[ -z "$license_file" && "$(basename "$EXT_DIR")" == "src" ]]; then
    parent_dir="$(dirname "$EXT_DIR")"
    for candidate in LICENSE COPYING LICENSE.rst LICENSE.md LICENSE.txt COPYING.rst COPYING.md COPYING.txt; do
        if [[ -f "$parent_dir/$candidate" ]]; then
            license_file="$parent_dir/$candidate"
            break
        fi
    done
fi

if [[ -n "$license_file" ]]; then
    head_content=$(head -20 "$license_file" 2>/dev/null || true)
    if echo "$head_content" | grep -qiE '(GNU GENERAL PUBLIC LICENSE|\bGPL\b|\bLGPL\b|\bMIT\b|\bBSD\b|\bApache\b|\bMPL\b|\bISC\b|\bArtistic\b|SPDX-License-Identifier)'; then
        print_result "PASS" "license" "License file found (appears GPL-compatible)"
    else
        print_result "WARN" "license" "License file found but could not confirm GPL-compatibility"
    fi
else
    print_result "WARN" "license" "No LICENSE or COPYING file — should use GPL-compatible license"
fi

# ---------------------------------------------------------------------------
# console.log check
# ---------------------------------------------------------------------------

# Search for console.log( in JS files (extension code), excluding comments.
# console.debug, console.warn, console.error are OK.

console_log_hits=""
console_log_guarded_hits=""
# Collect all JS files under EXT_DIR, respecting standard exclusions.
# Subprocess dirs are excluded — they run outside the Shell extension lifecycle.
_console_js_files=()
while IFS= read -r -d '' f; do
    _console_js_files+=("$f")
done < <(find "$EXT_DIR" -name '*.js' \
    -not -path '*/node_modules/*' -not -path '*/.git/*' \
    "${_SUBPROCESS_EXCL[@]}" -print0 2>/dev/null)

if [[ ${#_console_js_files[@]} -gt 0 ]]; then

    for f in "${_console_js_files[@]}"; do
        # Match console.log( but skip lines that are comments (// or *)
        while IFS= read -r match; do
            lineno="${match%%:*}"
            line="${match#*:}"
            # Strip leading whitespace for comment detection
            stripped="${line#"${line%%[![:space:]]*}"}"
            # Skip single-line comments
            [[ "$stripped" == //* ]] && continue
            # Skip block comment continuation lines
            [[ "$stripped" == \** ]] && continue
            rel_path="${f#"$EXT_DIR/"}"
            # Check if guarded by a build-type or runtime settings DEBUG condition
            start=$((lineno - 3))
            [[ $start -lt 1 ]] && start=1
            guard=$(sed -n "${start},$((lineno - 1))p" "$f" \
                | grep -iE "build-type['\"]?\]?\s*[=!]==?\s*['\"]debug['\"]|this[._]_?settings[._]DEBUG\b|if\s*\(\s*this[._]_?debug\b" || true)
            if [[ -n "$guard" ]]; then
                console_log_guarded_hits+="  $rel_path: $stripped"$'\n'
            else
                console_log_hits+="  $rel_path: $stripped"$'\n'
            fi
        done < <(grep -n 'console\.log(' "$f" 2>/dev/null || true)
    done
fi

if [[ -n "$console_log_hits" ]]; then
    # Count number of hits
    hit_count=$(echo -n "$console_log_hits" | grep -c '.' || true)
    print_result "FAIL" "no-console-log" "Found $hit_count console.log() call(s)|fix: Replace with console.debug() — it is silenced by default and enabled via G_MESSAGES_DEBUG, so no custom debug toggle is needed"
elif [[ -n "$console_log_guarded_hits" ]]; then
    # All console.log calls are behind a debug guard — guarded in production
    hit_count=$(echo -n "$console_log_guarded_hits" | grep -c '.' || true)
    print_result "WARN" "no-console-log" "Found $hit_count console.log() call(s) behind a debug guard — console.debug() is silenced by default and enabled via G_MESSAGES_DEBUG, making the custom guard redundant|fix: Replace with console.debug() and remove the custom debug toggle"
else
    print_result "PASS" "no-console-log" "No console.log() calls found"
fi

# ---------------------------------------------------------------------------
# Deprecated module imports
# ---------------------------------------------------------------------------

deprecated_hits=""
# Collect all JS files under EXT_DIR, respecting standard exclusions
_depr_js_files=()
while IFS= read -r -d '' f; do
    _depr_js_files+=("$f")
done < <(find "$EXT_DIR" -name '*.js' \
    -not -path '*/node_modules/*' -not -path '*/.git/*' -print0 2>/dev/null)

if [[ ${#_depr_js_files[@]} -gt 0 ]]; then

    # Match both ESM and legacy import patterns for deprecated modules
    # ESM: import ... from 'mainloop' / 'bytearray' / 'lang'
    # Legacy: const X = imports.misc.mainloop / imports.lang / imports.byteArray
    deprecated_pattern="(from ['\"]mainloop['\"]|from ['\"]bytearray['\"]|from ['\"]lang['\"]|imports\.misc\.mainloop|imports\.lang|imports\.byteArray|from ['\"]ByteArray['\"]|from ['\"]Lang['\"]|from ['\"]Mainloop['\"])"

    for f in "${_depr_js_files[@]}"; do
        while IFS= read -r match; do
            rel_path="${f#"$EXT_DIR/"}"
            deprecated_hits+="  $rel_path: $match"$'\n'
        done < <(grep -nE "$deprecated_pattern" "$f" 2>/dev/null || true)
    done
fi

if [[ -n "$deprecated_hits" ]]; then
    hit_count=$(echo -n "$deprecated_hits" | grep -c '.' || true)
    print_result "FAIL" "no-deprecated-modules" "Found $hit_count deprecated module import(s)"
else
    print_result "PASS" "no-deprecated-modules" "No deprecated module imports found"
fi

# ---------------------------------------------------------------------------
# Binary files check
# ---------------------------------------------------------------------------

binary_files=""
# Check by file extension
while IFS= read -r -d '' f; do
    rel_path="${f#"$EXT_DIR/"}"
    binary_files+="  $rel_path"$'\n'
done < <(find "$EXT_DIR" -type f \( \
    -name '*.so' -o -name '*.o' -o -name '*.a' -o \
    -name '*.exe' -o -name '*.bin' -o -name '*.dll' -o \
    -name '*.dylib' -o -name '*.wasm' \
    \) -not -path '*/node_modules/*' -not -path '*/.git/*' -print0 2>/dev/null)

# Check for ELF binaries without known extensions
while IFS= read -r -d '' f; do
    rel_path="${f#"$EXT_DIR/"}"
    # Skip files already caught by extension
    case "$rel_path" in
        *.so|*.o|*.a|*.exe|*.bin|*.dll|*.dylib|*.wasm) continue ;;
    esac
    # Check ELF magic bytes
    if head -c4 "$f" 2>/dev/null | grep -q $'\x7fELF'; then
        binary_files+="  $rel_path (ELF binary)"$'\n'
    fi
done < <(find "$EXT_DIR" -type f -not -path '*/node_modules/*' -not -path '*/.git/*' -not -name '*.js' -not -name '*.json' -not -name '*.xml' -not -name '*.css' -not -name '*.mo' -not -name '*.po' -not -name '*.pot' -not -name '*.md' -not -name '*.txt' -not -name '*.yml' -not -name '*.yaml' -not -name '*.sh' -not -name '*.py' -not -name '*.svg' -not -name '*.png' -not -name '*.jpg' -not -name '*.zip' -not -name '*.ui' -not -name '*.policy' -not -name '*.rules' -not -name 'LICENSE' -not -name 'COPYING' -print0 2>/dev/null)

if [[ -n "$binary_files" ]]; then
    hit_count=$(echo -n "$binary_files" | grep -c '.' || true)
    print_result "FAIL" "no-binary-files" "Found $hit_count binary file(s) — extensions MUST NOT include binaries"
else
    print_result "PASS" "no-binary-files" "No binary files found"
fi

# ---------------------------------------------------------------------------
# Non-GJS script detection
# ---------------------------------------------------------------------------

non_gjs_scripts=""
while IFS= read -r -d '' f; do
    rel_path="${f#"$EXT_DIR/"}"
    non_gjs_scripts+="  $rel_path"$'\n'
done < <(find "$EXT_DIR" -type f \( -name '*.py' -o -name '*.sh' -o -name '*.rb' -o -name '*.pl' \) \
    -not -path '*/node_modules/*' -not -path '*/.git/*' \
    -not -path "$EXT_DIR/scripts/*" -not -path "$EXT_DIR/tests/*" -not -path "$EXT_DIR/test/*" \
    -not -path "$EXT_DIR/kwin/*" -not -path "$EXT_DIR/docs/*" -not -path "$EXT_DIR/.github/*" \
    -not -path "$EXT_DIR/ci/*" -not -path "$EXT_DIR/build/*" \
    -not -path "$EXT_DIR/gulp/*" -not -path "$EXT_DIR/conf/*" -not -path "$EXT_DIR/grunt/*" \
    -print0 2>/dev/null)

if [[ -n "$non_gjs_scripts" ]]; then
    hit_count=$(echo -n "$non_gjs_scripts" | grep -c '.' || true)
    # Upgrade to FAIL if no pkexec justification exists (pkexec helpers are the main exception)
    has_pkexec=false
    while IFS= read -r -d '' f; do
        if grep -q 'pkexec' "$f" 2>/dev/null; then
            has_pkexec=true
            break
        fi
    done < <(find "$EXT_DIR" -name '*.js' -not -path '*/node_modules/*' -not -path '*/.git/*' -print0 2>/dev/null)
    if [[ "$has_pkexec" == true ]]; then
        print_result "PASS" "non-gjs-scripts" "Found $hit_count non-GJS script(s) — pkexec helper detected, scripts support privileged operations"
    else
        print_result "WARN" "non-gjs-scripts" "Found $hit_count non-GJS script(s) — scripts MUST be written in GJS; no pkexec/privileged helper justification found"
    fi
else
    print_result "PASS" "non-gjs-scripts" "No non-GJS scripts found"
fi

# ---------------------------------------------------------------------------
# Helper script permission check
# ---------------------------------------------------------------------------

non_exec_scripts=""
while IFS= read -r -d '' f; do
    if [[ ! -x "$f" ]]; then
        rel_path="${f#"$EXT_DIR/"}"
        non_exec_scripts+="  $rel_path"$'\n'
    fi
done < <(find "$EXT_DIR" -type f -name '*.sh' \
    -not -path '*/node_modules/*' -not -path '*/.git/*' \
    -not -path "$EXT_DIR/scripts/*" -not -path "$EXT_DIR/tests/*" -not -path "$EXT_DIR/test/*" \
    -not -path "$EXT_DIR/kwin/*" -not -path "$EXT_DIR/docs/*" -not -path "$EXT_DIR/.github/*" \
    -not -path "$EXT_DIR/ci/*" -not -path "$EXT_DIR/build/*" \
    -not -path "$EXT_DIR/gulp/*" -not -path "$EXT_DIR/conf/*" -not -path "$EXT_DIR/grunt/*" \
    -print0 2>/dev/null)

if [[ -n "$non_exec_scripts" ]]; then
    hit_count=$(echo -n "$non_exec_scripts" | grep -c '.' || true)
    print_result "WARN" "script-permissions" "Found $hit_count shell script(s) without execute permission — packaging tools may strip permissions"
else
    print_result "PASS" "script-permissions" "All shell scripts have execute permission (or no shell scripts found)"
fi

# ---------------------------------------------------------------------------
# Polkit policy file check
# ---------------------------------------------------------------------------

polkit_files=""
while IFS= read -r -d '' f; do
    rel_path="${f#"$EXT_DIR/"}"
    polkit_files+="  $rel_path"$'\n'
done < <(find "$EXT_DIR" -type f \( -name '*.policy' -o -name '*.rules' \) -not -path '*/node_modules/*' -not -path '*/.git/*' -print0 2>/dev/null)

if [[ -n "$polkit_files" ]]; then
    hit_count=$(echo -n "$polkit_files" | grep -c '.' || true)
    print_result "WARN" "polkit-files" "Found $hit_count polkit policy/rules file(s) — requires security review"
else
    print_result "PASS" "polkit-files" "No polkit policy files found"
fi

# check-polkit.py (polkit action ID cross-reference)
if [[ -f "$SCRIPT_DIR/check-polkit.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-polkit.py"
fi

# ---------------------------------------------------------------------------
# Minified/bundled JavaScript check
# ---------------------------------------------------------------------------

minified_files=""
for f in "$EXT_DIR"/*.js; do
    [[ -f "$f" ]] || continue
    rel_path="${f#"$EXT_DIR/"}"

    # Check for webpack boilerplate
    if grep -q '__webpack_require__' "$f" 2>/dev/null; then
        minified_files+="  $rel_path (webpack bundle)"$'\n'
        continue
    fi

    # Check for lines > 500 chars — need 3+ such lines to flag as minified.
    # A single long line (e.g., keyboard constant chain) in an otherwise
    # readable file is not minification.
    long_line_count=$(awk 'length > 500 { n++ } END { print n+0 }' "$f" 2>/dev/null || true)
    if [[ "$long_line_count" -ge 3 ]]; then
        minified_files+="  $rel_path ($long_line_count lines > 500 chars)"$'\n'
    fi
done
if [[ -d "$EXT_DIR/lib" ]]; then
    while IFS= read -r -d '' f; do
        rel_path="${f#"$EXT_DIR/"}"
        if grep -q '__webpack_require__' "$f" 2>/dev/null; then
            minified_files+="  $rel_path (webpack bundle)"$'\n'
            continue
        fi
        long_line_count=$(awk 'length > 500 { n++ } END { print n+0 }' "$f" 2>/dev/null || true)
        if [[ "$long_line_count" -ge 3 ]]; then
            minified_files+="  $rel_path ($long_line_count lines > 500 chars)"$'\n'
        fi
    done < <(find "$EXT_DIR/lib" -name '*.js' -print0 2>/dev/null)
fi

if [[ -n "$minified_files" ]]; then
    hit_count=$(echo -n "$minified_files" | grep -c '.' || true)
    print_result "FAIL" "minified-js" "Found $hit_count minified/bundled JS file(s) — reviewers cannot review minified code"
else
    print_result "PASS" "minified-js" "No minified or bundled JavaScript detected"
fi

# ---------------------------------------------------------------------------
# CSS scoping check (delegated to check-css.py)
# ---------------------------------------------------------------------------

if [[ -f "$SCRIPT_DIR/check-css.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-css.py"
else
    print_result "SKIP" "css-scoping" "check-css.py not found"
fi

# check-accessibility.py (basic a11y checks)
if [[ -f "$SCRIPT_DIR/check-accessibility.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-accessibility.py"
fi

# ---------------------------------------------------------------------------
# Tier 1: Pattern rules
# ---------------------------------------------------------------------------

run_pattern_rules

# ---------------------------------------------------------------------------
# ESLint check
# ---------------------------------------------------------------------------

if [[ -f "$EXT_DIR/eslint.config.mjs" ]] && [[ -x "$EXT_DIR/node_modules/.bin/eslint" ]]; then
    eslint_output=""
    eslint_exit=0
    eslint_output="$("$EXT_DIR/node_modules/.bin/eslint" "$EXT_DIR" 2>&1)" || eslint_exit=$?

    if [[ $eslint_exit -eq 0 ]]; then
        print_result "PASS" "eslint" "No errors"
    elif [[ $eslint_exit -eq 2 ]]; then
        print_result "WARN" "eslint" "ESLint configuration error (exit code 2)"
    else
        # Parse stylish format summary line: "X problems (Y errors, Z warnings)"
        errors=$(echo "$eslint_output" | grep -oP '\d+ error' | grep -oP '\d+' | tail -1)
        warnings=$(echo "$eslint_output" | grep -oP '\d+ warning' | grep -oP '\d+' | tail -1)
        errors="${errors:-0}"
        warnings="${warnings:-0}"
        if [[ "$errors" -gt 0 ]]; then
            print_result "FAIL" "eslint" "${errors} error(s), ${warnings} warning(s)"
        else
            print_result "WARN" "eslint" "${warnings} warning(s)"
        fi
    fi
else
    print_result "SKIP" "eslint" "No eslint.config.mjs or node_modules/.bin/eslint found"
fi

# ---------------------------------------------------------------------------
# Delegate to sub-scripts
# ---------------------------------------------------------------------------

if [[ "$SHOW_ALL" == true ]]; then
    echo ""
fi

# check-metadata.py
if [[ -x "$SCRIPT_DIR/check-metadata.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-metadata.py"
else
    print_result "SKIP" "metadata" "check-metadata.py not found"
fi

# check-schema.sh
run_subscript "$SCRIPT_DIR/check-schema.sh"

# check-schema-usage.py (schema key cross-reference)
if [[ -f "$SCRIPT_DIR/check-schema-usage.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-schema-usage.py"
fi

# check-imports.sh
run_subscript "$SCRIPT_DIR/check-imports.sh"

# check-quality.py (Tier 2 heuristics)
if [[ -f "$SCRIPT_DIR/check-quality.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-quality.py"
fi

# check-lifecycle.py (Tier 2 lifecycle heuristics)
if [[ -f "$SCRIPT_DIR/check-lifecycle.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-lifecycle.py"
fi

# check-gobject.py (GObject pattern validation)
if [[ -f "$SCRIPT_DIR/check-gobject.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-gobject.py"
fi

# check-async.py (async safety and cancellation)
if [[ -f "$SCRIPT_DIR/check-async.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-async.py"
fi

# check-prefs.py (prefs.js validation)
if [[ -f "$SCRIPT_DIR/check-prefs.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-prefs.py"
fi

# check-init.py (init-time Shell modification detection)
if [[ -f "$SCRIPT_DIR/check-init.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-init.py"
fi

# check-resources.py (cross-file resource tracking)
if [[ -f "$SCRIPT_DIR/check-resources.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-resources.py"
fi

# check-disclosures.py (capability disclosure matrix)
if [[ -f "$SCRIPT_DIR/check-disclosures.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-disclosures.py"
fi

# check-security.py (UUID-aware lookupByUUID cross-extension check)
if [[ -f "$SCRIPT_DIR/check-security.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-security.py"
fi

# check-package.sh
run_subscript "$SCRIPT_DIR/check-package.sh"

# ---------------------------------------------------------------------------
# Provenance-gated WARN suppression
# ---------------------------------------------------------------------------
# When code provenance is moderate-to-high (score >= 3), JSDoc annotations
# (R-SLOP-01/02) are intentional documentation, not AI slop signals. Score 3
# means strong hand-written indicators (domain vocabulary, nontrivial algorithms).
# AI-generated code typically scores 1-2. Suppress JSDoc warnings post-hoc.
# Future: move provenance awareness into apply-patterns.py for inline gating.

provenance_score=0
if provenance_line=$(grep 'quality/code-provenance' "$RESULTS_FILE" 2>/dev/null); then
    if [[ "$provenance_line" =~ provenance-score=([0-9]+) ]]; then
        provenance_score="${BASH_REMATCH[1]}"
    fi
fi

deferred_count=${#DEFERRED_SLOP_JSDOC[@]}
if [[ "$provenance_score" -ge 3 && "$deferred_count" -gt 0 ]]; then
    # Suppress deferred R-SLOP-01/02 WARNs (moderate-to-high provenance = intentional JSDoc)
    WARN_COUNT=$((WARN_COUNT - deferred_count))
    print_result "PASS" "provenance/jsdoc-suppressed" \
        "Suppressed $deferred_count JSDoc warnings (R-SLOP-01/02) — provenance score $provenance_score indicates hand-written code"
else
    # Flush deferred entries (low provenance or no deferred entries)
    for entry in "${DEFERRED_SLOP_JSDOC[@]}"; do
        _df_status="${entry%%|*}"
        _df_rest="${entry#*|}"
        _df_check="${_df_rest%%|*}"
        _df_detail="${_df_rest#*|}"
        _df_display="${_df_detail%%|fix:*}"
        if should_show "$_df_status"; then
            printf "[%-4s] %-38s %s\n" "$_df_status" "$_df_check" "$_df_display"
        fi
        echo "${entry}" >> "$RESULTS_FILE"
    done
fi

# ---------------------------------------------------------------------------
# Code Metrics
# ---------------------------------------------------------------------------

compute_metrics() {
    local js_count=0 total_lines=0 css_lines=0 schema_keys=0
    local largest_file="" largest_lines=0

    # Count JS files and lines
    while IFS= read -r -d '' f; do
        js_count=$((js_count + 1))
        local lines
        lines=$(wc -l < "$f" 2>/dev/null || echo 0)
        total_lines=$((total_lines + lines))
        if [[ $lines -gt $largest_lines ]]; then
            largest_lines=$lines
            largest_file="$(basename "$f")"
        fi
    done < <(find "$EXT_DIR" -name '*.js' -not -path '*/node_modules/*' -not -path '*/.git/*' -print0 2>/dev/null)

    # Count CSS lines
    local css_file=""
    if [[ -f "$EXT_DIR/stylesheet.css" ]]; then
        css_file="$EXT_DIR/stylesheet.css"
    elif [[ -f "$EXT_DIR/src/stylesheet.css" ]]; then
        css_file="$EXT_DIR/src/stylesheet.css"
    fi
    if [[ -n "$css_file" ]]; then
        css_lines=$(wc -l < "$css_file" 2>/dev/null || echo 0)
    fi

    # Count schema keys
    local schema_file=""
    schema_file=$(find "$EXT_DIR" -name '*.gschema.xml' -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null | head -1 || true)
    if [[ -n "$schema_file" ]]; then
        schema_keys=$(grep -c '<key ' "$schema_file" 2>/dev/null || echo 0)
    fi

    echo ""
    echo "[METRIC] js-files: $js_count"
    echo "[METRIC] total-lines: $total_lines"
    if [[ -n "$largest_file" ]]; then
        echo "[METRIC] largest-file: $largest_file ($largest_lines)"
    fi
    echo "[METRIC] css-lines: $css_lines"
    echo "[METRIC] schema-keys: $schema_keys"
}

if [[ "$SHOW_ALL" == true ]]; then
    compute_metrics
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

if [[ "$SHOW_ALL" == true ]]; then
    echo ""
fi
echo "----------------------------------------------------------------"
TOTAL=$((PASS_COUNT + FAIL_COUNT + WARN_COUNT + SKIP_COUNT))
echo "  Results: $TOTAL checks — $PASS_COUNT passed, $FAIL_COUNT failed, $WARN_COUNT warnings, $SKIP_COUNT skipped"
echo "----------------------------------------------------------------"
if [[ "$SHOW_ALL" != true ]]; then
    echo "  (run with --show all for full output)"
fi

if [[ "$REPORT" == true ]]; then
    echo ""
    echo "================================================================"
    echo "  REPORT"
    echo "================================================================"

    # Group by severity
    echo ""
    echo "--- BLOCKING ISSUES (FAIL) ---"
    grep "^FAIL|" "$RESULTS_FILE" | while IFS='|' read -r _ check detail; do
        detail="${detail%%|fix:*}"
        echo "  ✗ $check: $detail"
    done || true

    echo ""
    echo "--- WARNINGS ---"
    grep "^WARN|" "$RESULTS_FILE" | while IFS='|' read -r _ check detail; do
        detail="${detail%%|fix:*}"
        echo "  ⚠ $check: $detail"
    done || true

    # Collect fix suggestions from results that have |fix: fields
    fix_lines=""
    while IFS='|' read -r _ check detail_with_fix; do
        case "$detail_with_fix" in
            *"|fix:"*)
                fix="${detail_with_fix#*|fix:}"
                fix="${fix#"${fix%%[![:space:]]*}"}"
                fix_lines+="  $check: $fix"$'\n'
                ;;
        esac
    done < "$RESULTS_FILE"
    if [[ -n "$fix_lines" ]]; then
        echo ""
        echo "--- FIX SUGGESTIONS ---"
        printf '%s' "$fix_lines"
    fi

    echo ""
    echo "--- VERDICT ---"
    UNIQUE_WARN_COUNT=$(grep "^WARN|" "$RESULTS_FILE" | cut -d'|' -f2 | sort -u | wc -l)
    if [[ $FAIL_COUNT -ge 3 ]]; then
        echo "  WILL BE REJECTED: $FAIL_COUNT blocking issue(s) found"
    elif [[ $FAIL_COUNT -ge 1 ]]; then
        echo "  LIKELY REJECTED: $FAIL_COUNT blocking issue(s) found"
    elif [[ $UNIQUE_WARN_COUNT -gt 0 ]]; then
        echo "  MAY PASS WITH COMMENTS: $UNIQUE_WARN_COUNT checks flagged ($WARN_COUNT total findings)"
    else
        echo "  LIKELY TO PASS: No issues found"
    fi
    echo "================================================================"
fi

if [[ $FAIL_COUNT -gt 0 ]]; then
    exit 1
else
    exit 0
fi

