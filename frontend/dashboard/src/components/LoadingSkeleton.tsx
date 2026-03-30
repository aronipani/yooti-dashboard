/**
 * LoadingSkeleton — animated pulse placeholder while data loads.
 * Supports different layout variants for cards, tables, and text.
 */

export interface LoadingSkeletonProps {
  /** Layout variant: 'cards' renders a grid, 'table' renders rows, 'text' renders lines */
  variant?: 'cards' | 'table' | 'text'
  /** Number of skeleton items to render */
  count?: number
}

function SkeletonCard() {
  return (
    <div className="animate-pulse rounded-lg border border-gray-200 bg-white p-4">
      <div className="h-3 w-24 rounded bg-gray-200" />
      <div className="mt-3 h-6 w-16 rounded bg-gray-200" />
      <div className="mt-2 h-3 w-12 rounded bg-gray-200" />
    </div>
  )
}

function SkeletonRow() {
  return (
    <div className="flex animate-pulse gap-4 border-b border-gray-100 py-3">
      <div className="h-4 w-32 rounded bg-gray-200" />
      <div className="h-4 w-20 rounded bg-gray-200" />
      <div className="h-4 w-16 rounded bg-gray-200" />
      <div className="h-4 w-24 rounded bg-gray-200" />
    </div>
  )
}

function SkeletonLine() {
  return (
    <div className="animate-pulse py-1">
      <div className="h-4 w-full rounded bg-gray-200" />
    </div>
  )
}

export function LoadingSkeleton({ variant = 'cards', count = 4 }: LoadingSkeletonProps) {
  const items = Array.from({ length: count }, (_, i) => i)

  return (
    <div role="status" aria-label="Loading content">
      <span className="sr-only">Loading...</span>
      {variant === 'cards' && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {items.map((i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      )}
      {variant === 'table' && (
        <div className="space-y-0">
          {items.map((i) => (
            <SkeletonRow key={i} />
          ))}
        </div>
      )}
      {variant === 'text' && (
        <div className="space-y-2">
          {items.map((i) => (
            <SkeletonLine key={i} />
          ))}
        </div>
      )}
    </div>
  )
}
