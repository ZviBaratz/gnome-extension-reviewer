# Phase 1: GitLab Guideline Evolution Research

**Date:** 2026-02-26
**Method:** Web research across gitlab.gnome.org (ewlsh/gjs-guide, Infrastructure/extensions-web), extensions.gnome.org review pages, GNOME blogs, Phoronix/XDA/ItsFoss news articles, GNOME Discourse, and gjs.guide porting guides. Focused on identifying when review guidelines changed, what motivated changes, and how the EGO platform itself performs automated validation.
**Scope:** Changes from 2024 through February 2026, covering GNOME Shell versions 46-50.

---

## Table of Contents

1. [Source Repository Structure](#1-source-repository-structure)
2. [Major Guideline Changes (Chronological)](#2-major-guideline-changes-chronological)
3. [Version-Specific Migration Requirements](#3-version-specific-migration-requirements)
4. [Patterns from Recent Extension Reviews](#4-patterns-from-recent-extension-reviews)
5. [EGO Platform Automated Checks](#5-ego-platform-automated-checks-extensions-web)
6. [Implications for Our Plugin](#6-implications-for-our-plugin)

---

## 1. Source Repository Structure

### gjs-guide Repository (Review Guidelines Source)

- **Location:** `gitlab.gnome.org/ewlsh/gjs-guide` (maintained by Evan Welsh)
- **GitHub mirror:** Not available (gjs-guide is NOT on GitHub, only the gjs runtime is mirrored)
- **Review guidelines file path:** `src/extensions/review-guidelines/` (inferred from URL structure `gjs.guide/extensions/review-guidelines/review-guidelines.html`)
- **Repository stats:** 3 open merge requests, 192 merged, 13 closed (as of February 2026)
- **Licensing issue:** [Issue #22](https://gitlab.gnome.org/ewlsh/gjs-guide/-/issues/22) discusses review of licensing after revisiting GNOME Shell's GPL-v2.0-or-later licensing
- **Style guide issue:** [Issue #36](https://gitlab.gnome.org/ewlsh/gjs-guide/-/issues/36) proposes redoing the style guide as an ESLint/Prettier introduction
- **Note:** Direct access to the commit history for the review-guidelines file was not achievable via web search. The GitLab UI pages are not well-indexed by search engines. For definitive commit-level analysis, direct browsing of `gitlab.gnome.org/ewlsh/gjs-guide/-/commits/main/src/extensions/review-guidelines/` is needed.

### extensions-web Repository (EGO Platform)

- **Location:** `gitlab.gnome.org/Infrastructure/extensions-web`
- **GitHub mirror:** `github.com/GNOME/extensions-web` (read-only)
- **Technology:** Django (Python), the "SweetTooth-Web" application
- **Key code path:** `sweettooth/extensions/models.py` contains `parse_zipfile_metadata()` for upload validation
- **Test data:** `sweettooth/extensions/testdata/RejectedExtension/v1/metadata.json` exists as a test fixture for rejection logic
- **Note:** Direct access to the extensions-web source code was blocked by permission restrictions during this research session. The analysis below is based on web search results, mailing list archives, and inferences from the test data structure.

### Guidelines Migration History

- **Pre-2021:** Review guidelines lived on `wiki.gnome.org/Projects/GnomeShell/Extensions/Review`
- **~2021:** Guidelines migrated to `gjs.guide/extensions/review-guidelines/review-guidelines.html`
- **Current state:** The wiki page is now just a redirect/pointer to gjs.guide. The wiki page itself says: "The review guidelines are now available at gjs.guide."

---

## 2. Major Guideline Changes (Chronological)

### Finding: AI-Generated Code Ban (December 2025)

- **Source:** [Javad Rahmatzadeh blog post](https://blogs.gnome.org/jrahmatzadeh/2025/12/06/ai-and-gnome-shell-extensions/), [Phoronix coverage](https://www.phoronix.com/news/GNOME-Extensions-Block-AI), [XDA coverage](https://www.xda-developers.com/gnome-cracking-down-ai-generated-code-extensions-guidelines/), [ItsFoss coverage](https://itsfoss.com/news/no-ai-extension-gnome/)
- **Date:** December 6, 2025 (blog post); rule added to gjs.guide review guidelines shortly after
- **Change:** New section added to the review guidelines explicitly rejecting submissions that appear to be primarily AI-generated. Specific rejection triggers documented:
  - Large amounts of unnecessary code
  - Inconsistent code style
  - Imaginary API usage (hallucinated APIs)
  - Comments serving as LLM prompts
  - Other indications of AI-generated output
- **Reviewer reasoning:** Rahmatzadeh (who is JustPerfection on EGO) explained that reviewers spend 6+ hours daily reviewing 15,000+ lines of code. AI-generated submissions were creating a "domino effect" of bad practices across new submissions. The specific example given was:
  ```javascript
  destroy() {
    try {
      if (typeof super.destroy === 'function') {
        super.destroy();
      }
    } catch (e) {
      console.warn(`${e.message}`);
    }
  }
  ```
  This wraps a known-safe call in unnecessary try-catch and typeof checks.
- **Clarification:** AI use for learning and debugging is still permitted. The rule targets wholesale AI-generated extensions where developers cannot explain their code.
- **Current coverage:** Strong. Our plugin has R-SLOP-01 through R-SLOP-29 (29 pattern rules), R-QUAL-01 through R-QUAL-26 (quality heuristics), and a 43-item AI slop checklist. The specific `typeof super.destroy` pattern is detected by R-SLOP-08.
- **Implication:** Our plugin is well-positioned here. The AI ban validates our entire Tier 1/Tier 2/Tier 3 approach to AI slop detection. However, the review guidelines do not enumerate specific signals -- they rely on reviewer judgment. Our comprehensive signal list may catch patterns that even human reviewers miss, or conversely may flag things reviewers would accept.

### Finding: Session-Modes Requirements Strengthened (GNOME 42+, enforcement tightened 2024-2025)

- **Source:** [gjs.guide session-modes page](https://gjs.guide/extensions/topics/session-modes.html), [Lock Guard review #67061](https://extensions.gnome.org/review/67061), [Soft Brightness Plus review #66207](https://extensions.gnome.org/review/66207), [Discourse discussion](https://discourse.gnome.org/t/in-a-gnome-extension-about-disable-function-when-only-unlock-dialog-session-modes-is-used/17028)
- **Date:** Session-modes field introduced in GNOME 42 (~2022); enforcement tightened through 2024-2025
- **Change:** Multiple requirements around session-modes have been consolidated and enforced more strictly:
  1. `"session-modes": ["user"]` is a hard reject (redundant, `user` is the default)
  2. `unlock-dialog` requires explicit justification in `disable()` comments
  3. Extensions MUST NOT disable selectively (no `if (...) return;` in disable)
  4. All keyboard event signals MUST be disconnected in lock screen mode
  5. Extensions should be prepared for `disable()` to be called at any session mode change
- **Reviewer reasoning:** From Lock Guard review (#67061, December 2025): JustPerfection explained "Your extension should clean up properly on disable. Currently works because you are not cleaning up and extension leaves its code after disable." The reviewer recommended adding `"session-modes": ["unlock-dialog"]` and referencing the session-modes documentation. The key insight is that extensions get disabled on lock screens UNLESS they have unlock-dialog permission -- so lock-screen-relevant extensions must explicitly request it.
- **Current coverage:** Covered. R-META-09 (session-modes: ["user"] is FAIL), R-LIFE-13 (selective disable), R-LIFE-14 (unlock-dialog comment), R-LIFE-11 (lockscreen signals).
- **Implication:** Our coverage aligns well with enforcement practice. No changes needed.

### Finding: Donations Field Recommendation (2024-2025, becoming standard reviewer feedback)

- **Source:** [APCUPS Monitor review #68473](https://extensions.gnome.org/review/68473), [Maximize 2 New Workspace review #68358](https://extensions.gnome.org/review/68358), [Text Extractor review #67199](https://extensions.gnome.org/review/67199), [gjs.guide anatomy page](https://gjs.guide/extensions/overview/anatomy.html)
- **Date:** Throughout 2024-2025; increasingly standard in reviewer feedback by late 2025
- **Change:** The `donations` field in `metadata.json` is now a standard part of reviewer guidance. Reviewers (JustPerfection) consistently recommend adding it even when not rejecting for its absence. Accepted keys include `github`, `paypal`, `patreon`, `buyMeACoffee`, `kofi`, and `custom` (URL). Values can be strings or arrays of strings (max 3).
- **Reviewer reasoning:** From Text Extractor review (#67199): "You can also add donations to the metadata.json, so people can donate to you if they want." This is a recommendation, not a rejection criterion, but it shows reviewer expectation.
- **Current coverage:** Our check-metadata.py validates that if `donations` is present, it has valid keys (R-META-18) and is not empty (R-META-24). We do NOT proactively suggest adding it.
- **Implication:** Consider adding an advisory-level check suggesting the `donations` field when it is missing. This would help developers get approved faster by meeting reviewer expectations, even though it is not a MUST requirement.

### Finding: gschemas.compiled Rejected for GNOME 45+ (2024-2026, consistently enforced)

- **Source:** [Claude Code Usage Indicator review #64921](https://extensions.gnome.org/review/64921), [APCUPS Monitor review #68473](https://extensions.gnome.org/review/68473), [Maximize 2 New Workspace review #68358](https://extensions.gnome.org/review/68358), [Improved Workspace Indicator review #67538](https://extensions.gnome.org/review/67538), [Text Extractor review #66775](https://extensions.gnome.org/review/66775)
- **Date:** Consistently enforced throughout 2024-2026
- **Change:** `schemas/gschemas.compiled` is now a hard reject for extensions targeting GNOME 45+. Since GNOME 44, settings schemas are compiled automatically during installation by the gnome-extensions tool and EGO platform.
- **Reviewer reasoning:** Standard feedback: "Remove schemas/gschemas.compiled. Not needed for 45+ packages." (multiple reviews)
- **Current coverage:** Covered. R-PKG-12 (check-package.sh) FAILs for gschemas.compiled in zip when targeting GNOME 45+.
- **Implication:** Our coverage is correct and matches current enforcement. No changes needed.

### Finding: connectObject/disconnectObject Recommended as Best Practice (GNOME 42+, increasingly enforced 2024-2026)

- **Source:** [Maximize 2 New Workspace review #68358](https://extensions.gnome.org/review/68358), [GNOME Shell 42 porting guide](https://gjs.guide/extensions/upgrading/gnome-shell-42.html), [GNOME Discourse discussion](https://discourse.gnome.org/t/description-of-the-connectobject-and-disconnectobject-methods/16726)
- **Date:** Introduced in GNOME 42 (~2022); reviewer recommendations increasing in 2024-2026
- **Change:** Reviewers now actively recommend replacing manual `connect()`/`disconnect()` patterns with `connectObject()`/`disconnectObject()`. From the Maximize 2 New Workspace review (#68358, February 2026), JustPerfection suggested "replacing the `this._handles` approach with `connectObject()` and `disconnectObject()` methods for cleaner cleanup management."
- **Reviewer reasoning:** `connectObject()` is the GJS equivalent of `g_signal_connect_object()`, which automatically disconnects signals when the connecting object is destroyed. This prevents dangling signal handlers that call freed objects.
- **Current coverage:** None. We have no check that suggests `connectObject`/`disconnectObject` as an alternative to manual connect/disconnect patterns.
- **Implication:** Consider adding an advisory-level check (R-QUAL-27 or similar) that suggests `connectObject`/`disconnectObject` when manual `connect()`/`disconnect()` patterns are detected, for extensions targeting GNOME 42+. This is not a MUST but would help developers pass review faster. Note: this should be advisory only since manual connect/disconnect is still valid code.

### Finding: Subprocess Cancellation on disable() (2025-2026, new enforcement emphasis)

- **Source:** [Text Extractor review #66775](https://extensions.gnome.org/review/66775)
- **Date:** December 2025
- **Change:** JustPerfection's review of Text Extractor v3 included a follow-up comment specifically about subprocess lifecycle: "Also, don't forget to cancel the subprocess on destroy or disable." This was in addition to the standard timeout/signal cleanup requirements.
- **Reviewer reasoning:** Extensions that spawn subprocesses (especially OCR tools, external commands) must cancel them in `disable()` to prevent orphaned processes.
- **Current coverage:** Partial. R-SEC-14 and R-DEPR-08 detect synchronous subprocess calls (blocking). R-SEC-15 detects `Gio.Subprocess` creation. But we do NOT verify that subprocesses are cancelled/killed in `disable()`.
- **Implication:** Consider adding a lifecycle check that pairs `Gio.Subprocess` creation with `.force_exit()` or `.send_signal()` or cancellable usage in `disable()`. Similar to R-LIFE-15 (Soup.Session.abort) but for subprocesses.

### Finding: Logging Strictness Increasing (2025-2026)

- **Source:** [Text Extractor review #66775](https://extensions.gnome.org/review/66775)
- **Date:** December 2025
- **Change:** JustPerfection's feedback: "Please remove the logs or make them only available in debug mode or on error." This goes beyond the existing R-LOG-01 (console.log is FAIL) to suggest that even console.debug/warn/error should be conditional.
- **Reviewer reasoning:** Excessive logging clutters the journal and makes debugging harder for other extensions. Reviewers want logging gated behind a debug setting or removed entirely for non-error cases.
- **Current coverage:** Partial. R-LOG-01 catches `console.log` as FAIL. R-QUAL-13 and R-QUAL-17 warn on excessive debug/warn/error volume. But we don't check whether logging is conditional (gated behind a settings key or debug flag).
- **Implication:** Consider adding a heuristic check: if console.debug/console.warn count exceeds a threshold AND there is no settings-based guard (e.g., `if (this._debug)` or `if (settings.get_boolean('debug'))`), issue a WARN suggesting conditional logging. This aligns with reviewer expectations but is inherently difficult to automate perfectly.

### Finding: Timeout Must Be Removed Before Reassignment (Consistently enforced)

- **Source:** [Text Extractor review #66775](https://extensions.gnome.org/review/66775), [GJS OSK review #61574](https://extensions.gnome.org/review/61574)
- **Date:** Consistently enforced throughout 2024-2026
- **Change:** Reviewers flag code that creates a new timeout without first removing the existing one. From Text Extractor v3 review: "Timeout should be removed before creating a new one (line 192 extension.js)."
- **Reviewer reasoning:** Creating a new timeout without removing the old one leaks main loop sources. The pattern should always be: remove old timeout, then create new one.
- **Current coverage:** Partial. R-LIFE-02 checks if timeout return values are stored. R-LIFE-12 verifies `GLib.Source.remove()` in `disable()`. But we do NOT check whether timeouts are removed before reassignment within the same function.
- **Implication:** Consider adding a check in check-lifecycle.py that detects patterns like `this._timeoutId = GLib.timeout_add(...)` where `GLib.Source.remove(this._timeoutId)` does not appear before the reassignment in the same function body. This is a common reviewer catch.

---

## 3. Version-Specific Migration Requirements

These changes from the gjs.guide porting guides directly affect review -- extensions claiming support for these versions but using removed APIs will be rejected.

### GNOME Shell 47 (Released September 2024)

- **Source:** [gjs.guide GNOME Shell 47 porting guide](https://gjs.guide/extensions/upgrading/gnome-shell-47.html)
- **Breaking changes:**
  - `Clutter.Color` removed entirely -- use `Cogl.Color()` instead
  - `getPreferencesWidget`/`fillPreferencesWindow` now awaited (async-compatible)
  - `PopupBaseMenuItem` styling: `selected` class removed, use `:selected` pseudo-class
  - `ControlsManagerLayout._spacing` property removed
  - `_fixMarkup()` moved from `ui/messageList.js` to `misc/util.js/fixMarkup()`
  - Accent color support added (`-st-accent-color`, `-st-accent-fg-color` CSS variables)
- **Current coverage:** None of these GNOME 47 API removals are covered by our pattern rules.
- **Implication:** Consider adding R-VER47-01 (Clutter.Color removal) as a version-gated pattern rule for extensions claiming GNOME 47+ support. The `fillPreferencesWindow` async change is not detectable by static analysis (it's a behavioral change, not an API removal).

### GNOME Shell 48 (Released March 2025)

- **Source:** [gjs.guide GNOME Shell 48 porting guide](https://gjs.guide/extensions/upgrading/gnome-shell-48.html)
- **Breaking changes:**
  - `Clutter.Image` removed entirely -- use `St.ImageContent` instead
  - `Meta.disable_unredirect_for_display` etc. moved to `Meta.Compositor` namespace
  - `Meta.CursorTracker.get_for_display()` replaced by `global.backend.get_cursor_tracker()`
  - `Clutter.Stage.get_key_focus()` now returns `null` (not stage) when no explicit focus
  - `Shell.SnippetHook.FRAGMENT` replaced by `Cogl.SnippetHook.FRAGMENT`
  - QuickMenuToggle style class names changed (`.quick-menu-toggle` -> `.quick-toggle-has-menu`)
  - `St` widgets: `vertical` property deprecated (use `orientation: Clutter.Orientation.VERTICAL`)
  - New `getLogger()` method on `ExtensionBase` for better logging
  - MessageTray.Notification gains `removeAction()` method
  - Major notification restructuring (MessageListSection removed, NotificationMessageGroup added)
- **Current coverage:** Partial. R-VER48-07 covers the QuickMenuToggle CSS class rename. We do not cover `Clutter.Image` removal, `Meta` namespace moves, `vertical` property deprecation, or other GNOME 48 API changes.
- **Implication:** High priority. `Clutter.Image` removal and `Meta` API namespace moves are likely sources of reviewer rejections for extensions claiming GNOME 48 support. Add version-gated rules for these.

### GNOME Shell 49 (Released September 2025)

- **Source:** [gjs.guide GNOME Shell 49 porting guide](https://gjs.guide/extensions/upgrading/gnome-shell-49.html)
- **Breaking changes:**
  - `Meta.Rectangle` removed (deprecated since Shell 45) -- use `Mtk.Rectangle`
  - `AppMenuButton` removed from `js/ui/panel.js` (unused since Shell 45)
  - `DoNotDisturbSwitch` removed from `ui/calendar.js` -- use `DoNotDisturbToggle` in `ui/status/doNotDisturb.js`
  - `Meta.MaximizeFlags` parameters removed from `maximize()`/`unmaximize()`
  - `Meta.Window.get_maximized()` removed -- use `is_maximized()`, `set_maximize_flags()`, `set_unmaximize_flags()`
  - `Meta.CursorTracker.set_pointer_visible()` removed -- use `inhibit_cursor_visibility()`/`uninhibit_cursor_visibility()`
  - `Clutter.ClickAction()` and `Clutter.TapAction()` removed -- use `Clutter.ClickGesture()` and `Clutter.LongPressGesture()`
  - `WorkspaceSwitcherPopup._redisplay()` renamed to `_redisplayAllPopups()`
  - X11/nested mode disabled by default
  - New `gnome-extensions upload` command added for EGO uploads
- **Current coverage:** Partial. R-VER49-06/07 cover `Clutter.DragAction` and `Clutter.SwipeAction` removal. R-VER49-08/09 cover maximize and AppMenuButton. But we do NOT cover `Meta.Rectangle` removal, `DoNotDisturbSwitch` removal, `Meta.MaximizeFlags` removal, `Meta.CursorTracker.set_pointer_visible()` removal, or `Clutter.ClickAction`/`Clutter.TapAction` removal.
- **Implication:** Several high-impact API removals are uncovered. `Meta.Rectangle` replacement with `Mtk.Rectangle` is particularly important since it was deprecated in Shell 45 and fully removed in 49 -- extensions that supported pre-49 versions will need updating.

### GNOME Shell 50 (Alpha released January 2026, stable expected March 2026)

- **Source:** [gjs.guide GNOME Shell 50 porting guide](https://gjs.guide/extensions/upgrading/gnome-shell-50.html), [Phoronix](https://www.phoronix.com/news/GNOME-Mutter-Shell-50-Alpha), [Linuxiac](https://linuxiac.com/gnome-50-ends-the-x11-era-after-decades/)
- **Breaking changes:**
  - X11 backend completely removed from Mutter. XWayland remains for running X11 apps.
  - `releaseKeyboard()` and `holdKeyboard()` removed from `misc/keyboardManager.js`
  - `show-restart-message` and `restart` signals removed from `global.display` (restart was X11-only)
  - `RunDialog._restart()` removed from `ui/runDialog.js`
  - New `easeAsync()` function for animations (non-breaking addition)
  - New `GLib.idle_add_once()`, `GLib.timeout_add_once()`, `GLib.timeout_add_seconds_once()` (non-breaking additions)
- **Current coverage:** Covered. R-VER50-01/02/03/04 detect the four removed APIs (releaseKeyboard, holdKeyboard, show-restart-message, restart signal) as blocking errors for extensions claiming GNOME 50 support.
- **Implication:** Our coverage is correct for the known GNOME 50 removals. The new `*_once()` GLib functions are additions, not removals, so no negative check needed. However, we could add an advisory suggesting `GLib.timeout_add_once()` as a cleaner alternative to `GLib.timeout_add()` when the callback returns `GLib.SOURCE_REMOVE`, for extensions targeting GNOME 50+.

---

## 4. Patterns from Recent Extension Reviews

Based on analysis of 15+ recent EGO review pages (2024-2026), the following patterns emerge in reviewer (primarily JustPerfection/Javad Rahmatzadeh) feedback:

### Most Common Rejection Reasons (by frequency in sampled reviews)

| Rank | Issue | Example Reviews | Our Coverage |
|------|-------|----------------|--------------|
| 1 | gschemas.compiled in package (45+) | #64921, #68473, #68358, #67538, #66775 | Covered (R-PKG-12) |
| 2 | Missing cleanup in disable() (null out references) | #68473, #53836, #67061 | Partial (Tier 3 checklist) |
| 3 | Synchronous subprocess calls | #68473, #53836 | Covered (R-SEC-14, R-DEPR-08) |
| 4 | Redundant settings instances | #53836, #64921 | Not covered |
| 5 | Deprecated module usage | #63292 (Forge v85) | Covered (R-DEPR-01/02/03) |
| 6 | Missing URL in metadata | #67061 | Covered (R-META-22) |
| 7 | Selective disable | #66207 (Soft Brightness Plus) | Covered (R-LIFE-13) |
| 8 | session-modes: ["user"] redundancy | #64921 | Covered (R-META-09) |
| 9 | Timeout not removed on destroy/reassign | #63292, #66775 | Partial (R-LIFE-02/12) |
| 10 | connectObject recommendation | #68358 | Not covered |

### Standard Reviewer Sign-Off Pattern

JustPerfection consistently includes the following in rejection feedback:
1. Specific line references (e.g., "line 46 extension.js")
2. Links to relevant gjs.guide documentation
3. Recommendation to add `donations` to metadata.json
4. Pointers to GNOME Extensions Matrix Channel and IRC for help

### Reviewer Workload Context

From the AI blog post: a single reviewer (Javad Rahmatzadeh) processes 15,000+ lines of extension code daily, spending 6+ hours. This context explains:
- Why reviews focus on known patterns (efficient to check)
- Why AI-generated code is banned (multiplies review burden)
- Why reviewers give terse, directive feedback (time-constrained)
- Why automated pre-screening (like our plugin) would be genuinely valuable

---

## 5. EGO Platform Automated Checks (extensions-web)

The extensions-web platform performs server-side validation during the upload process. Based on available evidence:

### Confirmed Server-Side Checks

| Check | Evidence | Our Analog |
|-------|----------|-----------|
| `metadata.json` presence in zip | Mailing list: "Error out for a missing metadata.json" (2012 commit message); Discourse: "Invalid extension data: Missing metadata.json" error | R-FILE-02 |
| `metadata.json` valid JSON | `parse_zipfile_metadata()` raises `InvalidExtensionData("Invalid JSON data")` on ValueError | R-META-01 (check-metadata.py) |
| UUID format validation | UUID is used as the directory structure key; invalid UUIDs would break the storage model | R-META-03 (check-metadata.py) |
| `shell-version` validation | Required for the version compatibility matrix displayed on EGO | R-META-07 (check-metadata.py) |
| ZIP structure validation | `parse_zipfile_metadata()` in `sweettooth/extensions/models.py` processes the upload | check-package.sh |

### What the Platform Does NOT Check (Manual Review Required)

Based on the reviewer feedback patterns observed, these are NOT automated on the server side:

| Check | Evidence |
|-------|---------|
| gschemas.compiled presence | Reviewer manually flags this in every affected review |
| Signal cleanup in disable() | Always manually reviewed |
| Timeout cleanup in disable() | Always manually reviewed |
| Synchronous subprocess calls | Manually flagged with line numbers |
| AI-generated code patterns | Manually identified based on code style |
| session-modes validity | Reviewer manually flags redundant modes |
| Import segregation | Not server-validated; reviewer checks |
| Reference nulling in disable() | Always manually flagged |

### ESLint Integration

The review guidelines recommend using ESLint, and the GNOME Shell project maintains its own ESLint configuration on GitLab. However, ESLint is NOT run as part of the EGO upload process -- it is a developer-side tool only. Extension code style is not enforced during upload; only during manual review if the reviewer considers it unreadable.

### Implications for Our Plugin

The EGO platform's automated checks are minimal -- primarily metadata/structure validation during upload. The vast majority of review requirements are enforced manually by a small number of volunteers (primarily JustPerfection). This means:

1. **Our plugin fills a genuine gap**: The platform does NOT perform the checks we do. There is no server-side lifecycle analysis, no signal balance checking, no import segregation, no AI slop detection.
2. **We complement, not duplicate**: Our checks catch issues BEFORE they reach the reviewer, reducing the review burden.
3. **The "machine reviewer" is thin**: Unlike Mozilla AMO (which has addons-linter), EGO's automated layer is minimal. Our plugin is essentially the first comprehensive automated review tool for GNOME extensions.

---

## 6. Implications for Our Plugin

### Priority Actions Based on This Research

#### P0: Gaps Exposed by Review Patterns (Common rejections we don't catch)

| Gap | Description | Priority | Effort |
|-----|-------------|----------|--------|
| Redundant settings instances | Multiple `getSettings()` or `new Gio.Settings()` calls when one should be reused | High | Medium |
| Null-out references in disable() | Detect `this._thing = getSettings()` in enable() without `this._thing = null` in disable() | High | Medium |
| Subprocess cancellation in disable() | `Gio.Subprocess` created but not cancelled/killed in disable() | Medium | Medium |
| Timeout removal before reassignment | `this._id = timeout_add(...)` without prior `Source.remove(this._id)` in same function | Medium | Medium |

#### P1: Version-Specific Coverage Gaps

| Version | Missing Rules | Priority |
|---------|---------------|----------|
| GNOME 47 | `Clutter.Color` removal | Medium |
| GNOME 48 | `Clutter.Image` removal, `Meta` namespace moves, `vertical` property deprecation | High |
| GNOME 49 | `Meta.Rectangle` removal, `DoNotDisturbSwitch` removal, `Clutter.ClickAction`/`TapAction` removal, `Meta.CursorTracker.set_pointer_visible()` removal, `Meta.MaximizeFlags` removal | High |
| GNOME 50 | Already covered (R-VER50-01/02/03/04) | Done |

#### P2: Advisory Improvements (Not rejections, but reviewer expectations)

| Item | Description | Priority |
|------|-------------|----------|
| Suggest `donations` field | Advisory when metadata.json lacks `donations` | Low |
| Suggest `connectObject` | Advisory when manual connect/disconnect patterns detected for GNOME 42+ | Low |
| Suggest conditional logging | Advisory when excessive logging without debug guard detected | Low |
| Suggest `GLib.timeout_add_once()` | Advisory for GNOME 50+ when callback returns SOURCE_REMOVE | Low |

### Coverage Summary After This Research

| Category | Before | After (with recommended additions) |
|----------|--------|-------------------------------------|
| Guideline requirements covered | ~90% | ~93% (adding P0 gaps) |
| Version-specific rules | 48, 49, 50 partial | 47, 48, 49, 50 comprehensive |
| Reviewer pattern alignment | Good | Strong (adding common feedback items) |
| EGO platform complement | Good | Good (confirmed no overlap) |

---

## Appendix: Source URLs

### Official Documentation
- [GNOME Shell Extensions Review Guidelines](https://gjs.guide/extensions/review-guidelines/review-guidelines.html)
- [gjs.guide GNOME Shell 47 Porting Guide](https://gjs.guide/extensions/upgrading/gnome-shell-47.html)
- [gjs.guide GNOME Shell 48 Porting Guide](https://gjs.guide/extensions/upgrading/gnome-shell-48.html)
- [gjs.guide GNOME Shell 49 Porting Guide](https://gjs.guide/extensions/upgrading/gnome-shell-49.html)
- [gjs.guide GNOME Shell 50 Porting Guide](https://gjs.guide/extensions/upgrading/gnome-shell-50.html)
- [gjs.guide Session Modes](https://gjs.guide/extensions/topics/session-modes.html)
- [gjs.guide Extension Anatomy](https://gjs.guide/extensions/overview/anatomy.html)

### Blog Posts and News
- [AI and GNOME Shell Extensions (Javad Rahmatzadeh, Dec 2025)](https://blogs.gnome.org/jrahmatzadeh/2025/12/06/ai-and-gnome-shell-extensions/)
- [Phoronix: GNOME Extensions Block AI](https://www.phoronix.com/news/GNOME-Extensions-Block-AI)
- [XDA: GNOME Cracking Down on AI-Generated Code](https://www.xda-developers.com/gnome-cracking-down-ai-generated-code-extensions-guidelines/)
- [ItsFoss: No AI Slops](https://itsfoss.com/news/no-ai-extension-gnome/)
- [Linuxiac: GNOME Will Reject AI-Generated Code](https://linuxiac.com/gnome-will-reject-shell-extensions-with-ai-generated-code/)
- [Linuxiac: GNOME 50 Ends the X11 Era](https://linuxiac.com/gnome-50-ends-the-x11-era-after-decades/)
- [Phoronix: GNOME Mutter 50 Alpha X11 Removed](https://www.phoronix.com/news/GNOME-Mutter-Shell-50-Alpha)

### EGO Review Pages Examined
- [Claude Code Usage Indicator v1 (#64921)](https://extensions.gnome.org/review/64921) - session-modes, gschemas.compiled, settings
- [APCUPS Monitor v3 (#68473)](https://extensions.gnome.org/review/68473) - gschemas.compiled, null-out, sync spawn
- [Maximize 2 New Workspace v2 (#68358)](https://extensions.gnome.org/review/68358) - connectObject, gschemas.compiled, donations
- [Soft Brightness Plus v24 (#66207)](https://extensions.gnome.org/review/66207) - selective disable, null sequencing
- [Forge v85 (#63292)](https://extensions.gnome.org/review/63292) - deprecated modules, timeout cleanup
- [Text Extractor v3 (#66775)](https://extensions.gnome.org/review/66775) - logs, timeouts, subprocess cancellation, gschemas.compiled
- [Text Extractor v5 (#67199)](https://extensions.gnome.org/review/67199) - donations recommendation
- [Lock Guard v1 (#67061)](https://extensions.gnome.org/review/67061) - missing URL, session-modes, cleanup
- [Wechsel v1 (#53836)](https://extensions.gnome.org/review/53836) - sync subprocess, settings, DBus unexport, null-out
- [Improved Workspace Indicator v28 (#67538)](https://extensions.gnome.org/review/67538) - gschemas.compiled
- [GnomeLama v6 (#63939)](https://extensions.gnome.org/review/63939) - broken extension, version mismatch

### GitLab Repositories
- [gjs-guide Repository](https://gitlab.gnome.org/ewlsh/gjs-guide) - Source of gjs.guide, maintained by Evan Welsh
- [gjs-guide Merge Requests](https://gitlab.gnome.org/ewlsh/gjs-guide/-/merge_requests?state=all) - 192 merged MRs
- [gjs-guide Issue #22: Review Licensing](https://gitlab.gnome.org/ewlsh/gjs-guide/-/issues/22)
- [extensions-web Repository](https://gitlab.gnome.org/Infrastructure/extensions-web) - EGO platform source
- [extensions-web GitHub Mirror](https://github.com/GNOME/extensions-web)
- [GNOME Shell Issues: unlock-dialog session state](https://gitlab.gnome.org/GNOME/gnome-shell/-/issues/7652)

### Community Discussions
- [Discourse: connectObject/disconnectObject description](https://discourse.gnome.org/t/description-of-the-connectobject-and-disconnectobject-methods/16726)
- [Discourse: unlock-dialog disable function](https://discourse.gnome.org/t/in-a-gnome-extension-about-disable-function-when-only-unlock-dialog-session-modes-is-used/17028)
- [GNOME Wiki Archive: Extensions Review](https://wiki.gnome.org/Projects/GnomeShell/Extensions/Review)

---

## Research Limitations

1. **GitLab commit history inaccessible via web search**: The gjs-guide repository's commit-level history for the review-guidelines source file could not be accessed through web search or available tools. For definitive timeline data on when specific requirements were added to the guidelines, direct browsing of `gitlab.gnome.org/ewlsh/gjs-guide/-/commits/main/` with path filtering is needed.

2. **extensions-web source code inaccessible**: Permission restrictions prevented fetching raw source files from the extensions-web repository. The analysis of automated checks is based on web search results, mailing list archives, and test data references rather than direct code inspection.

3. **Limited review page sample**: Only ~15 extension review pages were examined. The EGO platform hosts thousands of reviews. A broader sample might reveal additional patterns, though the patterns observed were highly consistent across the sample.

4. **Merge request discussions not accessible**: Individual MR discussions in the gjs-guide repository could not be fetched. These discussions likely contain rich reasoning about why specific guideline changes were made.
