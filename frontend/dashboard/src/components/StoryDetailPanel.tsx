/**
 * StoryDetailPanel — side panel showing detailed metrics for a selected story.
 * Displays timeline, acceptance criteria status, and agent activity.
 */
import { X } from 'lucide-react'

export interface StoryDetail {
  /** Unique story identifier */
  id: string
  /** Story title */
  title: string
  /** Current status */
  status: string
  /** Story point estimate */
  points: number
  /** Assignee name */
  assignee: string
  /** Cycle time in days */
  cycleTimeDays: number
  /** Number of agent iterations used */
  agentIterations: number
  /** Number of acceptance criteria passed */
  acPassed: number
  /** Total number of acceptance criteria */
  acTotal: number
  /** Test coverage percentage */
  testCoverage: number
  /** List of key events in the story timeline */
  timeline: Array<{ date: string; event: string }>
}

export interface StoryDetailPanelProps {
  /** Story detail data to display */
  story: StoryDetail | null
  /** Callback to close the panel */
  onClose: () => void
}

export function StoryDetailPanel({ story, onClose }: StoryDetailPanelProps) {
  if (!story) return null

  const acPercentage = story.acTotal > 0
    ? Math.round((story.acPassed / story.acTotal) * 100)
    : 0

  return (
    <aside
      className="rounded-lg border border-gray-200 bg-white p-6 shadow-md"
      aria-label={`Details for story ${story.id}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{story.id}</h3>
          <p className="mt-1 text-sm text-gray-600">{story.title}</p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label="Close detail panel"
        >
          <X className="h-5 w-5" aria-hidden="true" />
        </button>
      </div>

      <dl className="mt-4 grid grid-cols-2 gap-4">
        <div>
          <dt className="text-xs font-medium text-gray-500">Status</dt>
          <dd className="mt-1 text-sm font-semibold text-gray-900">{story.status}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-gray-500">Points</dt>
          <dd className="mt-1 text-sm font-semibold text-gray-900">{story.points}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-gray-500">Assignee</dt>
          <dd className="mt-1 text-sm font-semibold text-gray-900">{story.assignee}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-gray-500">Cycle Time</dt>
          <dd className="mt-1 text-sm font-semibold text-gray-900">{story.cycleTimeDays}d</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-gray-500">Agent Iterations</dt>
          <dd className="mt-1 text-sm font-semibold text-gray-900">{story.agentIterations}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-gray-500">Test Coverage</dt>
          <dd className="mt-1 text-sm font-semibold text-gray-900">{story.testCoverage}%</dd>
        </div>
      </dl>

      {/* AC Progress Bar */}
      <div className="mt-4">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Acceptance Criteria</span>
          <span>{story.acPassed}/{story.acTotal} ({acPercentage}%)</span>
        </div>
        <div className="mt-1 h-2 w-full rounded-full bg-gray-200">
          <div
            className="h-2 rounded-full bg-green-500 transition-all"
            style={{ width: `${acPercentage}%` }}
            role="progressbar"
            aria-valuenow={acPercentage}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`${acPercentage}% acceptance criteria passed`}
          />
        </div>
      </div>

      {/* Timeline */}
      {story.timeline.length > 0 && (
        <div className="mt-6">
          <h4 className="text-sm font-medium text-gray-700">Timeline</h4>
          <ul className="mt-2 space-y-2">
            {story.timeline.map((entry, index) => (
              <li key={index} className="flex gap-3 text-sm">
                <span className="flex-shrink-0 text-xs text-gray-400">{entry.date}</span>
                <span className="text-gray-700">{entry.event}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </aside>
  )
}
