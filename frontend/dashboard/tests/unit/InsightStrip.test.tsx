/**
 * Unit tests for the InsightStrip component.
 * Tests alert rendering, severity styling, and accessibility.
 */
import React from 'react'
import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { InsightStrip, type InsightAlert } from '../../src/components/InsightStrip'

function makeAlert(overrides: Partial<InsightAlert> = {}): InsightAlert {
  return {
    type: 'QUALITY_DROP',
    severity: 'warn',
    message: 'Coverage dropped below threshold',
    ...overrides,
  }
}

describe('InsightStrip', () => {
  it('renders nothing when alerts array is empty', () => {
    const { container } = renderWithProviders(<InsightStrip alerts={[]} />)

    expect(container.firstChild).toBeNull()
  })

  it('renders all alert messages', () => {
    const alerts = [
      makeAlert({ type: 'BOTTLENECK', message: 'Sprint bottleneck detected' }),
      makeAlert({ type: 'QUALITY_DROP', message: 'Coverage dropped' }),
    ]

    renderWithProviders(<InsightStrip alerts={alerts} />)

    expect(screen.getByText('Sprint bottleneck detected')).toBeInTheDocument()
    expect(screen.getByText('Coverage dropped')).toBeInTheDocument()
  })

  it('renders each alert with role="alert"', () => {
    const alerts = [
      makeAlert({ message: 'Alert one' }),
      makeAlert({ message: 'Alert two' }),
    ]

    renderWithProviders(<InsightStrip alerts={alerts} />)

    const alertElements = screen.getAllByRole('alert')
    expect(alertElements).toHaveLength(2)
  })

  it('applies red styling for critical severity', () => {
    const alerts = [makeAlert({ severity: 'critical', message: 'Critical issue' })]

    renderWithProviders(<InsightStrip alerts={alerts} />)

    const alert = screen.getByRole('alert')
    expect(alert.className).toContain('red')
  })

  it('applies amber styling for warn severity', () => {
    const alerts = [makeAlert({ severity: 'warn', message: 'Warning issue' })]

    renderWithProviders(<InsightStrip alerts={alerts} />)

    const alert = screen.getByRole('alert')
    expect(alert.className).toContain('amber')
  })

  it('applies blue styling for info severity', () => {
    const alerts = [makeAlert({ severity: 'info', message: 'Info notice' })]

    renderWithProviders(<InsightStrip alerts={alerts} />)

    const alert = screen.getByRole('alert')
    expect(alert.className).toContain('blue')
  })

  it('falls back to info styling for unknown severity', () => {
    const alerts = [makeAlert({ severity: 'unknown', message: 'Unknown severity' })]

    renderWithProviders(<InsightStrip alerts={alerts} />)

    const alert = screen.getByRole('alert')
    expect(alert.className).toContain('blue')
  })

  it('has an aria-label region for the strip container', () => {
    const alerts = [makeAlert()]

    renderWithProviders(<InsightStrip alerts={alerts} />)

    expect(screen.getByRole('region')).toHaveAttribute(
      'aria-label',
      'Insights and alerts'
    )
  })

  it('has no accessibility violations with multiple alerts', async () => {
    const alerts = [
      makeAlert({ severity: 'critical', message: 'Critical alert' }),
      makeAlert({ severity: 'warn', message: 'Warning alert' }),
      makeAlert({ severity: 'info', message: 'Info alert' }),
    ]

    const { container } = renderWithProviders(<InsightStrip alerts={alerts} />)

    await expectNoA11yViolations(container)
  })

  it('has no accessibility violations when empty', async () => {
    const { container } = renderWithProviders(<InsightStrip alerts={[]} />)

    await expectNoA11yViolations(container)
  })
})
