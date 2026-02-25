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

# Check zip file size
zip_size=$(stat -c%s "$zip_file" 2>/dev/null || stat -f%z "$zip_file" 2>/dev/null || echo 0)
if [[ "$zip_size" -gt 5242880 ]]; then
    size_mb=$(echo "scale=1; $zip_size / 1048576" | bc 2>/dev/null || echo "?")
    echo "WARN|package/size|Package is ${size_mb}MB — consider reducing (recommended: under 5MB)"
else
    echo "PASS|package/size|Package size OK"
fi

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
    # Version control and AI tool artifacts
    "node_modules/"
    ".git/"
    ".claude/"
    "CLAUDE.md"
    ".cursorrules"
    ".cursor/"
    ".windsurf/"
    ".aider"
    "cline_docs/"
    ".github/copilot-instructions.md"
    # Build artifacts
    ".pot"
    ".pyc"
    "__pycache__/"
    # Secrets
    ".env"
    # Development files
    ".gitignore"
    "package.json"
    "package-lock.json"
    "eslint.config.mjs"
    ".eslintrc"
    "Makefile"
    ".editorconfig"
    ".prettierrc"
    ".vscode/"
    ".idea/"
    # Documentation (not needed at runtime)
    "CONTRIBUTING.md"
    "README.md"
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

# ---------------------------------------------------------------------------
# Check for nested directory structure
# ---------------------------------------------------------------------------

# extension.js should be at root, not inside a subdirectory
if echo "$zip_contents" | grep -qE "^[^/]+/extension\.js$"; then
    if ! echo "$zip_contents" | grep -qE "^extension\.js$"; then
        echo "FAIL|package/nested-structure|extension.js is inside a subdirectory — files must be at zip root"
    fi
fi

# ---------------------------------------------------------------------------
# Check for compiled schemas
# ---------------------------------------------------------------------------

if echo "$zip_contents" | grep -qE "\.gschema\.xml$"; then
    if echo "$zip_contents" | grep -qF "gschemas.compiled"; then
        echo "PASS|package/compiled-schemas|gschemas.compiled found"
    else
        echo "FAIL|package/compiled-schemas|Schema XML found but gschemas.compiled missing — run glib-compile-schemas"
    fi
fi
