# Reviewer Notes Template

Include in EGO submission comments. Only include sections that apply.

---

## pkexec / Polkit Usage

**Why privileged access is needed:** [explain what hardware or system resource
requires root, and why no D-Bus API alternative exists]

**Helper script:** `[path to helper script]` — performs [specific operation].
Validated via polkit action `[org.gnome.shell.extensions.yourext.action-id]`.

**Scope:** The helper only [reads/writes] `[specific file or device path]`.
No arbitrary command execution.

---

## Private API Usage

**APIs used:** `[Main.panel._indicators]`, `[statusArea._something]`, etc.

**Why no public alternative exists:** [explain why the public API is insufficient]

**Breakage plan:** [how the extension degrades if the private API changes]

---

## Network Access

**What is accessed:** [URL pattern or service name]

**Why:** [explain the purpose — e.g., "checks firmware update availability"]

**User control:** [how the user can disable or configure network access]

**Data sent:** [what data, if any, leaves the device]

---

## Clipboard Usage

**Why clipboard access is needed:** [explain the use case]

**Data handling:** [how clipboard data is processed and whether it is stored]

---

## File System Operations

**Files read/written:** `[specific paths]`

**Why GSettings is insufficient:** [explain why file I/O is needed beyond
GSettings for persistent configuration]

---

## Session Mode Usage

**Modes declared:** `["user", "unlock-dialog"]`

**Why lock screen presence is needed:** [explain the use case — e.g., "media
controls must remain accessible during lock screen"]

**Lock screen behavior:** [what the extension does/doesn't do on the lock screen]
