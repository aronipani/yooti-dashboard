/**
 * Unit tests for the KpiCard component.
 * Tests rendering, formatting, trend badge integration, and accessibility.
 */
import React from 'react'
import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { KpiCard } from '../../src/components/KpiCard'

describe('KpiCard', () => {
  it('renders label and numeric value', () => {
    renderWithProviders(<KpiCard label="Cycle Time" value={2.5} />)

    expect(screen.getByText('Cycle Time')).toBeInTheDocument()
    expect(screen.getByText('2.5')).toBeInTheDocument()
  })

  it('renders string value as-is', () => {
    renderWithProviders(<KpiCard label="Status" value="Healthy" />)

    expect(screen.getByText('Healthy')).toBeInTheDocument()
  })

  it('formats value as percent when format is percent', () => {
    renderWithProviders(<KpiCard label="Completion" value={85} format="percent" />)

    expect(screen.getByText('85%')).toBeInTheDocument()
  })

  it('formats value as hours when format is hours', () => {
    renderWithProviders(<KpiCard label="Exec Time" value={4} format="hours" />)

    expect(screen.getByText('4h')).toBeInTheDocument()
  })

  it('formats value as days when format is days', () => {
    renderWithProviders(<KpiCard label="Cycle" value={3} format="days" />)

    expect(screen.getByText('3d')).toBeInTheDocument()
  })

  it('shows TrendBadge when previousValue and numeric value are provided', () => {
    renderWithProviders(
      <KpiCard label="Coverage" value={92} previousValue={85} goodDirection="up" />
    )

    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('does not show TrendBadge when previousValue is not provided', () => {
    renderWithProviders(<KpiCard label="Coverage" value={92} />)

    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })

  it('does not show TrendBadge when value is a string', () => {
    renderWithProviders(
      <KpiCard label="Status" value="OK" previousValue={10} />
    )

    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })

  it('has an accessible article with label and value', () => {
    renderWithProviders(<KpiCard label="Shipped" value={8} format="number" />)

    const article = screen.getByRole('article')
    expect(article).toHaveAttribute('aria-label', 'Shipped: 8')
  })

  it('has no accessibility violations', async () => {
    const { container } = renderWithProviders(
      <KpiCard label="Completion" value={85} previousValue={80} format="percent" goodDirection="up" />
    )

    await expectNoA11yViolations(container)
  })

  it('has no accessibility violations without trend badge', async () => {
    const { container } = renderWithProviders(
      <KpiCard label="Stories" value={10} />
    )

    await expectNoA11yViolations(container)
  })
})
