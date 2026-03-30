/**
 * QualityTab — displays code quality, coverage, and mutation metrics from useCurrentMetrics.
 */
import { KpiCard } from '../components/KpiCard'
import { InsightStrip } from '../components/InsightStrip'
import { LoadingSkeleton } from '../components/LoadingSkeleton'
import { ErrorState } from '../components/ErrorState'
import { useCurrentMetrics } from '../lib/hooks'

export interface QualityTabProps {
  projectId: string
}

export function QualityTab({ projectId }: QualityTabProps) {
  const { data, isLoading, isError, error, refetch } = useCurrentMetrics(projectId)

  if (isLoading) return <LoadingSkeleton variant="cards" count={4} />
  if (isError) return <ErrorState message={error?.message ?? 'Failed to load quality data'} onRetry={() => { void refetch() }} />
  if (!data) return <LoadingSkeleton variant="cards" count={4} />

  const relevantAlerts = data.insight_alerts.filter(
    (a) => a.type === 'QUALITY_DROP' || a.type === 'REGRESSION_SPIKE' || a.type === 'CONSTITUTION_GAP'
  )

  return (
    <div className="space-y-6">
      <InsightStrip alerts={relevantAlerts} />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Code Coverage"
          value={data.coverage_new_code_avg}
          format="percent"
          goodDirection="up"
        />
        <KpiCard
          label="Mutation Score"
          value={data.mutation_score_avg}
          format="percent"
          goodDirection="up"
        />
        <KpiCard
          label="Regression Rate"
          value={data.regression_rate_pct}
          format="percent"
          goodDirection="down"
        />
        <KpiCard
          label="Constitution Pass"
          value={data.constitution_pass_pct}
          format="percent"
          goodDirection="up"
        />
      </div>

      {/* Gate Rejection Rates */}
      {Object.keys(data.gate_rejection_rates).length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-semibold text-gray-900">Gate Rejection Rates</h2>
          <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Gate</th>
                  <th scope="col" className="px-4 py-2 text-right text-xs font-medium uppercase text-gray-500">Rejection %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {Object.entries(data.gate_rejection_rates).map(([gate, rate]) => (
                  <tr key={gate}>
                    <td className="px-4 py-2 text-sm text-gray-900">{gate}</td>
                    <td className="px-4 py-2 text-right text-sm text-gray-900">{rate}%</td>
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
