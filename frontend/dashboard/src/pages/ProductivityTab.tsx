/**
 * ProductivityTab — displays velocity, throughput, and cycle time metrics.
 * Wired to useCurrentMetrics for real API data.
 */
import { KpiCard } from '../components/KpiCard'
import { InsightStrip } from '../components/InsightStrip'
import { LoadingSkeleton } from '../components/LoadingSkeleton'
import { ErrorState } from '../components/ErrorState'
import { useCurrentMetrics } from '../lib/hooks'

export interface ProductivityTabProps {
  projectId: string
}

export function ProductivityTab({ projectId }: ProductivityTabProps) {
  const { data, isLoading, isError, error, refetch } = useCurrentMetrics(projectId)

  if (isLoading) return <LoadingSkeleton variant="cards" count={4} />
  if (isError) return <ErrorState message={error?.message ?? 'Failed to load productivity data'} onRetry={() => { void refetch() }} />
  if (!data) return <LoadingSkeleton variant="cards" count={4} />

  const relevantAlerts = data.insight_alerts.filter(
    (a) => a.type === 'BOTTLENECK' || a.type === 'HUMAN_VS_AGENT'
  )

  return (
    <div className="space-y-6">
      <InsightStrip alerts={relevantAlerts} />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Stories Shipped"
          value={data.stories_shipped}
          format="number"
          goodDirection="up"
        />
        <KpiCard
          label="Stories Committed"
          value={data.stories_committed}
          format="number"
          goodDirection="up"
        />
        <KpiCard
          label="Avg Cycle Time"
          value={data.cycle_time_avg_days}
          format="days"
          goodDirection="down"
        />
        <KpiCard
          label="Sprint Completion"
          value={data.sprint_completion_pct}
          format="percent"
          goodDirection="up"
        />
      </div>

      {/* Phase breakdown */}
      {Object.keys(data.phase_avg_hrs).length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-semibold text-gray-900">Phase Breakdown (avg hrs)</h2>
          <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Phase</th>
                  <th scope="col" className="px-4 py-2 text-right text-xs font-medium uppercase text-gray-500">Hours</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {Object.entries(data.phase_avg_hrs).map(([phase, hrs]) => (
                  <tr key={phase}>
                    <td className="px-4 py-2 text-sm text-gray-900">{phase}</td>
                    <td className="px-4 py-2 text-right text-sm text-gray-900">{hrs}h</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  )
}
