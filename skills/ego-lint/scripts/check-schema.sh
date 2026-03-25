#!/usr/bin/env bash
# check-schema.sh — Validate GSettings schemas for EGO compliance.
#
# Usage: check-schema.sh EXTENSION_DIR
#
# Output: PIPE-delimited lines: STATUS|check-name|detail

set -euo pipefail

EXT_DIR="$(cd "${1:-.}" && pwd)"

# Extract the schema id from a .gschema.xml file.
# Uses a <schema>-specific grep to avoid picking up <enum id=> or other
# elements that appear before <schema id=> in files with multiple top-level
# elements (e.g. caffeine's schema has three <enum> elements first).
extract_schema_id() {
    local file="$1"
    grep -P '<schema\b' "$file" | grep -oP 'id="[^"]*"' | head -1 | sed 's/id="//;s/"//'
}

METADATA="$EXT_DIR/metadata.json"
# src/ layout fallback
[[ ! -f "$METADATA" && -f "$EXT_DIR/src/metadata.json" ]] && METADATA="$EXT_DIR/src/metadata.json"

SCHEMA_DIR="$EXT_DIR/schemas"
[[ ! -d "$SCHEMA_DIR" && -d "$EXT_DIR/src/schemas" ]] && SCHEMA_DIR="$EXT_DIR/src/schemas"

# Check if metadata.json has settings-schema
has_settings_schema=false
settings_schema=""
if [[ -f "$METADATA" ]]; then
    settings_schema="$(python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    m = json.load(f)
print(m.get('settings-schema', ''))
" "$METADATA" 2>/dev/null || true)"
    [[ -n "$settings_schema" ]] && has_settings_schema=true
fi

# Find schema files
schema_files=()
if [[ -d "$SCHEMA_DIR" ]]; then
    while IFS= read -r -d '' f; do
        schema_files+=("$f")
    done < <(find "$SCHEMA_DIR" -name '*.gschema.xml' -print0 2>/dev/null)
fi

# No schemas at all
if [[ ${#schema_files[@]} -eq 0 ]] && [[ "$has_settings_schema" == false ]]; then
    echo "SKIP|schema/exists|No schemas defined (not all extensions use schemas)"
    exit 0
fi

# settings-schema in metadata but no schema files
if [[ ${#schema_files[@]} -eq 0 ]] && [[ "$has_settings_schema" == true ]]; then
    echo "FAIL|schema/exists|settings-schema '$settings_schema' in metadata.json but no .gschema.xml files found"
    exit 0
fi

echo "PASS|schema/exists|Found ${#schema_files[@]} schema file(s)"

# Validate schema IDs match metadata
if [[ "$has_settings_schema" == true ]]; then
    for schema_file in "${schema_files[@]}"; do
        # Extract schema id from XML (use extract_schema_id to avoid matching <enum id=> etc.)
        schema_id="$(extract_schema_id "$schema_file")"
        if [[ "$schema_id" == "$settings_schema" ]]; then
            echo "PASS|schema/id-matches|Schema ID '$schema_id' matches metadata.json settings-schema"
        else
            echo "FAIL|schema/id-matches|Schema ID '$schema_id' does not match metadata.json settings-schema '$settings_schema'"
        fi
    done
fi

# Validate schema filename convention: <schema-id>.gschema.xml
for schema_file in "${schema_files[@]}"; do
    schema_id="$(extract_schema_id "$schema_file")"
    if [[ -n "$schema_id" ]]; then
        expected_filename="${schema_id}.gschema.xml"
        actual_filename="$(basename "$schema_file")"
        if [[ "$actual_filename" == "$expected_filename" ]]; then
            echo "PASS|schema/filename-convention|Schema filename matches ID: $actual_filename"
        else
            echo "FAIL|schema/filename-convention|Schema filename '$actual_filename' MUST be '$expected_filename'"
        fi
    fi
done

# Validate schema path
for schema_file in "${schema_files[@]}"; do
    schema_path="$(grep -oP 'path="[^"]*"' "$schema_file" | head -1 | sed 's/path="//;s/"//')"
    if [[ -n "$schema_path" ]]; then
        if [[ "$schema_path" == /org/gnome/shell/extensions/* ]]; then
            echo "PASS|schema/path|Schema path is correct: $schema_path"
        else
            echo "FAIL|schema/path|Schema path should start with /org/gnome/shell/extensions/, got: $schema_path"
        fi
        # Path must end with /
        if [[ "$schema_path" != */ ]]; then
            echo "FAIL|schema/path-trailing-slash|Schema path must end with /, got: $schema_path"
        else
            echo "PASS|schema/path-trailing-slash|Schema path ends with /"
        fi
    fi
done

# Check for GNOME trademark in schema IDs
for schema_file in "${schema_files[@]}"; do
    schema_id="$(extract_schema_id "$schema_file")"
    if [[ -n "$schema_id" ]]; then
        # Strip the standard prefix (case-insensitive), then check for 'gnome' in the extension-specific part
        lower_id="${schema_id,,}"
        ext_part="${lower_id#org.gnome.shell.extensions.}"
        if echo "$ext_part" | grep -qi "gnome"; then
            echo "FAIL|schema/gnome-trademark|GNOME trademark must not appear in schema ID extension part: $schema_id"
        fi
    fi
done

# Try glib-compile-schemas --strict --dry-run
if command -v glib-compile-schemas > /dev/null 2>&1; then
    compile_output=""
    compile_exit=0
    compile_output="$(glib-compile-schemas --strict --dry-run "$SCHEMA_DIR" 2>&1)" || compile_exit=$?
    if [[ $compile_exit -eq 0 ]]; then
        echo "PASS|schema/compile|glib-compile-schemas --strict --dry-run passed"
    else
        echo "FAIL|schema/compile|glib-compile-schemas failed: $compile_output"
    fi
else
    echo "SKIP|schema/compile|glib-compile-schemas not available"
fi
