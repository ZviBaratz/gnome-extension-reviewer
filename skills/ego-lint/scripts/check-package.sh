#!/usr/bin/env bash
# check-package.sh — Validate zip package contents for EGO compliance.
#
# Usage: check-package.sh EXTENSION_DIR
#
# Checks that the extension zip (if present) does not include forbidden files
# and does include required files.
#
# Output: PIPE-delimited lines: STATUS|check-name|detail

set -euo pipefail

EXT_DIR="$(cd "${1:-.}" && pwd)"

# Find zip files in the extension directory
zip_files=()
while IFS= read -r -d '' f; do
    zip_files+=("$f")
done < <(find "$EXT_DIR" -maxdepth 1 -name '*.zip' -print0 2>/dev/null)

if [[ ${#zip_files[@]} -eq 0 ]]; then
    echo "SKIP|package/exists|No zip package found in extension directory"
    exit 0
fi

# Use the first zip file found
zip_file="${zip_files[0]}"
zip_name="$(basename "$zip_file")"

echo "PASS|package/exists|Found package: $zip_name"

# Get zip contents
zip_contents=""
if command -v zipinfo > /dev/null 2>&1; then
    zip_contents="$(zipinfo -1 "$zip_file" 2>/dev/null)" || true
elif command -v unzip > /dev/null 2>&1; then
    zip_contents="$(unzip -l "$zip_file" 2>/dev/null | awk 'NR>3 && /^ / {print $NF}')" || true
else
    echo "SKIP|package/contents|Neither zipinfo nor unzip available"
    exit 0
fi

# ---------------------------------------------------------------------------
# Check for forbidden contents
# ---------------------------------------------------------------------------

forbidden_patterns=(
    "node_modules/"
    ".git/"
    ".claude/"
    "CLAUDE.md"
    ".pot"
    ".pyc"
    "__pycache__/"
    ".env"
)

forbidden_found=0
for pattern in "${forbidden_patterns[@]}"; do
    matches=""
    case "$pattern" in
        */)
            # Directory pattern: match lines containing the directory prefix
            matches="$(echo "$zip_contents" | grep -F "$pattern" || true)"
            ;;
        .*)
            # Extension or dotfile pattern
            matches="$(echo "$zip_contents" | grep -E "(^|/)${pattern//./\\.}$" || true)"
            if [[ -z "$matches" ]]; then
                # Also check for files ending with the extension
                matches="$(echo "$zip_contents" | grep -E "${pattern//./\\.}$" || true)"
            fi
            ;;
        *)
            # Exact filename
            matches="$(echo "$zip_contents" | grep -E "(^|/)${pattern}$" || true)"
            ;;
    esac

    if [[ -n "$matches" ]]; then
        match_count=$(echo "$matches" | wc -l | xargs)
        echo "FAIL|package/no-forbidden|Found forbidden content: $pattern ($match_count match(es))"
        forbidden_found=$((forbidden_found + 1))
    fi
done

if [[ $forbidden_found -eq 0 ]]; then
    echo "PASS|package/no-forbidden|No forbidden files found in package"
fi

# ---------------------------------------------------------------------------
# Check for required contents
# ---------------------------------------------------------------------------

required_files=("extension.js" "metadata.json")
missing_required=0

for req in "${required_files[@]}"; do
    if echo "$zip_contents" | grep -qE "(^|/)${req}$"; then
        echo "PASS|package/has-$req|$req found in package"
    else
        echo "FAIL|package/has-$req|$req missing from package"
        missing_required=$((missing_required + 1))
    fi
done
