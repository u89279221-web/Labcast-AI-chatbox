import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useDevices, type Device } from './api'
import { useLiveEvents, useWsStatus } from '@/lib/ws-client'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Loader2, Wifi, WifiOff, Cpu } from 'lucide-react'

export function DevicesPage() {
  const { data: devices, isLoading, isError } = useDevices()
  const queryClient = useQueryClient()
  const isWsConnected = useWsStatus()
  const [lastEventTime, setLastEventTime] = useState<Date | null>(null)

  // Listen for device heartbeat events on MQTT relay
  useLiveEvents('labcast/device/+/heartbeat', (payload: any) => {
    // When a heartbeat arrives, we know this device is online.
    // We can patch the TanStack Query cache directly to feel instantly real-time.
    queryClient.setQueryData(['devices'], (oldData: Device[] | undefined) => {
      if (!oldData) return oldData
      
      const deviceId = payload.device_id
      if (!deviceId) return oldData
      
      setLastEventTime(new Date())

      return oldData.map(device => {
        if (device.id === deviceId) {
          return {
            ...device,
            status: 'online',
            last_seen: new Date().toISOString(),
            config_version: payload.config_version || device.config_version,
            wifi_signal: payload.wifi_signal !== undefined ? payload.wifi_signal : device.wifi_signal,
          }
        }
        return device
      })
    })
  })
  
  // Listen for general device status events if the backend emits them
  useLiveEvents('labcast/device/+/status', (payload: any) => {
    queryClient.setQueryData(['devices'], (oldData: Device[] | undefined) => {
      if (!oldData) return oldData
      
      const deviceId = payload.device_id
      if (!deviceId) return oldData

      setLastEventTime(new Date())
      
      return oldData.map(device => {
        if (device.id === deviceId) {
          return {
            ...device,
            status: payload.status || device.status,
            last_seen: new Date().toISOString(),
          }
        }
        return device
      })
    })
  })

  // Format relative time (e.g., "Just now", "5s ago")
  const formatLastSeen = (isoString: string) => {
    const seconds = Math.floor((new Date().getTime() - new Date(isoString).getTime()) / 1000)
    
    if (seconds < 5) return 'Just now'
    if (seconds < 60) return `${seconds}s ago`
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes}m ago`
    
    return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-2xl font-bold tracking-tight">IoT Devices</h2>
          <p className="text-sm text-muted-foreground">Monitor hardware controllers attached to machines.</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="text-xs text-muted-foreground text-right">
            <div>Data Source</div>
            <div className="font-medium flex items-center justify-end gap-1">
              {isWsConnected ? (
                <><Wifi className="h-3 w-3 text-emerald-500" /> Live WebSocket</>
              ) : (
                <><WifiOff className="h-3 w-3 text-amber-500" /> Polling (REST)</>
              )}
            </div>
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Registered Devices</CardTitle>
            {lastEventTime && (
              <span className="text-xs text-muted-foreground animate-pulse">
                Last event: {lastEventTime.toLocaleTimeString()}
              </span>
            )}
          </div>
          <CardDescription>Live status of all connected IoT controllers.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex h-32 items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : isError ? (
            <div className="text-center text-destructive p-4 border rounded-md bg-destructive/10">
              Failed to load devices.
            </div>
          ) : !devices || devices.length === 0 ? (
            <div className="text-center py-10 text-muted-foreground border rounded-lg bg-muted/20">
              <Cpu className="h-10 w-10 mx-auto mb-3 opacity-20" />
              <p>No devices registered yet.</p>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Device ID</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Machine ID</TableHead>
                    <TableHead>Firmware</TableHead>
                    <TableHead>Signal</TableHead>
                    <TableHead className="text-right">Last Seen</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {devices.map((device) => (
                    <TableRow key={device.id}>
                      <TableCell className="font-medium">{device.id}</TableCell>
                      <TableCell>
                        <Badge 
                          variant={device.status === 'online' ? 'default' : 'secondary'}
                          className={device.status === 'online' ? 'bg-emerald-500 hover:bg-emerald-600' : ''}
                        >
                          {device.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{device.machine_id}</TableCell>
                      <TableCell className="text-muted-foreground">v{device.firmware_version}</TableCell>
                      <TableCell>
                        {device.wifi_signal ? `${device.wifi_signal} dBm` : '--'}
                      </TableCell>
                      <TableCell className="text-right tabular-nums text-muted-foreground">
                        {formatLastSeen(device.last_seen)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}


