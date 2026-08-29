import { create } from 'zustand'
import { jwtDecode } from 'jwt-decode'

export type Role = 'admin' | 'faculty' | 'technician' | 'student'

export interface User {
  id: string
  email: string
  role: Role
}

interface JwtPayload {
  sub: string
  email: string
  role: Role
  exp: number
}

interface AuthState {
  accessToken: string | null
  user: User | null
  setToken: (token: string) => void
  logout: () => void
  checkSession: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,

  setToken: (token: string) => {
    try {
      const decoded = jwtDecode<JwtPayload>(token)
      set({
        accessToken: token,
        user: { id: decoded.sub, email: decoded.email, role: decoded.role },
      })
      // Store a flag in sessionStorage for soft reloads UX (not the token itself)
      sessionStorage.setItem('wasLoggedIn', 'true')
    } catch (e) {
      console.error('Invalid token', e)
    }
  },

  logout: () => {
    set({ accessToken: null, user: null })
    sessionStorage.removeItem('wasLoggedIn')
  },

  // Called on app mount. If they were logged in, they still need to re-login unless
  // we implement a refresh token flow. For now, it just resets state if the token is gone.
  checkSession: () => {
    const wasLoggedIn = sessionStorage.getItem('wasLoggedIn') === 'true'
    if (!wasLoggedIn) {
      set({ accessToken: null, user: null })
    }
  },
}))
