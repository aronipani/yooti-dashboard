/**
 * AgentEfficiencyTab — displays agent execution, human wait, iteration, and escalation metrics.
 * Wired to useCurrentMetrics for real API data.
 */
import { KpiCard } from '../components/KpiCard'
import { InsightStrip } from '../components/InsightStrip'
import { LoadingSkeleton } from '../components/LoadingSkeleton'
import { ErrorState } from '../components/ErrorState'
import { useCurrentMetrics } from '../lib/hooks'

export interface AgentEfficiencyTabProps {
  projectId: string
}

export function AgentEfficiencyTab({ projectId }: AgentEfficiencyTabProps) {
  const { data, isLoading, isError, error, refetch } = useCurrentMetrics(projectId)

  if (isLoading) return <LoadingSkeleton variant="cards" count={4} />
  if (isError) return <ErrorState message={error?.message ?? 'Failed to load agent efficiency data'} onRetry={() => { void refetch() }} />
  if (!data) return <LoadingSkeleton variant="cards" count={4} />

  const relevantAlerts = data.insight_alerts.filter(
    (a) => a.type === 'HUMAN_VS_AGENT' || a.type === 'ESCALATION_SPIKE'
  )

  const breakdownEntries = Object.entries(data.escalation_breakdown)

  return (
    <div className="space-y-6">
      <InsightStrip alerts={relevantAlerts} />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-5">
        <KpiCard label="Agent Exec Time" value={data.agent_exec_hrs_avg} format="hours" goodDirection="down" />
        <KpiCard label="Human Wait Time" value={data.human_wait_hrs_avg} format="hours" goodDirection="down" />
        <KpiCard label="Avg Iterations" value={data.iteration_avg} format="number" goodDirection="down" />
        <KpiCard label="Escalation Rate" value={data.escalation_rate_pct} format="percent" goodDirection="down" />
        <KpiCard label="Correction Rate" value={data.correction_rate_pct} format="percent" goodDirection="down" />
      </div>

      {breakdownEntries.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-semibold text-gray-900">Escalation Breakdown</h2>
          <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Type</th>
                  <th scope="col" className="px-4 py-2 text-right text-xs font-medium uppercase text-gray-500">Count</th>
                  <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Distribution</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {breakdownEntries.map(([type, count]) => {
                  const total = breakdownEntries.reduce((sum, [, c]) => sum + c, 0)
                  const widthPercent = total > 0 ? Math.round((count / total) * 100) : 0
                  return (
                    <tr key={type}>
                      <td className="px-4 py-2 text-sm text-gray-900">{type}</td>
                      <td className="px-4 py-2 text-right text-sm text-gray-900">{count}</td>
                      <td className="px-4 py-2">
                        <div className="h-3 w-full rounded-full bg-gray-100">
                          <div className="h-3 rounded-full bg-orange-500" style={{ width: `${widthPercent}%` }} />
                        </div>
                      </td>
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
