/**
 * Unit tests for the TrendBadge component.
 * Tests directional logic, colour coding, and accessibility.
 */
import React from 'react'
import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { TrendBadge } from '../../src/components/TrendBadge'

describe('TrendBadge', () => {
  describe('direction detection', () => {
    it('shows up arrow when current > previous', () => {
      renderWithProviders(
        <TrendBadge current={100} previous={80} goodDirection="up" />
      )

      const badge = screen.getByRole('status')
      expect(badge).toHaveTextContent('+25%')
    })

    it('shows down arrow when current < previous', () => {
      renderWithProviders(
        <TrendBadge current={80} previous={100} goodDirection="up" />
      )

      const badge = screen.getByRole('status')
      expect(badge).toHaveTextContent('-20%')
    })

    it('shows 0% when current equals previous', () => {
      renderWithProviders(
        <TrendBadge current={50} previous={50} goodDirection="up" />
      )

      const badge = screen.getByRole('status')
      expect(badge).toHaveTextContent('0%')
    })
  })

  describe('colour coding', () => {
    it('applies green when up is good and value increased', () => {
      renderWithProviders(
        <TrendBadge current={90} previous={80} goodDirection="up" />
      )

      const badge = screen.getByRole('status')
      expect(badge.className).toContain('green')
    })

    it('applies red when up is good but value decreased', () => {
      renderWithProviders(
        <TrendBadge current={70} previous={80} goodDirection="up" />
      )

      const badge = screen.getByRole('status')
      expect(badge.className).toContain('red')
    })

    it('applies green when down is good and value decreased', () => {
      renderWithProviders(
        <TrendBadge current={3} previous={5} goodDirection="down" />
      )

      const badge = screen.getByRole('status')
      expect(badge.className).toContain('green')
    })

    it('applies red when down is good but value increased', () => {
      renderWithProviders(
        <TrendBadge current={7} previous={5} goodDirection="down" />
      )

      const badge = screen.getByRole('status')
      expect(badge.className).toContain('red')
    })

    it('applies gray when value is unchanged', () => {
      renderWithProviders(
        <TrendBadge current={50} previous={50} goodDirection="up" />
      )

      const badge = screen.getByRole('status')
      expect(badge.className).toContain('gray')
    })
  })

  describe('aria labels', () => {
    it('has Improved aria-label when trend is good', () => {
      renderWithProviders(
        <TrendBadge current={90} previous={80} goodDirection="up" />
      )

      expect(screen.getByRole('status')).toHaveAttribute(
        'aria-label',
        expect.stringContaining('Improved')
      )
    })

    it('has Worsened aria-label when trend is bad', () => {
      renderWithProviders(
        <TrendBadge current={70} previous={80} goodDirection="up" />
      )

      expect(screen.getByRole('status')).toHaveAttribute(
        'aria-label',
        expect.stringContaining('Worsened')
      )
    })

    it('has No change aria-label when flat', () => {
      renderWithProviders(
        <TrendBadge current={50} previous={50} goodDirection="up" />
      )

      expect(screen.getByRole('status')).toHaveAttribute('aria-label', 'No change')
    })
  })

  describe('edge cases', () => {
    it('handles previous value of 0 without division error', () => {
      renderWithProviders(
        <TrendBadge current={10} previous={0} goodDirection="up" />
      )

      const badge = screen.getByRole('status')
      expect(badge).toHaveTextContent('0%')
    })
  })

  it('has no accessibility violations for improving trend', async () => {
    const { container } = renderWithProviders(
      <TrendBadge current={90} previous={80} goodDirection="up" />
    )

    await expectNoA11yViolations(container)
  })

  it('has no accessibility violations for worsening trend', async () => {
    const { container } = renderWithProviders(
      <TrendBadge current={70} previous={80} goodDirection="up" />
    )

    await expectNoA11yViolations(container)
  })
})
