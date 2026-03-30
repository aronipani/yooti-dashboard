/**
 * Unit tests for the QualityTab component.
 * Tests loading state and accessibility.
 */
import React from 'react'
import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { QualityTab } from '../../src/pages/QualityTab'

describe('QualityTab', () => {
  it('shows loading skeleton when no data is available', () => {
    renderWithProviders(<QualityTab />)

    expect(screen.getByRole('status', { name: 'Loading content' })).toBeInTheDocument()
  })

  it('has no accessibility violations in loading state', async () => {
    const { container } = renderWithProviders(<QualityTab />)

    await expectNoA11yViolations(container)
  })
})
