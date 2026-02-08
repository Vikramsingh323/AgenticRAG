import React from 'react'
import { Message } from '../types'
import { Copy, Check, BarChart3 } from 'lucide-react'

interface MessageItemProps {
  message: Message
}

export function MessageItem({ message }: MessageItemProps) {
  const [copied, setCopied] = React.useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={`flex gap-3 mb-4 animate-slide-up ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
      {message.type === 'assistant' && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
            AI
          </div>
        </div>
      )}

      <div className={`max-w-2xl ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
        <div
          className={`rounded-lg px-4 py-3 ${
            message.type === 'user'
              ? 'bg-blue-600 text-white'
              : 'bg-white border border-gray-200 text-gray-800'
          }`}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

          {message.type === 'assistant' && (
            <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
              {message.confidence !== undefined && (
                <div className="flex items-center gap-2 text-xs">
                  <BarChart3 className="w-4 h-4" />
                  <span>Confidence: {(message.confidence * 100).toFixed(1)}%</span>
                </div>
              )}
              {message.sources && message.sources.length > 0 && (
                <details className="text-xs">
                  <summary className="cursor-pointer font-medium hover:underline">
                    📚 Sources ({message.sources.length})
                  </summary>
                  <div className="mt-2 space-y-1 pl-4">
                    {message.sources.slice(0, 3).map((source) => (
                      <div key={source} className="text-gray-600">
                        • {source}
                      </div>
                    ))}
                    {message.sources.length > 3 && (
                      <div className="text-gray-600">
                        • +{message.sources.length - 3} more
                      </div>
                    )}
                  </div>
                </details>
              )}
            </div>
          )}
        </div>

        <div className="flex gap-2 mt-2 opacity-0 group-hover:opacity-100 transition">
          <button
            onClick={handleCopy}
            className="text-gray-500 hover:text-gray-700 transition text-xs flex items-center gap-1"
          >
            {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
          </button>
          <span className="text-xs text-gray-500">
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>
      </div>

      {message.type === 'user' && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-gray-700 font-bold">
            You
          </div>
        </div>
      )}
    </div>
  )
}
