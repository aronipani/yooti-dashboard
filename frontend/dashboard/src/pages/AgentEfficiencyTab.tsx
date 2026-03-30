/**
 * AgentEfficiencyTab — displays agent execution, human wait, iteration, and escalation metrics.
 * Uses KPI cards for headline numbers and breakdowns for escalation and correction data.
 */
import { KpiCard } from '../components/KpiCard'
import { InsightStrip } from '../components/InsightStrip'
import { LoadingSkeleton } from '../components/LoadingSkeleton'
import { ErrorState } from '../components/ErrorState'

interface AgentEfficiencyData {
  agentExecHrsAvg: number
  previousAgentExecHrsAvg: number
  humanWaitHrsAvg: number
  previousHumanWaitHrsAvg: number
  iterationAvg: number
  previousIterationAvg: number
  escalationRatePct: number
  previousEscalationRatePct: number
  correctionRatePct: number
  previousCorrectionRatePct: number
  escalationBreakdown: Array<{ type: string; count: number }>
  alerts: Array<{ type: string; severity: string; message: string }>
}

/** Placeholder hook — will be replaced by useCurrentMetrics */
function usePlaceholderAgentEfficiency(): {
  data: AgentEfficiencyData | undefined
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

export function AgentEfficiencyTab() {
  const { data, isLoading, isError, error, refetch } = usePlaceholderAgentEfficiency()

  if (isLoading) return <LoadingSkeleton variant="cards" count={4} />
  if (isError) return <ErrorState message={error?.message ?? 'Failed to load agent efficiency data'} onRetry={refetch} />
  if (!data) return <LoadingSkeleton variant="cards" count={4} />

  return (
    <div className="space-y-6">
      <InsightStrip alerts={data.alerts} />

      {/* KPI Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-5">
        <KpiCard
          label="Agent Exec Time"
          value={data.agentExecHrsAvg}
          previousValue={data.previousAgentExecHrsAvg}
          format="hours"
          goodDirection="down"
        />
        <KpiCard
          label="Human Wait Time"
          value={data.humanWaitHrsAvg}
          previousValue={data.previousHumanWaitHrsAvg}
          format="hours"
          goodDirection="down"
        />
        <KpiCard
          label="Avg Iterations"
          value={data.iterationAvg}
          previousValue={data.previousIterationAvg}
          format="number"
          goodDirection="down"
        />
        <KpiCard
          label="Escalation Rate"
          value={data.escalationRatePct}
          previousValue={data.previousEscalationRatePct}
          format="percent"
          goodDirection="down"
        />
        <KpiCard
          label="Correction Rate"
          value={data.correctionRatePct}
          previousValue={data.previousCorrectionRatePct}
          format="percent"
          goodDirection="down"
        />
      </div>

      {/* Escalation Breakdown */}
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
              {data.escalationBreakdown.map((row) => {
                const total = data.escalationBreakdown.reduce((sum, r) => sum + r.count, 0)
                const widthPercent = total > 0 ? Math.round((row.count / total) * 100) : 0
                return (
                  <tr key={row.type}>
                    <td className="px-4 py-2 text-sm text-gray-900">{row.type}</td>
                    <td className="px-4 py-2 text-right text-sm text-gray-900">{row.count}</td>
                    <td className="px-4 py-2">
                      <div className="h-3 w-full rounded-full bg-gray-100">
                        <div
                          className="h-3 rounded-full bg-orange-500"
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
