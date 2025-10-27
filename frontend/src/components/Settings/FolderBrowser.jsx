import { useState, useEffect } from 'react'
import { Folder, ArrowLeft, Home } from 'lucide-react'
import api from '../../services/api'

function FolderBrowser({ isOpen, onClose, onSelectFolder }) {
  const [currentPath, setCurrentPath] = useState(null)
  const [parentPath, setParentPath] = useState(null)
  const [folders, setFolders] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Load initial folder (Downloads directory)
  useEffect(() => {
    if (isOpen) {
      // Start in Downloads folder instead of home
      const downloadsPath = '~/Downloads'
      loadFolders(downloadsPath)
    }
  }, [isOpen])

  const loadFolders = async (path) => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.browseFolders(path)
      setCurrentPath(data.currentPath)
      setParentPath(data.parentPath)
      setFolders(data.folders || [])
    } catch (error) {
      console.error('Failed to load folders:', error)
      setError('Failed to load folders')
    } finally {
      setLoading(false)
    }
  }

  const handleFolderClick = (folderPath) => {
    loadFolders(folderPath)
  }

  const handleGoBack = () => {
    if (parentPath) {
      loadFolders(parentPath)
    }
  }

  const handleSelectCurrent = () => {
    if (currentPath) {
      onSelectFolder(currentPath)
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 max-w-3xl w-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="mb-4">
          <h3 className="text-lg font-semibold mb-2">Select Folder</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={handleGoBack}
              disabled={!parentPath}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
              title="Go back"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => loadFolders('~/Downloads')}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg"
              title="Downloads folder"
            >
              <Home className="w-4 h-4" />
            </button>
            <div className="flex-1 px-3 py-2 bg-gray-900 rounded-lg font-mono text-sm truncate">
              {currentPath || 'Loading...'}
            </div>
          </div>
        </div>

        {/* Folder List */}
        <div className="flex-1 overflow-y-auto bg-gray-900 rounded-lg p-4 mb-4 min-h-[300px]">
          {loading ? (
            <div className="text-center py-8 text-gray-400">Loading folders...</div>
          ) : error ? (
            <div className="text-center py-8 text-red-400">{error}</div>
          ) : folders.length === 0 ? (
            <div className="text-center py-8 text-gray-400">No subfolders</div>
          ) : (
            <div className="space-y-1">
              {folders.map((folder) => (
                <button
                  key={folder.path}
                  onClick={() => handleFolderClick(folder.path)}
                  className="w-full px-4 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg flex items-center gap-3 transition-colors text-left"
                >
                  <Folder className="w-5 h-5 text-blue-400 flex-shrink-0" />
                  <span className="truncate">{folder.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={handleSelectCurrent}
            disabled={!currentPath}
            className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            Select Current Folder
          </button>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

export default FolderBrowser
