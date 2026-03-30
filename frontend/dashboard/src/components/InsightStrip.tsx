/**
 * InsightStrip — horizontal strip of alert banners.
 * Severity-based colouring: critical = red, warn = amber, info = blue.
 */
import { clsx } from 'clsx'
import { AlertTriangle, AlertCircle, Info } from 'lucide-react'

export interface InsightAlert {
  /** Category of the alert */
  type: string
  /** Severity level: 'critical' | 'warn' | 'info' */
  severity: string
  /** Human-readable alert message */
  message: string
}

export interface InsightStripProps {
  /** List of alerts to display */
  alerts: InsightAlert[]
}

const severityStyles: Record<string, string> = {
  critical: 'bg-red-100 text-red-800 border-red-200',
  warn: 'bg-amber-100 text-amber-800 border-amber-200',
  info: 'bg-blue-100 text-blue-800 border-blue-200',
}

const severityIcons: Record<string, typeof AlertTriangle> = {
  critical: AlertCircle,
  warn: AlertTriangle,
  info: Info,
}

export function InsightStrip({ alerts }: InsightStripProps) {
  if (alerts.length === 0) return null

  return (
    <div
      className="flex flex-col gap-2 md:flex-row md:flex-wrap"
      role="region"
      aria-label="Insights and alerts"
    >
      {alerts.map((alert, index) => {
        const Icon = severityIcons[alert.severity] ?? Info
        return (
          <div
            key={`${alert.type}-${index}`}
            className={clsx(
              'flex items-center gap-2 rounded-md border px-3 py-2 text-sm font-medium',
              severityStyles[alert.severity] ?? severityStyles.info,
            )}
            role="alert"
          >
            <Icon className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
            <span>{alert.message}</span>
          </div>
        )
      })}
    </div>
  )
}
