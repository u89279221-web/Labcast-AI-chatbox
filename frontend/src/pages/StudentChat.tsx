import { useParams, useSearchParams } from 'react-router-dom'
import { ChatWindow } from '@/features/chat/ChatWindow'
import { AlertTriangle } from 'lucide-react'

export function StudentChat() {
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const machineId = id || searchParams.get('machine')

  if (!machineId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[100dvh] bg-background p-4 text-center">
        <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
        <h1 className="text-2xl font-bold mb-2">Invalid Scan</h1>
        <p className="text-muted-foreground">No machine identifier was provided in the URL.</p>
        <p className="text-muted-foreground mt-2">Please scan a valid machine QR code.</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[100dvh] w-full bg-background overflow-hidden">
      <header className="bg-primary text-primary-foreground p-3 shadow-md shrink-0">
        <h1 className="text-lg font-bold text-center">LabCast Assistant</h1>
      </header>
      
      <main className="flex-1 overflow-hidden p-2 bg-muted/20">
        <ChatWindow 
          machineId={machineId} 
          title={`Machine: ${machineId}`} 
          className="h-full max-w-full rounded-lg border-0 shadow-sm"
        />
      </main>
    </div>
  )
}
