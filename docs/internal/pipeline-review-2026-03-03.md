# Pipeline Efficiency Review (2026-03-03)

> **Source**: Full ego-submit 3-agent parallel run on `hara-hachi-bu@ZviBaratz`
> (18 JS files, ~5,465 non-blank lines). Run by Claude Opus 4.6 in a fresh
> session with no prior reviewer-project context.
>
> **Context**: Previous rounds (F-001 through F-021) fixed rule false positives
> and added automation scripts. This review focuses on **pipeline-level
> efficiency** — where agents spend time on work that's already automated or
> redundant, and how the orchestration can be tightened.

## Run Metrics

| Agent | Scope | Duration | Tool Uses | Tokens |
|-------|-------|----------|-----------|--------|
| Agent 1 | ego-lint + package validation | 79s | 13 | 32K |
| Agent 2 | Lifecycle + signals + security | 381s | 42 | 143K |
| Agent 3 | Quality + AI patterns + metadata | 255s | 91 | 152K |
| **Total** | | **381s** (wall) | **146** | **327K** |

## Results

- ego-lint: 205 PASS, 0 FAIL, 9 WARN, 23 SKIP
- ego-review: 0 blocking, 1 advisory (private API — documented)
- AI patterns: 1/46 triggered (pkexec — justified)
- Disclosure matrix: All 6 capabilities OK
- Package: 100 KB, 34 files, clean
- **Verdict: READY TO SUBMIT**

WARN count increased from 7 (2026-03-02 run) to 9. The two new WARNs are
`R-VER48-04b` (×2) for the `vertical` property kept for GNOME 46 compat —
this was previously a single deduplicated WARN but now appears to fire twice
(lines 100 and 909 of quickSettingsPanel.js). Investigate whether
`deduplicate: true` is still working for this rule.

---

## Finding F-022: Agent 2 rebuilds the resource graph manually

**Impact**: ~200s of Agent 2's 381s total

**Problem**: ego-review Phase 3 (Signal & Resource Audit) instructs the agent
to grep for `connect(`, `timeout_add`, `FileMonitor`, and D-Bus proxy creation,
then cross-reference each against destroy methods. Agent 2 spent 42 tool uses
doing this — but `build-resource-graph.py` (run in Phase 2) already produces
all of this data.

The `--summary` flag (F-018) was added to make the graph output human-readable,
but the Phase 3 instructions still say to independently grep for every resource
type. The agent dutifully follows the instructions and re-discovers what the
graph already reported.

**Root cause**: Phase 3 instructions in `skills/ego-review/SKILL.md` were not
updated after F-018 (resource graph summary) was implemented. The instructions
still describe a manual audit workflow.

**Fix**: Rewrite Phase 3 in `skills/ego-review/SKILL.md`:

```markdown
### Phase 3: Signal & Resource Audit

1. Review the resource graph summary from Phase 2 (if 0 orphans and
   complete ownership, Phase 3 can be abbreviated)
2. Spot-check: pick 2-3 resource entries from the graph and verify
   by reading the cited file:line that create/destroy are correctly
   paired
3. Check for resource types the graph may miss:
   - GSettings connections (`.connect('changed::...')` vs
     `.disconnectObject()`)
   - Custom cleanup methods (`_cleanup()`, `_teardown()`, `_clear()`)
   - Login manager / D-Bus signal connections via `connectSignal()`
     (not `connectObject()`)
4. Only do a full manual grep if the graph reports orphans or
   incomplete ownership
```

This changes Phase 3 from "rebuild from scratch" to "verify and supplement,"
cutting Agent 2's work roughly in half.

**Status**: Open
**Priority**: P0
**Effort**: Small (SKILL.md edit only)

---

## Finding F-023: Agent 3 re-checks AI patterns already covered by Tier 1/2

**Impact**: ~40-50 of Agent 3's 91 tool uses

**Problem**: Despite F-021 adding `**Automated:**` fields to the AI slop
checklist, Agent 3 still searched every JS file for each of the 46 items.
The checklist marks items as automated, but the Phase 5a instructions in
`skills/ego-review/SKILL.md` don't tell the agent to skip them.

Current Phase 5a instruction:
> 1. For each checklist item, search the extension source for the
>    described pattern

This is unconditional — the agent checks all 46 items regardless of
automation status.

**Root cause**: The ego-review SKILL.md Phase 5a instructions were not updated
to reference the automation mapping added in F-021.

**Fix**: Update Phase 5a step 1:

```markdown
1. For each checklist item:
   - If marked `**Automated: Yes**` → use ego-lint's result (from
     Phase 0) instead of re-searching. Only verify if ego-lint
     reported a finding for that check.
   - If marked `**Automated: No**` or `**Automated: Partial**` →
     search the extension source for the described pattern.
```

**Status**: Open
**Priority**: P0
**Effort**: Small (SKILL.md edit only)

---

## Finding F-024: check-disclosures.py doesn't cover the full disclosure matrix

**Impact**: Agent 3 manually grepped for all 6 capabilities

**Problem**: F-012 added `check-disclosures.py`, but it only covers clipboard
and network. The ego-submit readiness report requires a 6-capability matrix
(clipboard, network, pkexec, subprocess, private API, file I/O). Agent 3 had
to manually grep for the other 4 capabilities and cross-reference against
metadata.json.

**Fix**: Extend `check-disclosures.py` to cover all 6 capabilities:

| Capability | Detection Pattern | Disclosure Check |
|------------|-------------------|------------------|
| Clipboard | `St.Clipboard` | "clipboard" in metadata description |
| Network | `Soup.Session`, `Soup.Message` | "network" in metadata description |
| pkexec | `pkexec` in helper.js-reachable code | "pkexec" or "polkit" in metadata description |
| Subprocess | `Gio.Subprocess`, `GLib.spawn` | "subprocess" or command name in metadata |
| Private API | `_indicators`, `_proxy`, `_getMenuItems`, etc. | "private" or "private API" in metadata |
| File I/O | `Gio.File` outside GSettings context | "file" or "sysfs" or "reads" in metadata |

Output format (pipe-delimited, consistent with other check scripts):
```
PASS|disclosure/clipboard|Found in code, disclosed in metadata
WARN|disclosure/subprocess|Found in code (lib/helper.js:134), NOT disclosed in metadata
PASS|disclosure/network|Not found in code
```

This eliminates ~15 of Agent 3's tool uses.

**Status**: Open
**Priority**: P1
**Effort**: Medium (extend existing script)

---

## Finding F-025: build-resource-graph.py should output the resource tracking table

**Impact**: Agent 2 manually formatted the resource tracking table

**Problem**: The readiness report template includes a resource tracking table:

```
| Resource | File:Line (create) | File:Line (destroy) | Owner | Status |
```

Agent 2 ran `build-resource-graph.py`, parsed its output, then manually
constructed this table. The `--summary` flag (F-018) outputs counts and orphan
status, but not the per-resource table.

**Fix**: Add a `--format=table` flag that outputs the markdown table directly.
The graph JSON already contains all the data; this is purely a formatting
change.

```bash
python3 build-resource-graph.py --format=table /path/to/extension
```

Output:
```markdown
| Type | Name | File:Line (create) | File:Line (destroy) | Owner | Status |
|------|------|--------------------|---------------------|-------|--------|
| timeout | _scheduleTimerId | stateManager.js:870 | stateManager.js:1129 | StateManager | OK |
| signal | power-profile-changed | stateManager.js:181 | stateManager.js:1165 | StateManager | OK |
...
```

**Status**: Open
**Priority**: P1
**Effort**: Small (formatting-only change to existing script)

---

## Finding F-026: Parallel protocol runs ego-lint concurrently with review agents

**Impact**: Review agents can't use ego-lint results to avoid duplication

**Problem**: The current parallel protocol (F-016) splits work as:
- Agent 1: ego-lint + package validation
- Agent 2: ego-review lifecycle + signals + security
- Agent 3: ego-review quality + AI patterns + metadata

Since Agent 1 runs concurrently with Agents 2-3, the review agents have no
access to ego-lint results. The SKILL.md says "Agents 2-3 skip Phase 0 since
Agent 1 handles it" — but this means Agents 2-3 can't use ego-lint output to
avoid re-reporting issues or to skip automated AI pattern checks.

The deduplication is deferred to "report compilation time," but by then all
three agents have already done their full work. The savings from F-022 and
F-023 (use ego-lint results to skip manual checks) are incompatible with
fully concurrent execution.

**Fix**: Change the pipeline to a two-phase approach:

```
Phase A (sequential, ~30s):
  Run ego-lint.sh → capture full output

Phase B (parallel, ~3-4 min):
  Agent 1: ego-review lifecycle + signals + security
           (receives ego-lint output as context)
  Agent 2: ego-review quality + AI + metadata + disclosure + package
           (receives ego-lint output as context)
```

ego-lint runs in ~30s, so the sequential overhead is minimal. The benefit is
that both review agents can:
- Skip AI pattern items marked as automated (F-023)
- Abbreviate Phase 3 when resource graph shows 0 orphans (F-022)
- Avoid re-reporting ego-lint WARNs in their findings
- Use code metrics from ego-lint output instead of computing them

This also simplifies from 3 agents to 2, reducing orchestration overhead.

**Status**: Open
**Priority**: P1
**Effort**: Medium (SKILL.md rewrite of parallel protocol)

---

## Finding F-027: R-VER48-04b deduplicate regression

**Impact**: 1 extra WARN (cosmetic)

**Problem**: `R-VER48-04b` has `deduplicate: true` but fired twice for
`quickSettingsPanel.js` (lines 100 and 909). Previous runs (2026-03-02) showed
this as a single WARN. Either the deduplication logic changed, or the rule's
scope/matching changed between runs.

**Fix**: Investigate whether `apply-patterns.py` deduplication is per-file or
per-rule. If per-rule, two hits in the same file should still be one WARN. If
per-file, this is correct behavior (two distinct locations). Clarify the
intended semantics.

**Status**: Open
**Priority**: P2
**Effort**: Small (investigate + fix if regression)

---

## Finding F-028: No mechanism to suppress known-justified warnings across runs

**Impact**: 9 WARNs reported every run, all previously documented

**Problem**: Every pipeline run on hara-hachi-bu produces the same 7-9 WARNs,
all of which have been analyzed and classified as correct/expected in the
findings registry. There's no way for the developer to acknowledge these and
have subsequent runs focus on *new* findings only.

This matters for iterative development: when fixing one issue and re-running
the pipeline, the signal-to-noise ratio is poor because the output is dominated
by known warnings.

**Fix**: Support an optional `.ego-lint-baseline.json` file in the extension
directory. Workflow:

```bash
# First run: save current warnings as baseline
ego-lint.sh --save-baseline /path/to/extension

# Subsequent runs: only show new warnings
ego-lint.sh /path/to/extension
# Output marks baseline items as [BASELINE] and new items as [NEW]
```

The baseline file stores rule IDs + file:line pairs. On subsequent runs:
- Warnings matching the baseline are tagged `[BASELINE]` (still shown, but
  visually distinct)
- New warnings are tagged `[NEW]` (highlighted)
- Summary line: "3 warnings (2 baseline, 1 new)"

This is the same pattern used by ESLint `--cache`, ruff baseline, and
mypy `--baseline-file`.

**Status**: Open
**Priority**: P2
**Effort**: Medium (ego-lint.sh + JSON baseline management)

---

## Summary

| ID | Finding | Priority | Effort | Type | Verified |
|----|---------|----------|--------|------|----------|
| F-022 | Phase 3 rebuilds resource graph manually | P0 | Small | SKILL.md | Yes (2026-03-03) |
| F-023 | Phase 5a re-checks automated AI patterns | P0 | Small | SKILL.md | Yes (2026-03-03) |
| F-024 | check-disclosures.py missing 4 capabilities | P1 | Medium | Script | Yes (2026-03-03) |
| F-025 | Resource graph should output markdown table | P1 | Small | Script | Yes (2026-03-03) |
| F-026 | Parallel protocol prevents ego-lint reuse | P1 | Medium | SKILL.md | Yes (2026-03-03) |
| F-027 | R-VER48-04b deduplicate regression | P2 | Small | Script | Yes (2026-03-03) |
| F-028 | No baseline suppression for known warnings | P2 | Medium | Script | N/A (deferred) |

**Estimated combined impact**: Implementing F-022 through F-026 would reduce
Agent 2 from 381s/42 uses to ~180s/20 uses and Agent 3 from 255s/91 uses to
~150s/50 uses, cutting total pipeline wall-clock time from ~6.3 min to ~3 min
and total token usage from ~327K to ~200K.

**Actual measured impact** (2026-03-03 verification run):
- Wall-clock: 381s → 241s (**-37%**, target was ~180s)
- Tokens: 327K → 264K (**-19%**, target was ~200K)
- Tool uses: 146 → 115 (**-21%**, target was ~70)
- Agents: 3 → 2 (Phase A sequential + Phase B parallel)

The improvements are significant but below the optimistic estimates. The lifecycle
audit (Agent 1) still takes ~184s because semantic verification of every `await`
guard requires reading many files — this is correct behavior (ego-lint's pattern
matching can miss complex guard structures). The quality audit (Agent 2) also
reads extensively for hallucinated API cross-referencing. These are genuine
value-add tasks that shouldn't be shortened.

**New finding from verification**: F-029 — `check-disclosures.py` private-api
regex too strict (see field-test-hara-hachi-bu.md).

---

## Relationship to Prior Findings

| New | Extends | Connection |
|-----|---------|------------|
| F-022 | F-018 | F-018 added `--summary` to the graph, but the SKILL.md wasn't updated to use it instead of manual grepping |
| F-023 | F-021 | F-021 added automation mapping to AI slop checklist, but the SKILL.md wasn't updated to skip automated items |
| F-024 | F-012 | F-012 added check-disclosures.py for clipboard+network, but the full 6-capability matrix wasn't implemented |
| F-025 | F-018 | F-018 added `--summary` (counts), but the per-resource table format is still missing |
| F-026 | F-016 | F-016 added parallel protocol, but the design prevents agents from using ego-lint results |
