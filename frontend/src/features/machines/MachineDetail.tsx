import { useState, useEffect, type ChangeEvent } from 'react'
import { useParams } from 'react-router-dom'
import { DragDropContext, Droppable, Draggable, type DropResult } from '@hello-pangea/dnd'
import { useMachineConfig, useUpdateMachine, useToggleEmergency } from './api'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { RoleGate } from '@/features/auth/RoleGate'
import { useAuthStore } from '@/features/auth/store'
import { Activity, AlertTriangle, GripVertical, Plus, Save, Trash2, PowerOff } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { DocumentsTab } from '@/features/documents/DocumentsTab'

export function MachineDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: config, isLoading, isError } = useMachineConfig(id!)
  const updateMachine = useUpdateMachine(id!)
  const toggleEmergency = useToggleEmergency(id!)
  const { toast } = useToast()
  
  const [sop, setSop] = useState<string[]>([])
  const [safetyText, setSafetyText] = useState('')
  const { user } = useAuthStore()
  const isReadOnly = user?.role === 'technician' || user?.role === 'student'

  // Sync state with query data when it loads
  useEffect(() => {
    if (config) {
      setSop(config.sop)
      setSafetyText(config.safety_text)
    }
  }, [config])

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Activity className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (isError || !config) {
    return (
      <div className="flex h-64 items-center justify-center flex-col text-destructive">
        <AlertTriangle className="h-8 w-8 mb-2" />
        <p>Failed to load machine configuration.</p>
      </div>
    )
  }

  const handleDragEnd = (result: DropResult) => {
    if (!result.destination || isReadOnly) return
    
    const items = Array.from(sop)
    const [reorderedItem] = items.splice(result.source.index, 1)
    items.splice(result.destination.index, 0, reorderedItem)
    setSop(items)
  }

  const handleSopChange = (index: number, value: string) => {
    const newSop = [...sop]
    newSop[index] = value
    setSop(newSop)
  }

  const removeSopStep = (index: number) => {
    const newSop = [...sop]
    newSop.splice(index, 1)
    setSop(newSop)
  }

  const addSopStep = () => {
    setSop([...sop, ''])
  }

  const handleSave = () => {
    updateMachine.mutate(
      { sop, safety_text: safetyText },
      {
        onSuccess: () => {
          toast({ title: 'Success', description: 'Machine configuration saved.' })
        },
        onError: () => {
          toast({ variant: 'destructive', title: 'Error', description: 'Failed to save configuration.' })
        }
      }
    )
  }

  const handleEmergency = () => {
    const newState = !config.emergency
    toggleEmergency.mutate(newState, {
      onSuccess: () => {
        toast({ 
          title: newState ? 'Emergency Triggered' : 'Emergency Cleared', 
          description: newState ? 'Machine is now in emergency state.' : 'Machine emergency state lifted.',
          variant: newState ? 'destructive' : 'default'
        })
      },
      onError: () => {
        toast({ variant: 'destructive', title: 'Error', description: 'Failed to toggle emergency state.' })
      }
    })
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-2xl font-bold tracking-tight">{config.name}</h2>
          <p className="text-sm text-muted-foreground">ID: {id}</p>
        </div>
        <div className="flex gap-4 items-center">
          {config.emergency && (
            <Badge variant="destructive" className="animate-pulse px-3 py-1 text-sm">
              EMERGENCY ACTIVE
            </Badge>
          )}
          {/* Emergency is allowed for tech, admin, faculty. We restrict to admin/faculty/tech here. */}
          <RoleGate allowedRoles={['admin', 'faculty', 'technician']}>
            <Button 
              size="lg"
              variant={config.emergency ? "outline" : "destructive"} 
              disabled={toggleEmergency.isPending}
              onClick={handleEmergency}
              className={`min-w-[150px] font-bold ${config.emergency ? 'border-destructive text-destructive hover:bg-destructive/10' : ''}`}
            >
              <PowerOff className="mr-2 h-5 w-5" />
              {config.emergency ? 'CLEAR EMERGENCY' : 'TRIGGER EMERGENCY'}
            </Button>
          </RoleGate>
        </div>
      </div>

      <Tabs defaultValue="config" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="config">Configuration</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
        </TabsList>
        
        <TabsContent value="config" className="space-y-6">
          <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Standard Operating Procedure (SOP)</CardTitle>
            <CardDescription>Drag to reorder the steps required to operate this machine.</CardDescription>
          </CardHeader>
          <CardContent>
            {isReadOnly ? (
              <ol className="list-decimal list-inside space-y-2">
                {sop.map((step, idx) => (
                  <li key={idx} className="text-sm">{step}</li>
                ))}
              </ol>
            ) : (
              <DragDropContext onDragEnd={handleDragEnd}>
                <Droppable droppableId="sop-list">
                  {(provided) => (
                    <div {...provided.droppableProps} ref={provided.innerRef} className="space-y-2">
                      {sop.map((step, index) => (
                        <Draggable key={`step-${index}`} draggableId={`step-${index}`} index={index}>
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              className={`flex items-center gap-2 bg-background p-2 rounded-md border ${snapshot.isDragging ? 'shadow-md border-primary' : ''}`}
                            >
                              <div {...provided.dragHandleProps} className="text-muted-foreground hover:text-foreground cursor-grab">
                                <GripVertical className="h-5 w-5" />
                              </div>
                              <span className="text-sm font-medium w-6 text-muted-foreground">{index + 1}.</span>
                              <Input 
                                value={step} 
                                onChange={(e) => handleSopChange(index, e.target.value)}
                                className="flex-1"
                              />
                              <Button variant="ghost" size="icon" onClick={() => removeSopStep(index)} className="text-destructive hover:text-destructive hover:bg-destructive/10">
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </DragDropContext>
            )}
            
            {!isReadOnly && (
              <Button variant="outline" size="sm" className="mt-4" onClick={addSopStep}>
                <Plus className="h-4 w-4 mr-2" /> Add Step
              </Button>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Safety Instructions</CardTitle>
            <CardDescription>Critical safety information for operators.</CardDescription>
          </CardHeader>
          <CardContent>
            {isReadOnly ? (
              <p className="text-sm whitespace-pre-wrap text-destructive/90">{safetyText}</p>
            ) : (
              <Textarea 
                value={safetyText} 
                onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setSafetyText(e.target.value)}
                rows={5}
                className="w-full"
              />
            )}
          </CardContent>
        </Card>
      </div>

      <RoleGate allowedRoles={['admin', 'faculty']}>
        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={updateMachine.isPending}>
            {updateMachine.isPending ? (
              <Activity className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            Save Configuration
          </Button>
        </div>
      </RoleGate>
        </TabsContent>
        
        <TabsContent value="documents">
          <DocumentsTab machineId={id!} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
