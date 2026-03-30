/**
 * ValueTab — displays delivery value metrics from useCurrentMetrics and useTrends.
 */
import { KpiCard } from '../components/KpiCard'
import { InsightStrip } from '../components/InsightStrip'
import { LoadingSkeleton } from '../components/LoadingSkeleton'
import { ErrorState } from '../components/ErrorState'
import { useCurrentMetrics, useTrends } from '../lib/hooks'

export interface ValueTabProps {
  projectId: string
}

export function ValueTab({ projectId }: ValueTabProps) {
  const { data, isLoading, isError, error, refetch } = useCurrentMetrics(projectId)
  const { data: trends } = useTrends(projectId)

  if (isLoading) return <LoadingSkeleton variant="cards" count={4} />
  if (isError) return <ErrorState message={error?.message ?? 'Failed to load value data'} onRetry={() => { void refetch() }} />
  if (!data) return <LoadingSkeleton variant="cards" count={4} />

  const relevantAlerts = data.insight_alerts

  // Group trends by sprint for the delivery trend table
  const sprintMap = new Map<number, { shipped: number; committed: number }>()
  if (trends) {
    for (const point of trends) {
      if (point.metric_name === 'stories_shipped') {
        const entry = sprintMap.get(point.sprint_num) ?? { shipped: 0, committed: 0 }
        entry.shipped = point.value
        sprintMap.set(point.sprint_num, entry)
      }
      if (point.metric_name === 'stories_committed') {
        const entry = sprintMap.get(point.sprint_num) ?? { shipped: 0, committed: 0 }
        entry.committed = point.value
        sprintMap.set(point.sprint_num, entry)
      }
    }
  }
  const deliveryTrend = Array.from(sprintMap.entries())
    .map(([sprint_num, vals]) => ({ sprint_num, ...vals }))
    .sort((a, b) => a.sprint_num - b.sprint_num)

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
          label="Sprint Completion"
          value={data.sprint_completion_pct}
          format="percent"
          goodDirection="up"
        />
        <KpiCard
          label="Coverage (New Code)"
          value={data.coverage_new_code_avg}
          format="percent"
          goodDirection="up"
        />
        <KpiCard
          label="Stories Committed"
          value={data.stories_committed}
          format="number"
          goodDirection="up"
        />
      </div>

      {deliveryTrend.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-semibold text-gray-900">Delivery Trend</h2>
          <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Sprint</th>
                  <th scope="col" className="px-4 py-2 text-right text-xs font-medium uppercase text-gray-500">Shipped</th>
                  <th scope="col" className="px-4 py-2 text-right text-xs font-medium uppercase text-gray-500">Committed</th>
                  <th scope="col" className="px-4 py-2 text-right text-xs font-medium uppercase text-gray-500">Completion %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {deliveryTrend.map((row) => {
                  const completionPct = row.committed > 0
                    ? Math.round((row.shipped / row.committed) * 100)
                    : 0
                  return (
                    <tr key={row.sprint_num}>
                      <td className="px-4 py-2 text-sm text-gray-900">Sprint {row.sprint_num}</td>
                      <td className="px-4 py-2 text-right text-sm text-gray-900">{row.shipped}</td>
                      <td className="px-4 py-2 text-right text-sm text-gray-900">{row.committed}</td>
                      <td className="px-4 py-2 text-right text-sm text-gray-900">{completionPct}%</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  )
}
