import { useMemo } from 'react'
import { useAnalyticsSummary, useAuditLogs } from './api'
import { AuditLogTable } from './AuditLogTable'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Activity, MessageSquare, ShieldAlert } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { format, parseISO } from 'date-fns'

export function AnalyticsDashboard() {
  const { data: summary, isLoading: isSummaryLoading } = useAnalyticsSummary()
  // Fetch a larger amount of logs to ensure we can build a decent time-series area chart
  const { data: logs, isLoading: isLogsLoading } = useAuditLogs(500)

  // Memoize the chart data transformations
  const chatsChartData = useMemo(() => {
    if (!summary?.chats_per_machine) return []
    return Object.entries(summary.chats_per_machine)
      .map(([machineId, count]) => ({ machineId, count }))
      .sort((a, b) => b.count - a.count)
  }, [summary])

  const emergencyChartData = useMemo(() => {
    if (!logs) return []
    
    // Filter for emergency toggle events
    const emergencyLogs = logs.filter(log => log.action === 'emergency_toggle')
    
    // Group by day
    const grouped = emergencyLogs.reduce((acc, log) => {
      // Use date-fns to start of day, or simply slice the ISO string
      const day = log.timestamp.split('T')[0]
      acc[day] = (acc[day] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    // Convert to sorted array
    return Object.entries(grouped)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => a.date.localeCompare(b.date))
  }, [logs])

  const isLoading = isSummaryLoading || isLogsLoading

  if (isLoading) {
    return <div className="py-10 text-center text-muted-foreground">Loading dashboard...</div>
  }

  if (!summary) {
    return <div className="py-10 text-center text-destructive">Failed to load analytics data.</div>
  }

  return (
    <div className="space-y-6 max-w-7xl">
      <div className="space-y-1">
        <h2 className="text-2xl font-bold tracking-tight">Analytics Dashboard</h2>
        <p className="text-sm text-muted-foreground">Platform usage and real-time monitoring.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Devices</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.active_devices}</div>
            <p className="text-xs text-muted-foreground">Currently online</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Emergency Alerts</CardTitle>
            <ShieldAlert className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.total_emergency_activations}</div>
            <p className="text-xs text-muted-foreground">Lifetime activations</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Chats</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.values(summary.chats_per_machine).reduce((a, b) => a + b, 0)}
            </div>
            <p className="text-xs text-muted-foreground">Across all machines</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Chats by Machine</CardTitle>
            <CardDescription>Number of chatbot interactions per target machine</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chatsChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--muted))" />
                <XAxis dataKey="machineId" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} />
                <RechartsTooltip 
                  cursor={{ fill: 'hsl(var(--muted) / 0.4)' }}
                  contentStyle={{ borderRadius: '8px', border: '1px solid hsl(var(--border))', backgroundColor: 'hsl(var(--background))' }}
                />
                <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Emergency Activations</CardTitle>
            <CardDescription>Frequency of emergency stops over time</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px]">
            {emergencyChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={emergencyChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(var(--destructive))" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="hsl(var(--destructive))" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--muted))" />
                  <XAxis 
                    dataKey="date" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                    tickFormatter={(value) => format(parseISO(value), 'MMM d')}
                  />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} allowDecimals={false} />
                  <RechartsTooltip 
                    contentStyle={{ borderRadius: '8px', border: '1px solid hsl(var(--border))', backgroundColor: 'hsl(var(--background))' }}
                    labelFormatter={(value) => format(parseISO(value as string), 'MMM d, yyyy')}
                  />
                  <Area type="monotone" dataKey="count" stroke="hsl(var(--destructive))" fillOpacity={1} fill="url(#colorCount)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-muted-foreground">
                No emergency activations logged recently.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="mt-8">
        <AuditLogTable />
      </div>
    </div>
  )
}
