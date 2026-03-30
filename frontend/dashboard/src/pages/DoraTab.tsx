/**
 * DoraTab — displays the four DORA metrics from useCurrentMetrics.
 */
import { KpiCard } from '../components/KpiCard'
import { InsightStrip } from '../components/InsightStrip'
import { LoadingSkeleton } from '../components/LoadingSkeleton'
import { ErrorState } from '../components/ErrorState'
import { useCurrentMetrics } from '../lib/hooks'

export interface DoraTabProps {
  projectId: string
}

export function DoraTab({ projectId }: DoraTabProps) {
  const { data, isLoading, isError, error, refetch } = useCurrentMetrics(projectId)

  if (isLoading) return <LoadingSkeleton variant="cards" count={4} />
  if (isError) return <ErrorState message={error?.message ?? 'Failed to load DORA metrics'} onRetry={() => { void refetch() }} />
  if (!data) return <LoadingSkeleton variant="cards" count={4} />

  const relevantAlerts = data.insight_alerts.filter(
    (a) => a.type === 'DORA_GAP'
  )

  return (
    <div className="space-y-6">
      <InsightStrip alerts={relevantAlerts} />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Deploy Frequency"
          value={data.deploy_frequency}
          format="number"
          goodDirection="up"
        />
        <KpiCard
          label="Lead Time"
          value={data.cycle_time_avg_days}
          format="days"
          goodDirection="down"
        />
        <KpiCard
          label="Change Failure Rate"
          value={data.regression_rate_pct}
          format="percent"
          goodDirection="down"
        />
        <KpiCard
          label="Time to Restore"
          value={data.human_wait_hrs_avg}
          format="hours"
          goodDirection="down"
        />
      </div>
    </div>
  )
}
