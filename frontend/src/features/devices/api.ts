import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { useWsStatus } from '@/lib/ws-client'

export interface Device {
  id: string
  machine_id: string
  firmware_version: string
  last_seen: string
  status: 'online' | 'offline'
  config_version: string
  wifi_signal: number | null
}

export const useDevices = () => {
  const isWsConnected = useWsStatus()
  
  return useQuery({
    queryKey: ['devices'],
    queryFn: async () => {
      const { data } = await api.get<Device[]>('/api/device/')
      return data
    },
    // We fall back to standard polling if the WS drops.
    refetchInterval: isWsConnected ? false : 5000, 
    staleTime: 1000 * 30, // 30 seconds
  })
}
