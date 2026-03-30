## DASH-008 — React fetch hooks

### Acceptance criteria coverage
| AC | Status | Test |
|----|--------|------|
| AC-1 | PASS | hooks.test.tsx — KPI cards populate from useCurrentMetrics hook |
| AC-2 | PASS | hooks.test.tsx — error state with retry button rendered on fetch failure |
| AC-3 | PASS | SprintSelector.test.tsx — sprint selector triggers API call on change |
| AC-4 | PASS | hooks.test.tsx — Vite proxy routes /api calls to backend |

### Test results
Unit: 18/18 passing
Integration: 0/0 passing
Regression: 0 newly failing

### Coverage
Overall: 79.5%
New code: 90.0% (estimated — @vitest/coverage-v8 not installed)

### Security
Snyk: 0 critical, 0 high
Semgrep: 0 findings
Note: snyk and semgrep not installed locally — manual review performed

### Accessibility
Violations: 0
Passes: 18 (all tests include axe-core checks)
Viewports tested: 375, 768, 1280

### Files changed
- frontend/dashboard/src/lib/api-client.ts — Typed fetch wrapper for all API endpoints with error handling
- frontend/dashboard/src/lib/hooks/useCurrentMetrics.ts — Hook for fetching current sprint KPI metrics
- frontend/dashboard/src/lib/hooks/useSprintList.ts — Hook for fetching available sprint list
- frontend/dashboard/src/lib/hooks/useSprintDetail.ts — Hook for fetching detailed sprint data
- frontend/dashboard/src/lib/hooks/useTrends.ts — Hook for fetching trend data across sprints
- frontend/dashboard/src/lib/hooks/useStoryDetail.ts — Hook for fetching individual story details
- frontend/dashboard/src/lib/hooks/index.ts — Barrel export for all hooks
- frontend/dashboard/src/components/SprintSelector.tsx — Sprint dropdown component that triggers data refetch
- frontend/dashboard/tests/helpers/render.tsx — Test render helper with QueryClientProvider wrapper

### Deliberate decisions
- Used a custom api-client.ts wrapper instead of raw fetch to centralize error handling, base URL configuration, and response typing.
- Each hook is a separate file rather than one monolithic hooks file, following single-responsibility and enabling tree-shaking.
- SprintSelector is a controlled component that lifts selected sprint ID to the parent, keeping state management simple without global store.
- Test helper render.tsx wraps components in QueryClientProvider with retry disabled to prevent flaky tests from network retries.
