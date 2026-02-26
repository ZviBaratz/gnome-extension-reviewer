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


def check_donations(meta):
    """Validate donations field structure and values."""
    if "donations" not in meta:
        return
    donations = meta["donations"]
    if not isinstance(donations, dict):
        result("FAIL", "metadata/donations-format", "donations must be an object")
        return
    if len(donations) == 0:
        result("FAIL", "metadata/donations-empty", "donations object is empty; drop the field entirely if unused")
        return
    valid_keys = {
        "buymeacoffee", "custom", "github", "kofi",
        "liberapay", "opencollective", "patreon", "paypal",
    }
    for key in donations:
        if key not in valid_keys:
            result("FAIL", "metadata/donations-invalid-key",
                   f"'{key}' is not a valid donations key; "
                   f"valid keys: {', '.join(sorted(valid_keys))}")
            return
        val = donations[key]
        if isinstance(val, list):
            if len(val) > 3:
                result("FAIL", "metadata/donations-array-length",
                       f"donations.{key} array has {len(val)} items (max 3)")
                return
        elif not isinstance(val, str):
            result("FAIL", "metadata/donations-value-type",
                   f"donations.{key} must be a string or array, "
                   f"got {type(val).__name__}")
            return
    result("PASS", "metadata/donations", "donations field is valid")


def check_session_modes_values(meta):
    """Validate that session-modes contains only allowed values."""
    sm = meta.get("session-modes")
    if sm is None or not isinstance(sm, list):
        return
    valid_values = {"user", "unlock-dialog"}
    for v in sm:
        if v not in valid_values:
            result("FAIL", "metadata/session-modes-invalid",
                   f"Invalid session-modes value '{v}'; "
                   f"allowed: {', '.join(sorted(valid_values))}")
            return
    result("PASS", "metadata/session-modes-values", "session-modes values are valid")


def check_version_name(meta):
    """Validate version-name format if present."""
    if "version-name" not in meta:
        return
    vn = meta["version-name"]
    if not isinstance(vn, str):
        result("FAIL", "metadata/version-name-format",
               f"version-name must be a string, got {type(vn).__name__}")
        return
    if not re.fullmatch(r"(?!^[. ]+$)[a-zA-Z0-9 .]{1,16}", vn):
        result("FAIL", "metadata/version-name-format",
               f"version-name '{vn}' is invalid; must be 1-16 alphanumeric/space/dot "
               "characters and not only dots/spaces")
        return
    result("PASS", "metadata/version-name-format", f"version-name '{vn}' is valid")


def check_shell_version_entries(meta):
    """Validate each shell-version entry format."""
    sv = meta.get("shell-version")
    if not isinstance(sv, list):
        return
    for entry in sv:
        if not isinstance(entry, str) or not entry or \
           not re.fullmatch(r"\d+(\.\d+)?", entry):
            result("FAIL", "metadata/shell-version-entry",
                   f"Invalid shell-version entry: {entry!r}; "
                   "expected format like '45' or '3.38'")
            return
    result("PASS", "metadata/shell-version-entries",
           "All shell-version entries are valid")


def check_description_length(meta):
    """Warn on very short descriptions."""
    desc = meta.get("description")
    if isinstance(desc, str) and 0 < len(desc) < 20:
        result("WARN", "metadata/description-short",
               f"Description is very short ({len(desc)} chars)")


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
        result("FAIL", "metadata/session-modes", 'session-modes ["user"] is redundant and MUST be dropped — it is the EGO default')
    else:
        result("PASS", "metadata/session-modes", "No redundant session-modes key")

    # --- settings-schema ---
    schema = meta.get("settings-schema")
    if schema is not None:
        if schema.startswith("org.gnome.shell.extensions."):
            result("PASS", "metadata/settings-schema", f"settings-schema has correct prefix: {schema}")
        else:
            result("FAIL", "metadata/settings-schema", f"settings-schema should start with org.gnome.shell.extensions., got: {schema}")

    # --- UUID must contain @ ---
    if uuid and "@" not in uuid:
        result("FAIL", "metadata/uuid-at-sign",
               f"UUID must contain @ (e.g., my-extension@username), got: {uuid}")
    elif uuid:
        result("PASS", "metadata/uuid-at-sign", "UUID contains @")

    # --- Non-standard fields ---
    STANDARD_FIELDS = {
        "uuid", "name", "description", "shell-version",
        "settings-schema", "gettext-domain", "url",
        "session-modes", "donations", "original-author",
        "version",  # deprecated but recognized — flagged separately below
        "version-name",  # optional display version per gjs.guide
    }
    non_standard = [k for k in meta if k not in STANDARD_FIELDS]
    if non_standard:
        for field in non_standard:
            result("WARN", "metadata/non-standard-field",
                   f"'{field}' is not a standard metadata field")
    else:
        result("PASS", "metadata/non-standard-field",
               "No non-standard metadata fields")

    # --- Deprecated version field ---
    if "version" in meta:
        result("WARN", "metadata/deprecated-version",
               "version field is ignored by EGO for GNOME 45+; consider removing")

    # --- Missing gettext-domain with locale/ ---
    locale_dir = os.path.join(ext_dir, 'locale')
    if os.path.isdir(locale_dir) and 'gettext-domain' not in meta:
        result("WARN", "metadata/missing-gettext-domain",
               "locale/ directory exists but gettext-domain not set in metadata.json")
    elif os.path.isdir(locale_dir):
        result("PASS", "metadata/gettext-domain", "gettext-domain set with locale/ directory")

    # --- Future shell-version ---
    sv = meta.get('shell-version', [])
    if isinstance(sv, list):
        for v in sv:
            try:
                if int(v) > CURRENT_STABLE:
                    result("FAIL", "metadata/future-shell-version",
                           f"shell-version '{v}' is newer than current stable ({CURRENT_STABLE})")
            except ValueError:
                pass

    # --- Additional validations ---
    check_donations(meta)
    check_session_modes_values(meta)
    check_version_name(meta)
    check_shell_version_entries(meta)
    check_description_length(meta)
    check_url_field(meta)
    check_shell_version_dev_limit(meta)
    check_esm_version_floor(meta, ext_dir)
    check_session_modes_consistency(meta, ext_dir)


CURRENT_STABLE = 48


def check_url_field(meta):
    """WARN if url field is missing from metadata."""
    if "url" not in meta:
        result("FAIL", "metadata/missing-url",
               "metadata.json has no url field — required for EGO submission")
    else:
        url = meta["url"]
        result("PASS", "metadata/missing-url", "url field is present")
        # Check if URL looks like a repository URL
        repo_patterns = [
            "github.com", "gitlab.", "codeberg.org", "sr.ht",
            "bitbucket.org", "pagure.io", "salsa.debian.org",
        ]
        if isinstance(url, str) and not any(p in url for p in repo_patterns):
            result("WARN", "metadata/url-format",
                   f"url '{url}' does not appear to be a repository URL — "
                   f"EGO expects a link to the source code repository")


def check_shell_version_dev_limit(meta):
    """FAIL if shell-version contains more than one development release."""
    sv = meta.get("shell-version", [])
    if not isinstance(sv, list):
        return
    dev_versions = []
    for v in sv:
        try:
            major = int(str(v).split(".")[0])
            if major > CURRENT_STABLE:
                dev_versions.append(v)
        except ValueError:
            pass
    if len(dev_versions) > 1:
        result("FAIL", "metadata/shell-version-dev-limit",
               f"shell-version has {len(dev_versions)} development releases "
               f"({', '.join(dev_versions)}); at most 1 allowed")
    else:
        result("PASS", "metadata/shell-version-dev-limit",
               "shell-version has at most 1 development release")


def check_session_modes_consistency(meta, ext_dir):
    """Warn if code references sessionMode but metadata doesn't declare unlock-dialog."""
    sm = meta.get("session-modes")
    if isinstance(sm, list) and "unlock-dialog" in sm:
        result("PASS", "metadata/session-modes-consistency",
               "session-modes includes 'unlock-dialog'")
        return

    session_mode_re = re.compile(r"sessionMode\.(currentMode|isLocked)")
    found = []
    for root, _dirs, files in os.walk(ext_dir):
        for fname in files:
            if not fname.endswith(".js"):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, ext_dir)
            try:
                with open(fpath, encoding="utf-8", errors="replace") as f:
                    for lineno, line in enumerate(f, 1):
                        stripped = line.lstrip()
                        if stripped.startswith("//") or stripped.startswith("*"):
                            continue
                        if session_mode_re.search(line):
                            found.append(f"{rel}:{lineno}")
            except OSError:
                continue

    if found:
        for loc in found:
            result("WARN", "metadata/session-modes-consistency",
                   f"{loc}: references sessionMode but metadata.json does not "
                   "declare session-modes with 'unlock-dialog'")
    else:
        result("PASS", "metadata/session-modes-consistency",
               "No sessionMode references without matching declaration")


def check_esm_version_floor(meta, ext_dir):
    """FAIL if shell-version contains pre-45 versions but extension uses ESM imports."""
    sv = meta.get("shell-version", [])
    if not isinstance(sv, list):
        return
    pre_esm = []
    for v in sv:
        try:
            major = int(str(v).split(".")[0])
            if 40 <= major < 45:
                pre_esm.append(v)
        except ValueError:
            pass
    if not pre_esm:
        return
    ext_js = os.path.join(ext_dir, "extension.js")
    if os.path.isfile(ext_js):
        with open(ext_js, encoding="utf-8", errors="replace") as f:
            content = f.read()
        if "import " in content and "from " in content:
            result("FAIL", "metadata/shell-version-esm-floor",
                   f"shell-version includes pre-ESM version(s) ({', '.join(pre_esm)}) "
                   "but extension uses ESM imports (GNOME 45+ only)")

if __name__ == "__main__":
    main()
