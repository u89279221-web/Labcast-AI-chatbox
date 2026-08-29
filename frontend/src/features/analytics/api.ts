import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

export interface AnalyticsSummary {
  chats_per_machine: Record<string, number>
  total_emergency_activations: number
  active_devices: number
}

export interface AuditLog {
  id: string
  timestamp: string
  user_id: string
  action: string
  target_id: string
  details?: Record<string, any>
}

export const useAnalyticsSummary = () => {
  return useQuery({
    queryKey: ['analytics', 'summary'],
    queryFn: async () => {
      const { data } = await api.get<AnalyticsSummary>('/api/analytics/summary')
      return data
    }
  })
}

export const useAuditLogs = (limit = 100) => {
  return useQuery({
    queryKey: ['analytics', 'logs', limit],
    queryFn: async () => {
      const { data } = await api.get<AuditLog[]>(`/api/analytics/logs?limit=${limit}`)
      return data
    }
  })
}
