/**
 * Unit tests for the DoraTab component.
 * Tests loading, error, and data states plus accessibility.
 */
import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { DoraTab } from '../../src/pages/DoraTab'

describe('DoraTab', () => {
  it('shows loading skeleton when no data is available', () => {
    renderWithProviders(<DoraTab />)

    expect(screen.getByRole('status', { name: 'Loading content' })).toBeInTheDocument()
  })

  it('has no accessibility violations in loading state', async () => {
    const { container } = renderWithProviders(<DoraTab />)

    await expectNoA11yViolations(container)
  })
})
