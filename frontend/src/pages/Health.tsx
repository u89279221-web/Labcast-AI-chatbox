import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Activity, ServerCrash } from 'lucide-react'
import { api } from '@/lib/api'

export function Health() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      // Pinging the /docs endpoint as a simple health check since it's unauthenticated
      const response = await api.get('/docs')
      return response.status === 200
    },
    retry: 1,
  })

  return (
    <div className="mx-auto grid w-full max-w-4xl items-start gap-4 md:gap-8">
      <Card>
        <CardHeader>
          <CardTitle>System Health</CardTitle>
          <CardDescription>
            Live status of the backend API connection.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="flex items-center gap-4 rounded-md border p-4">
            {isLoading ? (
              <Activity className="h-5 w-5 text-muted-foreground animate-spin" />
            ) : isError || !data ? (
              <ServerCrash className="h-5 w-5 text-destructive" />
            ) : (
              <Activity className="h-5 w-5 text-green-500" />
            )}
            
            <div className="flex-1 space-y-1">
              <p className="text-sm font-medium leading-none">
                API Connection
              </p>
              <p className="text-sm text-muted-foreground">
                {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
              </p>
            </div>
            
            {isLoading ? (
              <Badge variant="outline">Checking...</Badge>
            ) : isError || !data ? (
              <Badge variant="destructive">Offline</Badge>
            ) : (
              <Badge className="bg-green-500 hover:bg-green-600 text-white">Online</Badge>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
