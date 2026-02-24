# EGO Submission Checklist

Complete guide for submitting a GNOME Shell extension to extensions.gnome.org.

## EGO Account Setup

1. Create an account at [extensions.gnome.org](https://extensions.gnome.org/)
2. Verify your email address (check spam folder)
3. Log in and navigate to your profile to confirm account is active
4. Note: first-time submissions require manual review by a volunteer reviewer
   and may take days or weeks depending on the review queue

## Upload Requirements

- Single zip file containing the extension
- Zip must contain `extension.js` and `metadata.json` at the root level
- No nested directory inside the zip (files at root, not inside a folder)
- Keep the zip under 5MB -- extensions with large bundled resources may be
  rejected or questioned
- The zip is uploaded via the "Upload Extension" page on extensions.gnome.org

### Correct Zip Structure

```
extension.zip
├── extension.js
├── metadata.json
├── prefs.js
├── stylesheet.css
├── schemas/
│   ├── org.gnome.shell.extensions.my-ext.gschema.xml
│   └── gschemas.compiled
├── locale/
│   └── ...
├── lib/
│   └── ...
├── resources/
│   └── ...
└── LICENSE
```

### Incorrect Zip Structure

```
extension.zip
└── my-extension@user/     <-- WRONG: nested directory
    ├── extension.js
    ├── metadata.json
    └── ...
```

## What to Include in the Zip

| File / Directory | Required | Notes |
|---|---|---|
| `extension.js` | Yes | Main extension entry point |
| `metadata.json` | Yes | UUID, name, description, shell-version |
| `prefs.js` | If applicable | Preferences UI (GTK4/Adw) |
| `stylesheet.css` | If applicable | Custom styles for panel/UI elements |
| `schemas/` | If applicable | Must include both `.gschema.xml` and `gschemas.compiled` |
| `locale/` | If applicable | Compiled `.mo` translation files |
| `lib/` or other JS modules | If applicable | Extension's own module code |
| `resources/` | If applicable | Helper scripts, icons, bundled assets |
| `LICENSE` | Recommended | GPL-2.0-or-later is standard for GNOME extensions |

## What to Exclude from the Zip

These files must NOT appear in the uploaded zip:

- `node_modules/` -- development dependency tree
- `.git/` -- version control history
- `.claude/` and `CLAUDE.md` -- AI assistant configuration
- `.gitignore` -- not needed at runtime
- `package.json` and `package-lock.json` -- npm metadata
- `eslint.config.mjs` -- linter configuration
- `*.pot` -- translation template source files (only `.mo` files ship)
- `*.pyc` and `__pycache__/` -- Python bytecode
- `tests/` -- test suite
- `docs/` -- documentation directory
- `.env` -- environment variables
- `Makefile` -- build tooling
- `*.zip` -- do not nest zips
- Any IDE or editor configuration (`.vscode/`, `.idea/`)

## Description Best Practices

The description field on EGO is the first thing users and reviewers see. Write
it carefully.

**Structure:**
1. One-sentence summary of what the extension does
2. Key features as a short bullet list
3. Compatibility and requirements
4. Permission disclosures (if applicable)

**Permission Disclosures:**

If your extension uses privileged or uncommon operations, disclose them clearly:

- "Uses polkit (pkexec) to write battery charging thresholds to sysfs"
- "Accesses the clipboard to provide paste functionality"
- "Makes network requests to [service] for [purpose]"
- "Uses private GNOME Shell APIs: [list specific ones]"

Undisclosed permissions are a common reason for reviewer questions or rejection.

**Example:**

> Unified Quick Settings control for power profiles and battery charging
> thresholds.
>
> Features:
> - Power profile switching (Performance/Balanced/Power Saver)
> - Battery charging threshold control
> - Predefined profiles with auto-detection
>
> Requires: power-profiles-daemon, polkit helper for battery threshold writes.
> Tested on GNOME 47 and 48.

## Screenshot Guidelines

Screenshots are not required but strongly recommended, especially for UI
extensions. Good screenshots help users decide to install and help reviewers
understand the extension's purpose.

- Show the extension in action (panel menus open, preferences visible)
- Use a clean desktop with default Adwaita theme
- Include both light and dark theme variants if the extension supports both
- Show the preferences UI if it is complex or has many options
- Recommended resolution: 1920x1080 or similar widescreen aspect ratio
- Crop to the relevant area if a full desktop screenshot is too busy
- Avoid personal information visible in screenshots (notifications, filenames)

## Shell Version Compatibility

The `shell-version` array in `metadata.json` declares which GNOME Shell
versions the extension supports.

**Rules:**
- Only list versions you have actually tested on
- The current stable release (GNOME 48) should be included
- Do not claim compatibility with unreleased or beta versions
- If you only tested on one version, only list that version
- EGO may reject extensions claiming untested compatibility

**Testing on multiple versions:**
- Use [GNOME OS Nightly](https://os.gnome.org/) VM images for version testing
- Use Podman/toolbox containers with different GNOME versions
- At minimum: test on the latest stable release

## Top 10 First-Submission Mistakes

These are the most common reasons first-time submissions are rejected:

1. **`console.log()` in production code** -- Use `console.debug()` for
   operational messages. EGO reviewers grep for `console.log` and flag it.

2. **Leaked signals/timeouts across enable/disable cycles** -- Every resource
   created in `enable()` must be destroyed in `disable()`. This is the single
   most common rejection reason.

3. **GTK imports in extension.js** -- GTK/Adw can only be imported in
   `prefs.js` and modules loaded exclusively by prefs. Importing GTK in
   extension code crashes the shell on Wayland.

4. **Deprecated Mainloop/Lang imports** -- Use `GLib.timeout_add()` and ES6
   classes. `Mainloop` and `Lang` have been deprecated since GNOME 44.

5. **Missing LICENSE file** -- Include a `LICENSE` file (GPL-2.0-or-later is
   the GNOME ecosystem standard).

6. **`session-modes: ["user"]`** -- This is the default; setting it explicitly
   is flagged as unnecessary. Remove the key entirely unless you need
   `unlock-dialog` or other non-default modes.

7. **UUID does not match directory name** -- The `uuid` in `metadata.json`
   must exactly match the extension directory name.

8. **Schema ID does not match settings-schema** -- The `settings-schema` field
   in `metadata.json` must match the `id` attribute of the `<schema>` element
   in your `.gschema.xml` file.

9. **`node_modules/` or `.git/` in the zip** -- Development artifacts must not
   be shipped. They bloat the zip and indicate sloppy packaging.

10. **No description of what the extension does** -- The `description` field in
    `metadata.json` and the EGO listing must clearly explain the extension's
    purpose.

## Reviewer Notes Field

When uploading to EGO, there is a "Notes for reviewers" text area. This is
your chance to explain anything unusual about the extension. Reviewers read
this before looking at the code.

**Always explain:**
- Why `pkexec`/polkit is needed (if applicable)
- Why private GNOME Shell APIs are used (if applicable)
- Any special testing instructions
- Known limitations or platform-specific behavior

**Example:**

> This extension uses pkexec to write battery charging thresholds to sysfs
> because GJS cannot write to kernel interfaces directly. The helper script
> (resources/hhb-power-ctl) validates all inputs and only writes to specific
> /sys/class/power_supply paths.
>
> The extension accesses Main.panel.statusArea.quickSettings._indicators
> (private API) to reorder the Quick Settings indicator. There is no public
> API for indicator positioning.
>
> Tested on ThinkPad X1 Carbon Gen 11 with GNOME 47 and 48 on Fedora 41/42.

## Resubmission Guidance

If your extension is rejected:

1. **Read the reviewer comments carefully** -- they are specific and actionable
2. **Fix ALL mentioned issues**, not just some -- partial fixes lead to another
   round of review
3. **Check this checklist** for anything the reviewer might not have explicitly
   mentioned but would catch on re-review
4. **Bump the version** in `metadata.json` (EGO may not accept a resubmission
   with the same version string)
5. **Note what you fixed** in the reviewer notes field:
   "Fixed: removed console.log calls, added signal cleanup in disable(),
   removed node_modules from zip"
6. **Re-run ego-lint and ego-review** before resubmitting to catch any
   regressions from the fixes

Common reviewer feedback patterns:
- "Please remove console.log" -- replace all with `console.debug()`
- "Signal not disconnected" -- add cleanup to `disable()` or `destroy()`
- "Deprecated API" -- replace `Mainloop` with `GLib`, `Lang` with ES6 classes
- "File X should not be in the zip" -- update your packaging script

## After Approval

Once your extension is approved:

- The extension goes live on extensions.gnome.org immediately
- Users can install via the GNOME Extensions app or the EGO website
- Updates follow the same review process (upload new zip, wait for review)
- Monitor your GitHub/GitLab issues for user bug reports
- Keep `shell-version` updated when new GNOME releases ship
- Respond to user reviews on EGO if they report issues
- Consider setting up CI to run ego-lint on every commit

### Maintaining Compatibility

When a new GNOME Shell release is announced:

1. Test your extension on the new version (use GNOME OS Nightly images)
2. Fix any API breakage
3. Add the new version to `shell-version` in `metadata.json`
4. Upload the updated zip to EGO
5. Remove very old GNOME versions from `shell-version` once they are EOL
