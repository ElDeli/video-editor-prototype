import { useState, useEffect } from 'react'
import { FolderOpen, Plus, Trash2, Star, X } from 'lucide-react'
import api from '../../services/api'
import FolderBrowser from './FolderBrowser'

function OutputFolderSettings({ isOpen, onClose }) {
  const [folders, setFolders] = useState([])
  const [loading, setLoading] = useState(false)
  const [newFolderName, setNewFolderName] = useState('')
  const [newFolderPath, setNewFolderPath] = useState('')
  const [showBrowser, setShowBrowser] = useState(false)

  // Load folders when modal opens
  useEffect(() => {
    if (isOpen) {
      loadFolders()
    }
  }, [isOpen])

  const loadFolders = async () => {
    try {
      setLoading(true)
      const data = await api.getOutputFolders()
      setFolders(data)
    } catch (error) {
      console.error('Failed to load output folders:', error)
      alert('Failed to load output folders')
    } finally {
      setLoading(false)
    }
  }

  const handleAddFolder = async (e) => {
    e.preventDefault()
    if (!newFolderName.trim() || !newFolderPath.trim()) {
      alert('Please enter both name and path')
      return
    }

    try {
      setLoading(true)
      await api.addOutputFolder(newFolderName, newFolderPath)
      setNewFolderName('')
      setNewFolderPath('')
      await loadFolders()
    } catch (error) {
      console.error('Failed to add folder:', error)
      const errorMsg = error.response?.data?.error || error.message || 'Failed to add folder'
      alert(`Failed to add folder\n\nError: ${errorMsg}\n\nFolder Name: ${newFolderName}\nFolder Path: ${newFolderPath}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteFolder = async (folderId) => {
    if (!confirm('Delete this output folder?')) return

    try {
      setLoading(true)
      await api.deleteOutputFolder(folderId)
      await loadFolders()
    } catch (error) {
      console.error('Failed to delete folder:', error)
      alert('Failed to delete folder')
    } finally {
      setLoading(false)
    }
  }

  const handleSetDefault = async (folderId) => {
    try {
      setLoading(true)
      await api.setDefaultOutputFolder(folderId)
      await loadFolders()
    } catch (error) {
      console.error('Failed to set default folder:', error)
      alert('Failed to set default folder')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <FolderOpen className="w-6 h-6" />
            Output Folder Settings
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Add New Folder Form */}
        <form onSubmit={handleAddFolder} className="mb-6 p-4 bg-gray-900 rounded-lg">
          <h3 className="text-lg font-medium mb-3">Add Output Folder</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Folder Name</label>
              <input
                type="text"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                placeholder="e.g., Instagram Reels"
                className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Folder Path</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newFolderPath}
                  onChange={(e) => setNewFolderPath(e.target.value)}
                  placeholder="/Users/username/Videos/Instagram"
                  className="flex-1 px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowBrowser(true)}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-2 transition-colors whitespace-nowrap"
                >
                  <FolderOpen className="w-4 h-4" />
                  Browse
                </button>
              </div>
            </div>
            <button
              type="submit"
              className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              disabled={loading}
            >
              <Plus className="w-4 h-4" />
              Add Folder
            </button>
          </div>
        </form>

        {/* Folders List */}
        <div>
          <h3 className="text-lg font-medium mb-3">Configured Folders</h3>
          {loading && folders.length === 0 ? (
            <div className="text-center py-8 text-gray-400">Loading...</div>
          ) : folders.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              No output folders configured yet
            </div>
          ) : (
            <div className="space-y-2">
              {folders.map((folder) => (
                <div
                  key={folder.id}
                  className={`p-4 rounded-lg border ${
                    folder.is_default
                      ? 'bg-blue-900 bg-opacity-30 border-blue-600'
                      : 'bg-gray-900 border-gray-700'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium">{folder.name}</h4>
                        {folder.is_default && (
                          <span className="px-2 py-0.5 bg-blue-600 text-xs rounded-full flex items-center gap-1">
                            <Star className="w-3 h-3" />
                            Default
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-400 font-mono break-all">
                        {folder.path}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      {!folder.is_default && (
                        <button
                          onClick={() => handleSetDefault(folder.id)}
                          className="p-2 hover:bg-blue-600 rounded-lg transition-colors"
                          title="Set as default"
                          disabled={loading}
                        >
                          <Star className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => handleDeleteFolder(folder.id)}
                        className="p-2 hover:bg-red-600 rounded-lg transition-colors"
                        title="Delete folder"
                        disabled={loading}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-gray-700">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>

      {/* Folder Browser Modal */}
      <FolderBrowser
        isOpen={showBrowser}
        onClose={() => setShowBrowser(false)}
        onSelectFolder={(path) => {
          setNewFolderPath(path)
          setShowBrowser(false)
        }}
      />
    </div>
  )
}

export default OutputFolderSettings
