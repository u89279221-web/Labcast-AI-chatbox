import { Link } from 'react-router-dom'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Activity, AlertTriangle, Cpu } from 'lucide-react'
import { useMachines } from './api'

export function MachinesList() {
  const { data: machines, isLoading, isError } = useMachines()

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Activity className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (isError || !machines) {
    return (
      <div className="flex h-64 items-center justify-center flex-col text-destructive">
        <AlertTriangle className="h-8 w-8 mb-2" />
        <p>Failed to load machines.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight">Connected Machines</h2>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {machines.map((machine) => (
          <Link key={machine.id} to={`/machines/${machine.id}`}>
            <Card className="hover:border-primary/50 transition-colors cursor-pointer h-full">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-base font-semibold truncate pr-4">
                  {machine.name}
                </CardTitle>
                <Cpu className="h-4 w-4 text-muted-foreground flex-shrink-0" />
              </CardHeader>
              <CardContent>
                <div className="text-xs text-muted-foreground mb-4">ID: {machine.id}</div>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="outline" className="bg-green-500/10 text-green-600 hover:bg-green-500/20 border-green-500/20">
                    Online
                  </Badge>
                  {machine.emergency && (
                    <Badge variant="destructive" className="animate-pulse">
                      Emergency Active
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
