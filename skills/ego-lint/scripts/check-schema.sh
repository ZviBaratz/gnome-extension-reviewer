#!/usr/bin/env bash
# check-schema.sh — Validate GSettings schemas for EGO compliance.
#
# Usage: check-schema.sh EXTENSION_DIR
#
# Output: PIPE-delimited lines: STATUS|check-name|detail

set -euo pipefail

EXT_DIR="$(cd "${1:-.}" && pwd)"

# Extract ALL schema ids from a .gschema.xml file.
# Filters to <schema\b lines to avoid matching <enum id=> or other elements.
extract_all_schema_ids() {
    local file="$1"
    grep -P '<schema\b' "$file" | grep -oP 'id="[^"]*"' | sed 's/id="//;s/"//'
}

# Extract the first schema id from a .gschema.xml file.
# For single-schema files this is the only schema. For multi-schema files
# (e.g. a main schema + .keybindings sub-schema), prefer using
# extract_all_schema_ids() + targeted matching instead.
extract_schema_id() {
    local file="$1"
    extract_all_schema_ids "$file" | head -1
}

# Return true (0) if a specific schema ID exists anywhere in a .gschema.xml file.
schema_id_in_file() {
    local file="$1"
    local target_id="$2"
    extract_all_schema_ids "$file" | grep -qxF "$target_id"
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

# Validate schema IDs match metadata.
# Extensions may have supplementary schemas (e.g. profile schemas, keybinding
# schemas) whose IDs legitimately differ from the primary settings-schema.
# Require that AT LEAST ONE schema file contains the settings-schema ID.
# Supplementary files that don't contain it get SKIP (not FAIL).
if [[ "$has_settings_schema" == true ]]; then
    primary_schema_file=""
    for schema_file in "${schema_files[@]}"; do
        # Check whether settings-schema appears as ANY <schema id=> in the file.
        # Multi-schema XML (e.g. main schema + .keybindings sub-schema) must not
        # fail just because a sub-schema appears first.
        if schema_id_in_file "$schema_file" "$settings_schema"; then
            echo "PASS|schema/id-matches|Schema ID '$settings_schema' found in $(basename "$schema_file")"
            primary_schema_file="$schema_file"
        else
            all_ids="$(extract_all_schema_ids "$schema_file" | paste -sd ' ')"
            echo "SKIP|schema/id-matches|Supplementary schema $(basename "$schema_file") has different ID (found: ${all_ids}) — OK for profile/keybinding schemas"
        fi
    done
    if [[ -z "$primary_schema_file" ]]; then
        # Check for namespace-prefix pattern: settings-schema used as a prefix
        # (e.g. metadata says "org.foo.bar" but gschema defines "org.foo.bar.state").
        # This is valid — the extension builds sub-schema paths by appending suffixes.
        prefix_match=""
        for schema_file in "${schema_files[@]}"; do
            if extract_all_schema_ids "$schema_file" | grep -q "^${settings_schema}\."; then
                prefix_match="$schema_file"
                break
            fi
        done
        if [[ -n "$prefix_match" ]]; then
            echo "PASS|schema/id-matches|settings-schema '$settings_schema' used as namespace prefix — sub-schemas found in $(basename "$prefix_match")"
            primary_schema_file="$prefix_match"
        else
            echo "FAIL|schema/id-matches|settings-schema '$settings_schema' not found in any .gschema.xml file"
        fi
    fi
fi

# Validate schema filename convention: <settings-schema>.gschema.xml
# When settings-schema is defined in metadata.json, only the PRIMARY schema
# file (the one containing the settings-schema ID) must follow the naming
# convention. Supplementary schemas (profile, keybinding, etc.) may use
# different names. For extensions without settings-schema, apply to all files.
for schema_file in "${schema_files[@]}"; do
    if [[ "$has_settings_schema" == true ]]; then
        # Only enforce filename convention on the primary schema file.
        if ! schema_id_in_file "$schema_file" "$settings_schema"; then
            echo "SKIP|schema/filename-convention|Supplementary schema $(basename "$schema_file") — filename convention not required"
            continue
        fi
        ref_id="$settings_schema"
    else
        ref_id="$(extract_schema_id "$schema_file")"
    fi
    if [[ -n "$ref_id" ]]; then
        expected_filename="${ref_id}.gschema.xml"
        actual_filename="$(basename "$schema_file")"
        if [[ "$actual_filename" == "$expected_filename" ]]; then
            echo "PASS|schema/filename-convention|Schema filename matches settings-schema: $actual_filename"
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
