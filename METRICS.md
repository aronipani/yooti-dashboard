# Yooti Dashboard — Metrics Reference

This document describes every metric displayed in the Yooti Dashboard — what it measures, how it is computed, where the source data comes from, and what action to take when it signals a problem.

For architecture details see:
- [`docs/ARCH-DASHBOARD.md`](ARCH-DASHBOARD.md) — DynamoDB schema, Lambda design, API contract
- [`docs/ARCH-GITHUB-AGENT.md`](ARCH-GITHUB-AGENT.md) — GitHub Metrics Enrichment Agent (Sprint 2)

---

## How metrics flow into the dashboard

```
.agent/ pipeline artifacts
        │
        ▼
aggregate-metrics.py          reads gate files, evidence packages,
                               audit logs, escalation files
        │
        ▼
POST /metrics/ingest           validates payload, writes to DynamoDB,
                               triggers insight engine
        │
        ▼
DynamoDB (yooti-metrics)       single-table design, no Scan operations
        │
        ▼
GET /metrics/current           single GetItem on CURRENT#SNAPSHOT
        │
        ▼
React dashboard                6 tabs, React Query hooks, auto-refresh
```

The `aggregate-metrics.py` script is the bridge between the Yooti pipeline and the dashboard. It reads files the agent and humans have written during story delivery, computes derived metrics, and posts them to the ingest endpoint. It runs at the end of each sprint (or on demand).

The ingest endpoint does two things atomically: it writes the sprint data to DynamoDB and updates the `CURRENT#SNAPSHOT` record which is what the dashboard reads on every page load via a single `GetItem` — no Query, no Scan.

---

## Metric Definitions

### Productivity Metrics

---

#### Stories Shipped

**What it is:** The count of stories that reached Gate G5 (release approval) during the current sprint.

**How it is computed:**
```
stories_shipped = count of stories where
  .agent/gates/{story_id}-G5-approved.md exists
  AND gate date falls within sprint window
```

**Source:** Gate files in `.agent/gates/`

**Why it matters:** The primary delivery velocity metric. Unlike story points (which are estimates), stories shipped is a binary fact — a story either crossed all 5 gates or it didn't.

**What to do if low:** Check the Story Drill-down tab to see which gate stories are stuck at. G2 delays = architect bandwidth. G3 delays = PR review backlog. G4 delays = evidence package failures.

---

#### Cycle Time

**What it is:** Average elapsed time from Gate G1 approval (PM sign-off) to Gate G3 merge (PR merged) across all stories completed this sprint.

**How it is computed:**
```
cycle_time_hours = mean(
  G3_timestamp - G1_timestamp
  for each story where G3 exists
)
```

**Source:** Timestamps in `.agent/gates/{story_id}-G1-approved.md` and `G3-approved.md`

**Why it matters:** Cycle time is the end-to-end measure of how fast a story moves from approved requirement to merged code. It includes all human wait time and all agent execution time. A rising cycle time with stable story count usually means gate bottlenecks, not agent slowness.

**Benchmark:** For S/M complexity stories with a well-tuned pipeline, cycle time should be under 4 hours. XL stories may take 24+ hours legitimately.

---

#### Completion %

**What it is:** Percentage of stories committed to the sprint that reached COMPLETE status.

**How it is computed:**
```
completion_pct = (stories_complete / stories_committed) * 100
```

**Source:** `.agent/requirements/` (committed) vs `.agent/gates/` (complete)

**Why it matters:** Measures sprint predictability. A team consistently delivering 90%+ completion is a team with well-sized stories and a reliable pipeline.

**What to do if low:** Below 70% for two sprints = stories are too large. Break XL and L stories into smaller pieces before sprint start.

---

#### Phase Breakdown

**What it is:** Average time spent in each pipeline phase across all stories in the sprint.

**Phases measured:**

| Phase | What it covers |
|-------|---------------|
| Requirements | G1 sign-off to Phase 2 start |
| Planning | Phase 2 (plan generation) to G2 sign-off |
| Coding | G2 sign-off to Phase 5 complete |
| Review | Phase 5 complete to G3 merge |
| QA | G3 merge to G4 sign-off |

**Source:** Phase transition events in `.agent/logs/{story_id}.log.json`

**Why it matters:** The phase breakdown reveals where the pipeline is slow. If Coding dominates, stories may need smaller tasks. If Review dominates, the team needs to prioritise PR reviews. If Planning dominates, the architect G2 process is the bottleneck.

---

#### Human Wait vs Agent Exec

**What it is:** Total hours humans spent waiting at gates vs total hours the agent spent executing, across all stories in the sprint.

**How it is computed:**
```
human_wait_hours = sum of time between:
  - Phase 2 complete → G2 sign-off
  - Phase 5 complete → G3 merge
  - G3 merge → G4 sign-off

agent_exec_hours = sum of time between:
  - G2 sign-off → Phase 5 complete (phases 3+4+5)
```

**Source:** Gate file timestamps + audit log phase events

**Why it matters:** This is the central Yooti value metric. If human wait > agent exec, the bottleneck is human gates, not the agent. A healthy pipeline has agent exec dominating — the agent is doing most of the work and humans are reviewing quickly.

**Target ratio:** Agent exec should be 3-5x human wait for a Stage 3 pipeline.

---

### Quality Metrics

---

#### Code Coverage

**What it is:** Two values — overall coverage across all files touched this sprint, and new code coverage for code written this sprint specifically.

**How it is computed:** Read directly from `.agent/evidence/{story_id}/coverage-summary.json` which the agent writes during Phase 5. Values are averaged across all stories.

**Thresholds (configurable in `yooti.config.json`):**
```json
"coverage_overall": 75,
"coverage_new_code": 80
```

**Why it matters:** Overall coverage measures the health of the existing codebase. New code coverage measures whether the agent is writing adequate tests for the code it generates. New code coverage is held to a higher standard because the agent has full control over what it writes — there's no legacy excuse.

---

#### Mutation Score

**What it is:** The percentage of code mutations (deliberate bugs) that were caught by the test suite. Run by Stryker (TypeScript) or mutmut (Python).

**How it is computed:** Read from `.agent/evidence/{story_id}/mutation-score.json`

**Threshold:** >= 85% triggers a warning. Below 70% is a signal the tests are not actually testing behaviour.

**Why it matters:** Coverage tells you lines were executed. Mutation score tells you whether the tests would catch a bug on those lines. An agent can achieve 100% coverage with tests that make no meaningful assertions. Mutation score catches this.

**What to do if low:** Low mutation score + high coverage = the agent is writing tests that call code but don't assert outcomes. Add `yooti test:require` entries with specific Given/When/Then scenarios before Phase 4.

---

#### Regression Rate

**What it is:** Count of tests that were passing before the sprint and are now failing after the sprint's code was merged.

**How it is computed:**
```
regression_rate = count(newly_failing)
from .agent/evidence/{story_id}/regression-diff.json
```

**Threshold:** Zero tolerance. Any regression blocks Gate G4.

**Why it matters:** The agent must never break existing tests. The regression baseline captured at `yooti sprint:start` is the reference point. If any previously passing test fails after a story's code is merged, the story cannot proceed to G4 until it's fixed.

---

#### Constitution Pass %

**What it is:** Percentage of stories where the code audit found zero violations.

**How it is computed:**
```
constitution_pass_pct = (stories_with_zero_violations / total_stories) * 100
```

**Source:** `.agent/evidence/{story_id}/code-audit.md` written by the agent during Phase 5 Step 6b.

**What the audit checks:**
- No hardcoded secrets or API keys
- Parameterised SQL queries only
- Auth middleware on protected endpoints
- Type annotations on all functions
- No bare except/empty catch blocks
- No debug print/console.log statements
- Test file exists for every source file
- axe-core test in every React component test

**Why it matters:** The code audit is the agent self-auditing against the constitutions it was given. A 100% pass rate means the agent is following the architectural rules. Violations below 100% are flagged for architect review.

---

#### Security Findings

**What it is:** Count of HIGH and CRITICAL findings from Snyk (dependency scan) and Semgrep (code scan).

**Source:** `.agent/evidence/{story_id}/security-scan.json`

**Threshold:** Zero tolerance for HIGH/CRITICAL. Blocks Gate G4.

**Why it matters:** The agent installs dependencies and writes code. Both surfaces can introduce vulnerabilities. Snyk catches known CVEs in packages. Semgrep catches code patterns like SQL injection, hardcoded credentials, and insecure defaults.

---

### Agent Efficiency Metrics

---

#### Iterations per Story

**What it is:** Average number of self-heal loop iterations the agent ran across all tasks in the sprint.

**How it is computed:**
```
iterations_per_story = mean(
  count(ITERATION_START events)
  per story in audit log
)
```

**Source:** `.agent/logs/{story_id}.log.json` — `ITERATION_START` events

**Benchmark:**
- 1-2 iterations = excellent (agent got it right first or second try)
- 3 iterations = acceptable
- 4-5 iterations = stories may be too complex or constitutions need tightening
- Hitting the 5-iteration limit = escalation written, human intervention required

**Why it matters:** High iteration counts are expensive — each iteration is an LLM call. More importantly, high iterations mean the agent is fighting the codebase. The root causes are almost always: stories too large, constitutions too vague, or missing context files.

---

#### Escalation Rate

**What it is:** Percentage of tasks that wrote an escalation file during Phase 4.

**How it is computed:**
```
escalation_rate = (tasks_with_escalations / total_tasks) * 100
```

**Source:** `.agent/escalations/` directory — one file per escalation

**Threshold:** > 10% triggers a CRITICAL alert.

**Escalation types and their causes:**

| Type | Meaning | Fix |
|------|---------|-----|
| `SCOPE_ERROR` | Agent needed a file not in its plan | Improve plan decomposition at G2 |
| `ENV_ERROR` | Missing environment variable or service | Add to .env.example, update preflight |
| `AMBIGUITY` | AC was unclear or contradictory | PM needs to clarify the story |
| `ARCH_ERROR` | Architectural constraint could not be satisfied | Architect needs to revise the plan |
| `IMPORT_ERROR` | Package not in requirements.txt | Add dependency, acknowledge escalation |

**Why it matters:** Escalation rate is the leading indicator of story and plan quality. A sprint with 0 escalations means stories were well-specified, plans were sound, and the agent had everything it needed. Escalation rate > 10% means the team needs to invest more in Phase 2 (planning) and G2 (architect review).

---

#### Correction Rate

**What it is:** Percentage of tasks that received a correction injection via `yooti correct:inject` during Phase 4.

**Source:** `.agent/corrections/` directory

**Why it matters:** Corrections are human interventions mid-generation. They're necessary but they represent a failure in the upfront process — either the plan was wrong, the constitutions were incomplete, or the agent misunderstood the scope. High correction rates point to gaps in CLAUDE.md or constitution files.

---

#### Self-Heal Success Rate

**What it is:** Percentage of quality loop failures (lint, type check, test failures) that the agent resolved without human intervention, within the 5-iteration limit.

**How it is computed:**
```
self_heal_success = (tasks_resolved_autonomously / tasks_with_failures) * 100
```

**Why it matters:** This measures the agent's ability to diagnose and fix its own mistakes. A high self-heal rate means the quality loop is working as designed. A low rate means the agent is hitting problems it can't solve — usually type errors in complex TypeScript or pytest fixture issues in Python.

---

### Value Metrics

---

#### Time Saved

**What it is:** Estimated developer hours saved by agent automation vs a developer doing the same work manually.

**How it is computed:**
```
time_saved = (estimated_manual_hours - agent_exec_hours)

estimated_manual_hours = story_points * hours_per_point_benchmark
hours_per_point_benchmark = 4 hours (configurable)
```

**Why it matters:** This is the headline ROI metric for Yooti. For a design partner conversation: if the agent delivered 40 story points in a sprint at 4 hours/point benchmark, that's 160 estimated manual hours. If agent exec was 20 hours total, time saved = 140 hours.

**Important caveat:** This is an estimate based on a configurable benchmark. Actual savings depend on story complexity, team skill, and codebase familiarity. Use it as a directional indicator, not a precise measurement.

---

#### Commitment Rate

**What it is:** Percentage of stories committed to the sprint that were delivered.

**Target:** >= 80% consistently. Below 70% for two sprints = systemic sizing problem.

---

#### Delivery Trend

**What it is:** Sprint-over-sprint velocity trend shown as a sparkline. Plots stories shipped per sprint over the last N sprints.

**Source:** `TREND#velocity#SPRINT#{num}` records in DynamoDB, populated by the trend calculator in the ingest pipeline.

**Why it matters:** A rising trend means the pipeline is maturing — the team is getting better at writing stories, the agent is getting better context, and gates are moving faster. A flat or declining trend after sprint 3 indicates a systemic bottleneck that needs architectural attention.

---

### DORA Metrics

DORA (DevOps Research and Assessment) metrics are the industry standard for measuring software delivery performance. The Yooti dashboard computes them from pipeline data.

---

#### Deployment Frequency

**What it is:** How often code is deployed to production. Measured as deployments per day/week/month.

**DORA bands:**
- Elite: On demand (multiple times per day)
- High: Once per day to once per week
- Medium: Once per week to once per month
- Low: Less than once per month

**Source:** G5 gate timestamps (release approvals)

**Yooti impact:** Each story that passes G5 is a potential production deployment. High story throughput + fast G5 approval = high deployment frequency.

---

#### Lead Time for Changes

**What it is:** Time from first commit on a feature branch to that code running in production.

**How it is computed:**
```
lead_time = G5_timestamp - first_commit_timestamp
```

**DORA bands:**
- Elite: < 1 hour
- High: 1 day to 1 week
- Medium: 1 week to 1 month
- Low: > 1 month

**Yooti impact:** The agent eliminates the largest component of lead time — writing code. Lead time in a Yooti pipeline is dominated by human gate review time, not coding time.

---

#### Change Failure Rate

**What it is:** Percentage of deployments that result in a degraded service, requiring a hotfix or rollback.

**How it is computed:** Tracked via incident/rollback records. In the current RI this is manually logged.

**DORA bands:**
- Elite: 0-5%
- High: 5-10%
- Medium: 10-15%
- Low: > 15%

**Yooti impact:** The quality gates (coverage, security scan, code audit, regression diff) exist specifically to keep change failure rate near zero. A spike in change failure rate is a signal that gates were bypassed or thresholds were set too low.

---

#### Time to Restore

**What it is:** Mean Time to Recovery (MTTR) — how long it takes to restore service after a production incident.

**DORA bands:**
- Elite: < 1 hour
- High: < 1 day
- Medium: 1 day to 1 week
- Low: > 1 week

**Yooti impact:** Not directly impacted by the pipeline, but the audit trail (gate files, evidence packages, code audit) provides forensic context that speeds up incident diagnosis.

---

## Configuring Thresholds

All quality thresholds are configurable in `yooti.config.json`:

```json
"quality_gates": {
  "coverage_overall": 75,
  "coverage_new_code": 80,
  "mutation_score_warn": 85,
  "lint_errors": 0,
  "type_errors": 0,
  "security_critical": 0,
  "security_high": 0
}
```

These values are read by `yooti qa:review` during Gate G4. Raising thresholds increases quality assurance. Lowering them reduces false blocks on early-stage projects.

The `qa:review` command enforces these thresholds as hard gates — any story that fails a hard gate cannot proceed to G5 until the issue is resolved.

---

## Further Reading

- [`docs/ARCH-DASHBOARD.md`](ARCH-DASHBOARD.md) — Full architecture: DynamoDB single-table design, all 10 access patterns, Lambda handler design, SAM template structure, and Gate G2 architectural decisions
- [`docs/ARCH-GITHUB-AGENT.md`](ARCH-GITHUB-AGENT.md) — GitHub Metrics Enrichment Agent: LangGraph graph design, 8 node definitions, GitHub API rate limit handling, zero-LLM-call architecture
