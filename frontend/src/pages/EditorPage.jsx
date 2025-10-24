import { useState, useEffect } from 'react'
import ScriptEditor from '../components/ScriptEditor/ScriptEditor'
import Timeline from '../components/Timeline/Timeline'
import VideoPreview from '../components/VideoPreview/VideoPreview'
import Header from '../components/Header'
import { useProject } from '../hooks/useProject'

function EditorPage() {
  const { project, scenes, selectedSceneId, setSelectedSceneId } = useProject()
  const [previewData, setPreviewData] = useState(null)
  const [isEmbedded, setIsEmbedded] = useState(false)

  // Check if we're in embedded mode (loaded via iframe from main dashboard)
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const embedded = urlParams.get('embedded') === 'true'
    setIsEmbedded(embedded)
  }, [])

  const handlePreviewGenerated = (data) => {
    setPreviewData(data)
  }

  const handlePreviewRegenerated = (data) => {
    // Force preview update by creating a new object with timestamp
    // This ensures ReactPlayer reloads even if the URL is the same
    setPreviewData({
      ...data,
      _timestamp: Date.now() // Add timestamp to force re-render
    })
  }

  return (
    <div className={`flex flex-col bg-darker ${isEmbedded ? 'h-full' : 'h-screen'}`}>
      {/* Pass embedded state to Header to hide title */}
      <Header onPreviewGenerated={handlePreviewGenerated} isEmbedded={isEmbedded} />

      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Script Editor */}
        <div className="w-1/4 border-r border-gray-700 overflow-y-auto">
          <ScriptEditor />
        </div>

        {/* Center Panel - Timeline */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto">
            <Timeline onPreviewRegenerated={handlePreviewRegenerated} />
          </div>
        </div>

        {/* Right Panel - Video Preview */}
        <div className="w-1/3 border-l border-gray-700 overflow-y-auto">
          <VideoPreview previewData={previewData} />
        </div>
      </div>
    </div>
  )
}

export default EditorPage
