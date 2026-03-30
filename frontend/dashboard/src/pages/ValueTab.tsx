/**
 * ValueTab — displays delivery value metrics: stories shipped, completion rate, AC coverage.
 * Uses KPI cards for headline numbers and trend data.
 */
import { KpiCard } from '../components/KpiCard'
import { InsightStrip } from '../components/InsightStrip'
import { LoadingSkeleton } from '../components/LoadingSkeleton'
import { ErrorState } from '../components/ErrorState'

interface ValueData {
  storiesShipped: number
  previousStoriesShipped: number
  sprintCompletionPct: number
  previousSprintCompletionPct: number
  acCoveragePct: number
  previousAcCoveragePct: number
  storiesCommitted: number
  previousStoriesCommitted: number
  deliveryTrend: Array<{ sprint_num: number; shipped: number; committed: number }>
  alerts: Array<{ type: string; severity: string; message: string }>
}

/** Placeholder hook — will be replaced by useCurrentMetrics */
function usePlaceholderValue(): {
  data: ValueData | undefined
  isLoading: boolean
  isError: boolean
  error: Error | null
  refetch: () => void
} {
  return {
    data: undefined,
    isLoading: false,
    isError: false,
    error: null,
    refetch: () => undefined,
  }
}

export function ValueTab() {
  const { data, isLoading, isError, error, refetch } = usePlaceholderValue()

  if (isLoading) return <LoadingSkeleton variant="cards" count={4} />
  if (isError) return <ErrorState message={error?.message ?? 'Failed to load value data'} onRetry={refetch} />
  if (!data) return <LoadingSkeleton variant="cards" count={4} />

  return (
    <div className="space-y-6">
      <InsightStrip alerts={data.alerts} />

      {/* KPI Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Stories Shipped"
          value={data.storiesShipped}
          previousValue={data.previousStoriesShipped}
          format="number"
          goodDirection="up"
        />
        <KpiCard
          label="Sprint Completion"
          value={data.sprintCompletionPct}
          previousValue={data.previousSprintCompletionPct}
          format="percent"
          goodDirection="up"
        />
        <KpiCard
          label="AC Coverage"
          value={data.acCoveragePct}
          previousValue={data.previousAcCoveragePct}
          format="percent"
          goodDirection="up"
        />
        <KpiCard
          label="Stories Committed"
          value={data.storiesCommitted}
          previousValue={data.previousStoriesCommitted}
          format="number"
          goodDirection="up"
        />
      </div>

      {/* Delivery Trend Table */}
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
              {data.deliveryTrend.map((row) => {
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
    </div>
  )
}
