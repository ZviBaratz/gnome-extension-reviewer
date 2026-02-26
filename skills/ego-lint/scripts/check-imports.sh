#!/usr/bin/env bash
# check-imports.sh — Validate import segregation between extension and prefs contexts.
#
# Usage: check-imports.sh EXTENSION_DIR
#
# The rule:
#   - Extension runtime code (extension.js, lib/**/*.js) must NOT import GTK libraries.
#   - Prefs code (prefs.js) must NOT import Shell runtime libraries.
#
# Output: PIPE-delimited lines: STATUS|check-name|detail

set -euo pipefail

EXT_DIR="$(cd "${1:-.}" && pwd)"

violations=0

# ---------------------------------------------------------------------------
# Check extension runtime code for banned GTK imports
# ---------------------------------------------------------------------------

# Banned in extension runtime: gi://Gtk, gi://Gdk, gi://Adw
gtk_pattern="gi://Gtk|gi://Gdk|gi://Adw"

# Build list of runtime JS files
runtime_files=()
if [[ -f "$EXT_DIR/extension.js" ]]; then
    runtime_files+=("$EXT_DIR/extension.js")
fi
if [[ -d "$EXT_DIR/lib" ]]; then
    while IFS= read -r -d '' f; do
        runtime_files+=("$f")
    done < <(find "$EXT_DIR/lib" -name '*.js' -print0 2>/dev/null)
fi

for f in "${runtime_files[@]}"; do
    while IFS= read -r match; do
        rel_path="${f#"$EXT_DIR/"}"
        echo "FAIL|imports/no-gtk-in-extension|$rel_path: $match"
        violations=$((violations + 1))
    done < <(grep -nE "$gtk_pattern" "$f" 2>/dev/null || true)
done

# ---------------------------------------------------------------------------
# Check prefs code for banned Shell runtime imports
# ---------------------------------------------------------------------------

# Banned in prefs: gi://Clutter, gi://Meta, gi://St, gi://Shell
shell_pattern="gi://Clutter|gi://Meta|gi://St|gi://Shell"

if [[ -f "$EXT_DIR/prefs.js" ]]; then
    while IFS= read -r match; do
        echo "FAIL|imports/no-shell-in-prefs|prefs.js: $match"
        violations=$((violations + 1))
    done < <(grep -nE "$shell_pattern" "$EXT_DIR/prefs.js" 2>/dev/null || true)
fi

# ---------------------------------------------------------------------------
# Check resource path case: prefs uses /Shell/Extensions/, extension uses /shell/
# ---------------------------------------------------------------------------

# prefs.js must NOT use resource:///org/gnome/shell/ (lowercase 's') — that's the extension context
if [[ -f "$EXT_DIR/prefs.js" ]]; then
    while IFS= read -r match; do
        echo "FAIL|imports/resource-path-case|prefs.js: wrong resource path case — use resource:///org/gnome/Shell/Extensions/ (capitalized Shell)"
        violations=$((violations + 1))
        break  # Report once
    done < <(grep -nE 'resource:///org/gnome/shell/' "$EXT_DIR/prefs.js" 2>/dev/null || true)
fi

# extension.js must NOT use resource:///org/gnome/Shell/Extensions/ — that's the prefs context
if [[ -f "$EXT_DIR/extension.js" ]]; then
    while IFS= read -r match; do
        echo "FAIL|imports/resource-path-case|extension.js: wrong resource path case — use resource:///org/gnome/shell/ (lowercase)"
        violations=$((violations + 1))
        break  # Report once
    done < <(grep -nE 'resource:///org/gnome/Shell/Extensions/' "$EXT_DIR/extension.js" 2>/dev/null || true)
fi

# ---------------------------------------------------------------------------
# Shared module dependency graph — transitive import segregation (GAP-015)
# Files reachable from prefs.js must not import Shell runtime libraries,
# even if they live in lib/ and are also used by extension.js.
# ---------------------------------------------------------------------------

resolve_import() {
    local dir="$1" import_path="$2"
    local resolved
    resolved="$(cd "$dir" && realpath -m "$import_path" 2>/dev/null)" || return
    if [[ -f "$resolved" ]]; then
        echo "$resolved"
    elif [[ -f "${resolved}.js" ]]; then
        echo "${resolved}.js"
    fi
}

get_local_imports() {
    local file="$1"
    local dir
    dir="$(dirname "$file")"
    grep -E "from\s+['\"]\.\.?/" "$file" 2>/dev/null | \
        sed -E "s/.*from\s+['\"]([^'\"]+)['\"].*/\1/" | \
        while IFS= read -r path; do
            resolve_import "$dir" "$path"
        done
}

if [[ -f "$EXT_DIR/prefs.js" ]]; then
    # BFS from prefs.js to find all prefs-reachable modules
    declare -A prefs_visited
    prefs_queue=("$EXT_DIR/prefs.js")
    prefs_visited["$EXT_DIR/prefs.js"]=1
    prefs_idx=0

    while [[ $prefs_idx -lt ${#prefs_queue[@]} ]]; do
        current="${prefs_queue[$prefs_idx]}"
        prefs_idx=$((prefs_idx + 1))

        while IFS= read -r neighbor; do
            [[ -z "$neighbor" ]] && continue
            if [[ -z "${prefs_visited[$neighbor]:-}" ]]; then
                prefs_visited["$neighbor"]=1
                prefs_queue+=("$neighbor")
            fi
        done < <(get_local_imports "$current")
    done

    # Check prefs-reachable modules (excluding prefs.js itself) for Shell imports
    for f in "${!prefs_visited[@]}"; do
        [[ "$f" == "$EXT_DIR/prefs.js" ]] && continue
        rel_path="${f#"$EXT_DIR/"}"
        while IFS= read -r match; do
            echo "FAIL|imports/shared-module-shell|$rel_path: Shell runtime import in module reachable from prefs.js: $match"
            violations=$((violations + 1))
        done < <(grep -nE "$shell_pattern" "$f" 2>/dev/null || true)
    done
fi

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

if [[ $violations -eq 0 ]]; then
    echo "PASS|imports/segregation|Import contexts are properly segregated"
fi
