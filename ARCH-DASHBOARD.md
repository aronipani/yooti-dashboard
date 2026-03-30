# Architecture Document — Yooti Metrics Dashboard
# Document type: Architecture Decision Record (ADR)
# Status: Draft — for Gate G2 review
# Author: Generated from Yooti pipeline session
# Last updated: 2026-03-29

---

## 1. Context and purpose

The Yooti Metrics Dashboard is the Reference Implementation for Sprint 2
of the yooti-cli project. It serves two purposes:

First, it is a genuinely useful product — a dashboard that shows pipeline
metrics for any team using Yooti, including productivity, quality, agent
efficiency, value, and DORA-comparable metrics.

Second, it proves the Yooti framework by being built through the Yooti
pipeline itself. The metrics it displays for its own construction are the
first real data it shows.

This document defines the architecture that the architect must review and
approve at Gate G2 before any code is written for DASH-001 through DASH-009.

---

## 2. System overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  FRONTEND — React 18 + Vite + shadcn/ui + Tailwind                  │
│  Hosted: S3 + CloudFront (production) / Vite dev server (local)     │
│  Six tabs: Productivity, Quality, Agent Efficiency,                 │
│            Value, DORA, Story Drill-down                            │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTPS — REST API calls
┌────────────────────────▼────────────────────────────────────────────┐
│  API GATEWAY — REST API                                              │
│  GET  /metrics/current            GET  /metrics/trends              │
│  GET  /metrics/sprints            GET  /metrics/story/{id}          │
│  GET  /metrics/sprint/{num}       POST /metrics/ingest              │
└────────────────────────┬────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────────┐
│  LAMBDA FUNCTIONS — Python 3.12                                      │
│  get_current_metrics    get_sprint_list    get_sprint_detail        │
│  get_trends             get_story_detail   ingest_metrics           │
└────────────────────────┬────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────────┐
│  DYNAMODB — single table: yooti-metrics                              │
│  One table per environment (dev / staging / prod)                   │
│  Multi-tenant by project_id prefix                                  │
└─────────────────────────────────────────────────────────────────────┘

  LOCAL DEVELOPMENT
  ─────────────────
  DynamoDB      → LocalStack (port 4566)
  API Gateway   → LocalStack (port 4566)
  Lambda        → LocalStack or python scripts/invoke_local.py
  Frontend      → Vite dev server (port 5173), proxy → LocalStack
  Data ingest   → python pipeline/scripts/aggregate-metrics.py
```

---

## 3. DynamoDB — single table design

### Table name: yooti-metrics

One table per environment. Provisioned via SAM template.
Multi-tenant: all projects share one table, isolated by PK prefix.

### Key schema

| Attribute | Type | Role |
|-----------|------|------|
| PK | String | Partition key |
| SK | String | Sort key |

### GSI

| Index | PK | SK | Purpose |
|-------|----|----|---------|
| GSI-1 | project_id | updated_at | Fetch latest sprint without knowing sprint number |

### Entity map

```
ENTITY                  PK                              SK
──────────────────────  ──────────────────────────────  ──────────────────────────────────────
Sprint summary          PROJECT#<project_id>            SPRINT#<num>#SUMMARY
Story metrics           PROJECT#<project_id>            SPRINT#<num>#STORY#<story_id>
Phase durations         PROJECT#<project_id>            SPRINT#<num>#PHASE#<story_id>
Trend series            PROJECT#<project_id>            TREND#<metric_name>#SPRINT#<num>
Current snapshot        PROJECT#<project_id>            CURRENT#SNAPSHOT
Gate events             PROJECT#<project_id>            GATE#<story_id>#G<n>
Escalation log          PROJECT#<project_id>            ESC#<story_id>#<task_id>
```

### Sprint summary attributes

```
sprint_num              int
project_id              str
cycle_time_avg_days     Decimal
sprint_completion_pct   Decimal
agent_exec_hrs_avg      Decimal
human_wait_hrs_avg      Decimal
deploy_frequency        int
stories_shipped         int
stories_committed       int
coverage_new_code_avg   Decimal
mutation_score_avg      Decimal
regression_rate_pct     Decimal
constitution_pass_pct   Decimal
escalation_rate_pct     Decimal
iteration_avg           Decimal
correction_rate_pct     Decimal
gate_rejection_rates    Map  { G1: int, G2: int, G3: int, G4: int, G5: int }
escalation_breakdown    Map  { ENV_ERROR: int, SCOPE_ERROR: int, ... }
phase_avg_hrs           Map  { g1_wait, phase2, g2_wait, phase4, g3_wait, g4_g5 }
insight_alerts          List[Map]
created_at              str  ISO 8601
updated_at              str  ISO 8601
```

### Story metrics attributes

```
story_id                str
sprint_num              int
type                    str  feature | bugfix | refactor | security-patch | aws-lambda
status                  str  shipped | blocked | in-progress | incomplete
cycle_time_hrs          Decimal
iteration_count         int
escalation_type         str | None
correction_count        int
plan_revision_count     int
coverage_new_code_pct   Decimal
mutation_score_pct      Decimal | None
security_critical       int
security_high           int
regression_introduced   bool
constitution_violations int
ac_coverage_pct         Decimal
dod_items_passed        int
dod_items_total         int
gate_timestamps         Map  { g1, g2, g3, g4, g5 } ISO 8601 or None
reviewers               List[str]
created_at              str
updated_at              str
```

### Current snapshot attributes

All sprint summary fields plus:

```
sprint_num              int   — which sprint this represents
last_ingested_at        str   — when aggregate-metrics.py last ran
insight_alerts          List[Map]  — computed threshold alerts
ttl                     int   — Unix timestamp, 90 days from ingest
```

### Insight alert shape

```json
{
  "type": "BOTTLENECK",
  "severity": "warn",
  "message": "G3 wait (19h) exceeds target (15h). Consider Stage 4.",
  "metric": "g3_wait_hrs",
  "value": 19,
  "threshold": 15
}
```

Alert types: BOTTLENECK | HUMAN_VS_AGENT | CONSTITUTION_GAP |
QUALITY_DROP | REGRESSION_SPIKE | ESCALATION_SPIKE | DORA_GAP

---

## 4. Access patterns — all resolved without Scan

| ID | Description | Operation | Key expression |
|----|-------------|-----------|----------------|
| AP-1 | Dashboard load — current KPIs | GetItem | PK=PROJECT#id, SK=CURRENT#SNAPSHOT |
| AP-2 | All stories in a sprint | Query | PK=PROJECT#id, SK begins_with(SPRINT#10#STORY) |
| AP-3 | Sprint summary | GetItem | PK=PROJECT#id, SK=SPRINT#10#SUMMARY |
| AP-4 | All sprint summaries (selector) | Query | PK=PROJECT#id, SK begins_with(SPRINT#) FilterExpression SK ends_with(SUMMARY) |
| AP-5 | Trend series for one metric | Query | PK=PROJECT#id, SK begins_with(TREND#cycle_time_avg) |
| AP-6 | All trends for a sprint | Query | PK=PROJECT#id, SK begins_with(TREND#) |
| AP-7 | Phase durations for a story | GetItem | PK=PROJECT#id, SK=SPRINT#10#PHASE#PROJ-123 |
| AP-8 | Gate events for a story | Query | PK=PROJECT#id, SK begins_with(GATE#PROJ-123) |
| AP-9 | Escalations for a sprint | Query | PK=PROJECT#id, SK begins_with(ESC#) filter sprint_num |
| AP-10 | Write all sprint entities | BatchWriteItem | — |

**Constraint enforced by constitution:** No Scan operation is permitted
anywhere in the repository layer. All reads use Query or GetItem.

---

## 5. API contract

### Base URL

```
Local:      http://localhost:4566/restapis/<id>/local/_user_request_
Staging:    https://<api-id>.execute-api.us-east-1.amazonaws.com/Staging
Production: https://<api-id>.execute-api.us-east-1.amazonaws.com/Prod
```

### Endpoints

#### GET /metrics/current

Returns the current sprint snapshot for a project.
Single DynamoDB GetItem — AP-1.

```
Query params:  project_id (required)
Response 200:  { project_id, sprint_num, kpis, insights, last_ingested_at }
Response 400:  { error: "INVALID_PROJECT_ID", message, statusCode }
Response 404:  { error: "SPRINT_NOT_FOUND", message, statusCode }
Lambda:        get_current_metrics
```

#### GET /metrics/sprints

Returns all sprint summary records for a project. Populates sprint selector.

```
Query params:  project_id (required)
Response 200:  { sprints: [ { sprint_num, cycle_time_avg_days, ... } ] }
               Sorted by sprint_num descending.
Lambda:        get_sprint_list
```

#### GET /metrics/sprint/{sprint_num}

Returns full sprint detail — summary, stories, phase durations.

```
Path params:   sprint_num (positive integer)
Query params:  project_id (required)
Response 200:  { sprint_num, summary, phase_avg_hrs, gate_rejection_rates,
                 escalation_breakdown, stories[] }
Response 400:  { error: "INVALID_SPRINT_NUM" }
Response 404:  { error: "SPRINT_NOT_FOUND" }
Lambda:        get_sprint_detail
```

#### GET /metrics/trends

Returns metric trend series for charting.

```
Query params:  project_id (required), metric (optional — all metrics if omitted)
Response 200:  { trends: { metric_name: [ { sprint_num, value, delta, direction } ] } }
Lambda:        get_trends
```

#### GET /metrics/story/{story_id}

Returns per-story detail including gate timeline and escalation log.

```
Path params:   story_id
Query params:  project_id (required), sprint (required)
Response 200:  { story_id, sprint_num, type, status, cycle_time_hrs,
                 phase_durations, gate_timestamps, agent_metrics,
                 evidence, escalation_log }
Response 404:  { error: "STORY_NOT_FOUND" }
Lambda:        get_story_detail
```

#### POST /metrics/ingest

Called by aggregate-metrics.py after reading .agent/ files.
Idempotent — safe to call multiple times for the same sprint.

```
Body:          { project_id, sprint_num, stories[] }
Response 201:  { sprint_num, stories_ingested } — first write
Response 200:  { sprint_num, stories_ingested } — re-ingest
Response 400:  { error: "INVALID_PROJECT_ID" | "INVALID_SPRINT_NUM" }
Response 500:  { error: "INTERNAL_ERROR" } — never expose detail
Lambda:        ingest_metrics
```

### Standard error shape

```json
{
  "error": "STORY_NOT_FOUND",
  "message": "Story PROJ-123 not found in sprint 10",
  "statusCode": 404
}
```

Error responses never include: stack traces, file paths, exception types,
internal variable names, or DynamoDB error codes.

### Auth

| Environment | Method |
|-------------|--------|
| Local / LocalStack | None — open |
| Staging / Production | x-api-key header |

API key stored in .env as YOOTI_DASHBOARD_API_KEY. Never in code.

---

## 6. Lambda function definitions

### get_current_metrics

```
Trigger:    GET /metrics/current
Input:      event["queryStringParameters"]["project_id"]
Operation:  Single GetItem — AP-1
Output:     200 with kpis + insights | 400 | 404 | 500
Cold start: boto3 client at module level — not inside handler
Env vars:   TABLE_NAME
```

### get_sprint_list

```
Trigger:    GET /metrics/sprints
Input:      event["queryStringParameters"]["project_id"]
Operation:  Query — AP-4, sorted descending
Output:     200 with sprints array | 400 | 500
Env vars:   TABLE_NAME
```

### get_sprint_detail

```
Trigger:    GET /metrics/sprint/{sprint_num}
Input:      event["pathParameters"]["sprint_num"]
            event["queryStringParameters"]["project_id"]
Operations: GetItem (AP-3) + Query stories (AP-2) + Query phases
Output:     200 with full sprint | 400 | 404 | 500
Env vars:   TABLE_NAME
```

### get_trends

```
Trigger:    GET /metrics/trends
Input:      project_id, optional metric filter
Operation:  Query — AP-5 or AP-6
Output:     200 with grouped trend series | 400 | 500
Env vars:   TABLE_NAME
```

### get_story_detail

```
Trigger:    GET /metrics/story/{story_id}
Input:      story_id, project_id, sprint
Operations: GetItem (story) + Query (gates AP-8) + Query (escalations AP-9)
Output:     200 with story detail | 400 | 404 | 500
Env vars:   TABLE_NAME
```

### ingest_metrics

```
Trigger:    POST /metrics/ingest
Input:      event["body"] — JSON string
Operations: Validate → BatchWriteItem (AP-10) → Update CURRENT#SNAPSHOT
            → Compute insight alerts
Output:     201 (first write) | 200 (re-ingest) | 400 | 500
Idempotent: Yes — safe to call twice for same sprint
Env vars:   TABLE_NAME
```

---

## 7. Deployment — SAM template structure

```yaml
Resources:

  MetricsTable:
    Type: AWS::DynamoDB::Table
    # Single table, PAY_PER_REQUEST, SSE enabled, TTL on ttl attribute
    # GSI-1: project_id (PK) + updated_at (SK)

  GetCurrentMetricsFunction:   # GET /metrics/current
  GetSprintListFunction:       # GET /metrics/sprints
  GetSprintDetailFunction:     # GET /metrics/sprint/{num}
  GetTrendsFunction:           # GET /metrics/trends
  GetStoryDetailFunction:      # GET /metrics/story/{id}
  IngestMetricsFunction:       # POST /metrics/ingest

  MetricsApi:
    Type: AWS::Serverless::Api
    # CORS configured for Vite dev origin and production domain
    # API key required for staging/prod, open for local

  FrontendBucket:              # S3 bucket for React build
  CloudFrontDistribution:      # CDN for frontend

Outputs:
  ApiEndpoint
  CloudFrontDomain
  TableName
```

---

## 8. Local development setup

### Prerequisites

```bash
docker compose up localstack -d   # starts LocalStack on port 4566
python scripts/create_local_resources.py  # creates DynamoDB table
```

### Environment variables (.env)

```bash
# DynamoDB / Lambda
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
AWS_ENDPOINT_URL=http://localhost:4566
TABLE_NAME=yooti-metrics

# API
YOOTI_DASHBOARD_API_URL=http://localhost:4566/restapis/local/local/_user_request_
YOOTI_DASHBOARD_API_KEY=  # empty for local

# Frontend
VITE_API_BASE_URL=/api     # proxied by Vite to LocalStack
VITE_PROJECT_ID=yooti-ri
```

### Vite proxy config

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:4566',
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

### Data flow — local development

```
1. Run Yooti sprint on a project
   yooti sprint:report

2. aggregate-metrics.py reads .agent/ files and POSTs to ingest
   python pipeline/scripts/aggregate-metrics.py

3. Lambda writes to LocalStack DynamoDB

4. Vite dev server fetches from LocalStack via proxy

5. Dashboard renders real data at http://localhost:5173
```

---

## 9. Key architectural decisions

### D1 — Single table design

One DynamoDB table for all entity types. All access patterns resolved
with Query or GetItem. No Scan permitted. Enables low-latency reads
and predictable cost at scale.

### D2 — CURRENT#SNAPSHOT as hot path

Dashboard load calls GetItem on one item — not a Query across sprints.
This keeps p99 dashboard load time under 50ms regardless of sprint count.
Updated atomically on every ingest.

### D3 — Insight alerts computed at ingest time

Alerts are computed when data is ingested — not at query time. Query
latency is not affected by alert logic complexity. Adding new alert types
requires no change to query Lambda functions.

### D4 — project_id prefix enables multi-tenancy

All PKs prefixed with PROJECT#<id>. One table serves all Yooti projects.
Each project's data is isolated by PK prefix. No cross-project queries
possible by construction.

### D5 — Frontend served from S3 + CloudFront

Static React build. No server-side rendering. All data from API.
Enables independent deploy of frontend and backend.

### D6 — Idempotent ingest

POST /metrics/ingest can be called multiple times for the same sprint.
Subsequent calls update all items. Returns 200 not 201 on re-ingest.
Allows yooti sprint:report to be run multiple times safely.

---

## 10. Constraints the architect must enforce at Gate G2

These constraints must appear in the plan annotations for every task:

```
DATABASE
  No Scan anywhere in the repository layer
  All writes use conditional expressions where appropriate
  TABLE_NAME always from os.environ — never hardcoded

API GATEWAY
  event["body"] is always parsed with json.loads — never assumed to be dict
  Error responses never expose internal detail
  All path parameters and query strings validated before use

LAMBDA
  boto3 client instantiated at module level — not inside handler
  All config from os.environ
  Every handler catches all exceptions — none propagate uncaught
  Handler returns dict — never raises

TESTING
  All unit tests use @mock_aws — no real DynamoDB calls
  All unit tests run without LocalStack or Docker
  Integration tests in tests/integration/ — run separately
  MSW (Mock Service Worker) for frontend hook tests
```

---

## 11. Open questions for Gate G2 discussion

1. CORS configuration: what origin domains need to be whitelisted for
   production? Confirm before generating the SAM template.

2. API key rotation strategy: who generates the API key for each project
   and how is it delivered to aggregate-metrics.py?

3. TTL policy: current snapshot TTL is 90 days. Should historical sprint
   summaries also have a TTL or should they be kept indefinitely?

4. CloudFront caching: the /metrics/current endpoint changes on every
   ingest. Cache-Control headers should set max-age=0 for this endpoint.
   Confirm caching strategy for all six endpoints.

---

*Architecture document for Gate G2 review — Yooti Dashboard RI*
*Status: pending architect approval*
