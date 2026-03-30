/**
 * DoraTab — displays the four DORA metrics.
 * Deployment Frequency, Lead Time for Changes, Change Failure Rate, Time to Restore.
 */
import { KpiCard } from '../components/KpiCard'
import { InsightStrip } from '../components/InsightStrip'
import { LoadingSkeleton } from '../components/LoadingSkeleton'
import { ErrorState } from '../components/ErrorState'

interface DoraData {
  deploymentFrequency: number
  previousDeploymentFrequency: number
  leadTimeForChanges: number
  previousLeadTimeForChanges: number
  changeFailureRate: number
  previousChangeFailureRate: number
  timeToRestore: number
  previousTimeToRestore: number
  recentDeployments: Array<{ date: string; status: string; duration: string }>
  alerts: Array<{ type: string; severity: string; message: string }>
}

function usePlaceholderDora(): {
  data: DoraData | undefined
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

export function DoraTab() {
  const { data, isLoading, isError, error, refetch } = usePlaceholderDora()

  if (isLoading) return <LoadingSkeleton variant="cards" count={4} />
  if (isError) return <ErrorState message={error?.message ?? 'Failed to load DORA metrics'} onRetry={refetch} />
  if (!data) return <LoadingSkeleton variant="cards" count={4} />

  return (
    <div className="space-y-6">
      <InsightStrip alerts={data.alerts} />

      {/* DORA KPI Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Deployment Frequency"
          value={data.deploymentFrequency}
          previousValue={data.previousDeploymentFrequency}
          format="number"
          goodDirection="up"
        />
        <KpiCard
          label="Lead Time for Changes"
          value={data.leadTimeForChanges}
          previousValue={data.previousLeadTimeForChanges}
          format="hours"
          goodDirection="down"
        />
        <KpiCard
          label="Change Failure Rate"
          value={data.changeFailureRate}
          previousValue={data.previousChangeFailureRate}
          format="percent"
          goodDirection="down"
        />
        <KpiCard
          label="Time to Restore"
          value={data.timeToRestore}
          previousValue={data.previousTimeToRestore}
          format="hours"
          goodDirection="down"
        />
      </div>

      {/* Recent Deployments */}
      <section>
        <h2 className="mb-3 text-lg font-semibold text-gray-900">Recent Deployments</h2>
        <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Date</th>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Status</th>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Duration</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.recentDeployments.map((deploy, i) => (
                <tr key={i}>
                  <td className="px-4 py-2 text-sm text-gray-900">{deploy.date}</td>
                  <td className="px-4 py-2 text-sm">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                        deploy.status === 'success'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {deploy.status}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-sm text-gray-500">{deploy.duration}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
