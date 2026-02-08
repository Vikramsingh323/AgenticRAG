export interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  confidence?: number
  sources?: string[]
}

export interface ChatResponse {
  answer_text: string
  confidence_score: number
  source_chunk_ids: string[]
  top_chunks: Array<{
    id: string
    text: string
    combined_score: number
  }>
}

export interface DocumentUpload {
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'success' | 'error'
  error?: string
}
