import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AppLayout } from '@/components/layout/AppLayout'
import { Health } from '@/pages/Health'
import { Login } from '@/features/auth/Login'
import { ProtectedRoute } from '@/features/auth/ProtectedRoute'
import { RoleGate } from '@/features/auth/RoleGate'
import { Toaster } from '@/components/ui/toaster'
import { MachinesList } from '@/features/machines/MachinesList'
import { MachineDetail } from '@/features/machines/MachineDetail'
import { MachineChat } from '@/features/machines/MachineChat'
import { StudentChat } from '@/pages/StudentChat'
import { DevicesPage } from './features/devices/DevicesPage'
import { MaintenancePage } from './features/maintenance/MaintenancePage'
import { AnalyticsDashboard } from './features/analytics/AnalyticsDashboard'
import { DocumentsPage } from './features/documents/DocumentsPage'
import { GlobalChatPage } from './features/chat/GlobalChatPage'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          {/* Public Standalone Chat */}
          <Route path="/student-chat" element={<StudentChat />} />
          <Route path="/chat/:id" element={<StudentChat />} />
          
          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<Navigate to="/health" replace />} />
              <Route path="/health" element={<Health />} />
              
              {/* Machine Routes */}
              <Route path="/machines" element={<MachinesList />} />
              <Route path="/machines/:id" element={<MachineDetail />} />
              <Route path="/machines/:id/chat" element={<MachineChat />} />
              <Route path="/documents" element={
                <RoleGate allowedRoles={['admin', 'faculty']}>
                  <DocumentsPage />
                </RoleGate>
              } />
              <Route path="/chat" element={
                <RoleGate allowedRoles={['admin', 'faculty', 'student']}>
                  <GlobalChatPage />
                </RoleGate>
              } />
              <Route path="/devices" element={
                <RoleGate allowedRoles={['admin', 'technician']}>
                  <DevicesPage />
                </RoleGate>
              } />
              <Route path="/maintenance" element={
                <RoleGate allowedRoles={['admin', 'technician']}>
                  <MaintenancePage />
                </RoleGate>
              } />
              <Route path="/analytics" element={
                <RoleGate allowedRoles={['admin']}>
                  <AnalyticsDashboard />
                </RoleGate>
              } />
              <Route path="/settings" element={<div>Settings Page</div>} />
            </Route>
          </Route>
        </Routes>
        <Toaster />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
