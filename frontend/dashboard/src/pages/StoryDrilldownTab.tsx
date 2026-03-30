/**
 * StoryDrilldownTab — displays story list with click-through to detail panel.
 * Combines StoryTable and StoryDetailPanel for per-story drill-down.
 */
import { useState } from 'react'
import { StoryTable, type StoryRow } from '../components/StoryTable'
import { StoryDetailPanel, type StoryDetail } from '../components/StoryDetailPanel'
import { LoadingSkeleton } from '../components/LoadingSkeleton'
import { ErrorState } from '../components/ErrorState'

interface StoryDrilldownData {
  stories: StoryRow[]
  storyDetails: Record<string, StoryDetail>
}

/** Placeholder hook — will be replaced by useSprintDetail + useStoryDetail */
function usePlaceholderStoryDrilldown(): {
  data: StoryDrilldownData | undefined
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

export function StoryDrilldownTab() {
  const [selectedStoryId, setSelectedStoryId] = useState<string | null>(null)
  const { data, isLoading, isError, error, refetch } = usePlaceholderStoryDrilldown()

  if (isLoading) return <LoadingSkeleton variant="table" count={5} />
  if (isError) return <ErrorState message={error?.message ?? 'Failed to load stories'} onRetry={refetch} />
  if (!data) return <LoadingSkeleton variant="table" count={5} />

  const selectedStory = selectedStoryId
    ? data.storyDetails[selectedStoryId] ?? null
    : null

  return (
    <div className="flex flex-col gap-6 lg:flex-row">
      {/* Story Table */}
      <div className="flex-1">
        <StoryTable
          stories={data.stories}
          onSelect={(id) => setSelectedStoryId(id)}
          selectedId={selectedStoryId ?? undefined}
        />
      </div>

      {/* Detail Panel */}
      {selectedStory && (
        <div className="w-full lg:w-96">
          <StoryDetailPanel
            story={selectedStory}
            onClose={() => setSelectedStoryId(null)}
          />
        </div>
      )}
    </div>
  )
}
