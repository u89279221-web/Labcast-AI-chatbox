import { useState } from 'react'
import { useCreateMaintenanceRecord, useUpdateMaintenanceRecord, type MaintenanceRecord } from './api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/hooks/use-toast'

interface MaintenanceFormProps {
  initialData?: MaintenanceRecord
  onSuccess?: () => void
  onCancel?: () => void
}

export function MaintenanceForm({ initialData, onSuccess, onCancel }: MaintenanceFormProps) {
  const isEditing = !!initialData
  
  const [machineId, setMachineId] = useState(initialData?.machine_id || '')
  const [description, setDescription] = useState(initialData?.description || '')
  
  // Format for datetime-local input: YYYY-MM-DDThh:mm
  const formatForInput = (dateStr?: string | null) => {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) return ''
    // Adjust for timezone offset to show local time in the input
    const offset = d.getTimezoneOffset()
    const local = new Date(d.getTime() - (offset * 60 * 1000))
    return local.toISOString().slice(0, 16)
  }

  const [performedAt, setPerformedAt] = useState(formatForInput(initialData?.performed_at))
  const [nextDueAt, setNextDueAt] = useState(formatForInput(initialData?.next_due_at))

  const { toast } = useToast()
  
  const createMutation = useCreateMaintenanceRecord()
  const updateMutation = useUpdateMaintenanceRecord()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const payload = {
        machine_id: machineId,
        description,
        performed_at: performedAt ? new Date(performedAt).toISOString() : null,
        next_due_at: nextDueAt ? new Date(nextDueAt).toISOString() : null,
      }

      if (isEditing) {
        await updateMutation.mutateAsync({ id: initialData.id, payload })
        toast({ title: 'Maintenance record updated successfully' })
      } else {
        await createMutation.mutateAsync(payload)
        toast({ title: 'Maintenance record created successfully' })
      }
      
      onSuccess?.()
    } catch (error: any) {
      toast({
        title: 'Error saving record',
        description: error.response?.data?.detail || error.message,
        variant: 'destructive',
      })
    }
  }

  const isPending = createMutation.isPending || updateMutation.isPending

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="machineId">Machine ID</Label>
        <Input 
          id="machineId" 
          value={machineId} 
          onChange={(e) => setMachineId(e.target.value)} 
          placeholder="e.g., CNC01"
          required
          disabled={isEditing}
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea 
          id="description" 
          value={description} 
          onChange={(e) => setDescription(e.target.value)} 
          placeholder="What was done?"
          required
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="performedAt">Performed At</Label>
          <Input 
            id="performedAt" 
            type="datetime-local" 
            value={performedAt} 
            onChange={(e) => setPerformedAt(e.target.value)} 
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="nextDueAt">Next Due At</Label>
          <Input 
            id="nextDueAt" 
            type="datetime-local" 
            value={nextDueAt} 
            onChange={(e) => setNextDueAt(e.target.value)} 
          />
        </div>
      </div>

      <div className="flex justify-end gap-2 pt-4">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isPending}>
          {isPending ? 'Saving...' : 'Save Record'}
        </Button>
      </div>
    </form>
  )
}
