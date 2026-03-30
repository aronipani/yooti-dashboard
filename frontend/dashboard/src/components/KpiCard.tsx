/**
 * KpiCard — displays a metric value, label, and optional trend badge.
 * Colour-coded: green if improving, red if worsening (based on goodDirection).
 */
import { TrendBadge } from './TrendBadge'

export interface KpiCardProps {
  /** Human-readable metric label */
  label: string
  /** Current metric value */
  value: string | number
  /** Previous period value for trend comparison */
  previousValue?: number
  /** How to format the value for display */
  format?: 'number' | 'percent' | 'hours' | 'days'
  /** Which direction is considered an improvement */
  goodDirection?: 'up' | 'down'
}

function formatValue(value: string | number, format?: string): string {
  if (typeof value === 'string') return value
  switch (format) {
    case 'percent':
      return `${value}%`
    case 'hours':
      return `${value}h`
    case 'days':
      return `${value}d`
    case 'number':
    default:
      return typeof value === 'number' ? value.toLocaleString() : String(value)
  }
}

export function KpiCard({
  label,
  value,
  previousValue,
  format,
  goodDirection = 'up',
}: KpiCardProps) {
  const numericValue = typeof value === 'number' ? value : undefined

  return (
    <article
      className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
      aria-label={`${label}: ${formatValue(value, format)}`}
    >
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <div className="mt-1 flex items-baseline gap-2">
        <span className="text-2xl font-semibold text-gray-900">
          {formatValue(value, format)}
        </span>
        {previousValue !== undefined && numericValue !== undefined && (
          <TrendBadge
            current={numericValue}
            previous={previousValue}
            goodDirection={goodDirection}
          />
        )}
      </div>
    </article>
  )
}
