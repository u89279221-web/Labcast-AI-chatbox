import { useState, useEffect } from 'react'
import { useMachines } from '@/features/machines/api'
import { ChatWindow } from './ChatWindow'
import { Cpu } from 'lucide-react'

export function GlobalChatPage() {
  const { data: machines, isLoading } = useMachines()
  const [selectedMachineId, setSelectedMachineId] = useState<string>('CNC01')

  useEffect(() => {
    if (machines && machines.length > 0 && !machines.find(m => m.id === selectedMachineId)) {
      setSelectedMachineId(machines[0].id)
    }
  }, [machines])

  if (isLoading) {
    return <div className="py-10 text-center text-muted-foreground">Loading AI Assistant...</div>
  }

  const currentMachine = machines?.find(m => m.id === selectedMachineId)

  return (
    <div className="space-y-4 max-w-5xl">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h2 className="text-2xl font-bold tracking-tight">AI Assistant</h2>
          <p className="text-sm text-muted-foreground">Ask RAG-powered questions isolated to specific machine manuals.</p>
        </div>

        {machines && machines.length > 0 && (
          <div className="flex items-center gap-2 bg-background p-1.5 rounded-lg border shadow-sm">
            <Cpu className="h-4 w-4 text-muted-foreground ml-2" />
            <span className="text-sm font-medium text-muted-foreground">Select Target Machine:</span>
            <select
              value={selectedMachineId}
              onChange={(e) => setSelectedMachineId(e.target.value)}
              className="bg-transparent text-sm font-semibold py-1 px-2 focus:outline-none cursor-pointer"
            >
              {machines.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.id} ({m.name})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <ChatWindow 
        machineId={selectedMachineId} 
        title={`Assistant: ${currentMachine ? currentMachine.name : selectedMachineId}`} 
        className="h-[75vh]" 
      />
    </div>
  )
}
