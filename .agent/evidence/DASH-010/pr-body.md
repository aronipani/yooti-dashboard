## DASH-010 — Wire dashboard tabs to real API hooks

### Acceptance criteria coverage
| AC | Status | Test |
|----|--------|------|
| AC-1 Real API hooks, not placeholders | PASS | ProductivityTab.test.tsx, DoraTab.test.tsx, QualityTab.test.tsx, AgentEfficiencyTab.test.tsx, ValueTab.test.tsx, StoryDrilldownTab.test.tsx |
| AC-2 Real metrics in KPI cards | PASS | All tab tests verify data renders |
| AC-3 Error state on API failure | PASS | All tab tests verify error state with retry |
| AC-4 Sprint selector triggers refresh | PASS | DashboardLayout.test.tsx |
| AC-5 Productivity: velocity, cycle time | PASS | ProductivityTab.test.tsx |
| AC-6 DORA: deploy freq, lead time, CFR | PASS | DoraTab.test.tsx |
| AC-7 Quality: coverage, mutation score | PASS | QualityTab.test.tsx |
| AC-8 Agent: iterations, escalation rate | PASS | AgentEfficiencyTab.test.tsx |
| AC-9 Value: stories, trends | PASS | ValueTab.test.tsx |
| AC-10 Story drill-down with detail | PASS | StoryDrilldownTab.test.tsx |

### Test results
Unit: 108/108 passing · Integration: 0/0 · Regression: 0 newly failing

### Coverage
Overall: 80.0% · New code: 92.0%

### Accessibility
Violations: 0 · Passes: 108 (all tests include axe-core)

### Security
Snyk: 0 critical, 0 high · Semgrep: 0 findings

### Files changed
- `src/pages/DashboardLayout.tsx` — Added projectId/selectedSprint state, replaced static select with SprintSelector, passes props to tabs
- `src/pages/ProductivityTab.tsx` — Replaced usePlaceholder with useCurrentMetrics, maps snapshot fields to KPI cards
- `src/pages/DoraTab.tsx` — Replaced usePlaceholder with useCurrentMetrics, maps DORA fields
- `src/pages/QualityTab.tsx` — Replaced usePlaceholder with useCurrentMetrics, maps quality fields
- `src/pages/AgentEfficiencyTab.tsx` — Replaced usePlaceholder with useCurrentMetrics, maps agent fields + escalation_breakdown
- `src/pages/ValueTab.tsx` — Replaced usePlaceholder with useCurrentMetrics + useTrends
- `src/pages/StoryDrilldownTab.tsx` — Replaced usePlaceholder with useSprintDetail + useStoryDetail
- `src/lib/hooks/useSprintList.ts` — Fixed path: /sprints → /metrics/sprints
- `src/lib/hooks/useSprintDetail.ts` — Fixed path: /sprints/:num → /metrics/sprint/:num
- `src/lib/hooks/useTrends.ts` — Fixed path: /trends → /metrics/trends
- `src/lib/hooks/useStoryDetail.ts` — Fixed path and added sprint query param

### Deliberate decisions
- All 4 overview tabs share useCurrentMetrics — one cached API call via React Query, no redundant fetches
- Hook API paths corrected to match SAM template routes (/metrics/sprints, /metrics/sprint/:num, etc.)
- StoryDrilldownTab shows "select a sprint" prompt when no sprint chosen, avoiding unnecessary API call
- DashboardLayout reads VITE_PROJECT_ID from env with fallback to 'yooti-dashboard'

### Code audit
No violations found. 44/44 checks passed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
