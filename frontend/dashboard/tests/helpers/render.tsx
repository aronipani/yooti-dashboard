/**
 * Test render helper — yooti-dashboard Frontend
 * Wraps components with providers for testing.
 * Always use renderWithProviders instead of render.
 *
 * Usage:
 *   import { renderWithProviders } from '../helpers/render'
 *   const { getByText } = renderWithProviders(<MyComponent />)
 */
import React, { type ReactElement } from 'react'
import { render, type RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { axe, toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)

function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })
}

// Add your providers here (router, theme, auth, etc.)
function AllProviders({ children }: { children: React.ReactNode }) {
  const queryClient = createTestQueryClient()
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, "wrapper">
) {
  return render(ui, { wrapper: AllProviders, ...options })
}

/**
 * Create a wrapper component for renderHook that includes all providers.
 */
export function createWrapper() {
  const queryClient = createTestQueryClient()
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    )
  }
}

/**
 * Run axe accessibility check on a container.
 * Call this in EVERY component test.
 *
 * Usage:
 *   const { container } = renderWithProviders(<Button />)
 *   await expectNoA11yViolations(container)
 */
export async function expectNoA11yViolations(container: HTMLElement) {
  const results = await axe(container)
  expect(results).toHaveNoViolations()
}
