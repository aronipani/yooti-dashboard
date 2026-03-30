/**
 * Unit tests for the QualityTab component.
 * Tests loading, data rendering, error states, and accessibility.
 */
import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { QualityTab } from '../../src/pages/QualityTab'
import { apiClient } from '../../src/lib/api-client'
import type { CurrentSnapshot } from '../../src/lib/types'

vi.mock('../../src/lib/api-client', () => ({
  apiClient: { get: vi.fn(), post: vi.fn() },
}))

const mockedGet = vi.mocked(apiClient.get)

function makeSnapshot(overrides: Partial<CurrentSnapshot> = {}): CurrentSnapshot {
  return {
    sprint_num: 1, project_id: 'proj-001', cycle_time_avg_days: 2.5,
    sprint_completion_pct: 85, stories_shipped: 8, stories_committed: 10,
    coverage_new_code_avg: 92, regression_rate_pct: 3, escalation_rate_pct: 5,
    deploy_frequency: 4, agent_exec_hrs_avg: 1.2, human_wait_hrs_avg: 4.0,
    iteration_avg: 2.1, correction_rate_pct: 10, constitution_pass_pct: 98,
    mutation_score_avg: 78, gate_rejection_rates: {}, escalation_breakdown: {},
    phase_avg_hrs: {}, insight_alerts: [], last_ingested_at: '2026-03-29T00:00:00Z',
    ...overrides,
  }
}

describe('QualityTab', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('shows loading skeleton while fetching', () => {
    mockedGet.mockReturnValue(new Promise(() => {}))
    renderWithProviders(<QualityTab projectId="proj-001" />)
    expect(screen.getByRole('status', { name: 'Loading content' })).toBeInTheDocument()
  })

  it('renders quality KPI cards with real data', async () => {
    mockedGet.mockResolvedValueOnce({ data: makeSnapshot() })
    renderWithProviders(<QualityTab projectId="proj-001" />)

    await waitFor(() => {
      expect(screen.getByText('Code Coverage')).toBeInTheDocument()
    })

    expect(screen.getByText('92%')).toBeInTheDocument()
    expect(screen.getByText('78%')).toBeInTheDocument()
    expect(screen.getByText('98%')).toBeInTheDocument()
  })

  it('shows error state when API fails', async () => {
    mockedGet.mockRejectedValueOnce(new Error('fail'))
    renderWithProviders(<QualityTab projectId="proj-001" />)

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument()
    })
  })

  it('has no accessibility violations with data', async () => {
    mockedGet.mockResolvedValueOnce({ data: makeSnapshot() })
    const { container } = renderWithProviders(<QualityTab projectId="proj-001" />)

    await waitFor(() => {
      expect(screen.getByText('Code Coverage')).toBeInTheDocument()
    })

    await expectNoA11yViolations(container)
  })
})
