/**
 * ErrorState — error message display with optional retry button.
 * Used as a fallback when data fetching or processing fails.
 */
import { AlertCircle } from 'lucide-react'

export interface ErrorStateProps {
  /** Human-readable error message */
  message: string
  /** Callback to retry the failed operation */
  onRetry?: () => void
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div
      className="flex flex-col items-center justify-center gap-4 rounded-lg border border-red-200 bg-red-50 p-8 text-center"
      role="alert"
    >
      <AlertCircle className="h-10 w-10 text-red-500" aria-hidden="true" />
      <p className="text-sm font-medium text-red-800">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
        >
          Retry
        </button>
      )}
    </div>
  )
}
