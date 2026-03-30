/**
 * Unit tests for React Query hooks.
 * Mocks apiClient directly — no MSW dependency.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { createWrapper } from '../helpers/render'
import { apiClient } from '../../src/lib/api-client'
import {
  useCurrentMetrics,
  useSprintList,
  useSprintDetail,
  useTrends,
  useStoryDetail,
} from '../../src/lib/hooks'
import type {
  CurrentSnapshot,
  SprintSummary,
  SprintDetail,
  TrendPoint,
  StoryMetrics,
} from '../../src/lib/types'

vi.mock('../../src/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

const mockedGet = vi.mocked(apiClient.get)

const PROJECT_ID = 'proj-001'

/** Factory for a minimal SprintSummary. */
function makeSprintSummary(overrides: Partial<SprintSummary> = {}): SprintSummary {
  return {
    sprint_num: 1,
    project_id: PROJECT_ID,
    cycle_time_avg_days: 2.5,
    sprint_completion_pct: 85,
    stories_shipped: 8,
    stories_committed: 10,
    coverage_new_code_avg: 92,
    regression_rate_pct: 0,
    escalation_rate_pct: 5,
    deploy_frequency: 3,
    agent_exec_hrs_avg: 1.2,
    human_wait_hrs_avg: 4.0,
    iteration_avg: 2.1,
    correction_rate_pct: 10,
    constitution_pass_pct: 100,
    mutation_score_avg: 78,
    gate_rejection_rates: {},
    escalation_breakdown: {},
    phase_avg_hrs: {},
    insight_alerts: [],
    ...overrides,
  }
}

describe('useCurrentMetrics', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches current metrics for a project', async () => {
    const snapshot: CurrentSnapshot = {
      ...makeSprintSummary(),
      last_ingested_at: '2026-03-29T00:00:00Z',
    }
    mockedGet.mockResolvedValueOnce({ data: snapshot })

    const wrapper = createWrapper()
    const { result } = renderHook(() => useCurrentMetrics(PROJECT_ID), { wrapper })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(mockedGet).toHaveBeenCalledWith('/metrics/current', {
      params: { project_id: PROJECT_ID },
    })
    expect(result.current.data?.last_ingested_at).toBe('2026-03-29T00:00:00Z')
  })

  it('does not fetch when projectId is empty', () => {
    const wrapper = createWrapper()
    const { result } = renderHook(() => useCurrentMetrics(''), { wrapper })

    expect(result.current.fetchStatus).toBe('idle')
    expect(mockedGet).not.toHaveBeenCalled()
  })
})

describe('useSprintList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches sprint list for a project', async () => {
    const sprints: SprintSummary[] = [
      makeSprintSummary({ sprint_num: 1 }),
      makeSprintSummary({ sprint_num: 2 }),
    ]
    mockedGet.mockResolvedValueOnce({ data: sprints })

    const wrapper = createWrapper()
    const { result } = renderHook(() => useSprintList(PROJECT_ID), { wrapper })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(mockedGet).toHaveBeenCalledWith('/sprints', {
      params: { project_id: PROJECT_ID },
    })
    expect(result.current.data).toHaveLength(2)
  })
})

describe('useSprintDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches sprint detail for a specific sprint', async () => {
    const detail: SprintDetail = {
      sprint_num: 3,
      summary: makeSprintSummary({ sprint_num: 3 }),
      phase_avg_hrs: { planning: 2 },
      gate_rejection_rates: { G2: 0.1 },
      escalation_breakdown: { scope: 1 },
      stories: [],
    }
    mockedGet.mockResolvedValueOnce({ data: detail })

    const wrapper = createWrapper()
    const { result } = renderHook(
      () => useSprintDetail(PROJECT_ID, 3),
      { wrapper }
    )

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(mockedGet).toHaveBeenCalledWith('/sprints/3', {
      params: { project_id: PROJECT_ID },
    })
    expect(result.current.data?.sprint_num).toBe(3)
  })

  it('does not fetch when sprintNum is null', () => {
    const wrapper = createWrapper()
    const { result } = renderHook(
      () => useSprintDetail(PROJECT_ID, null),
      { wrapper }
    )

    expect(result.current.fetchStatus).toBe('idle')
    expect(mockedGet).not.toHaveBeenCalled()
  })
})

describe('useTrends', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches trends with optional metric filter', async () => {
    const trends: TrendPoint[] = [
      {
        sprint_num: 1,
        value: 85,
        delta_from_prev: 0,
        direction: 'flat',
        metric_name: 'sprint_completion_pct',
      },
    ]
    mockedGet.mockResolvedValueOnce({ data: trends })

    const wrapper = createWrapper()
    const { result } = renderHook(
      () => useTrends(PROJECT_ID, 'sprint_completion_pct'),
      { wrapper }
    )

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(mockedGet).toHaveBeenCalledWith('/trends', {
      params: { project_id: PROJECT_ID, metric: 'sprint_completion_pct' },
    })
    expect(result.current.data).toHaveLength(1)
  })

  it('fetches all trends when no metric is specified', async () => {
    mockedGet.mockResolvedValueOnce({ data: [] })

    const wrapper = createWrapper()
    const { result } = renderHook(
      () => useTrends(PROJECT_ID),
      { wrapper }
    )

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(mockedGet).toHaveBeenCalledWith('/trends', {
      params: { project_id: PROJECT_ID },
    })
  })
})

describe('useStoryDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches story detail for a specific story', async () => {
    const story: StoryMetrics = {
      story_id: 'DASH-001',
      sprint_num: 2,
      type: 'feature',
      status: 'complete',
      cycle_time_hrs: 12,
      iteration_count: 3,
      escalation_type: null,
      correction_count: 1,
      coverage_new_code_pct: 95,
      gate_timestamps: { G1: '2026-03-28T10:00:00Z', G2: null },
      phase_durations: { planning: 2, coding: 8 },
      escalation_log: [],
    }
    mockedGet.mockResolvedValueOnce({ data: story })

    const wrapper = createWrapper()
    const { result } = renderHook(
      () => useStoryDetail(PROJECT_ID, 2, 'DASH-001'),
      { wrapper }
    )

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(mockedGet).toHaveBeenCalledWith('/sprints/2/stories/DASH-001', {
      params: { project_id: PROJECT_ID },
    })
    expect(result.current.data?.story_id).toBe('DASH-001')
  })

  it('does not fetch when storyId is null', () => {
    const wrapper = createWrapper()
    const { result } = renderHook(
      () => useStoryDetail(PROJECT_ID, 2, null),
      { wrapper }
    )

    expect(result.current.fetchStatus).toBe('idle')
    expect(mockedGet).not.toHaveBeenCalled()
  })

  it('does not fetch when sprintNum is null', () => {
    const wrapper = createWrapper()
    const { result } = renderHook(
      () => useStoryDetail(PROJECT_ID, null, 'DASH-001'),
      { wrapper }
    )

    expect(result.current.fetchStatus).toBe('idle')
    expect(mockedGet).not.toHaveBeenCalled()
  })
})
