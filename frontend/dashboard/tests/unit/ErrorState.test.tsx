/**
 * Unit tests for the ErrorState component.
 * Tests error message display, retry button, and accessibility.
 */
import React from 'react'
import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'
import { ErrorState } from '../../src/components/ErrorState'

describe('ErrorState', () => {
  it('renders the error message', () => {
    renderWithProviders(<ErrorState message="Something went wrong" />)

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })

  it('has role="alert" for assistive technology', () => {
    renderWithProviders(<ErrorState message="Error occurred" />)

    expect(screen.getByRole('alert')).toBeInTheDocument()
  })

  it('shows retry button when onRetry is provided', () => {
    renderWithProviders(<ErrorState message="Failed" onRetry={vi.fn()} />)

    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument()
  })

  it('does not show retry button when onRetry is not provided', () => {
    renderWithProviders(<ErrorState message="Failed" />)

    expect(screen.queryByRole('button', { name: 'Retry' })).not.toBeInTheDocument()
  })

  it('calls onRetry when retry button is clicked', async () => {
    const onRetry = vi.fn()
    const user = userEvent.setup()

    renderWithProviders(<ErrorState message="Failed" onRetry={onRetry} />)

    await user.click(screen.getByRole('button', { name: 'Retry' }))

    expect(onRetry).toHaveBeenCalledOnce()
  })

  it('has no accessibility violations with retry button', async () => {
    const { container } = renderWithProviders(
      <ErrorState message="Something went wrong" onRetry={vi.fn()} />
    )

    await expectNoA11yViolations(container)
  })

  it('has no accessibility violations without retry button', async () => {
    const { container } = renderWithProviders(
      <ErrorState message="Something went wrong" />
    )

    await expectNoA11yViolations(container)
  })
})
