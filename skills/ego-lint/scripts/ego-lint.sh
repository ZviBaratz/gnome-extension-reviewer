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

EXT_DIR="${1:-.}"
EXT_DIR="$(cd "$EXT_DIR" && pwd)"

FAIL_COUNT=0
WARN_COUNT=0
PASS_COUNT=0
SKIP_COUNT=0

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

print_result() {
    local status="$1"
    local check="$2"
    local detail="$3"

    # Fixed-width formatting: [STATUS] check-name  detail
    printf "[%-4s] %-38s %s\n" "$status" "$check" "$detail"

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
        print_result "$status" "$check" "$detail"
    done <<< "$output"
}

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

echo "================================================================"
echo "  ego-lint — GNOME Shell Extension Compliance Checker"
echo "================================================================"
echo ""
echo "Extension: $EXT_DIR"
echo ""

# ---------------------------------------------------------------------------
# File structure checks
# ---------------------------------------------------------------------------

if [[ -f "$EXT_DIR/extension.js" ]]; then
    print_result "PASS" "file-structure/extension.js" "extension.js exists"
else
    print_result "FAIL" "file-structure/extension.js" "extension.js is missing"
fi

if [[ -f "$EXT_DIR/metadata.json" ]]; then
    print_result "PASS" "file-structure/metadata.json" "metadata.json exists"
else
    print_result "FAIL" "file-structure/metadata.json" "metadata.json is missing"
fi

# ---------------------------------------------------------------------------
# License check
# ---------------------------------------------------------------------------

if [[ -f "$EXT_DIR/LICENSE" ]] || [[ -f "$EXT_DIR/COPYING" ]]; then
    print_result "PASS" "license" "License file found"
else
    print_result "WARN" "license" "No LICENSE or COPYING file found"
fi

# ---------------------------------------------------------------------------
# console.log check
# ---------------------------------------------------------------------------

# Search for console.log( in JS files (extension code), excluding comments.
# console.debug, console.warn, console.error are OK.

console_log_hits=""
if compgen -G "$EXT_DIR/*.js" > /dev/null 2>&1 || \
   compgen -G "$EXT_DIR/lib/**/*.js" > /dev/null 2>&1; then

    # Build file list
    js_files=()
    for f in "$EXT_DIR"/*.js; do
        [[ -f "$f" ]] && js_files+=("$f")
    done
    if [[ -d "$EXT_DIR/lib" ]]; then
        while IFS= read -r -d '' f; do
            js_files+=("$f")
        done < <(find "$EXT_DIR/lib" -name '*.js' -print0 2>/dev/null)
    fi

    for f in "${js_files[@]}"; do
        # Match console.log( but skip lines that are comments (// or *)
        while IFS= read -r line; do
            # Strip leading whitespace for comment detection
            stripped="${line#"${line%%[![:space:]]*}"}"
            # Skip single-line comments
            [[ "$stripped" == //* ]] && continue
            # Skip block comment continuation lines
            [[ "$stripped" == \** ]] && continue
            rel_path="${f#"$EXT_DIR/"}"
            console_log_hits+="  $rel_path: $stripped"$'\n'
        done < <(grep -n 'console\.log(' "$f" 2>/dev/null || true)
    done
fi

if [[ -n "$console_log_hits" ]]; then
    # Count number of hits
    hit_count=$(echo -n "$console_log_hits" | grep -c '.' || true)
    print_result "FAIL" "no-console-log" "Found $hit_count console.log() call(s)"
else
    print_result "PASS" "no-console-log" "No console.log() calls found"
fi

# ---------------------------------------------------------------------------
# Deprecated module imports
# ---------------------------------------------------------------------------

deprecated_hits=""
if compgen -G "$EXT_DIR/*.js" > /dev/null 2>&1 || \
   compgen -G "$EXT_DIR/lib/**/*.js" > /dev/null 2>&1; then

    js_files=()
    for f in "$EXT_DIR"/*.js; do
        [[ -f "$f" ]] && js_files+=("$f")
    done
    if [[ -d "$EXT_DIR/lib" ]]; then
        while IFS= read -r -d '' f; do
            js_files+=("$f")
        done < <(find "$EXT_DIR/lib" -name '*.js' -print0 2>/dev/null)
    fi

    # Match both ESM and legacy import patterns for deprecated modules
    # ESM: import ... from 'mainloop' / 'bytearray' / 'lang'
    # Legacy: const X = imports.misc.mainloop / imports.lang / imports.byteArray
    deprecated_pattern="(from ['\"]mainloop['\"]|from ['\"]bytearray['\"]|from ['\"]lang['\"]|imports\.misc\.mainloop|imports\.lang|imports\.byteArray|from ['\"]ByteArray['\"]|from ['\"]Lang['\"]|from ['\"]Mainloop['\"])"

    for f in "${js_files[@]}"; do
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
while IFS= read -r -d '' f; do
    rel_path="${f#"$EXT_DIR/"}"
    binary_files+="  $rel_path"$'\n'
done < <(find "$EXT_DIR" -type f \( -name '*.so' -o -name '*.o' -o -name '*.exe' -o -name '*.bin' \) -print0 2>/dev/null)

if [[ -n "$binary_files" ]]; then
    hit_count=$(echo -n "$binary_files" | grep -c '.' || true)
    print_result "FAIL" "no-binary-files" "Found $hit_count binary file(s)"
else
    print_result "PASS" "no-binary-files" "No binary files found"
fi

# ---------------------------------------------------------------------------
# CSS scoping check
# ---------------------------------------------------------------------------

if [[ -f "$EXT_DIR/stylesheet.css" ]]; then
    # Extract class names that appear as the FIRST (leftmost/top-level) class in a
    # CSS selector. Descendant classes (e.g., .my-scope .subtitle) are ignored since
    # they reference existing classes, not define new ones.
    # A "scoped" class contains a hyphen or underscore (namespace prefix).
    unscoped_classes=""
    while IFS= read -r classname; do
        # Classes with a hyphen or underscore are likely namespaced
        if [[ "$classname" != *-* ]] && [[ "$classname" != *_* ]]; then
            unscoped_classes+="  .$classname"$'\n'
        fi
    done < <(sed 's|/\*[^*]*\*\+\([^/*][^*]*\*\+\)*/||g; /\/\*/,/\*\//d' "$EXT_DIR/stylesheet.css" 2>/dev/null | \
             grep -oE '^\s*\.[a-zA-Z][a-zA-Z0-9_-]*' | sed 's/^[[:space:]]*\.//; s/[[:space:]]*$//' | sort -u)

    if [[ -n "$unscoped_classes" ]]; then
        hit_count=$(echo -n "$unscoped_classes" | grep -c '.' || true)
        print_result "WARN" "css-scoping" "Found $hit_count potentially unscoped CSS class(es)"
    else
        print_result "PASS" "css-scoping" "CSS classes appear properly scoped"
    fi
else
    print_result "SKIP" "css-scoping" "No stylesheet.css found"
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
        local errors warnings
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

echo ""

# check-metadata.py
if [[ -x "$SCRIPT_DIR/check-metadata.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-metadata.py"
else
    print_result "SKIP" "metadata" "check-metadata.py not found"
fi

# check-schema.sh
run_subscript "$SCRIPT_DIR/check-schema.sh"

# check-imports.sh
run_subscript "$SCRIPT_DIR/check-imports.sh"

# check-quality.py (Tier 2 heuristics)
if [[ -f "$SCRIPT_DIR/check-quality.py" ]]; then
    run_subscript "$SCRIPT_DIR/check-quality.py"
fi

# check-package.sh
run_subscript "$SCRIPT_DIR/check-package.sh"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

echo ""
echo "----------------------------------------------------------------"
TOTAL=$((PASS_COUNT + FAIL_COUNT + WARN_COUNT + SKIP_COUNT))
echo "  Results: $TOTAL checks — $PASS_COUNT passed, $FAIL_COUNT failed, $WARN_COUNT warnings, $SKIP_COUNT skipped"
echo "----------------------------------------------------------------"

if [[ $FAIL_COUNT -gt 0 ]]; then
    exit 1
else
    exit 0
fi
