import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore, type Role } from './store'

interface ProtectedRouteProps {
  allowedRoles?: Role[]
}

export function ProtectedRoute({ allowedRoles }: ProtectedRouteProps) {
  const { accessToken, user } = useAuthStore()

  if (!accessToken) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    // If authenticated but unauthorized for this route, fallback to home or a 403 page
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
