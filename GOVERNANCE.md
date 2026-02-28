# Governance

## Rule Authority

Every rule in ego-lint must be grounded in at least one of:

1. **Official guidelines** — [gjs.guide](https://gjs.guide) review guidelines, GNOME Shell documentation
2. **Observed reviewer behavior** — real EGO review decisions (cite the review or pattern)
3. **GNOME Shell source changes** — API removals, renames, or deprecations tracked via GitLab

Rules without a citation can be proposed but will be marked advisory until validated against real extensions.

## Rule Lifecycle

- **New rules start as advisory** (WARN) unless they correspond to a documented MUST requirement
- Rules are **upgraded to blocking** (FAIL) after validation confirms no false positives across multiple real extensions
- Rules are **downgraded or removed** if they produce persistent false positives that can't be resolved
- Rules are **deprecated** (not removed) when the GNOME versions they apply to are no longer supported

## Severity Disputes

If you disagree with a rule's severity:

1. Open an issue with the rule ID, your reasoning, and an example
2. If you're an EGO reviewer, note that — reviewer experience carries weight
3. We'll validate against the regression baseline and adjust if warranted

Blocking rules that produce false positives on well-written extensions are treated as bugs.

## Community Input

- **Anyone** can propose rules via issue or PR
- **EGO reviewers** are encouraged to contribute patterns from real rejections — these carry the most weight
- **Disagreements** are resolved by checking against official guidelines first, then observed reviewer behavior

## Co-maintainers

The project is actively looking for 2–3 EGO reviewers as co-maintainers to:

- Review and approve rule changes
- Validate heuristic checks against real review experience
- Help prioritize which rejection patterns to automate next

### Onboarding path

1. **Contribute 2–3 rules or fixes** — pattern rules, false-positive reports, or severity adjustments
2. **Discuss write access** — after contributions demonstrate familiarity with the rule system and testing conventions
3. **Responsibilities**: rule PR review, severity validation against real extensions, false-positive triage

Timeline: typically 2–4 weeks from first contribution to write access discussion.

If you're an active EGO reviewer and interested, open an issue or reach out.

## Decision Process

For rule changes:
1. Proposer opens issue or PR with citation
2. At least one co-maintainer (or the project lead) reviews
3. New rules land as advisory; severity upgrades require test validation
4. Changes that affect blocking rules require running the full test suite (378+ assertions) and regression baseline
