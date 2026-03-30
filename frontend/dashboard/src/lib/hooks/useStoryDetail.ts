/**
 * Hook to fetch metrics for a specific story within a sprint.
 */
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'
import type { StoryMetrics } from '../types'

export function useStoryDetail(
  projectId: string,
  sprintNum: number | null,
  storyId: string | null
) {
  return useQuery({
    queryKey: ['storyDetail', projectId, sprintNum, storyId],
    queryFn: async (): Promise<StoryMetrics> => {
      const { data } = await apiClient.get<StoryMetrics>(
        `/sprints/${sprintNum}/stories/${storyId}`,
        { params: { project_id: projectId } }
      )
      return data
    },
    enabled: !!projectId && sprintNum !== null && !!storyId,
  })
}
