import React from 'react'
import { Menu, X, Upload, RotateCcw, Settings } from 'lucide-react'

interface HeaderProps {
  onUploadClick: () => void
  onReindexClick: () => void
  onSettingsClick?: () => void
  loading?: boolean
}

export function Header({
  onUploadClick,
  onReindexClick,
  onSettingsClick,
  loading = false,
}: HeaderProps) {
  const [sidebarOpen, setSidebarOpen] = React.useState(false)

  return (
    <header className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg">
      <div className="px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 hover:bg-white/10 rounded"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
            <div>
              <h1 className="text-2xl font-bold">RAG Chatbot</h1>
              <p className="text-blue-100 text-sm">Powered by Retrieval-Augmented Generation</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onReindexClick}
              disabled={loading}
              className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 disabled:opacity-50 disabled:cursor-not-allowed transition"
              title="Reindex documents"
            >
              <RotateCcw className="h-4 w-4" />
              <span className="text-sm">Reindex</span>
            </button>
            <button
              onClick={onUploadClick}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 disabled:opacity-50 disabled:cursor-not-allowed transition"
              title="Upload documents"
            >
              <Upload className="h-4 w-4" />
              <span className="text-sm">Upload</span>
            </button>
            {onSettingsClick && (
              <button
                onClick={onSettingsClick}
                className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 transition"
                title="Settings"
              >
                <Settings className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {sidebarOpen && (
        <div className="lg:hidden border-t border-blue-500 px-4 py-2 bg-blue-700 space-y-2">
          <button
            onClick={() => {
              onReindexClick()
              setSidebarOpen(false)
            }}
            className="w-full flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-blue-600 transition text-left"
          >
            <RotateCcw className="h-4 w-4" />
            Reindex Documents
          </button>
          {onSettingsClick && (
            <button
              onClick={() => {
                onSettingsClick()
                setSidebarOpen(false)
              }}
              className="w-full flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-blue-600 transition text-left"
            >
              <Settings className="h-4 w-4" />
              Settings
            </button>
          )}
        </div>
      )}
    </header>
  )
}
