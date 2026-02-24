#!/usr/bin/env python3
"""check-metadata.py — Validate metadata.json for EGO compliance.

Usage: check-metadata.py EXTENSION_DIR

Output: one line per check in PIPE-delimited format: STATUS|check-name|detail
"""

import json
import os
import re
import sys


def result(status, check, detail):
    print(f"{status}|{check}|{detail}")


def main():
    if len(sys.argv) < 2:
        result("FAIL", "metadata/args", "No extension directory provided")
        sys.exit(1)

    ext_dir = os.path.realpath(sys.argv[1])
    metadata_path = os.path.join(ext_dir, "metadata.json")
    dir_name = os.path.basename(ext_dir)

    # --- Existence and valid JSON ---
    if not os.path.isfile(metadata_path):
        result("FAIL", "metadata/exists", "metadata.json not found")
        return

    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        result("FAIL", "metadata/valid-json", f"Invalid JSON: {e}")
        return

    result("PASS", "metadata/valid-json", "metadata.json is valid JSON")

    # --- Required fields ---
    required = ["uuid", "name", "description", "shell-version"]
    missing = [field for field in required if field not in meta]
    if missing:
        result("FAIL", "metadata/required-fields", f"Missing required field(s): {', '.join(missing)}")
    else:
        result("PASS", "metadata/required-fields", "All required fields present")

    # --- UUID format ---
    uuid = meta.get("uuid", "")
    if uuid:
        if re.fullmatch(r"[a-zA-Z0-9._@-]+", uuid):
            result("PASS", "metadata/uuid-format", f"UUID format is valid: {uuid}")
        else:
            result("FAIL", "metadata/uuid-format", f"UUID contains invalid characters: {uuid}")

        # UUID matches directory name
        if uuid == dir_name:
            result("PASS", "metadata/uuid-matches-dir", f"UUID matches directory name")
        else:
            result("FAIL", "metadata/uuid-matches-dir", f"UUID '{uuid}' does not match directory '{dir_name}'")

        # No @gnome.org namespace
        if "@gnome.org" in uuid:
            result("FAIL", "metadata/uuid-no-gnome-org", "UUID must not use @gnome.org namespace")
        else:
            result("PASS", "metadata/uuid-no-gnome-org", "UUID does not use @gnome.org namespace")

    # --- shell-version ---
    sv = meta.get("shell-version")
    if sv is not None:
        if isinstance(sv, list):
            result("PASS", "metadata/shell-version-array", "shell-version is an array")

            if "48" in sv:
                result("PASS", "metadata/shell-version-current", "shell-version includes current GNOME 48")
            else:
                result("WARN", "metadata/shell-version-current", "shell-version does not include GNOME 48")
        else:
            result("FAIL", "metadata/shell-version-array", f"shell-version must be an array, got {type(sv).__name__}")

    # --- session-modes ---
    if "session-modes" in meta and meta["session-modes"] == ["user"]:
        result("WARN", "metadata/session-modes", 'session-modes ["user"] is redundant (EGO default)')
    else:
        result("PASS", "metadata/session-modes", "No redundant session-modes key")

    # --- settings-schema ---
    schema = meta.get("settings-schema")
    if schema is not None:
        if schema.startswith("org.gnome.shell.extensions."):
            result("PASS", "metadata/settings-schema", f"settings-schema has correct prefix: {schema}")
        else:
            result("FAIL", "metadata/settings-schema", f"settings-schema should start with org.gnome.shell.extensions., got: {schema}")


if __name__ == "__main__":
    main()
