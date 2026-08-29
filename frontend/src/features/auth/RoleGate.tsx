import type { ReactNode } from 'react'
import { useAuthStore, type Role } from './store'

interface RoleGateProps {
  children: ReactNode
  allowedRoles: Role[]
  fallback?: ReactNode
}

export function RoleGate({ children, allowedRoles, fallback = null }: RoleGateProps) {
  const { user } = useAuthStore()

  if (!user || !allowedRoles.includes(user.role)) {
    return fallback ? <>{fallback}</> : null
  }

  return <>{children}</>
}
