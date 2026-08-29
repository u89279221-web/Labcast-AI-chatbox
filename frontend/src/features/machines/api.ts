import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'

export interface Machine {
  id: string
  name: string
  emergency: boolean
}

export interface MachineConfig {
  name: string
  sop: string[]
  safety_text: string
  emergency: boolean
}

export const useMachines = () => {
  return useQuery({
    queryKey: ['machines'],
    queryFn: async () => {
      const response = await api.get<Machine[]>('/api/machine/')
      return response.data
    },
  })
}

export const useMachineConfig = (machineId: string) => {
  return useQuery({
    queryKey: ['machineConfig', machineId],
    queryFn: async () => {
      const response = await api.get<MachineConfig>(`/api/machine/${machineId}/config`)
      return response.data
    },
  })
}

export const useUpdateMachine = (machineId: string) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: { sop?: string[]; safety_text?: string }) => {
      const response = await api.post(`/api/machine/${machineId}/update`, data)
      return response.data
    },
    onSuccess: () => {
      // Invalidate both the list and the specific machine config to ensure fresh data
      queryClient.invalidateQueries({ queryKey: ['machines'] })
      queryClient.invalidateQueries({ queryKey: ['machineConfig', machineId] })
    },
  })
}

export const useToggleEmergency = (machineId: string) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (emergency: boolean) => {
      const response = await api.post(`/api/machine/${machineId}/emergency`, { emergency })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['machines'] })
      queryClient.invalidateQueries({ queryKey: ['machineConfig', machineId] })
    },
  })
}
