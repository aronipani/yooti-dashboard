/**
 * Unit tests for the StoryDetailPanel component.
 * Tests rendering, close button, empty state, and accessibility.
 */
import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { StoryDetailPanel, type StoryDetail } from '../../src/components/StoryDetailPanel'

function makeStory(overrides: Partial<StoryDetail> = {}): StoryDetail {
  return {
    id: 'DASH-001',
    title: 'Build repository layer',
    status: 'complete',
    points: 5,
    assignee: 'Agent',
    cycleTimeDays: 2,
    agentIterations: 3,
    acPassed: 4,
    acTotal: 5,
    testCoverage: 95,
    timeline: [
      { date: '2026-03-28', event: 'G1 approved' },
      { date: '2026-03-29', event: 'PR opened' },
    ],
    ...overrides,
  }
}

describe('StoryDetailPanel', () => {
  it('renders nothing when story is null', () => {
    const { container } = renderWithProviders(
      <StoryDetailPanel story={null} onClose={vi.fn()} />
    )

    expect(container.firstChild).toBeNull()
  })

  it('renders story ID and title', () => {
    renderWithProviders(
      <StoryDetailPanel story={makeStory()} onClose={vi.fn()} />
    )

    expect(screen.getByText('DASH-001')).toBeInTheDocument()
    expect(screen.getByText('Build repository layer')).toBeInTheDocument()
  })

  it('renders all detail fields', () => {
    renderWithProviders(
      <StoryDetailPanel story={makeStory()} onClose={vi.fn()} />
    )

    expect(screen.getByText('complete')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.getByText('Agent')).toBeInTheDocument()
    expect(screen.getByText('2d')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('95%')).toBeInTheDocument()
  })

  it('renders acceptance criteria progress bar', () => {
    renderWithProviders(
      <StoryDetailPanel story={makeStory()} onClose={vi.fn()} />
    )

    expect(screen.getByText('4/5 (80%)')).toBeInTheDocument()
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '80')
  })

  it('renders timeline events', () => {
    renderWithProviders(
      <StoryDetailPanel story={makeStory()} onClose={vi.fn()} />
    )

    expect(screen.getByText('G1 approved')).toBeInTheDocument()
    expect(screen.getByText('PR opened')).toBeInTheDocument()
  })

  it('does not render timeline section when timeline is empty', () => {
    renderWithProviders(
      <StoryDetailPanel story={makeStory({ timeline: [] })} onClose={vi.fn()} />
    )

    expect(screen.queryByText('Timeline')).not.toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', async () => {
    const onClose = vi.fn()
    const user = userEvent.setup()

    renderWithProviders(
      <StoryDetailPanel story={makeStory()} onClose={onClose} />
    )

    await user.click(screen.getByRole('button', { name: 'Close detail panel' }))

    expect(onClose).toHaveBeenCalledOnce()
  })

  it('has an accessible aside with story ID label', () => {
    renderWithProviders(
      <StoryDetailPanel story={makeStory()} onClose={vi.fn()} />
    )

    expect(screen.getByRole('complementary')).toHaveAttribute(
      'aria-label',
      'Details for story DASH-001'
    )
  })

  it('has no accessibility violations', async () => {
    const { container } = renderWithProviders(
      <StoryDetailPanel story={makeStory()} onClose={vi.fn()} />
    )

    await expectNoA11yViolations(container)
  })

  it('has no accessibility violations when story is null', async () => {
    const { container } = renderWithProviders(
      <StoryDetailPanel story={null} onClose={vi.fn()} />
    )

    await expectNoA11yViolations(container)
  })
})
