/**
 * Example React unit test — yooti-dashboard Frontend
 * Demonstrates component testing with accessibility checks.
 * Delete this file once you have real tests.
 */
import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders, expectNoA11yViolations } from '../helpers/render'

function ExampleButton({ label }: { label: string }) {
  return <button type="button">{label}</button>
}

describe('Example — React component test', () => {
  it('renders the button with label', () => {
    renderWithProviders(<ExampleButton label="Click me" />)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('has no accessibility violations', async () => {
    const { container } = renderWithProviders(<ExampleButton label="Click me" />)
    await expectNoA11yViolations(container)
  })
})
