/**
 * StoryDrilldownTab — displays story list from useSprintDetail with click-through
 * to detail panel via useStoryDetail.
 */
import { useState } from 'react'
import { StoryTable, type StoryRow } from '../components/StoryTable'
import { StoryDetailPanel, type StoryDetail } from '../components/StoryDetailPanel'
import { LoadingSkeleton } from '../components/LoadingSkeleton'
import { ErrorState } from '../components/ErrorState'
import { useSprintDetail, useStoryDetail } from '../lib/hooks'
import type { StoryMetrics } from '../lib/types'

export interface StoryDrilldownTabProps {
  projectId: string
  selectedSprint: number | null
}

function toStoryRow(story: StoryMetrics): StoryRow {
  return {
    id: story.story_id,
    title: story.story_id,
    status: story.status,
    points: story.iteration_count,
    cycleTimeDays: Math.round((story.cycle_time_hrs / 24) * 10) / 10,
    assignee: story.escalation_type ?? 'Agent',
  }
}

function toStoryDetail(story: StoryMetrics): StoryDetail {
  return {
    id: story.story_id,
    title: story.story_id,
    status: story.status,
    points: story.iteration_count,
    assignee: story.escalation_type ?? 'Agent',
    cycleTimeDays: Math.round((story.cycle_time_hrs / 24) * 10) / 10,
    agentIterations: story.iteration_count,
    acPassed: 0,
    acTotal: 0,
    testCoverage: story.coverage_new_code_pct,
    timeline: Object.entries(story.gate_timestamps)
      .filter(([, ts]) => ts !== null)
      .map(([gate, ts]) => ({ date: ts as string, event: `${gate} approved` })),
  }
}

export function StoryDrilldownTab({ projectId, selectedSprint }: StoryDrilldownTabProps) {
  const [selectedStoryId, setSelectedStoryId] = useState<string | null>(null)

  const {
    data: sprintDetail,
    isLoading,
    isError,
    error,
    refetch,
  } = useSprintDetail(projectId, selectedSprint)

  const { data: storyMetrics } = useStoryDetail(
    projectId,
    selectedSprint,
    selectedStoryId,
  )

  if (selectedSprint === null) {
    return (
      <p className="py-8 text-center text-sm text-gray-500">
        Please select a sprint from the selector above to view stories.
      </p>
    )
  }

  if (isLoading) return <LoadingSkeleton variant="table" count={5} />
  if (isError) return <ErrorState message={error?.message ?? 'Failed to load stories'} onRetry={() => { void refetch() }} />
  if (!sprintDetail) return <LoadingSkeleton variant="table" count={5} />

  const stories = sprintDetail.stories.map(toStoryRow)
  const selectedStory = storyMetrics ? toStoryDetail(storyMetrics) : null

  return (
    <div className="flex flex-col gap-6 lg:flex-row">
      <div className="flex-1">
        <StoryTable
          stories={stories}
          onSelect={(id) => setSelectedStoryId(id)}
          selectedId={selectedStoryId ?? undefined}
        />
      </div>

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
