/**
 * Unit tests for the ValueTab component.
 * Tests loading state and accessibility.
 */
import React from 'react'
import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { ValueTab } from '../../src/pages/ValueTab'

describe('ValueTab', () => {
  it('shows loading skeleton when no data is available', () => {
    renderWithProviders(<ValueTab />)

    expect(screen.getByRole('status', { name: 'Loading content' })).toBeInTheDocument()
  })

  it('has no accessibility violations in loading state', async () => {
    const { container } = renderWithProviders(<ValueTab />)

    await expectNoA11yViolations(container)
  })
})
