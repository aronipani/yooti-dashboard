/**
 * TrendBadge — displays directional trend arrow with delta text.
 * Green if moving in goodDirection, red if opposite, gray if unchanged.
 */
import { clsx } from 'clsx'
import { ArrowUp, ArrowDown, Minus } from 'lucide-react'

export interface TrendBadgeProps {
  /** Current metric value */
  current: number
  /** Previous metric value for comparison */
  previous: number
  /** Which direction is considered an improvement */
  goodDirection: 'up' | 'down'
}

function computeDelta(current: number, previous: number): number {
  if (previous === 0) return 0
  return ((current - previous) / Math.abs(previous)) * 100
}

export function TrendBadge({ current, previous, goodDirection }: TrendBadgeProps) {
  const delta = computeDelta(current, previous)
  const roundedDelta = Math.round(delta * 10) / 10
  const isUp = current > previous
  const isDown = current < previous
  const isFlat = current === previous

  const isGood =
    (isUp && goodDirection === 'up') || (isDown && goodDirection === 'down')
  const isBad =
    (isUp && goodDirection === 'down') || (isDown && goodDirection === 'up')

  const colorClass = isFlat
    ? 'text-gray-500 bg-gray-100'
    : isGood
      ? 'text-green-700 bg-green-100'
      : 'text-red-700 bg-red-100'

  const Icon = isFlat ? Minus : isUp ? ArrowUp : ArrowDown

  const ariaLabel = isFlat
    ? 'No change'
    : `${isGood ? 'Improved' : 'Worsened'} by ${Math.abs(roundedDelta)}%`

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium',
        colorClass,
      )}
      aria-label={ariaLabel}
      role="status"
    >
      <Icon className="h-3 w-3" aria-hidden="true" />
      <span>{isFlat ? '0%' : `${roundedDelta > 0 ? '+' : ''}${roundedDelta}%`}</span>
    </span>
  )
}
