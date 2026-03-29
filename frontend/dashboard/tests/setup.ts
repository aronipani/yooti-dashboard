/**
 * Test setup — yooti-dashboard Frontend
 * Runs before every test file. Configures jsdom and testing-library.
 */
import { afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'

// Cleanup rendered components after each test
afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})
