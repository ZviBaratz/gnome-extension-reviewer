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
# Result
# ---------------------------------------------------------------------------

if [[ $violations -eq 0 ]]; then
    echo "PASS|imports/segregation|Import contexts are properly segregated"
fi
