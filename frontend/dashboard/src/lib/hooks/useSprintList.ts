/**
 * Hook to fetch the list of sprint summaries for a project.
 */
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'
import type { SprintSummary } from '../types'

export function useSprintList(projectId: string) {
  return useQuery({
    queryKey: ['sprintList', projectId],
    queryFn: async (): Promise<SprintSummary[]> => {
      const { data } = await apiClient.get<SprintSummary[]>(
        '/sprints',
        { params: { project_id: projectId } }
      )
      return data
    },
    enabled: !!projectId,
  })
}
