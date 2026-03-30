# Architecture Document — GitHub Metrics Enrichment Agent
# Document type: Architecture Decision Record (ADR)
# Status: Draft — for Gate G2 review
# Author: Generated from Yooti pipeline session
# Last updated: 2026-03-29

---

## 1. Context and purpose

The GitHub Metrics Enrichment Agent closes the gap between Yooti's native
pipeline metrics and LinearB-comparable metrics. Yooti captures data from
gate files and evidence packages. GitHub captures PR-level data that Yooti
does not: pickup time, review time, PR size, and review depth.

This agent runs after aggregate-metrics.py, fetches GitHub PR data for each
story in the sprint, and enriches the ingest payload before it reaches
DynamoDB. The dashboard then shows a complete metric set.

This document defines the LangGraph architecture that the architect must
review and approve at Gate G2 before any code is written for
GHAGENT-001 through GHAGENT-004.

---

## 2. Critical design decision — no LLM calls

This is a LangGraph state machine. It makes zero LLM calls.

LangGraph is used for its state management, conditional routing,
and checkpoint/resume capability — not for language model inference.

Every node is a deterministic Python function. Same input always
produces same output. No prompt engineering. No model costs per run.

This must be noted in the Gate G2 plan annotations for every task.
The three-layer testing model (unit/integration/eval) still applies,
but Layer 3 (evals with real LLM calls) does not exist for this agent.

---

## 3. System overview

```
TRIGGER
yooti sprint:report
      │
      ▼
aggregate-metrics.py          reads .agent/ files → builds base payload
      │
      ▼
GitHubMetricsAgent            LangGraph state machine
      │
      ├── reads: GITHUB_TOKEN, GITHUB_REPO from .env
      ├── calls: GitHub REST API (api.github.com)
      │          read-only: pull_requests + reviews + comments
      └── outputs: enriched stories with PR metrics added
            │
            ▼
POST /metrics/ingest          enriched payload → DynamoDB → dashboard

EXTERNAL DEPENDENCIES
  GitHub REST API    api.github.com  — read-only, fine-grained token
  Yooti ingest API   localhost or AWS — POST /metrics/ingest

NO AWS SERVICES USED BY THIS AGENT
  Does not call DynamoDB, Lambda, SQS, SNS, or any other AWS service.
  The aws.md constitution does NOT apply to this agent.
  The langgraph.md constitution applies.
```

---

## 4. LangGraph state definition

```python
from typing import TypedDict, Optional
from datetime import datetime


class EnrichedStory(TypedDict):
    story_id: str
    pr_found: bool
    pr_number: Optional[int]
    pr_url: Optional[str]
    pr_created_at: Optional[str]
    first_review_at: Optional[str]
    merged_at: Optional[str]
    lines_added: int
    lines_deleted: int
    files_changed: int
    review_comment_count: int
    reviewer_count: int
    reviewers: list[str]
    pickup_time_hrs: Optional[float]
    review_time_hrs: Optional[float]
    pr_size_lines: int
    enrich_status: str   # FOUND | NO_PR | ERROR | SKIPPED


class EnrichmentError(TypedDict):
    story_id: str
    error_type: str      # RATE_LIMIT | AUTH_ERROR | API_5XX | NOT_FOUND
    message: str
    timestamp: str


class GitHubMetricsState(TypedDict):
    # Input — set before graph starts
    project_id: str
    sprint_num: int
    stories: list[dict]             # base stories from aggregate-metrics.py

    # Accumulator — grows as graph processes each story
    enriched: list[EnrichedStory]

    # Cursor — enables resume from any point
    current_idx: int

    # Error log — non-fatal failures accumulate here
    errors: list[EnrichmentError]

    # Rate limit state — set by handle_error node
    rate_limit_reset: Optional[str]  # ISO timestamp

    # Output
    ingest_payload: Optional[dict]
    ingest_status: Optional[str]     # SUCCESS | FAILED | PARTIAL
```

### State rules — enforced by constitution

```
IMMUTABILITY
  Nodes return dicts of updated fields only.
  Nodes never mutate state in place.
  Every node independently testable with a dict input.

ERRORS ARE STATE
  Every node returns {"error_type": ..., "message": ...} on failure.
  Nodes never raise — they return.
  Errors accumulate in state["errors"] — they do not halt the run
  unless error_type is AUTH_ERROR.

RESUMABILITY
  current_idx tracks position.
  If the process is interrupted, a new run reads state from checkpoint
  and continues from current_idx.
  LangGraph MemorySaver used for local checkpointing.
```

---

## 5. Node definitions

### load_stories

```
Purpose:   Validate input and prepare the story list for processing.
Input:     state["stories"] — base payload from aggregate-metrics.py
Output:    state update: { stories: validated_list, current_idx: 0 }
Errors:    Returns error if stories is empty or malformed.
LLM calls: None
Tests:     Happy path, empty list, malformed story dict
```

### find_pr_for_story

```
Purpose:   Find the merged GitHub PR for the current story by branch name.
           Branch conventions tried in order:
             1. feature/{story_id}
             2. {story_id} (lowercase)
             3. {story_id} (uppercase)
Input:     state["stories"][state["current_idx"]]
           GITHUB_TOKEN, GITHUB_REPO from os.environ
Output:    state update: { _current_pr: pr_dict | None }
Errors:    RATE_LIMIT → includes X-RateLimit-Reset timestamp
           AUTH_ERROR → invalid or expired token
           API_5XX    → transient GitHub error
           NOT_FOUND  → no PR for this branch (not an error — normal)
LLM calls: None
Tests:     PR found on feature/ branch, PR found on plain branch,
           no PR found, rate limit response, auth error, 5xx response
```

### fetch_pr_details

```
Purpose:   Fetch additions, deletions, changed_files from the PR object.
           This data is already in the find_pr response — this node
           extracts and validates it.
Input:     state["_current_pr"]
Output:    state update: { _current_details: { lines_added, lines_deleted,
                                               files_changed } }
Errors:    Returns error dict if PR data is malformed.
LLM calls: None
Tests:     Normal PR, PR with zero additions, missing fields
```

### fetch_reviews_and_comments

```
Purpose:   Fetch all review events and line-level comments for the PR.
           Paginates comments (100 per page) until exhausted.
           Filters out bot reviewers.
Input:     state["_current_pr"]["number"]
Output:    state update: { _current_reviews: list, _current_comments: list }
Errors:    RATE_LIMIT, API_5XX — same as find_pr_for_story
LLM calls: None
Tests:     3 reviews + 7 comments, zero reviews, bot reviewer filtered,
           pagination (>100 comments), rate limit mid-pagination
```

### compute_metrics

```
Purpose:   Compute all derived metrics from fetched data.
           All arithmetic — no external calls.
Input:     state["_current_pr"], state["_current_reviews"],
           state["_current_comments"], state["_current_details"]
Output:    state update: { _current_enriched: EnrichedStory }
Errors:    Returns error if timestamps cannot be parsed.
LLM calls: None

Calculations:
  pickup_time_hrs:
    (first_review_at - pr_created_at).total_seconds() / 3600
    None if no reviews exist

  review_time_hrs:
    (merged_at - first_review_at).total_seconds() / 3600
    None if no reviews or not merged

  pr_size_lines:
    lines_added + lines_deleted

  reviewers:
    Unique login names from reviews where user.type != "Bot"

Tests:     pickup 4 hrs, no reviews → None, merged before review (edge case)
```

### accumulate_and_advance

```
Purpose:   Append the current enriched story to state["enriched"].
           Increment current_idx.
           Route: more stories? → find_pr_for_story
                  all done?    → post_to_ingest_api
Input:     state["_current_enriched"] | state["_current_error"]
           state["current_idx"], state["stories"]
Output:    state update: { enriched: [..., new_story],
                           current_idx: current_idx + 1 }
Errors:    None — this node cannot fail.
LLM calls: None
Tests:     Middle of list (routes back), last story (routes to post)
```

### handle_error

```
Purpose:   Route errors to appropriate recovery action.
           RATE_LIMIT → sleep until reset time, then retry find_pr
           AUTH_ERROR → halt graph immediately, log clearly
           API_5XX    → retry up to 3 times with exponential backoff
           NOT_FOUND  → mark story as NO_PR, call accumulate_and_advance
Input:     state["errors"][-1] — most recent error
Output:    state update: { rate_limit_reset: timestamp | None }
           Routes to: find_pr_for_story (retry) | accumulate_and_advance
                      (skip) | END (halt on auth)
LLM calls: None
Tests:     Rate limit → wait and retry, auth error → halt,
           5xx → retry 3x then skip, not found → mark and advance
```

### post_to_ingest_api

```
Purpose:   Build the final enriched payload and POST to /metrics/ingest.
Input:     state["enriched"], state["project_id"], state["sprint_num"]
           YOOTI_DASHBOARD_API_URL from os.environ
Output:    state update: { ingest_status: "SUCCESS" | "FAILED",
                           ingest_payload: payload_dict }
Errors:    Returns FAILED status if API unavailable — does not raise.
LLM calls: None
Tests:     Successful post → 201, re-ingest → 200, API unavailable
```

---

## 6. Graph wiring — conditional edges

```python
from langgraph.graph import StateGraph, END

graph = StateGraph(GitHubMetricsState)

# Add all nodes
graph.add_node("load_stories",              load_stories)
graph.add_node("find_pr_for_story",         find_pr_for_story)
graph.add_node("fetch_pr_details",          fetch_pr_details)
graph.add_node("fetch_reviews_and_comments",fetch_reviews_and_comments)
graph.add_node("compute_metrics",           compute_metrics)
graph.add_node("accumulate_and_advance",    accumulate_and_advance)
graph.add_node("handle_error",              handle_error)
graph.add_node("post_to_ingest_api",        post_to_ingest_api)

# Entry point
graph.set_entry_point("load_stories")
graph.add_edge("load_stories", "find_pr_for_story")

# After find_pr: check for errors
graph.add_conditional_edges(
    "find_pr_for_story",
    route_after_find_pr,
    {
        "fetch_pr_details": "fetch_pr_details",
        "handle_error":     "handle_error",
    }
)

# After fetch_pr_details: always proceed to reviews
graph.add_edge("fetch_pr_details", "fetch_reviews_and_comments")

# After fetch_reviews: check for errors
graph.add_conditional_edges(
    "fetch_reviews_and_comments",
    route_after_fetch,
    {
        "compute_metrics": "compute_metrics",
        "handle_error":    "handle_error",
    }
)

graph.add_edge("compute_metrics", "accumulate_and_advance")

# After accumulate: loop or finish
graph.add_conditional_edges(
    "accumulate_and_advance",
    route_after_accumulate,
    {
        "find_pr_for_story":  "find_pr_for_story",  # more stories
        "post_to_ingest_api": "post_to_ingest_api",  # all done
    }
)

# After handle_error: retry, skip, or halt
graph.add_conditional_edges(
    "handle_error",
    route_after_error,
    {
        "find_pr_for_story":       "find_pr_for_story",   # retry
        "accumulate_and_advance":  "accumulate_and_advance", # skip
        END:                       END,                   # auth halt
    }
)

graph.add_edge("post_to_ingest_api", END)

app = graph.compile(checkpointer=MemorySaver())
```

### Routing functions

```python
def route_after_find_pr(state: GitHubMetricsState) -> str:
    if state.get("_current_error"):
        return "handle_error"
    if state.get("_current_pr") is None:
        # No PR found — treat as NOT_FOUND and skip
        return "handle_error"
    return "fetch_pr_details"

def route_after_fetch(state: GitHubMetricsState) -> str:
    if state.get("_current_error"):
        return "handle_error"
    return "compute_metrics"

def route_after_accumulate(state: GitHubMetricsState) -> str:
    if state["current_idx"] >= len(state["stories"]):
        return "post_to_ingest_api"
    return "find_pr_for_story"

def route_after_error(state: GitHubMetricsState) -> str:
    last_error = state["errors"][-1]
    error_type = last_error["error_type"]
    if error_type == "AUTH_ERROR":
        return END                         # halt — cannot recover
    if error_type == "NOT_FOUND":
        return "accumulate_and_advance"    # skip this story
    if error_type == "RATE_LIMIT":
        return "find_pr_for_story"         # retry after wait
    # API_5XX — retry up to 3 times then skip
    retries = sum(1 for e in state["errors"]
                  if e["error_type"] == "API_5XX"
                  and e.get("story_id") == last_error.get("story_id"))
    if retries < 3:
        return "find_pr_for_story"
    return "accumulate_and_advance"
```

---

## 7. GitHub API usage

### Token requirements

```
Type:         Fine-grained personal access token
Permissions:  Contents (read), Pull requests (read)
Scope:        Single repository — not all repositories
Rotation:     Manual — added to .env, not committed

Create at:    github.com/settings/tokens?type=beta
```

### Rate limits

```
Authenticated:   5,000 requests/hour
Per story:       ~3 requests (find PR + reviews + comments page 1)
Per sprint:      15 stories × 3 = ~45 requests
Safety margin:   Well within limits for normal sprint sizes

Rate limit handling:
  HTTP 403 with X-RateLimit-Remaining: 0
  Wait until X-RateLimit-Reset (Unix timestamp)
  Print: "GitHub rate limit — resuming at HH:MM:SS"
  Retry automatically — no manual intervention needed
```

### Endpoints called

```
GET /repos/{owner}/{repo}/pulls
  params: state=closed, head={owner}:{branch}, per_page=5
  Purpose: find merged PR by branch name

GET /repos/{owner}/{repo}/pulls/{number}/reviews
  Purpose: get review events with timestamps

GET /repos/{owner}/{repo}/pulls/{number}/comments
  params: per_page=100, page=N
  Purpose: get inline review comments (paginated)
```

---

## 8. Testing strategy — three layers

### Layer 1 — Unit tests (no external calls)

All nodes tested in isolation with `unittest.mock.patch("requests.get")`.
No real GitHub API calls. No LangGraph graph execution.
Fast — full suite under 5 seconds.

```
test_load_stories.py          happy path, empty list, malformed
test_find_pr_for_story.py     found, not found, rate limit, auth error
test_fetch_pr_details.py      normal, zero changes, missing fields
test_fetch_reviews.py         reviews + comments, pagination, bots filtered
test_compute_metrics.py       pickup time, no reviews, pr size
test_accumulate.py            middle, last story, routing
test_handle_error.py          each error type → correct route
test_post_to_ingest.py        success, re-ingest, API unavailable
```

### Layer 2 — Integration tests (full graph, mocked requests)

Full graph execution with `unittest.mock.patch("requests.get")`.
Mocked responses simulate all scenarios.
Tests the full state flow and routing logic.

```
test_graph_integration.py

  test_happy_path_10_stories:
    All 10 PRs found. All enriched. Ingest called once.
    Assert: len(enriched) == 10, ingest_status == SUCCESS

  test_story_with_no_pr_skipped:
    Story 5 of 10 has no PR.
    Assert: enriched[4].enrich_status == NO_PR, len(enriched) == 10

  test_rate_limit_mid_run:
    Story 5 triggers rate limit. Handle_error waits. Story 5 retried.
    Assert: len(enriched) == 10, rate limit story eventually enriched

  test_auth_error_halts_graph:
    Story 3 triggers auth error.
    Assert: graph ends at story 3, ingest not called

  test_resume_from_checkpoint:
    Run halted at story 5. New run with same thread_id.
    Assert: resumes from story 5, does not re-process 1-4

  test_5xx_retry_then_skip:
    Story 7 returns 5xx three times.
    Assert: story 7 marked ERROR, other stories enriched
```

### Layer 3 — No evals

This agent makes no LLM calls. Layer 3 does not exist.
The integration test suite covers all behaviour deterministically.

---

## 9. Project structure

```
agents/
  github_metrics/
    __init__.py
    state.py              GitHubMetricsState TypedDict definition
    graph.py              Graph wiring + routing functions
    runner.py             Entry point called by aggregate-metrics.py
    nodes/
      __init__.py
      load_stories.py
      find_pr.py
      fetch_pr_details.py
      fetch_reviews.py
      compute_metrics.py
      accumulate.py
      handle_error.py
      post_to_ingest.py
    tests/
      unit/
        test_load_stories.py
        test_find_pr.py
        test_fetch_pr_details.py
        test_fetch_reviews.py
        test_compute_metrics.py
        test_accumulate.py
        test_handle_error.py
        test_post_to_ingest.py
      integration/
        test_graph_integration.py
```

---

## 10. Dependencies

```toml
# pyproject.toml additions for github_metrics agent
[tool.poetry.dependencies]
langgraph = ">=0.2"
langchain-core = ">=0.2"
requests = ">=2.31"

[tool.poetry.dev-dependencies]
pytest = ">=7"
pytest-cov = ">=4"
```

No boto3 or moto — this agent does not use AWS services.

---

## 11. Integration with aggregate-metrics.py

The agent is invoked as the final step in the aggregation pipeline:

```python
# pipeline/scripts/aggregate-metrics.py

def run(agent_dir: str, ingest_url: str) -> None:
    # Step 1 — read .agent/ files (existing)
    stories = read_agent_files(agent_dir)
    base_payload = build_base_payload(stories)

    # Step 2 — GitHub enrichment (new)
    enriched_payload = base_payload
    if os.environ.get("GITHUB_TOKEN") and os.environ.get("GITHUB_REPO"):
        print("GitHub enrichment enabled")
        from agents.github_metrics.runner import enrich
        result = enrich(
            project_id=base_payload["project_id"],
            sprint_num=base_payload["sprint_num"],
            stories=base_payload["stories"],
            ingest_url=ingest_url,
        )
        print(f"{result['enriched_count']} stories enriched from GitHub")
        if result["skipped_count"] > 0:
            print(f"{result['skipped_count']} skipped (no PR found)")
        return  # runner handles ingest
    else:
        print("GitHub enrichment skipped — GITHUB_TOKEN or GITHUB_REPO not set")

    # Step 3 — ingest base payload (only if enrichment skipped)
    post_ingest(base_payload, ingest_url)
```

---

## 12. Environment variables

```bash
# Required for GitHub enrichment
GITHUB_TOKEN=ghp_your_fine_grained_token
GITHUB_REPO=your-org/your-repo

# Ingest endpoint (same as dashboard)
YOOTI_DASHBOARD_API_URL=http://localhost:4566/restapis/local/_user_request_
YOOTI_DASHBOARD_API_KEY=   # empty for local
```

---

## 13. Key architectural decisions

### D1 — LangGraph for state not intelligence

LangGraph is chosen for checkpoint/resume, conditional routing, and
accumulated state — not for LLM inference. This keeps the agent
fast, deterministic, and zero-cost per run.

### D2 — Errors accumulate, they do not halt

All error types except AUTH_ERROR are non-fatal. The run continues,
errors are logged in state, and the summary reports what was skipped.
A 30-story sprint where 2 stories have no PR should not fail.

### D3 — Branch naming convention drives PR discovery

The agent finds PRs by branch name. The Yooti convention `feature/{story_id}`
is the primary search. Fallbacks try lowercase and uppercase story_id.
Teams using different conventions can extend `find_pr_for_story`.

### D4 — No AWS services

The agent calls the GitHub API and the Yooti ingest API.
It does not call DynamoDB, Lambda, or any other AWS service directly.
This keeps IAM permissions simple and the agent portable.

### D5 — MemorySaver for local checkpointing

LangGraph's MemorySaver checkpoints state to memory during a run.
If the process is interrupted, a restart with the same thread_id resumes
from the last checkpoint. For long sprints (50+ stories) this is valuable.

---

## 14. Constraints the architect must enforce at Gate G2

```
LANGGRAPH CONSTITUTION
  Nodes return dicts of updated fields — never mutate state in place
  Nodes return {"error_type": ..., "message": ...} on failure — never raise
  Every node independently testable with a plain dict
  State fields use Optional for anything that may not be present

GITHUB API
  GITHUB_TOKEN always from os.environ — never hardcoded
  GITHUB_REPO always from os.environ — never hardcoded
  Fine-grained token with read-only scope — confirmed in .env.example
  Rate limit handling required in handle_error node

TESTING
  No real GitHub API calls in any unit test — mock requests.get
  No LangGraph graph execution in unit tests — test nodes in isolation
  Integration tests execute the full compiled graph with mocked requests
  No Layer 3 evals — this agent makes no LLM calls
```

---

## 15. Open questions for Gate G2 discussion

1. Branch naming: what conventions does the team use beyond `feature/{id}`?
   Are there hotfix/, bugfix/, or chore/ prefixes that should be tried?

2. Bot filtering: the current filter excludes users where type == "Bot".
   Does the team use any human accounts that should also be excluded
   (e.g. a shared team review account)?

3. Pagination limit: comments are paginated 100 per page indefinitely.
   Should there be a maximum page limit for very large PRs?

4. Checkpoint persistence: MemorySaver is in-memory only. If the process
   crashes (not interrupted gracefully), the checkpoint is lost.
   Should we use SqliteSaver for disk-based persistence?

5. Historical enrichment: should the agent be able to enrich past sprints
   retroactively, or only the current sprint?

---

*Architecture document for Gate G2 review — GitHub Metrics Enrichment Agent*
*Status: pending architect approval*
