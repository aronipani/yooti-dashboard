/**
 * Hook to fetch trend data across sprints for a given metric.
 */
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'
import type { TrendPoint } from '../types'

export function useTrends(projectId: string, metric?: string) {
  return useQuery({
    queryKey: ['trends', projectId, metric],
    queryFn: async (): Promise<TrendPoint[]> => {
      const params: Record<string, string> = { project_id: projectId }
      if (metric) {
        params.metric = metric
      }
      const { data } = await apiClient.get<TrendPoint[]>(
        '/trends',
        { params }
      )
      return data
    },
    enabled: !!projectId,
  })
}
