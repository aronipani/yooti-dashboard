/**
 * Hook to fetch current sprint metrics snapshot for a project.
 */
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'
import type { CurrentSnapshot } from '../types'

export function useCurrentMetrics(projectId: string) {
  return useQuery({
    queryKey: ['currentMetrics', projectId],
    queryFn: async (): Promise<CurrentSnapshot> => {
      const { data } = await apiClient.get<CurrentSnapshot>(
        '/metrics/current',
        { params: { project_id: projectId } }
      )
      return data
    },
    enabled: !!projectId,
  })
}
