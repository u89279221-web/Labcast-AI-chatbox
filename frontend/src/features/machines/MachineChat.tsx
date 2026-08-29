import { useParams, useNavigate } from 'react-router-dom'
import { ChatWindow } from '@/features/chat/ChatWindow'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'

export function MachineChat() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  if (!id) return null

  return (
    <div className="space-y-4 max-w-4xl">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h2 className="text-2xl font-bold tracking-tight">Machine Chat</h2>
      </div>
      
      <ChatWindow machineId={id} title={`AI Assistant: ${id}`} className="h-[75vh]" />
    </div>
  )
}
