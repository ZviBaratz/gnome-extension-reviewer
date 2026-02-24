# Security Checklist

EGO reviewers scrutinize security-sensitive patterns. Extensions run in the
GNOME Shell process with full access to the user session, so even minor
security issues can have serious consequences.

## Subprocess Execution

### When is subprocess execution acceptable?

Subprocess execution is a red flag for reviewers. It is acceptable only when
there is no D-Bus or GLib/Gio API alternative:

- **Acceptable:** `pkexec` for privileged sysfs writes (no D-Bus alternative)
- **Acceptable:** Calling well-known system tools (e.g., `powerprofilesctl`)
- **Not acceptable:** Shell commands that could be replaced by Gio.File operations
- **Not acceptable:** Parsing command output when a D-Bus property exists

### Subprocess execution rules

- **Never** execute user-provided strings as commands
- **Never** use shell expansion or eval (`/bin/sh -c "user_input"`)
- Use `Gio.Subprocess` with explicit argv arrays, not shell strings
- Use `GLib.spawn_command_line_async` only for simple, fixed commands
- Validate all arguments before passing to any subprocess
- Set a timeout on long-running commands to prevent hangs

```javascript
// WRONG: shell string with interpolation
const proc = Gio.Subprocess.new(
    ['/bin/sh', '-c', `echo ${userInput}`],  // Command injection
    Gio.SubprocessFlags.NONE
);

// CORRECT: explicit argv, no shell
const proc = Gio.Subprocess.new(
    ['/usr/bin/some-tool', '--flag', validatedArg],
    Gio.SubprocessFlags.NONE
);
```

## pkexec and Privilege Escalation

Extensions that use `pkexec` receive extra scrutiny. Reviewers verify:

### Helper script requirements

1. **Validate ALL inputs** -- every argument must be checked
2. **Whitelist, don't blacklist** -- only accept known-good values
3. **Use `set -eu`** -- fail on undefined variables and errors
4. **Write only to specific paths** -- hardcode allowed sysfs paths
5. **No user-controlled path components** -- never construct paths from arguments

```bash
#!/bin/bash
set -eu

# CORRECT: whitelist of valid commands, validated integer arguments
case "$1" in
    BAT0_END)
        val="$2"
        if ! [[ "$val" =~ ^[0-9]+$ ]] || [ "$val" -lt 0 ] || [ "$val" -gt 100 ]; then
            echo "Invalid value: $val" >&2
            exit 1
        fi
        echo "$val" > /sys/class/power_supply/BAT0/charge_control_end_threshold
        ;;
    *)
        echo "Unknown command: $1" >&2
        exit 1
        ;;
esac
```

### Polkit rules

- Scope rules to specific actions, not blanket root access
- Require active local session (`subject.active && subject.local`)
- Scope to appropriate user group (e.g., `sudo`, `wheel`)
- Document polkit usage in EGO submission notes

```javascript
// polkit rule: scoped to specific helper, active local session
polkit.addRule(function(action, subject) {
    if (action.id === "org.freedesktop.policykit.exec" &&
        action.lookup("program") === "/usr/local/bin/my-helper" &&
        subject.active && subject.local) {
        return polkit.Result.YES;
    }
});
```

## Clipboard Operations

Clipboard access must be disclosed and user-initiated:

- **Must disclose** clipboard access in `metadata.json` description
- **Only write** to clipboard when the user explicitly requests it (e.g., click)
- **Never read** clipboard contents automatically or on a timer
- **Never send** clipboard contents to any external service

```javascript
// CORRECT: user-initiated clipboard write
_onCopyClicked() {
    const clipboard = St.Clipboard.get_default();
    clipboard.set_text(St.ClipboardType.CLIPBOARD, this._text);
}

// WRONG: automatic clipboard read on enable
enable() {
    const clipboard = St.Clipboard.get_default();
    clipboard.get_text(St.ClipboardType.CLIPBOARD, (_, text) => {
        this._processClipboard(text);  // Privacy violation
    });
}
```

## Network Access

Network access is heavily scrutinized and must be disclosed:

- **Must disclose** network access in `metadata.json` description
- Use `Soup.Session` (libsoup3) -- not `fetch`, not `XMLHttpRequest`
- Handle network errors gracefully (timeouts, DNS failures, HTTP errors)
- Never leak user-identifying data in requests (no MAC address, hostname, etc.)
- Use HTTPS for all connections
- Never phone home or track usage without explicit user consent

```javascript
// CORRECT: Soup.Session with error handling
const session = new Soup.Session();
const message = Soup.Message.new('GET', 'https://api.example.com/data');
try {
    const bytes = await session.send_and_read_async(message, 0, null);
    if (message.get_status() !== Soup.Status.OK)
        throw new Error(`HTTP ${message.get_status()}`);
    // process bytes
} catch (e) {
    console.error('Network request failed:', e.message);
}
```

## File Path Handling

### Path traversal prevention

- Never construct file paths from user input without validation
- Use `GLib.build_filenamev()` for path construction
- Reject path components containing `..` or starting with `/`
- Validate filenames against an allowlist when possible

```bash
# WRONG: user input in path
echo "$value" > /sys/class/power_supply/$battery/charge_control_end_threshold

# CORRECT: validated battery name
case "$battery" in
    BAT0|BAT1|BAT2|BAT3) ;;
    *) echo "Invalid battery: $battery" >&2; exit 1 ;;
esac
echo "$value" > "/sys/class/power_supply/$battery/charge_control_end_threshold"
```

### File operation safety

- Check that files exist before reading (`Gio.File.query_exists()`)
- Handle `GLib.FileError` and `Gio.IOErrorEnum` gracefully
- Use `Gio.File` APIs, not shell commands (`cat`, `echo >`)
- Set appropriate permissions when creating files

## Data Storage

- **Configuration:** Use GSettings (schema compiled and installed)
- **Cache/data files:** Use XDG directories (`GLib.get_user_data_dir()`, etc.)
- **Never** store passwords, tokens, or secrets in GSettings or plain text files
- **Never** store data outside of standard XDG paths
- **Sanitize** any data written to files (escape special characters)

## Disclosure Requirements Summary

The following capabilities must be declared in the `metadata.json` description
or EGO submission notes:

| Capability | Must Disclose? | Where |
|---|---|---|
| Subprocess execution | Yes | Submission notes |
| pkexec / privilege escalation | Yes | Submission notes + description |
| Clipboard read/write | Yes | Description |
| Network access | Yes | Description |
| File system writes (outside GSettings) | Yes | Submission notes |
| Session mode usage | Yes | Submission notes |
