import React from 'react'
import { Message } from '../types'
import { MessageItem } from './MessageItem'
import { MessageInput } from './MessageInput'
import { Loader2 } from 'lucide-react'

interface ChatWindowProps {
  messages: Message[]
  loading: boolean
  error?: string | null
  onSendMessage: (message: string) => void
}

export function ChatWindow({
  messages,
  loading,
  error,
  onSendMessage,
}: ChatWindowProps) {
  const messagesEndRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="text-4xl mb-4">💬</div>
            <h3 className="text-lg font-semibold text-gray-800">Start a Conversation</h3>
            <p className="text-sm text-gray-600 max-w-md mt-2">
              Ask questions about your documents. The RAG system will search through your document
              database and provide accurate, cited answers.
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div key={message.id} className="group">
                <MessageItem message={message} />
              </div>
            ))}
            {loading && (
              <div className="flex gap-3 justify-start animate-fade-in">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                    AI
                  </div>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
                  <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="px-4 py-3 bg-red-50 border-t border-red-200 text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <MessageInput onSend={onSendMessage} loading={loading} />
      </div>
    </div>
  )
}
