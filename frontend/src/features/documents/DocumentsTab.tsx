import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useDocuments, useUploadDocument, useDeleteDocument } from './api'
import type { Document } from './api'
import { RoleGate } from '@/features/auth/RoleGate'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useToast } from '@/hooks/use-toast'
import { FileText, UploadCloud, Loader2, AlertCircle, Trash2 } from 'lucide-react'

interface DocumentsTabProps {
  machineId: string
}

export function DocumentsTab({ machineId }: DocumentsTabProps) {
  const { data: documents, isLoading, isError } = useDocuments(machineId)
  const uploadMutation = useUploadDocument(machineId)
  const deleteMutation = useDeleteDocument(machineId)
  const { toast } = useToast()
  
  const handleDelete = (doc: Document) => {
    deleteMutation.mutate(doc.id, {
      onSuccess: () => {
        toast({
          title: 'Document Deleted',
          description: `"${doc.filename}" has been permanently removed from the database.`,
        })
      },
      onError: (error: any) => {
        toast({
          title: 'Delete Failed',
          description: error.response?.data?.detail || 'Failed to delete document',
          variant: 'destructive',
        })
      }
    })
  }

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    // Create form data
    const formData = new FormData()
    formData.append('file', file)
    formData.append('doc_type', 'manual') // default to manual for now

    uploadMutation.mutate(formData, {
      onSuccess: (data) => {
        toast({
          title: 'Upload Successful',
          description: `${data.filename} processed successfully.`,
        })
      },
      onError: (error: any) => {
        toast({
          title: 'Upload Failed',
          description: error.response?.data?.detail || 'An error occurred during upload.',
          variant: 'destructive',
        })
      }
    })
  }, [uploadMutation, toast])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    disabled: uploadMutation.isPending
  })

  return (
    <div className="space-y-6">
      <RoleGate allowedRoles={['admin', 'faculty']}>
        <Card>
          <CardHeader>
            <CardTitle>Upload Document</CardTitle>
            <CardDescription>Upload manuals, safety guides, or SOPs (PDF, Word, or Text).</CardDescription>
          </CardHeader>
          <CardContent>
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-colors ${
                isDragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:bg-muted/50'
              } ${uploadMutation.isPending ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <input {...getInputProps()} />
              
              <div className="flex flex-col items-center gap-2">
                {uploadMutation.isPending ? (
                  <>
                    <Loader2 className="h-10 w-10 text-primary animate-spin mb-2" />
                    <p className="text-sm font-medium">Extracting text... this may take a moment.</p>
                  </>
                ) : (
                  <>
                    <UploadCloud className={`h-10 w-10 mb-2 ${isDragActive ? 'text-primary' : 'text-muted-foreground'}`} />
                    <p className="text-sm font-medium">
                      {isDragActive ? 'Drop the file here' : 'Drag & drop a file (PDF, Word, TXT) here, or click to browse'}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">PDFs, Word documents (.docx), and Text files will be automatically parsed and indexed for AI search.</p>
                  </>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </RoleGate>

      <Card>
        <CardHeader>
          <CardTitle>Document Library</CardTitle>
          <CardDescription>Documents currently indexed for this machine.</CardDescription>
        </CardHeader>
        <CardContent>
          <RoleGate 
            allowedRoles={['admin', 'faculty']} 
            fallback={
              <div className="text-center py-6 text-muted-foreground">
                <AlertCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>You do not have permission to view the document library.</p>
              </div>
            }
          >
            {isLoading ? (
              <div className="flex justify-center p-8">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            ) : isError ? (
              <div className="text-center text-destructive p-4 border rounded-md bg-destructive/10">
                Failed to load documents.
              </div>
            ) : documents?.length === 0 ? (
              <div className="text-center py-10 text-muted-foreground border rounded-lg bg-muted/20">
                <FileText className="h-10 w-10 mx-auto mb-3 opacity-20" />
                <p>No documents found for this machine.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {documents?.map((doc: Document) => (
                  <div key={doc.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/30 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded bg-primary/10 text-primary flex items-center justify-center shrink-0">
                        <FileText className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-medium text-sm line-clamp-1">{doc.filename}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(doc.uploaded_at).toLocaleDateString()} • {doc.doc_type}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {doc.extraction_method === 'OCR' ? (
                        <Badge variant="outline" className="bg-amber-100 text-amber-800 hover:bg-amber-100 border-amber-300 dark:bg-amber-900/30 dark:text-amber-200 dark:border-amber-700/50">
                          Extracted via OCR
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="bg-emerald-100 text-emerald-800 hover:bg-emerald-100 border-emerald-300 dark:bg-emerald-900/30 dark:text-emerald-200 dark:border-emerald-700/50">
                          Extracted
                        </Badge>
                      )}

                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                        title="Delete document"
                        disabled={deleteMutation.isPending}
                        onClick={() => handleDelete(doc)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </RoleGate>
        </CardContent>
      </Card>
    </div>
  )
}
