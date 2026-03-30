/**
 * ProductivityTab — displays velocity, throughput, and cycle time metrics.
 * Uses KPI cards for headline numbers and a simple bar display for trends.
 */
import { KpiCard } from '../components/KpiCard'
import { InsightStrip } from '../components/InsightStrip'
import { LoadingSkeleton } from '../components/LoadingSkeleton'
import { ErrorState } from '../components/ErrorState'

/** Placeholder data structure — will be replaced by hook data */
interface ProductivityData {
  velocity: number
  previousVelocity: number
  throughput: number
  previousThroughput: number
  avgCycleTime: number
  previousAvgCycleTime: number
  wipCount: number
  previousWipCount: number
  sprintBurndown: Array<{ day: string; remaining: number; ideal: number }>
  alerts: Array<{ type: string; severity: string; message: string }>
}

/** Placeholder hook — will be replaced by useCurrentMetrics */
function usePlaceholderProductivity(): {
  data: ProductivityData | undefined
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

export function ProductivityTab() {
  const { data, isLoading, isError, error, refetch } = usePlaceholderProductivity()

  if (isLoading) return <LoadingSkeleton variant="cards" count={4} />
  if (isError) return <ErrorState message={error?.message ?? 'Failed to load productivity data'} onRetry={refetch} />
  if (!data) return <LoadingSkeleton variant="cards" count={4} />

  return (
    <div className="space-y-6">
      {/* Alerts */}
      <InsightStrip alerts={data.alerts} />

      {/* KPI Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Velocity"
          value={data.velocity}
          previousValue={data.previousVelocity}
          format="number"
          goodDirection="up"
        />
        <KpiCard
          label="Throughput"
          value={data.throughput}
          previousValue={data.previousThroughput}
          format="number"
          goodDirection="up"
        />
        <KpiCard
          label="Avg Cycle Time"
          value={data.avgCycleTime}
          previousValue={data.previousAvgCycleTime}
          format="days"
          goodDirection="down"
        />
        <KpiCard
          label="WIP Count"
          value={data.wipCount}
          previousValue={data.previousWipCount}
          format="number"
          goodDirection="down"
        />
      </div>

      {/* Sprint Burndown — simple table representation */}
      <section>
        <h2 className="mb-3 text-lg font-semibold text-gray-900">Sprint Burndown</h2>
        <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Day</th>
                <th scope="col" className="px-4 py-2 text-right text-xs font-medium uppercase text-gray-500">Remaining</th>
                <th scope="col" className="px-4 py-2 text-right text-xs font-medium uppercase text-gray-500">Ideal</th>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Progress</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.sprintBurndown.map((row) => {
                const maxPoints = data.sprintBurndown[0]?.ideal ?? 1
                const widthPercent = maxPoints > 0 ? Math.round((row.remaining / maxPoints) * 100) : 0
                return (
                  <tr key={row.day}>
                    <td className="px-4 py-2 text-sm text-gray-900">{row.day}</td>
                    <td className="px-4 py-2 text-right text-sm text-gray-900">{row.remaining}</td>
                    <td className="px-4 py-2 text-right text-sm text-gray-500">{row.ideal}</td>
                    <td className="px-4 py-2">
                      <div className="h-3 w-full rounded-full bg-gray-100">
                        <div
                          className="h-3 rounded-full bg-blue-500"
                          style={{ width: `${widthPercent}%` }}
                        />
                      </div>
                    </td>
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
