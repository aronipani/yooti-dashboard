/**
 * ChartWrapper — wraps a chart with loading, error, and empty states.
 * Provides a consistent container for all Chart.js visualisations.
 */
import { LoadingSkeleton } from './LoadingSkeleton'
import { ErrorState } from './ErrorState'

export interface ChartWrapperProps {
  /** Chart title displayed above the visualisation */
  title: string
  /** Whether data is currently loading */
  isLoading: boolean
  /** Whether an error occurred during data fetch */
  isError: boolean
  /** Error message to display when isError is true */
  errorMessage?: string
  /** Callback to retry the failed fetch */
  onRetry?: () => void
  /** Chart content to render when data is ready */
  children: React.ReactNode
}

export function ChartWrapper({
  title,
  isLoading,
  isError,
  errorMessage = 'Failed to load chart data',
  onRetry,
  children,
}: ChartWrapperProps) {
  return (
    <section
      className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
      aria-label={title}
    >
      <h3 className="mb-3 text-sm font-semibold text-gray-700">{title}</h3>
      {isLoading && <LoadingSkeleton variant="text" count={3} />}
      {isError && !isLoading && (
        <ErrorState message={errorMessage} onRetry={onRetry} />
      )}
      {!isLoading && !isError && (
        <div role="img" aria-label={`${title} chart`}>
          {children}
        </div>
      )}
    </section>
  )
}
