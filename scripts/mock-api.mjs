/**
 * Lightweight mock API server for local dashboard development.
 * Serves seeded data from memory — no DynamoDB, no SAM, no Docker needed.
 *
 * Usage: node scripts/mock-api.mjs
 * Runs on http://localhost:3001
 */
import { createServer } from 'node:http'

const PORT = 3001

// ── Seed data ───────────────────────────────────────────────

const currentSnapshot = {
  sprint_num: 2,
  project_id: 'yooti-dashboard',
  cycle_time_avg_days: 2.1,
  sprint_completion_pct: 90,
  stories_shipped: 9,
  stories_committed: 10,
  coverage_new_code_avg: 92,
  regression_rate_pct: 0,
  escalation_rate_pct: 5,
  deploy_frequency: 4,
  agent_exec_hrs_avg: 1.3,
  human_wait_hrs_avg: 3.2,
  iteration_avg: 2.4,
  correction_rate_pct: 8,
  constitution_pass_pct: 100,
  mutation_score_avg: 80,
  gate_rejection_rates: { G2: 5, G3: 0 },
  escalation_breakdown: { SCOPE_ERROR: 1 },
  phase_avg_hrs: { requirements: 1, planning: 2, coding: 8, review: 3 },
  insight_alerts: [
    { type: 'QUALITY_DROP', severity: 'info', message: 'Mutation score 80% — approaching 85% target', metric: 'mutation_score_avg', value: 80, threshold: 85 },
  ],
  last_ingested_at: new Date().toISOString(),
}

const sprintSummaries = [
  {
    sprint_num: 2, project_id: 'yooti-dashboard',
    cycle_time_avg_days: 2.1, sprint_completion_pct: 90,
    stories_shipped: 9, stories_committed: 10,
    coverage_new_code_avg: 92, regression_rate_pct: 0,
    escalation_rate_pct: 5, deploy_frequency: 4,
    agent_exec_hrs_avg: 1.3, human_wait_hrs_avg: 3.2,
    iteration_avg: 2.4, correction_rate_pct: 8,
    constitution_pass_pct: 100, mutation_score_avg: 80,
    gate_rejection_rates: { G2: 5, G3: 0 },
    escalation_breakdown: { SCOPE_ERROR: 1 },
    phase_avg_hrs: { requirements: 1, planning: 2, coding: 8, review: 3 },
    insight_alerts: [],
  },
  {
    sprint_num: 1, project_id: 'yooti-dashboard',
    cycle_time_avg_days: 3.2, sprint_completion_pct: 78,
    stories_shipped: 7, stories_committed: 9,
    coverage_new_code_avg: 89, regression_rate_pct: 2,
    escalation_rate_pct: 11, deploy_frequency: 3,
    agent_exec_hrs_avg: 2.1, human_wait_hrs_avg: 5.4,
    iteration_avg: 3.1, correction_rate_pct: 15,
    constitution_pass_pct: 96, mutation_score_avg: 72,
    gate_rejection_rates: { G2: 10, G3: 5 },
    escalation_breakdown: { SCOPE_ERROR: 3, ENV_ERROR: 2, SPEC_AMBIGUITY: 1 },
    phase_avg_hrs: { requirements: 2, planning: 3, coding: 12, review: 4 },
    insight_alerts: [
      { type: 'BOTTLENECK', severity: 'warn', message: 'Coding phase averaging 12h', metric: 'phase_avg_hrs.coding', value: 12, threshold: 8 },
      { type: 'ESCALATION_SPIKE', severity: 'critical', message: 'Escalation rate 11% above threshold', metric: 'escalation_rate_pct', value: 11, threshold: 10 },
    ],
  },
]

const stories = [
  { story_id: 'DASH-001', sprint_num: 2, type: 'feature', status: 'complete', cycle_time_hrs: 14, iteration_count: 3, escalation_type: null, correction_count: 1, coverage_new_code_pct: 95, gate_timestamps: { G1: '2026-03-25T10:00:00Z', G2: '2026-03-26T14:00:00Z', G3: '2026-03-27T09:00:00Z' }, phase_durations: { requirements: 1, planning: 2, coding: 8, review: 3 }, escalation_log: [] },
  { story_id: 'DASH-002', sprint_num: 2, type: 'feature', status: 'complete', cycle_time_hrs: 10, iteration_count: 2, escalation_type: null, correction_count: 0, coverage_new_code_pct: 92, gate_timestamps: { G1: '2026-03-25T10:00:00Z', G2: '2026-03-26T14:00:00Z', G3: '2026-03-27T11:00:00Z' }, phase_durations: { requirements: 1, planning: 2, coding: 6, review: 1 }, escalation_log: [] },
  { story_id: 'DASH-003', sprint_num: 2, type: 'feature', status: 'complete', cycle_time_hrs: 6, iteration_count: 1, escalation_type: null, correction_count: 0, coverage_new_code_pct: 90, gate_timestamps: { G1: '2026-03-25T10:00:00Z', G2: '2026-03-26T14:00:00Z', G3: null }, phase_durations: { requirements: 1, planning: 1, coding: 3, review: 1 }, escalation_log: [] },
  { story_id: 'DASH-004', sprint_num: 2, type: 'feature', status: 'complete', cycle_time_hrs: 12, iteration_count: 2, escalation_type: null, correction_count: 1, coverage_new_code_pct: 91, gate_timestamps: { G1: '2026-03-25T10:00:00Z', G2: '2026-03-26T14:00:00Z', G3: null }, phase_durations: { requirements: 1, planning: 2, coding: 7, review: 2 }, escalation_log: [] },
  { story_id: 'DASH-005', sprint_num: 2, type: 'feature', status: 'complete', cycle_time_hrs: 16, iteration_count: 3, escalation_type: 'SCOPE_ERROR', correction_count: 2, coverage_new_code_pct: 88, gate_timestamps: { G1: '2026-03-25T10:00:00Z', G2: '2026-03-26T14:00:00Z', G3: null }, phase_durations: { requirements: 2, planning: 2, coding: 9, review: 3 }, escalation_log: [{ type: 'SCOPE_ERROR', task_id: 'T001', timestamp: '2026-03-27T08:00:00Z' }] },
  { story_id: 'DASH-006', sprint_num: 2, type: 'feature', status: 'complete', cycle_time_hrs: 4, iteration_count: 1, escalation_type: null, correction_count: 0, coverage_new_code_pct: 100, gate_timestamps: { G1: '2026-03-25T10:00:00Z', G2: '2026-03-26T14:00:00Z', G3: '2026-03-26T16:00:00Z' }, phase_durations: { requirements: 0.5, planning: 0.5, coding: 2, review: 1 }, escalation_log: [] },
  { story_id: 'DASH-007', sprint_num: 2, type: 'feature', status: 'complete', cycle_time_hrs: 11, iteration_count: 2, escalation_type: null, correction_count: 0, coverage_new_code_pct: 93, gate_timestamps: { G1: '2026-03-25T10:00:00Z', G2: '2026-03-26T14:00:00Z', G3: null }, phase_durations: { requirements: 1, planning: 2, coding: 6, review: 2 }, escalation_log: [] },
  { story_id: 'DASH-008', sprint_num: 2, type: 'feature', status: 'complete', cycle_time_hrs: 8, iteration_count: 2, escalation_type: null, correction_count: 0, coverage_new_code_pct: 94, gate_timestamps: { G1: '2026-03-25T10:00:00Z', G2: '2026-03-26T14:00:00Z', G3: null }, phase_durations: { requirements: 1, planning: 1, coding: 5, review: 1 }, escalation_log: [] },
  { story_id: 'DASH-009', sprint_num: 2, type: 'feature', status: 'in_progress', cycle_time_hrs: 20, iteration_count: 4, escalation_type: null, correction_count: 1, coverage_new_code_pct: 87, gate_timestamps: { G1: '2026-03-25T10:00:00Z', G2: '2026-03-26T14:00:00Z', G3: null }, phase_durations: { requirements: 2, planning: 3, coding: 12, review: 3 }, escalation_log: [] },
]

const trends = [
  { sprint_num: 1, value: 3.2, delta_from_prev: 0, direction: 'flat', metric_name: 'cycle_time_avg_days' },
  { sprint_num: 2, value: 2.1, delta_from_prev: -34.4, direction: 'down', metric_name: 'cycle_time_avg_days' },
  { sprint_num: 1, value: 78, delta_from_prev: 0, direction: 'flat', metric_name: 'sprint_completion_pct' },
  { sprint_num: 2, value: 90, delta_from_prev: 15.4, direction: 'up', metric_name: 'sprint_completion_pct' },
  { sprint_num: 1, value: 7, delta_from_prev: 0, direction: 'flat', metric_name: 'stories_shipped' },
  { sprint_num: 2, value: 9, delta_from_prev: 28.6, direction: 'up', metric_name: 'stories_shipped' },
  { sprint_num: 1, value: 9, delta_from_prev: 0, direction: 'flat', metric_name: 'stories_committed' },
  { sprint_num: 2, value: 10, delta_from_prev: 11.1, direction: 'up', metric_name: 'stories_committed' },
  { sprint_num: 1, value: 89, delta_from_prev: 0, direction: 'flat', metric_name: 'coverage_new_code_avg' },
  { sprint_num: 2, value: 92, delta_from_prev: 3.4, direction: 'up', metric_name: 'coverage_new_code_avg' },
  { sprint_num: 1, value: 3, delta_from_prev: 0, direction: 'flat', metric_name: 'deploy_frequency' },
  { sprint_num: 2, value: 4, delta_from_prev: 33.3, direction: 'up', metric_name: 'deploy_frequency' },
  { sprint_num: 1, value: 11, delta_from_prev: 0, direction: 'flat', metric_name: 'escalation_rate_pct' },
  { sprint_num: 2, value: 5, delta_from_prev: -54.5, direction: 'down', metric_name: 'escalation_rate_pct' },
]

// ── Router ──────────────────────────────────────────────────

function parseUrl(raw) {
  const url = new URL(raw, 'http://localhost')
  return { pathname: url.pathname, params: Object.fromEntries(url.searchParams) }
}

function json(res, status, body) {
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
  })
  res.end(JSON.stringify(body))
}

const server = createServer((req, res) => {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    json(res, 204, '')
    return
  }

  const { pathname, params } = parseUrl(req.url)

  // GET /metrics/current
  if (pathname === '/metrics/current' && req.method === 'GET') {
    json(res, 200, currentSnapshot)
    return
  }

  // GET /metrics/sprints
  if (pathname === '/metrics/sprints' && req.method === 'GET') {
    json(res, 200, sprintSummaries)
    return
  }

  // GET /metrics/sprint/:num
  const sprintMatch = pathname.match(/^\/metrics\/sprint\/(\d+)$/)
  if (sprintMatch && req.method === 'GET') {
    const num = parseInt(sprintMatch[1])
    const summary = sprintSummaries.find(s => s.sprint_num === num)
    if (!summary) {
      json(res, 404, { error: 'SPRINT_NOT_FOUND' })
      return
    }
    const sprintStories = stories.filter(s => s.sprint_num === num)
    json(res, 200, {
      sprint_num: num,
      summary,
      phase_avg_hrs: summary.phase_avg_hrs,
      gate_rejection_rates: summary.gate_rejection_rates,
      escalation_breakdown: summary.escalation_breakdown,
      stories: sprintStories,
    })
    return
  }

  // GET /metrics/trends
  if (pathname === '/metrics/trends' && req.method === 'GET') {
    const metric = params.metric
    const filtered = metric ? trends.filter(t => t.metric_name === metric) : trends
    json(res, 200, filtered)
    return
  }

  // GET /metrics/story/:id
  const storyMatch = pathname.match(/^\/metrics\/story\/(.+)$/)
  if (storyMatch && req.method === 'GET') {
    const storyId = decodeURIComponent(storyMatch[1])
    const story = stories.find(s => s.story_id === storyId)
    if (!story) {
      json(res, 404, { error: 'STORY_NOT_FOUND' })
      return
    }
    json(res, 200, story)
    return
  }

  // POST /metrics/ingest (accept and log, no-op for mock)
  if (pathname === '/metrics/ingest' && req.method === 'POST') {
    let body = ''
    req.on('data', chunk => { body += chunk })
    req.on('end', () => {
      console.log('[ingest]', body.substring(0, 200))
      json(res, 201, { sprint_num: 1, status: 'ingested' })
    })
    return
  }

  json(res, 404, { error: 'NOT_FOUND', path: pathname })
})

server.listen(PORT, () => {
  console.log(`Mock API running on http://localhost:${PORT}`)
  console.log('Endpoints:')
  console.log('  GET  /metrics/current')
  console.log('  GET  /metrics/sprints')
  console.log('  GET  /metrics/sprint/:num')
  console.log('  GET  /metrics/trends')
  console.log('  GET  /metrics/story/:id')
  console.log('  POST /metrics/ingest')
})
