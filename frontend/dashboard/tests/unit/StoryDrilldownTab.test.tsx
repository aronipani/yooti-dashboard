/**
 * Unit tests for the StoryDrilldownTab component.
 * Tests loading state and accessibility.
 */
import React from 'react'
import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { StoryDrilldownTab } from '../../src/pages/StoryDrilldownTab'

describe('StoryDrilldownTab', () => {
  it('shows loading skeleton when no data is available', () => {
    renderWithProviders(<StoryDrilldownTab />)

    expect(screen.getByRole('status', { name: 'Loading content' })).toBeInTheDocument()
  })

  it('has no accessibility violations in loading state', async () => {
    const { container } = renderWithProviders(<StoryDrilldownTab />)

    await expectNoA11yViolations(container)
  })
})
