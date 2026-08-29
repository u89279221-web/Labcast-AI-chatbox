import { useLiveEvents, useWsStatus } from '@/lib/ws-client'
import { useToast } from '@/hooks/use-toast'
import { WifiOff, Wifi } from 'lucide-react'

export function GlobalEmergencyListener() {
  const { toast } = useToast()
  const isConnected = useWsStatus()

  useLiveEvents('labcast/machine/+/emergency', (payload: any) => {
    // If the emergency is active, show a destructive toast
    if (payload.emergency) {
      toast({
        title: '⚠️ EMERGENCY TRIGGERED',
        description: `Machine ${payload.machine_id} has entered an emergency state!`,
        variant: 'destructive',
        duration: 10000,
      })
    } else {
      toast({
        title: 'Emergency Cleared',
        description: `Machine ${payload.machine_id} emergency state lifted.`,
        duration: 5000,
      })
    }
  })

  // Optional: could show a small indicator in the corner for WS status
  return (
    <div className="fixed bottom-4 right-4 z-50 pointer-events-none flex items-center gap-2">
      {/* 
        This is a headless component mostly, but it can render a subtle connection indicator
      */}
      <div className={`rounded-full p-2 bg-background border shadow-sm flex items-center justify-center transition-colors ${isConnected ? 'text-emerald-500' : 'text-muted-foreground'}`}>
        {isConnected ? <Wifi className="h-4 w-4" /> : <WifiOff className="h-4 w-4" />}
      </div>
    </div>
  )
}
