# Yooti — Prompt Guide
# The exact prompt to use at every pipeline stage
# Agent: Claude Code · Project: yooti-dashboard

---

## How to use this guide

Copy the prompt for your current stage and paste it into Claude Code.
You do not need to explain the pipeline — the agent reads CLAUDE.md.
Shorter prompts are better. If the prompt is long, something is
missing from CLAUDE.md — fix it there, not in the prompt.

---

## PHASE 2 — Story decomposition (plan files only)

```
Proceed to Phase 2 for [DASH-ID].
```

For multiple stories:
```
Proceed to Phase 2 for DASH-001, DASH-002, DASH-003.
```

What the agent produces: .plan.md files in .agent/plans/
What it does NOT produce: any code, tests, or implementation
When to use: after G1 approval, before G2 review

---

## PHASE 4 — Code generation

```
Proceed to Phase 4 for [DASH-ID].
```

For multiple stories in dependency order:
```
Proceed to Phase 4 for all approved stories in dependency order.
```

What the agent produces: code, tests, evidence package, PR
Prerequisite: G2 gate must be signed first
When to use: after G2 approval

---

## PHASE 5 — Evidence package (if agent skipped it)

```
Phase 5 was skipped for [DASH-ID].
Generate the evidence package in .agent/evidence/[DASH-ID]/
Read the coverage from services/api_python/coverage.json
Do not re-run tests — just generate the evidence files and PR body.
```

When to use: if the agent opened a PR without generating evidence

---

## PHASE 2 — Regenerate plans (if plans are wrong)

```
The plans for [DASH-ID] are incorrect.
Delete .agent/plans/[DASH-ID]-*.plan.md
Re-read .claude/CLAUDE.md decomposition rules.
Regenerate plans — split by layer not by AC.
Do not write any code.
```

When to use: if the architect rejects plans at G2

---

## CORRECTION — Fix a specific issue mid-generation

```
Read .agent/corrections/[TASK-ID]-[timestamp].md
Apply the correction to [TASK-ID].
Re-run the quality loop.
Do not change anything outside the correction scope.
```

When to use: after running yooti correct:inject

---

## ESCALATION — Resolve a blocked task

```
Read .agent/escalations/[TASK-ID]-[type].md
The escalation has been resolved: [brief description of resolution]
Continue with [TASK-ID].
```

When to use: after resolving an agent escalation

---

## CONSTITUTION VIOLATION — Fix a specific violation

```
The code audit for [DASH-ID] found violations.
Read .agent/evidence/[DASH-ID]/code-audit.md
Fix each violation listed.
Re-run the quality loop.
Regenerate the evidence package.
Do not change any tests.
```

When to use: if code-audit.md shows violations before PR

---

## COVERAGE — Fix low coverage

```
Coverage for [DASH-ID] is below 80%.
Run: pytest tests/unit/ --cov=src --cov-report=term-missing
Add tests for every uncovered line in business logic files.
Do not add coverage exclusions without architect approval.
```

When to use: if coverage gate fails at G4

---

## SPRINT START — Beginning of a new sprint

Step 1 — PM approves stories:
```
yooti story:approve --all
```

Step 2 — Start sprint:
```
yooti sprint:start
```

Step 3 — Generate plans:
```
Proceed to Phase 2 for all new stories in this sprint.
```

Step 4 — Architect reviews:
```
yooti plan:review DASH-NNN
```

Step 5 — Generate code:
```
Proceed to Phase 4 for all approved stories in dependency order.
```

---

## SPRINT END — Closing a sprint

Step 1 — QA review each story:
```
yooti qa:review DASH-NNN
```

Step 2 — Sprint report:
```
yooti sprint:report
```

Step 3 — Retrospective:
```
yooti sprint:retro
```

---

## DAILY — Standup

```
yooti sm:standup
```

---

## COMMON MISTAKES AND FIXES

| Symptom | Cause | Fix |
|---------|-------|-----|
| Agent writes code during Phase 2 | CLAUDE.md Phase 2 section missing | Add Phase 2 section to CLAUDE.md |
| Agent creates one task per AC | Decomposition rules not read | Re-run Phase 2 with explicit instruction to re-read rules |
| PR opened without evidence package | Phase 5 skipped | Use Phase 5 regeneration prompt above |
| Coverage shows stale 76% | Evidence not regenerated after fix | Use evidence regeneration prompt |
| Agent touches out-of-scope files | Scope section unclear in plan | Amend plan with yooti plan:amend, re-run task |
| Constitution violations found | Agent did not read constitutions | Use violation fix prompt above |
| Docker ports mismatch | .env and docker-compose not in sync | Read docker.md constitution, fix both files |
