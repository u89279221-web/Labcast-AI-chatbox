import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'

export interface Document {
  id: string
  machine_id: string
  filename: string
  doc_type: string
  uploaded_at: string
  extraction_method: string
}

export interface DocumentUploadResponse {
  id: string
  filename: string
  message: string
  extracted_length: number
  extraction_method: string
}

export const useDocuments = (machineId: string) => {
  return useQuery({
    queryKey: ['documents', machineId],
    queryFn: async () => {
      const { data } = await api.get<Document[]>(`/api/machine/${machineId}/documents`)
      return data
    },
    retry: false
  })
}

export const useUploadDocument = (machineId: string) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (formData: FormData) => {
      const { data } = await api.post<DocumentUploadResponse>(`/api/machine/${machineId}/documents`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', machineId] })
    },
  })
}

export const useDeleteDocument = (machineId: string) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (documentId: string) => {
      const { data } = await api.delete<{ message: string }>(`/api/machine/${machineId}/documents/${documentId}`)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', machineId] })
    },
  })
}
