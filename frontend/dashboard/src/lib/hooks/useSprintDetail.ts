/**
 * Hook to fetch detailed sprint data including stories.
 */
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'
import type { SprintDetail } from '../types'

export function useSprintDetail(projectId: string, sprintNum: number | null) {
  return useQuery({
    queryKey: ['sprintDetail', projectId, sprintNum],
    queryFn: async (): Promise<SprintDetail> => {
      const { data } = await apiClient.get<SprintDetail>(
        `/sprints/${sprintNum}`,
        { params: { project_id: projectId } }
      )
      return data
    },
    enabled: !!projectId && sprintNum !== null,
  })
}
