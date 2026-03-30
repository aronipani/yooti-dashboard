/**
 * Unit tests for the DashboardLayout component.
 * Tests tab navigation, active tab rendering, and accessibility.
 */
import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { DashboardLayout } from '../../src/pages/DashboardLayout'

describe('DashboardLayout', () => {
  it('renders the dashboard title', () => {
    renderWithProviders(<DashboardLayout />)

    expect(screen.getByText('Yooti Dashboard')).toBeInTheDocument()
  })

  it('renders all six tab buttons', () => {
    renderWithProviders(<DashboardLayout />)

    const tabs = screen.getAllByRole('tab')
    expect(tabs).toHaveLength(6)

    expect(screen.getByRole('tab', { name: 'Productivity' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Quality' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Agent Efficiency' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Value' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'DORA' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Story Drill-down' })).toBeInTheDocument()
  })

  it('defaults to Productivity tab selected', () => {
    renderWithProviders(<DashboardLayout />)

    const productivityTab = screen.getByRole('tab', { name: 'Productivity' })
    expect(productivityTab).toHaveAttribute('aria-selected', 'true')
  })

  it('switches active tab on click', async () => {
    const user = userEvent.setup()
    renderWithProviders(<DashboardLayout />)

    const qualityTab = screen.getByRole('tab', { name: 'Quality' })
    await user.click(qualityTab)

    expect(qualityTab).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByRole('tab', { name: 'Productivity' })).toHaveAttribute(
      'aria-selected',
      'false'
    )
  })

  it('renders a tabpanel linked to the active tab', () => {
    renderWithProviders(<DashboardLayout />)

    const tabpanel = screen.getByRole('tabpanel')
    expect(tabpanel).toHaveAttribute('aria-labelledby', 'tab-productivity')
    expect(tabpanel).toHaveAttribute('id', 'tabpanel-productivity')
  })

  it('updates tabpanel id when switching tabs', async () => {
    const user = userEvent.setup()
    renderWithProviders(<DashboardLayout />)

    await user.click(screen.getByRole('tab', { name: 'DORA' }))

    const tabpanel = screen.getByRole('tabpanel')
    expect(tabpanel).toHaveAttribute('id', 'tabpanel-dora')
    expect(tabpanel).toHaveAttribute('aria-labelledby', 'tab-dora')
  })

  it('has a navigation landmark for tabs', () => {
    renderWithProviders(<DashboardLayout />)

    expect(screen.getByRole('navigation', { name: 'Dashboard tabs' })).toBeInTheDocument()
  })

  it('has a tablist role container', () => {
    renderWithProviders(<DashboardLayout />)

    expect(screen.getByRole('tablist')).toBeInTheDocument()
  })

  it('renders sprint selector in header', () => {
    renderWithProviders(<DashboardLayout />)

    expect(screen.getByLabelText('Select sprint')).toBeInTheDocument()
  })

  it('has no accessibility violations', async () => {
    const { container } = renderWithProviders(<DashboardLayout />)

    await expectNoA11yViolations(container)
  })
})
