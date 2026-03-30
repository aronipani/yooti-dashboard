/**
 * Unit tests for the AgentEfficiencyTab component.
 * Tests loading state and accessibility.
 */
import React from 'react'
import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { AgentEfficiencyTab } from '../../src/pages/AgentEfficiencyTab'

describe('AgentEfficiencyTab', () => {
  it('shows loading skeleton when no data is available', () => {
    renderWithProviders(<AgentEfficiencyTab />)

    expect(screen.getByRole('status', { name: 'Loading content' })).toBeInTheDocument()
  })

  it('has no accessibility violations in loading state', async () => {
    const { container } = renderWithProviders(<AgentEfficiencyTab />)

    await expectNoA11yViolations(container)
  })
})
