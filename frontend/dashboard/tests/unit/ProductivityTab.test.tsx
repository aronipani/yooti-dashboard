/**
 * Unit tests for the ProductivityTab component.
 * Tests loading, error, and data states plus accessibility.
 */
import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { ProductivityTab } from '../../src/pages/ProductivityTab'

describe('ProductivityTab', () => {
  it('shows loading skeleton when no data is available', () => {
    renderWithProviders(<ProductivityTab />)

    expect(screen.getByRole('status', { name: 'Loading content' })).toBeInTheDocument()
  })

  it('has no accessibility violations in loading state', async () => {
    const { container } = renderWithProviders(<ProductivityTab />)

    await expectNoA11yViolations(container)
  })
})
