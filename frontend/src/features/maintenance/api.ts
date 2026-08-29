import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'

export interface MaintenanceRecord {
  id: string
  machine_id: string
  technician_id: string
  description: string
  performed_at: string | null
  next_due_at: string | null
}

export interface MaintenanceCreate {
  machine_id: string
  description: string
  performed_at?: string | null
  next_due_at?: string | null
}

export interface MaintenanceUpdate {
  description?: string
  performed_at?: string | null
  next_due_at?: string | null
}

export const useMaintenanceRecords = (machineId?: string) => {
  return useQuery({
    queryKey: ['maintenance', machineId],
    queryFn: async () => {
      const url = machineId ? `/api/maintenance/?machine_id=${machineId}` : '/api/maintenance/'
      const { data } = await api.get<MaintenanceRecord[]>(url)
      return data
    }
  })
}

export const useCreateMaintenanceRecord = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: MaintenanceCreate) => {
      const { data } = await api.post<MaintenanceRecord>('/api/maintenance/', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance'] })
    }
  })
}

export const useUpdateMaintenanceRecord = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string, payload: MaintenanceUpdate }) => {
      const { data } = await api.put<MaintenanceRecord>(`/api/maintenance/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance'] })
    }
  })
}
