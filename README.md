# Yooti Dashboard

Metrics dashboard for the Yooti autonomous SDLC pipeline. Displays sprint-level KPIs, quality metrics, DORA metrics, agent efficiency data, and per-story drill-down — all powered by real pipeline data from `.agent/` artifacts.

---

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/METRICS.md`](docs/METRICS.md) | Deep-dive metrics reference — definitions, computation, thresholds, and what to do when something looks wrong |
| [`docs/ARCH-DASHBOARD.md`](docs/ARCH-DASHBOARD.md) | Dashboard architecture — DynamoDB single-table design, all 10 access patterns, Lambda handler design, SAM template, Gate G2 decisions |
| [`docs/ARCH-GITHUB-AGENT.md`](docs/ARCH-GITHUB-AGENT.md) | GitHub Metrics Enrichment Agent — LangGraph graph design, 8 node definitions, GitHub API rate limiting, zero-LLM-call architecture |

---

## Product Overview

The Yooti Dashboard is the observability layer for teams running the Yooti autonomous SDLC pipeline. It answers the question every engineering manager, architect, and PM needs answered every sprint:

> **Is the agent actually delivering value — and where is the work getting stuck?**

The dashboard ingests data directly from the `.agent/` pipeline artifacts (gates, evidence packages, escalation logs, audit trails) and presents six views that cover the full delivery lifecycle: from story commitment to production, from human wait time to agent execution time, from code quality to business value delivered.

### Who uses it

| Role | Primary tab | What they need to know |
|------|------------|------------------------|
| Engineering Manager | Productivity, Value | Velocity, cycle time, stories shipped vs committed |
| Architect | Quality, Agent Efficiency | Coverage trends, escalation rate, constitution compliance |
| Scrum Master | DORA, Productivity | Deployment frequency, lead time, phase bottlenecks |
| PM | Value, Story Drill-down | Stories delivered, points completed, per-story gate timeline |

---

## Dashboard Screens

> For full metric definitions, computation logic, source data, thresholds, and remediation guidance see [`docs/METRICS.md`](docs/METRICS.md).

### Productivity Tab

The primary delivery health view. Shows whether the team is shipping at a sustainable pace and where time is being spent.

**Metrics displayed:**

| Metric | Description | Source |
|--------|-------------|--------|
| Stories Shipped | Count of stories reaching G5 this sprint | Gate files |
| Cycle Time | Average time from G1 approval to G3 merge | Gate timestamps |
| Completion % | Stories complete vs stories committed | Requirements + gates |
| Phase Breakdown | Time in Requirements / Planning / Coding / Review | Evidence packages |
| Human Wait vs Agent Exec | Hours spent waiting on humans vs agent running | Audit logs |

**What to look for:** High human wait time relative to agent exec time signals a gate bottleneck — usually G2 (architect review) or G3 (PR review). If coding phase dominates, stories may be too large.

---

### Quality Tab

Code health across the sprint. Tracks whether quality standards are being maintained as velocity increases.

**Metrics displayed:**

| Metric | Description | Threshold |
|--------|-------------|-----------|
| Code Coverage | Overall and new code coverage | >= 75% / 80% |
| Mutation Score | Stryker/mutmut score | >= 85% warn |
| Regression Rate | Newly failing tests vs baseline | 0 tolerance |
| Constitution Pass % | Stories with 0 code audit violations | Target 100% |
| Security Findings | Snyk critical/high findings | 0 tolerance |

**What to look for:** A declining mutation score alongside rising coverage is a signal the agent is writing low-value tests. Constitution pass % below 100% means architect annotations are not being followed.

---

### Agent Efficiency Tab

The core Yooti-specific view. Measures how well the autonomous pipeline is operating — not just whether code was shipped, but how efficiently the agent worked.

**Metrics displayed:**

| Metric | Description | What it signals |
|--------|-------------|-----------------|
| Iterations per Story | Average self-heal loop count | > 3 = stories too complex |
| Escalation Rate | % of tasks that wrote escalation files | > 10% = spec ambiguity |
| Correction Rate | % of tasks that received human corrections | Architect annotation gaps |
| Self-Heal Success | % of iterations that resolved without human | Agent constitution quality |
| G2 Review Time | Hours from sprint start to G2 sign-off | Architect availability |

**What to look for:** Escalation rate is the leading indicator of story quality. High escalation = stories were ambiguous or plans were underspecified. Correction rate > 10% means CLAUDE.md or constitutions need strengthening.

---

### Value Tab

Business delivery view. Connects technical metrics to outcomes — what was committed, what shipped, and is the trend improving?

**Metrics displayed:**

| Metric | Description |
|--------|-------------|
| Stories Shipped | Total stories completed this sprint |
| Points Completed | Story points delivered |
| Commitment Rate | Stories delivered vs stories committed (%) |
| Time Saved | Estimated developer hours saved by agent automation |
| Delivery Trend | Sprint-over-sprint velocity trend (sparkline) |

**What to look for:** Commitment rate below 80% consistently signals stories are too large or Gate G2 is taking too long. Time saved is the headline ROI metric for Yooti design partner conversations.

---

### DORA Tab

Industry-standard DevOps Research and Assessment metrics. Benchmarks the team's delivery performance against DORA elite/high/medium/low bands.

**Metrics displayed:**

| DORA Metric | Description | Elite threshold |
|------------|-------------|-----------------|
| Deployment Frequency | How often code reaches production | On demand |
| Lead Time for Changes | Commit to production time | < 1 hour |
| Change Failure Rate | % of deployments causing incidents | < 5% |
| Time to Restore | MTTR when incidents occur | < 1 hour |

**What to look for:** Lead time is most directly impacted by Yooti — the agent eliminates manual coding and PR preparation time. Change failure rate reflects the quality gates working correctly.

---

### Story Drill-down Tab

Per-story forensics. Click any story to see its complete gate timeline, phase durations, and delivery breakdown.

**What it shows:**

- Story table with status, complexity, points, and current gate
- Click-through to individual story detail
- Gate timeline: G1 → G2 → G3 → G4 → G5 with timestamps and reviewer
- Phase durations: time in each pipeline phase
- Evidence summary: test counts, coverage, security findings
- Escalation and correction history if any occurred

**What to look for:** Stories with long G2→G3 gaps indicate PR review backlog. Stories with multiple escalations indicate spec quality issues. Phase duration outliers identify where the pipeline slows down for specific story types.

---

### Insight Alerts

The dashboard surfaces automated alerts computed at ingest time by the insight engine:

| Alert | Trigger | Severity |
|-------|---------|----------|
| BOTTLENECK | Any phase > threshold hours | warn |
| HUMAN_VS_AGENT | Human wait > agent exec time | warn |
| CONSTITUTION_GAP | Constitution pass < 95% | warn |
| QUALITY_DROP | Coverage or mutation score drops sprint-over-sprint | info/warn |
| REGRESSION_SPIKE | Regression rate > 0 | critical |
| ESCALATION_SPIKE | Escalation rate > 10% | critical |
| DORA_GAP | Any DORA metric below team target | warn |

Alerts appear as `InsightStrip` banners at the top of affected tabs.

---

## Creating the Reference Implementation (RI)

This section documents how this dashboard was built using the Yooti CLI autonomous pipeline. Follow these steps to recreate it or build a similar RI for a different project.

### Prerequisites

```
Node.js >= 20
Python >= 3.12
Git + GitHub CLI (gh)
Docker Desktop
AWS SAM CLI
@yooti/cli installed globally
```

Install the CLI:
```bash
npm install -g @yooti/cli
yooti doctor   # verify all prerequisites
```

---

### Step 1 — Initialise the project

```bash
yooti init yooti-dashboard
```

Wizard answers used for this RI:

| Question | Answer |
|----------|--------|
| Project type | full |
| Context | greenfield |
| Backend stack | Python + FastAPI |
| Frontend stack | React 18 + Vite |
| Agent framework | LangGraph |
| Database | PostgreSQL + Redis |
| LLM provider | Anthropic |
| Deploy | AWS SAM |
| AWS region | us-east-1 |
| Stage | 3 (Review) |
| Item prefix | DASH |

---

### Step 2 — Import stories

```bash
yooti story:import --file PM-STORIES-FLAT.json
```

Or add stories individually:
```bash
yooti story:add
```

This RI used 13 stories — 9 in Sprint 1 (DASH-001 to DASH-009) and 4 in Sprint 2 (GHAGENT-001 to GHAGENT-004).

---

### Step 3 — Gate G1 — PM approves stories

```bash
yooti story:approve --all
```

Review each story's acceptance criteria and ambiguity flags before approving.

---

### Step 4 — Start the sprint

```bash
# If using AWS SAM, start LocalStack first
docker compose up localstack -d

yooti sprint:start
```

This runs preflight checks and captures the regression baseline.

---

### Step 5 — Phase 2 — Generate plans

Open Claude Code in the project root and run:

```
Proceed to Phase 2 for all stories in this sprint.
```

The agent generates `.agent/plans/DASH-NNN-TNNN.plan.md` files for each task. No code is written at this phase.

---

### Step 6 — Gate G2 — Architect reviews plans

```bash
yooti plan:review DASH-001
# repeat for each story
```

For each task choose: Approve / Approve with annotation / Request revision.

Annotations are read by the agent before writing any code. Use them to enforce architectural constraints.

**Example annotations used in this RI:**
- `DASH-001-T002`: `FilterExpression must use Attr("SK").contains("#SUMMARY")`
- `DASH-006-T001`: `MetricsTable must include TimeToLiveSpecification with ttl attribute`

---

### Step 7 — Phase 4 — Code generation

In Claude Code:

```
Proceed to Phase 4 for all approved stories in dependency order.
```

The agent writes code TDD-first, runs the quality loop, self-heals failures, and stops at Gate G3 (PR). Monitor for escalations:

```bash
dir .agent\escalations\
```

---

### Step 8 — Phase 5 — Evidence package

In Claude Code:

```
Proceed to Phase 5 for all completed stories.
```

The agent generates per-story evidence packages containing test results, coverage, security scan, and code audit — then opens PRs in GitHub.

---

### Step 9 — Gate G3 — Developer reviews PRs

Review each PR in GitHub in dependency order (#1 → #9). Merge in order.

Log the gate decisions:
```bash
yooti log:event DASH-001   # Gate decision → G3 → APPROVED
```

Create gate files:
```powershell
$stories = @("DASH-001","DASH-002","DASH-003","DASH-004","DASH-005","DASH-006","DASH-007","DASH-008","DASH-009")
foreach ($s in $stories) {
  "# Gate G3`nStory: $s`nDecision: APPROVED`nReviewed by: [name]`nDate: $(Get-Date -Format 'o')" | Set-Content ".agent/gates/$s-G3-approved.md"
}
```

---

### Step 10 — Gate G4 — QA review

```bash
yooti qa:review DASH-001
# repeat for each story
```

Reads the evidence package and checks all hard gates. Approve each story.

---

### Step 11 — Gate G5 — Release

```powershell
$stories = @("DASH-001","DASH-002","DASH-003","DASH-004","DASH-005","DASH-006","DASH-007","DASH-008","DASH-009")
foreach ($s in $stories) {
  "# Gate G5`nStory: $s`nDecision: APPROVED`nReviewed by: [name]`nDate: $(Get-Date -Format 'o')" | Set-Content ".agent/gates/$s-G5-approved.md"
}
```

---

### Step 12 — Sprint report

```bash
yooti sprint:report
```

Shows completion status, gate progress, coverage, and DoD for all stories.

---

## Architecture

```
Browser (localhost:5173)
  |
  | /api/* (Vite proxy strips /api prefix)
  v
React Frontend (Vite)                    Mock API (node scripts/mock-api.mjs)
  - 6 tabs, React Query hooks    --->    localhost:3001
  - Tailwind CSS, axe-core                  |
                                            | (or in production)
                                            v
                                    API Gateway + Lambda (SAM)
                                            |
                                            v
                                    DynamoDB (single table)
```

### Layers

| Layer | Location | Stack | Purpose |
|-------|----------|-------|---------|
| Frontend | `frontend/dashboard/` | React 18, TypeScript, Vite, Tailwind, React Query | 6-tab dashboard UI |
| API | `services/api_python/src/handlers/` | Python 3.12, Lambda, API Gateway | 6 REST endpoints |
| Repository | `services/api_python/src/repository/` | boto3, DynamoDB | Single-table data access |
| Services | `services/api_python/src/services/` | Python | Insight engine, trend calculator |
| Pipeline | `pipeline/scripts/` | Python | Reads `.agent/` files, computes KPIs, POSTs to ingest |
| Infrastructure | `template.yaml` | SAM, CloudFormation | Lambda + API Gateway + DynamoDB |

## API Endpoints

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| GET | `/metrics/current` | `get_current_metrics` | Current sprint snapshot (single GetItem) |
| GET | `/metrics/sprints` | `get_sprint_list` | All sprint summaries, descending |
| GET | `/metrics/sprint/{num}` | `get_sprint_detail` | Sprint detail with stories |
| GET | `/metrics/trends` | `get_trends` | Metric trend series across sprints |
| GET | `/metrics/story/{id}` | `get_story_detail` | Per-story detail with gate timeline |
| POST | `/metrics/ingest` | `ingest_metrics` | Ingests sprint data, updates snapshot |

## DynamoDB Single-Table Design

Table: `yooti-metrics`

| Entity | PK | SK | Access Pattern |
|--------|----|----|----------------|
| Current snapshot | `PROJECT#{id}` | `CURRENT#SNAPSHOT` | GetItem |
| Sprint summary | `PROJECT#{id}` | `SPRINT#{num}#SUMMARY` | GetItem / Query begins_with |
| Story metrics | `PROJECT#{id}` | `SPRINT#{num}#STORY#{story_id}` | Query begins_with |
| Phase durations | `PROJECT#{id}` | `SPRINT#{num}#PHASE#{story_id}` | GetItem |
| Trend point | `PROJECT#{id}` | `TREND#{metric}#SPRINT#{num}` | Query begins_with |
| Gate event | `PROJECT#{id}` | `GATE#{story_id}#G{n}` | Query begins_with |
| Escalation | `PROJECT#{id}` | `ESC#{story_id}#{task_id}` | Query begins_with |

No Scan operations anywhere. All reads use GetItem or Query with begins_with.

## Project Structure

```
yooti-dashboard/
├── frontend/dashboard/           # React frontend
│   ├── src/
│   │   ├── components/           # KpiCard, TrendBadge, InsightStrip, StoryTable, etc.
│   │   ├── pages/                # DashboardLayout + 6 tab pages
│   │   └── lib/                  # API client, types, React Query hooks
│   ├── tests/unit/               # 108 unit tests (vitest + axe-core)
│   ├── vite.config.ts            # Dev server + proxy to API
│   └── package.json
├── services/api_python/          # Python Lambda backend
│   ├── src/
│   │   ├── handlers/             # 6 Lambda handlers + response helpers
│   │   ├── repository/           # DynamoDB repository (keys, errors, CRUD)
│   │   ├── services/             # Insight engine, trend calculator
│   │   └── validators/           # Ingest payload validation
│   ├── tests/unit/               # 129 unit tests (pytest + moto)
│   ├── main.py                   # FastAPI entry point (Docker dev)
│   └── requirements.txt
├── pipeline/scripts/             # Data aggregation pipeline
│   ├── aggregate-metrics.py      # Reads .agent/ files, POSTs to ingest
│   ├── lib/                      # File readers, metric calculator, ingest client
│   └── tests/                    # 37 unit tests
├── scripts/
│   ├── mock-api.mjs              # Zero-dependency mock API for local dev
│   └── seed_local.py             # Seeds LocalStack DynamoDB with test data
├── template.yaml                 # SAM template (Lambda + API Gateway + DynamoDB)
├── docker-compose.yml            # Local dev stack
├── env.local.json                # SAM local env vars (points to LocalStack)
└── .agent/                       # Yooti pipeline artifacts
    ├── requirements/             # Validated story specs
    ├── plans/                    # Task decomposition plans
    ├── gates/                    # G1–G5 approval records
    └── evidence/                 # Test results, coverage, PR bodies
```

## Local Development

### Quick start (mock API — no Docker needed)

```bash
# Terminal 1: mock API server
node scripts/mock-api.mjs

# Terminal 2: frontend dev server
cd frontend/dashboard
npm install
npm run dev

# Open http://localhost:5173
```

### Full stack (SAM + LocalStack)

```bash
# Start LocalStack
docker compose up localstack -d

# Create DynamoDB table
aws dynamodb create-table \
  --endpoint-url http://localhost:4566 \
  --table-name yooti-metrics \
  --key-schema AttributeName=PK,KeyType=HASH AttributeName=SK,KeyType=RANGE \
  --attribute-definitions AttributeName=PK,AttributeType=S AttributeName=SK,AttributeType=S \
    AttributeName=project_id,AttributeType=S AttributeName=updated_at,AttributeType=S \
  --global-secondary-indexes '[{"IndexName":"GSI-1","KeySchema":[{"AttributeName":"project_id","KeyType":"HASH"},{"AttributeName":"updated_at","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}]' \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Seed test data
python scripts/seed_local.py

# Build and start SAM
sam build
sam local start-api --port 3001 --env-vars env.local.json

# Frontend (separate terminal)
cd frontend/dashboard && npm run dev
```

### Docker Compose (full stack)

```bash
docker compose up -d
# API:        http://localhost:8000
# Frontend:   http://localhost:5173
# LocalStack: http://localhost:4566
```

## Testing

```bash
# Frontend (108 tests)
cd frontend/dashboard && npx vitest run

# Python API (129 tests)
cd services/api_python && python -m pytest tests/unit/ --noconftest

# Pipeline scripts (37 tests)
cd pipeline/scripts && python -m pytest tests/

# Total: 274 tests
```

## Data Flow

```
.agent/ files (gates, evidence, logs, escalations)
        |
        v
aggregate-metrics.py  ---->  POST /metrics/ingest
                                    |
                                    v
                             ingest_metrics handler
                                    |
                              ┌─────┴─────┐
                              v           v
                        batch_write   insight_engine
                        (sprint +     (compute alerts)
                         stories)          |
                              |           v
                              └─────┬─────┘
                                    v
                             put_current_snapshot
                             (CURRENT#SNAPSHOT)
                                    |
                                    v
                             GET /metrics/current
                                    |
                                    v
                             Dashboard renders
                             KPI cards + alerts
```

## Stories Completed

| Story | Title | Tests |
|-------|-------|-------|
| DASH-001 | DynamoDB repository layer | 56 |
| DASH-002 | POST /metrics/ingest | 28 |
| DASH-003 | GET /metrics/current | 9 |
| DASH-004 | GET /metrics/sprints + sprint/{id} | 12 |
| DASH-005 | GET /metrics/trends + story/{id} | 24 |
| DASH-006 | SAM template wiring | 0 (infra) |
| DASH-007 | aggregate-metrics.py pipeline | 37 |
| DASH-008 | React fetch hooks + SprintSelector | 18 |
| DASH-009 | Six-tab React dashboard | 74 |
| DASH-010 | Wire tabs to real API hooks | 16 |
