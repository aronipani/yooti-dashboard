/**
 * Unit tests for the SprintSelector component.
 * Tests loading, error, and success states plus accessibility.
 */
import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { SprintSelector } from '../../src/components/SprintSelector'
import { apiClient } from '../../src/lib/api-client'
import type { SprintSummary } from '../../src/lib/types'

vi.mock('../../src/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

const mockedGet = vi.mocked(apiClient.get)

const PROJECT_ID = 'proj-001'

function makeSprintSummary(num: number): SprintSummary {
  return {
    sprint_num: num,
    project_id: PROJECT_ID,
    cycle_time_avg_days: 2,
    sprint_completion_pct: 80,
    stories_shipped: 5,
    stories_committed: 6,
    coverage_new_code_avg: 90,
    regression_rate_pct: 0,
    escalation_rate_pct: 5,
    deploy_frequency: 2,
    agent_exec_hrs_avg: 1,
    human_wait_hrs_avg: 3,
    iteration_avg: 2,
    correction_rate_pct: 10,
    constitution_pass_pct: 100,
    mutation_score_avg: 75,
    gate_rejection_rates: {},
    escalation_breakdown: {},
    phase_avg_hrs: {},
    insight_alerts: [],
  }
}

describe('SprintSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading state while fetching sprints', () => {
    mockedGet.mockReturnValue(new Promise(() => {}))

    renderWithProviders(
      <SprintSelector projectId={PROJECT_ID} value={null} onChange={vi.fn()} />
    )

    expect(screen.getByTestId('sprint-selector-loading')).toBeInTheDocument()
  })

  it('shows error state with retry button on failure', async () => {
    mockedGet.mockRejectedValueOnce(new Error('Network error'))

    renderWithProviders(
      <SprintSelector projectId={PROJECT_ID} value={null} onChange={vi.fn()} />
    )

    await waitFor(() => {
      expect(screen.getByTestId('sprint-selector-error')).toBeInTheDocument()
    })

    expect(screen.getByText('Failed to load sprints.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
  })

  it('renders sprint options sorted descending after successful fetch', async () => {
    const sprints = [makeSprintSummary(1), makeSprintSummary(3), makeSprintSummary(2)]
    mockedGet.mockResolvedValueOnce({ data: sprints })

    renderWithProviders(
      <SprintSelector projectId={PROJECT_ID} value={null} onChange={vi.fn()} />
    )

    await waitFor(() => {
      expect(screen.getByTestId('sprint-selector')).toBeInTheDocument()
    })

    const options = screen.getAllByRole('option')
    // First option is the placeholder "Choose a sprint"
    expect(options[0]).toHaveTextContent('Choose a sprint')
    expect(options[1]).toHaveTextContent('Sprint 3')
    expect(options[2]).toHaveTextContent('Sprint 2')
    expect(options[3]).toHaveTextContent('Sprint 1')
  })

  it('calls onChange when a sprint is selected', async () => {
    const sprints = [makeSprintSummary(1), makeSprintSummary(2)]
    mockedGet.mockResolvedValueOnce({ data: sprints })
    const onChange = vi.fn()
    const user = userEvent.setup()

    renderWithProviders(
      <SprintSelector projectId={PROJECT_ID} value={null} onChange={onChange} />
    )

    await waitFor(() => {
      expect(screen.getByTestId('sprint-selector')).toBeInTheDocument()
    })

    await user.selectOptions(screen.getByTestId('sprint-selector'), '2')

    expect(onChange).toHaveBeenCalledWith(2)
  })

  it('shows the selected value', async () => {
    const sprints = [makeSprintSummary(1), makeSprintSummary(2)]
    mockedGet.mockResolvedValueOnce({ data: sprints })

    renderWithProviders(
      <SprintSelector projectId={PROJECT_ID} value={2} onChange={vi.fn()} />
    )

    await waitFor(() => {
      expect(screen.getByTestId('sprint-selector')).toBeInTheDocument()
    })

    expect(screen.getByTestId('sprint-selector')).toHaveValue('2')
  })

  it('has no accessibility violations in loaded state', async () => {
    const sprints = [makeSprintSummary(1), makeSprintSummary(2)]
    mockedGet.mockResolvedValueOnce({ data: sprints })

    const { container } = renderWithProviders(
      <SprintSelector projectId={PROJECT_ID} value={null} onChange={vi.fn()} />
    )

    await waitFor(() => {
      expect(screen.getByTestId('sprint-selector')).toBeInTheDocument()
    })

    await expectNoA11yViolations(container)
  })

  it('has no accessibility violations in loading state', async () => {
    mockedGet.mockReturnValue(new Promise(() => {}))

    const { container } = renderWithProviders(
      <SprintSelector projectId={PROJECT_ID} value={null} onChange={vi.fn()} />
    )

    await expectNoA11yViolations(container)
  })

  it('has no accessibility violations in error state', async () => {
    mockedGet.mockRejectedValueOnce(new Error('fail'))

    const { container } = renderWithProviders(
      <SprintSelector projectId={PROJECT_ID} value={null} onChange={vi.fn()} />
    )

    await waitFor(() => {
      expect(screen.getByTestId('sprint-selector-error')).toBeInTheDocument()
    })

    await expectNoA11yViolations(container)
  })
})
