/**
 * Unit tests for the StoryDrilldownTab component.
 * Tests loading, data rendering, story selection, and accessibility.
 */
import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { StoryDrilldownTab } from '../../src/pages/StoryDrilldownTab'
import { apiClient } from '../../src/lib/api-client'
import type { SprintDetail, StoryMetrics } from '../../src/lib/types'

vi.mock('../../src/lib/api-client', () => ({
  apiClient: { get: vi.fn(), post: vi.fn() },
}))

const mockedGet = vi.mocked(apiClient.get)

function makeSprintDetail(): SprintDetail {
  return {
    sprint_num: 3,
    summary: {
      sprint_num: 3, project_id: 'proj-001', cycle_time_avg_days: 2,
      sprint_completion_pct: 80, stories_shipped: 5, stories_committed: 6,
      coverage_new_code_avg: 90, regression_rate_pct: 0, escalation_rate_pct: 5,
      deploy_frequency: 2, agent_exec_hrs_avg: 1, human_wait_hrs_avg: 3,
      iteration_avg: 2, correction_rate_pct: 10, constitution_pass_pct: 100,
      mutation_score_avg: 75, gate_rejection_rates: {}, escalation_breakdown: {},
      phase_avg_hrs: {}, insight_alerts: [],
    },
    phase_avg_hrs: {},
    gate_rejection_rates: {},
    escalation_breakdown: {},
    stories: [
      {
        story_id: 'DASH-001', sprint_num: 3, type: 'feature', status: 'complete',
        cycle_time_hrs: 12, iteration_count: 3, escalation_type: null,
        correction_count: 1, coverage_new_code_pct: 95,
        gate_timestamps: {}, phase_durations: null, escalation_log: [],
      },
      {
        story_id: 'DASH-002', sprint_num: 3, type: 'feature', status: 'complete',
        cycle_time_hrs: 8, iteration_count: 2, escalation_type: null,
        correction_count: 0, coverage_new_code_pct: 92,
        gate_timestamps: {}, phase_durations: null, escalation_log: [],
      },
    ],
  }
}

describe('StoryDrilldownTab', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('shows loading skeleton while fetching', () => {
    mockedGet.mockReturnValue(new Promise(() => {}))
    renderWithProviders(<StoryDrilldownTab projectId="proj-001" selectedSprint={3} />)
    expect(screen.getByRole('status', { name: 'Loading content' })).toBeInTheDocument()
  })

  it('renders story table with real data', async () => {
    mockedGet.mockResolvedValue({ data: makeSprintDetail() })

    renderWithProviders(<StoryDrilldownTab projectId="proj-001" selectedSprint={3} />)

    await waitFor(() => {
      expect(screen.getAllByText('DASH-001').length).toBeGreaterThan(0)
    })

    expect(screen.getAllByText('DASH-002').length).toBeGreaterThan(0)
  })

  it('shows message when no sprint is selected', () => {
    renderWithProviders(<StoryDrilldownTab projectId="proj-001" selectedSprint={null} />)
    expect(screen.getByText(/select a sprint/i)).toBeInTheDocument()
  })

  it('shows error state when API fails', async () => {
    mockedGet.mockRejectedValue(new Error('fail'))
    renderWithProviders(<StoryDrilldownTab projectId="proj-001" selectedSprint={3} />)

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument()
    })
  })

  it('has no accessibility violations when no sprint selected', async () => {
    const { container } = renderWithProviders(
      <StoryDrilldownTab projectId="proj-001" selectedSprint={null} />
    )

    await expectNoA11yViolations(container)
  })
})
