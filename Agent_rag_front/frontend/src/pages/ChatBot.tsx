import React from 'react'
import { Header } from '../components/Header'
import { ChatWindow } from '../components/ChatWindow'
import { FileUpload } from '../components/FileUpload'
import { useChatbot } from '../hooks/useChatbot'
import apiClient from '../api/client'

export default function ChatBot() {
  const { messages, loading, error, sendMessage, clearHistory } = useChatbot()
  const [showUpload, setShowUpload] = React.useState(false)
  const [uploadLoading, setUploadLoading] = React.useState(false)

  const handleUpload = async (file: File) => {
    setUploadLoading(true)
    try {
      await apiClient.uploadDocument(file)
      alert(`Document "${file.name}" uploaded successfully!`)
    } catch (error) {
      console.error('Upload failed:', error)
      throw error
    } finally {
      setUploadLoading(false)
    }
  }

  const handleReindex = async () => {
    try {
      await apiClient.reindex()
      alert('Documents reindexed successfully!')
    } catch (error) {
      console.error('Reindex failed:', error)
      alert('Failed to reindex documents')
    }
  }

  return (
    <div className="flex flex-col h-screen">
      <Header
        onUploadClick={() => setShowUpload(!showUpload)}
        onReindexClick={handleReindex}
        loading={uploadLoading}
      />

      <div className="flex-1 flex gap-4 p-4 overflow-hidden">
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          <ChatWindow
            messages={messages}
            loading={loading}
            error={error}
            onSendMessage={sendMessage}
          />
        </div>

        {/* Upload Sidebar */}
        {showUpload && (
          <div className="w-80 bg-white rounded-lg shadow-lg p-4 overflow-y-auto border border-gray-200">
            <h2 className="text-lg font-semibold mb-4 text-gray-800">Upload Documents</h2>
            <FileUpload onUpload={handleUpload} loading={uploadLoading} />
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="font-semibold text-sm text-gray-800 mb-2">📝 Tips</h3>
              <ul className="text-xs text-gray-700 space-y-1">
                <li>• Upload PDF or Markdown files</li>
                <li>• Files are automatically indexed</li>
                <li>• Use "Reindex" to rebuild the index</li>
                <li>• Ask questions about your documents</li>
              </ul>
            </div>
            <button
              onClick={() => setShowUpload(false)}
              className="w-full mt-4 px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
