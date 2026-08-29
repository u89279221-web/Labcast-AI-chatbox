import { useMutation } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { useAuthStore } from './store'
import { useToast } from '@/hooks/use-toast'

export function useAuth() {
  const store = useAuthStore()
  const { toast } = useToast()

  const loginMutation = useMutation({
    mutationFn: async (credentials: Record<string, string>) => {
      // Backend expects OAuth2 form data
      const formData = new URLSearchParams()
      formData.append('username', credentials.email)
      formData.append('password', credentials.password)

      const response = await api.post('/api/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      return response.data
    },
    onSuccess: (data) => {
      store.setToken(data.access_token)
      toast({
        title: 'Logged in successfully',
      })
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail || error?.message || 'Please check your email and password.'
      toast({
        variant: 'destructive',
        title: 'Login failed',
        description: detail,
      })
    },
  })

  return {
    user: store.user,
    isAuthenticated: !!store.accessToken,
    login: loginMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    logout: store.logout,
  }
}
