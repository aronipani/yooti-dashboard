/**
 * StoryTable — tabular list of stories with key metrics.
 * Clicking a row triggers the onSelect callback for drill-down.
 */

export interface StoryRow {
  /** Unique story identifier */
  id: string
  /** Story title */
  title: string
  /** Current status */
  status: string
  /** Story point estimate */
  points: number
  /** Cycle time in days */
  cycleTimeDays: number
  /** Assignee name */
  assignee: string
}

export interface StoryTableProps {
  /** List of stories to display */
  stories: StoryRow[]
  /** Callback when a story row is selected */
  onSelect: (storyId: string) => void
  /** Currently selected story ID, if any */
  selectedId?: string
}

export function StoryTable({ stories, onSelect, selectedId }: StoryTableProps) {
  if (stories.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-gray-500">
        No stories found for this sprint.
      </p>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">ID</th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Title</th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Status</th>
            <th scope="col" className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">Points</th>
            <th scope="col" className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">Cycle Time</th>
            <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Assignee</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {stories.map((story) => (
            <tr
              key={story.id}
              onClick={() => onSelect(story.id)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  onSelect(story.id)
                }
              }}
              tabIndex={0}
              role="button"
              aria-selected={selectedId === story.id}
              className={`cursor-pointer transition-colors hover:bg-gray-50 ${
                selectedId === story.id ? 'bg-blue-50' : ''
              }`}
            >
              <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-blue-600">{story.id}</td>
              <td className="px-4 py-3 text-sm text-gray-900">{story.title}</td>
              <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500">{story.status}</td>
              <td className="whitespace-nowrap px-4 py-3 text-right text-sm text-gray-900">{story.points}</td>
              <td className="whitespace-nowrap px-4 py-3 text-right text-sm text-gray-900">{story.cycleTimeDays}d</td>
              <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500">{story.assignee}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
