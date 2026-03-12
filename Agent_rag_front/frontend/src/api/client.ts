import axios, { AxiosInstance, AxiosError } from 'axios'
import { ChatResponse } from '../types'

export interface APIError {
  error: string
  details?: string
  status?: number
}

class APIClient {
  private client: AxiosInstance

  constructor(baseURL: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000') {
    this.client = axios.create({
      baseURL,
      timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
      headers: {
        'Content-Type': 'application/json',
      }
    })

    // Add response interceptor for better error handling
    this.client.interceptors.response.use(
      response => response,
      error => {
        const errorData: APIError = {
          error: 'Unknown error',
          status: error.response?.status
        }

        if (error.response) {
          // Server responded with error status
          errorData.error = error.response.data?.error || `Server error (${error.response.status})`
          errorData.details = error.response.data?.details
        } else if (error.request) {
          // Request made but no response
          errorData.error = 'Network error: No response from server'
          errorData.details = `Could not connect to ${this.client.defaults.baseURL}`
        } else {
          // Something else happened
          errorData.error = 'Request error'
          errorData.details = error.message
        }

        return Promise.reject(errorData)
      }
    )
  }

  async chat(question: string, chatHistory?: string[]): Promise<ChatResponse> {
    try {
      const response = await this.client.post<ChatResponse>('/api/chat', {
        question,
        chat_history: chatHistory || [],
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async uploadDocument(file: File): Promise<{ message: string; filename: string }> {
    try {
      const formData = new FormData()
      formData.append('file', file)

      // Don't set Content-Type header - let axios set it with proper boundary
      const response = await this.client.post('/api/upload', formData)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async getSystemInfo(): Promise<{ status: string; version: string }> {
    try {
      const response = await this.client.get('/api/health')
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async reindex(): Promise<{ message: string }> {
    try {
      const response = await this.client.post('/api/reindex', {})
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  private handleError(error: any): APIError {
    if (error.error) {
      return error // Already formatted by interceptor
    }

    return {
      error: 'Network error',
      details: error?.message || 'Unknown error occurred',
      status: error?.status
    }
  }
}

export default new APIClient()
