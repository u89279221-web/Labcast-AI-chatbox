import { useEffect } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Settings, Activity, FileText, Cpu, MessageSquare, Wrench, LogOut } from 'lucide-react'
import { useAuthStore } from '@/features/auth/store'
import { RoleGate } from '@/features/auth/RoleGate'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { GlobalEmergencyListener } from '@/features/machines/GlobalEmergencyListener'
import { wsClient } from '@/lib/ws-client'

export function AppLayout() {
  const { user, accessToken, logout } = useAuthStore()
  const location = useLocation()

  useEffect(() => {
    if (user && accessToken) {
      wsClient.connect(accessToken)
    } else {
      wsClient.disconnect()
    }
  }, [user, accessToken])

  const NavItem = ({ to, icon: Icon, label, roles }: { to: string, icon: any, label: string, roles?: any[] }) => {
    const isActive = location.pathname === to
    
    const content = (
      <Link
        to={to}
        className={`flex items-center gap-3 rounded-lg px-3 py-2 transition-all ${
          isActive 
            ? 'bg-muted text-primary' 
            : 'text-muted-foreground hover:text-primary hover:bg-muted'
        }`}
      >
        <Icon className="h-5 w-5" />
        {label}
      </Link>
    )

    if (roles) {
      return <RoleGate allowedRoles={roles}>{content}</RoleGate>
    }
    
    return content
  }

  return (
    <div className="flex min-h-screen w-full bg-muted/40">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-10 hidden w-64 flex-col border-r bg-background sm:flex">
        <div className="flex h-14 items-center border-b px-4 lg:h-[60px] lg:px-6">
          <Link to="/" className="flex items-center gap-2 font-semibold">
            <Activity className="h-6 w-6 text-primary" />
            <span className="text-lg">LabCast AI</span>
          </Link>
        </div>
        <nav className="flex-1 space-y-1 px-2 py-4 overflow-y-auto">
          <NavItem to="/" icon={LayoutDashboard} label="Dashboard" />
          
          <NavItem 
            to="/machines" 
            icon={Cpu} 
            label="Machines" 
            roles={['admin', 'faculty', 'technician']} 
          />
          
          <NavItem 
            to="/documents" 
            icon={FileText} 
            label="Documents" 
            roles={['admin', 'faculty']} 
          />
          
          <NavItem 
            to="/chat" 
            icon={MessageSquare} 
            label="AI Assistant" 
            roles={['admin', 'faculty', 'student']} 
          />
          
          <NavItem 
            to="/devices" 
            icon={Cpu} 
            label="IoT Devices" 
            roles={['admin', 'technician']} 
          />
          
          <NavItem 
            to="/maintenance" 
            icon={Wrench} 
            label="Maintenance" 
            roles={['admin', 'technician']} 
          />

          <NavItem 
            to="/analytics" 
            icon={Activity} 
            label="Analytics" 
            roles={['admin']} 
          />
        </nav>
        <div className="mt-auto border-t p-4">
          <NavItem to="/settings" icon={Settings} label="Settings" />
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex flex-col sm:gap-4 sm:py-4 sm:pl-64 w-full">
        {/* Top Nav */}
        <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6">
          <div className="flex flex-1 items-center gap-4 md:ml-auto md:gap-2 lg:gap-4">
            <h1 className="text-xl font-semibold tracking-tight">
              {location.pathname === '/' ? 'Dashboard' : location.pathname.substring(1).charAt(0).toUpperCase() + location.pathname.substring(2)}
            </h1>
            <div className="ml-auto flex items-center space-x-4">
              {user && (
                <div className="flex items-center gap-4">
                  <div className="flex flex-col text-right">
                    <span className="text-sm font-medium">{user.email}</span>
                    <Badge variant="outline" className="w-fit ml-auto uppercase text-[10px]">
                      {user.role}
                    </Badge>
                  </div>
                  <Button variant="outline" size="icon" onClick={() => logout()}>
                    <LogOut className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="flex-1 items-start gap-4 p-4 sm:px-6 sm:py-0 md:gap-8">
          <Outlet />
        </main>
      </div>
      
      {/* Global Realtime Listeners */}
      <GlobalEmergencyListener />
    </div>
  )
}
