import { useState, useCallback } from 'react'
import { Message, ChatResponse } from '../types'
import apiClient from '../api/client'

export function useChatbot() {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendMessage = useCallback(async (content: string) => {
    setError(null)
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setLoading(true)

    try {
      // Get chat history (last 4 messages for context)
      const chatHistory = messages
        .slice(-4)
        .map((m) => `${m.type === 'user' ? 'User' : 'Assistant'}: ${m.content}`)

      const response = await apiClient.chat(content, chatHistory)
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.answer_text,
        timestamp: new Date(),
        confidence: response.confidence_score,
        sources: response.source_chunk_ids,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to get response'
      setError(errorMsg)
      console.error('Chat error:', err)
    } finally {
      setLoading(false)
    }
  }, [messages])

  const clearHistory = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearHistory,
  }
}
