import { useState } from 'react'
import { useMaintenanceRecords, type MaintenanceRecord } from './api'
import { MaintenanceForm } from './MaintenanceForm'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Wrench, Calendar, Plus } from 'lucide-react'

export function MaintenancePage() {
  const { data: records, isLoading } = useMaintenanceRecords()
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingRecord, setEditingRecord] = useState<MaintenanceRecord | undefined>(undefined)

  // Logic to highlight upcoming maintenance (due within 7 days)
  const today = new Date()
  const sevenDaysFromNow = new Date()
  sevenDaysFromNow.setDate(sevenDaysFromNow.getDate() + 7)

  const upcomingRecords = records?.filter(record => {
    if (!record.next_due_at) return false
    const dueDate = new Date(record.next_due_at)
    return dueDate > today && dueDate <= sevenDaysFromNow
  }) || []

  const handleEdit = (record: MaintenanceRecord) => {
    setEditingRecord(record)
    setIsDialogOpen(true)
  }

  const handleOpenChange = (open: boolean) => {
    setIsDialogOpen(open)
    if (!open) {
      // Small timeout so animation finishes before resetting form
      setTimeout(() => setEditingRecord(undefined), 200)
    }
  }

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '--'
    return new Date(dateStr).toLocaleDateString()
  }

  return (
    <div className="space-y-6 max-w-6xl">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-2xl font-bold tracking-tight">Maintenance</h2>
          <p className="text-sm text-muted-foreground">Manage service records and track upcoming schedules.</p>
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={handleOpenChange}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Log Maintenance
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingRecord ? 'Edit Record' : 'Log Maintenance'}</DialogTitle>
            </DialogHeader>
            <MaintenanceForm 
              initialData={editingRecord}
              onSuccess={() => setIsDialogOpen(false)}
              onCancel={() => setIsDialogOpen(false)}
            />
          </DialogContent>
        </Dialog>
      </div>

      {upcomingRecords.length > 0 && (
        <Card className="border-amber-500/50 bg-amber-500/5 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-amber-600 flex items-center gap-2 text-lg">
              <Calendar className="h-5 w-5" />
              Upcoming Maintenance (Next 7 Days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {upcomingRecords.map(record => (
                <div key={record.id} className="flex items-center justify-between p-3 rounded-lg bg-background border shadow-sm">
                  <div className="flex items-center gap-4">
                    <Badge variant="outline" className="text-amber-600 border-amber-600/30 bg-amber-50">
                      Due: {formatDate(record.next_due_at)}
                    </Badge>
                    <div className="font-medium">{record.machine_id}</div>
                    <div className="text-sm text-muted-foreground line-clamp-1 max-w-[400px]">
                      {record.description}
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => handleEdit(record)}>
                    Update
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>All Records</CardTitle>
          <CardDescription>Comprehensive history of all maintenance activities.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-10 text-center text-muted-foreground">Loading records...</div>
          ) : !records || records.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground border rounded-lg bg-muted/20">
              <Wrench className="h-10 w-10 mx-auto mb-3 opacity-20" />
              <p>No maintenance records found.</p>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Machine</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Performed</TableHead>
                    <TableHead>Next Due</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {records.map((record) => (
                    <TableRow key={record.id}>
                      <TableCell className="font-medium">{record.machine_id}</TableCell>
                      <TableCell className="max-w-xs truncate">{record.description}</TableCell>
                      <TableCell>{formatDate(record.performed_at)}</TableCell>
                      <TableCell>{formatDate(record.next_due_at)}</TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" onClick={() => handleEdit(record)}>
                          Edit
                        </Button>
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
