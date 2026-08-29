import { useMutation } from '@tanstack/react-query'
import { api } from '@/lib/api'

export interface ChatResponse {
  answer: string
  source_snippet: string
}

export const useChatMutation = (machineId: string) => {
  return useMutation({
    mutationFn: async (question: string) => {
      const response = await api.post<ChatResponse>(`/api/machine/${machineId}/chat`, { question })
      return response.data
    },
  })
}
