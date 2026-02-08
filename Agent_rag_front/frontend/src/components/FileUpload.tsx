import React from 'react'
import { Upload, X, CheckCircle, AlertCircle } from 'lucide-react'
import { DocumentUpload } from '../types'

interface FileUploadProps {
  onUpload: (file: File) => void
  loading?: boolean
}

export function FileUpload({ onUpload, loading = false }: FileUploadProps) {
  const fileInputRef = React.useRef<HTMLInputElement>(null)
  const [uploads, setUploads] = React.useState<DocumentUpload[]>([])

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files) return

    for (const file of Array.from(files)) {
      if (!file.name.endsWith('.pdf') && !file.name.endsWith('.md')) {
        alert('Only PDF and Markdown files are supported')
        continue
      }

      const upload: DocumentUpload = {
        file,
        progress: 0,
        status: 'uploading',
      }
      setUploads((prev) => [...prev, upload])

      try {
        await onUpload(file)
        setUploads((prev) =>
          prev.map((u) =>
            u.file === file ? { ...u, status: 'success', progress: 100 } : u
          )
        )
      } catch (error) {
        setUploads((prev) =>
          prev.map((u) =>
            u.file === file
              ? {
                  ...u,
                  status: 'error',
                  error: error instanceof Error ? error.message : 'Upload failed',
                }
              : u
          )
        )
      }
    }
  }

  const removeUpload = (index: number) => {
    setUploads((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-4">
      <div
        className="border-2 border-dashed border-blue-300 rounded-lg p-6 text-center hover:bg-blue-50 transition cursor-pointer"
        onClick={() => fileInputRef.current?.click()}
      >
        <Upload className="mx-auto h-8 w-8 text-blue-500 mb-2" />
        <p className="text-sm text-gray-700">
          <span className="font-medium text-blue-600">Click to upload</span> or drag and drop
        </p>
        <p className="text-xs text-gray-500">PDF or Markdown files</p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.md"
          onChange={handleFileSelect}
          className="hidden"
          disabled={loading}
        />
      </div>

      {uploads.length > 0 && (
        <div className="space-y-2">
          {uploads.map((upload, index) => (
            <div key={index} className="flex items-center gap-3 p-3 bg-white rounded-lg border">
              {upload.status === 'uploading' && (
                <div className="flex-1">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">
                      {upload.file.name}
                    </span>
                    <span className="text-xs text-gray-500">{upload.progress}%</span>
                  </div>
                  <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500 transition-all"
                      style={{ width: `${upload.progress}%` }}
                    />
                  </div>
                </div>
              )}
              {upload.status === 'success' && (
                <>
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="flex-1 text-sm text-gray-700">{upload.file.name}</span>
                </>
              )}
              {upload.status === 'error' && (
                <>
                  <AlertCircle className="h-5 w-5 text-red-500" />
                  <div className="flex-1">
                    <p className="text-sm text-gray-700">{upload.file.name}</p>
                    <p className="text-xs text-red-500">{upload.error}</p>
                  </div>
                </>
              )}
              <button
                onClick={() => removeUpload(index)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="h-4 w-4 text-gray-500" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
