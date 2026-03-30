/**
 * QualityTab — displays code quality, test coverage, and defect metrics.
 * Uses KPI cards and a file-level coverage breakdown table.
 */
import { KpiCard } from '../components/KpiCard'
import { InsightStrip } from '../components/InsightStrip'
import { LoadingSkeleton } from '../components/LoadingSkeleton'
import { ErrorState } from '../components/ErrorState'

interface QualityData {
  testCoverage: number
  previousTestCoverage: number
  defectRate: number
  previousDefectRate: number
  firstPassRate: number
  previousFirstPassRate: number
  lintWarnings: number
  previousLintWarnings: number
  fileCoverage: Array<{ file: string; lines: number; branches: number }>
  alerts: Array<{ type: string; severity: string; message: string }>
}

function usePlaceholderQuality(): {
  data: QualityData | undefined
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

export function QualityTab() {
  const { data, isLoading, isError, error, refetch } = usePlaceholderQuality()

  if (isLoading) return <LoadingSkeleton variant="cards" count={4} />
  if (isError) return <ErrorState message={error?.message ?? 'Failed to load quality data'} onRetry={refetch} />
  if (!data) return <LoadingSkeleton variant="cards" count={4} />

  return (
    <div className="space-y-6">
      <InsightStrip alerts={data.alerts} />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Test Coverage"
          value={data.testCoverage}
          previousValue={data.previousTestCoverage}
          format="percent"
          goodDirection="up"
        />
        <KpiCard
          label="Defect Rate"
          value={data.defectRate}
          previousValue={data.previousDefectRate}
          format="percent"
          goodDirection="down"
        />
        <KpiCard
          label="First Pass Rate"
          value={data.firstPassRate}
          previousValue={data.previousFirstPassRate}
          format="percent"
          goodDirection="up"
        />
        <KpiCard
          label="Lint Warnings"
          value={data.lintWarnings}
          previousValue={data.previousLintWarnings}
          format="number"
          goodDirection="down"
        />
      </div>

      {/* File Coverage Breakdown */}
      <section>
        <h2 className="mb-3 text-lg font-semibold text-gray-900">File Coverage</h2>
        <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">File</th>
                <th scope="col" className="px-4 py-2 text-right text-xs font-medium uppercase text-gray-500">Lines</th>
                <th scope="col" className="px-4 py-2 text-right text-xs font-medium uppercase text-gray-500">Branches</th>
                <th scope="col" className="px-4 py-2 text-left text-xs font-medium uppercase text-gray-500">Coverage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.fileCoverage.map((file) => (
                <tr key={file.file}>
                  <td className="px-4 py-2 text-sm font-mono text-gray-900">{file.file}</td>
                  <td className="px-4 py-2 text-right text-sm text-gray-900">{file.lines}%</td>
                  <td className="px-4 py-2 text-right text-sm text-gray-900">{file.branches}%</td>
                  <td className="px-4 py-2">
                    <div className="h-3 w-full rounded-full bg-gray-100">
                      <div
                        className={`h-3 rounded-full ${file.lines >= 80 ? 'bg-green-500' : file.lines >= 60 ? 'bg-amber-500' : 'bg-red-500'}`}
                        style={{ width: `${file.lines}%` }}
                      />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
