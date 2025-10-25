import { Film, Play, Download, Upload, Settings } from 'lucide-react'
import { useProject } from '../hooks/useProject'
import { useState, useEffect } from 'react'
import api from '../services/api'
import VoiceSelector from './VoiceSelector'
import MusicManager from './BackgroundMusic/MusicManager'
import OutputFolderSettings from './Settings/OutputFolderSettings'

function Header({ onPreviewGenerated, isEmbedded = false }) {
  const { project, loading, scenes, updateScenesFromPreview, fetchProject } = useProject()
  const [generating, setGenerating] = useState(false)
  const [selectedVoice, setSelectedVoice] = useState('de-DE-KatjaNeural')
  const [targetLanguage, setTargetLanguage] = useState('auto')
  const [aiImageModel, setAiImageModel] = useState('flux-dev')  // Changed from flux-schnell for better quality
  const [showSettings, setShowSettings] = useState(false)

  // Update selected voice, language, and AI model when project changes
  useEffect(() => {
    if (project && project.tts_voice) {
      setSelectedVoice(project.tts_voice)
    }
    if (project && project.target_language) {
      setTargetLanguage(project.target_language)
    }
    if (project && project.ai_image_model) {
      setAiImageModel(project.ai_image_model)
    }
  }, [project])

  // Handle voice change
  const handleVoiceChange = async (newVoice) => {
    setSelectedVoice(newVoice)

    if (project) {
      try {
        await api.updateProject(project.id, { tts_voice: newVoice })
      } catch (error) {
        console.error('Failed to update voice:', error)
      }
    }
  }

  // Handle language change
  const handleLanguageChange = async (e) => {
    const newLanguage = e.target.value
    setTargetLanguage(newLanguage)

    if (project) {
      try {
        await api.updateProject(project.id, { target_language: newLanguage })
      } catch (error) {
        console.error('Failed to update language:', error)
      }
    }
  }

  // Handle AI image model change
  const handleAiImageModelChange = async (e) => {
    const newModel = e.target.value
    setAiImageModel(newModel)

    if (project) {
      try {
        await api.updateProject(project.id, { ai_image_model: newModel })
      } catch (error) {
        console.error('Failed to update AI image model:', error)
      }
    }
  }

  const handleGeneratePreview = async () => {
    if (!project || scenes.length === 0) return

    setGenerating(true)
    try {
      const result = await api.generatePreview(project.id)
      console.log('Preview generated:', result)

      // CRITICAL: Update scenes with actual durations from backend
      if (result.updated_scenes) {
        console.log('✅ Updating frontend scenes with actual durations')
        updateScenesFromPreview(result.updated_scenes)
      } else {
        console.warn('⚠️ No updated_scenes in preview response')
      }

      // Notify parent component
      if (onPreviewGenerated) {
        onPreviewGenerated(result)
      }

      alert(`Preview ready!\n${result.scene_count} scenes, ${result.total_duration}s total\n\n${result.message}`)
    } catch (error) {
      console.error('Failed to generate preview:', error)
      alert('Failed to generate preview. Please try again.')
    } finally {
      setGenerating(false)
    }
  }

  const handleExport = async () => {
    if (!project || scenes.length === 0) return

    const confirmed = confirm(`Export video in 1080p?\n\nProject: ${project.name}\nScenes: ${scenes.length}\n\nThis will take several minutes.`)
    if (!confirmed) return

    setGenerating(true)
    try {
      // Step 1: Generate the video
      const result = await api.exportVideo(project.id, '1080p')
      console.log('Export complete:', result)

      // Step 2: Trigger browser download
      const downloadUrl = `/api/projects/${project.id}/download?resolution=1080p`
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = `${project.name}_1080p.mp4`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      alert(`Export complete!\n\n${result.scene_count} scenes, ${result.total_duration}s total\n\nDownload starting...`)
    } catch (error) {
      console.error('Failed to export video:', error)
      alert('Failed to export video. Please try again.')
    } finally {
      setGenerating(false)
    }
  }

  const handleUploadToQueue = async () => {
    if (!project || scenes.length === 0) return

    const confirmed = confirm(`Upload video to output queue?\n\nProject: ${project.name}\nScenes: ${scenes.length}\n\nThe video will be copied to your configured output folder.`)
    if (!confirmed) return

    setGenerating(true)
    try {
      const result = await api.uploadToQueue(project.id)
      console.log('Upload to queue complete:', result)
      alert(`Upload successful!\n\nVideo copied to: ${result.folder_name}\n\nLocation: ${result.destination_path}`)
    } catch (error) {
      console.error('Failed to upload to queue:', error)
      const errorMessage = error.response?.data?.error || 'Failed to upload to queue'
      alert(`Upload failed: ${errorMessage}\n\nPlease configure an output folder in Settings first.`)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <header className={`bg-dark border-b border-gray-700 ${isEmbedded ? 'px-3 py-2' : 'px-4 py-2'}`}>
      {/* Compact single-row layout for embedded mode */}
      {isEmbedded ? (
        <div className="flex items-center justify-between gap-2 flex-wrap">
          {/* Left side: Settings */}
          <div className="flex items-center gap-2 flex-wrap">
            {/* Voice Selector */}
            <VoiceSelector
              selectedVoice={selectedVoice}
              onVoiceChange={handleVoiceChange}
              disabled={!project || loading}
            />

            {/* Target Language Selector */}
            <select
              value={targetLanguage}
              onChange={handleLanguageChange}
              disabled={!project || loading}
              className="px-3 py-2 bg-dark border border-gray-600 rounded-lg text-sm hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <option value="auto">🌐 Auto (No Translation)</option>
              <option value="de">🇩🇪 Deutsch</option>
              <option value="en">🇬🇧 English</option>
              <option value="es">🇪🇸 Español</option>
              <option value="fr">🇫🇷 Français</option>
              <option value="it">🇮🇹 Italiano</option>
              <option value="pt">🇵🇹 Português</option>
              <option value="pl">🇵🇱 Polski</option>
              <option value="nl">🇳🇱 Nederlands</option>
              <option value="tr">🇹🇷 Türkçe</option>
              <option value="ru">🇷🇺 Русский</option>
              <option value="ja">🇯🇵 日本語</option>
              <option value="zh">🇨🇳 中文</option>
            </select>

            {/* AI Image Model Selector */}
            <select
              value={aiImageModel}
              onChange={handleAiImageModelChange}
              disabled={!project || loading}
              className="px-3 py-2 bg-dark border border-gray-600 rounded-lg text-sm hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="AI Model for Scene Backgrounds"
            >
              <option value="flux-pro-1.1">🎨 Flux Pro 1.1 - $0.04/img (Best Quality)</option>
              <option value="flux-pro">🎨 Flux Pro - $0.055/img (Very Good)</option>
              <option value="flux-dev">🎨 Flux Dev - $0.025/img (Balanced)</option>
              <option value="flux-schnell">⚡ Flux Schnell - $0.003/img (Fast)</option>
              <option value="ideogram-v3">📝 Ideogram V3 - $0.09/img (Text in Images)</option>
              <option value="recraft-v3">🎭 Recraft V3 - $0.04/img (Style Variety)</option>
              <option value="sdxl">💰 SDXL - $0.003/img (Cheap)</option>
            </select>

            {/* Background Music Manager */}
            {project && (
              <MusicManager
                project={project}
                onUpdate={() => fetchProject?.(project.id)}
              />
            )}
          </div>

          {/* Right side: Action Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleGeneratePreview}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              disabled={!project || loading || scenes.length === 0 || generating}
            >
              <Play className="w-4 h-4" />
              {generating ? 'Generating...' : 'Preview'}
            </button>

            <button
              onClick={handleExport}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              disabled={!project || loading || scenes.length === 0 || generating}
            >
              <Download className="w-4 h-4" />
              {generating ? 'Exporting...' : 'Export'}
            </button>

            <button
              onClick={handleUploadToQueue}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              disabled={!project || loading || scenes.length === 0 || generating}
            >
              <Upload className="w-4 h-4" />
              Upload to Queue
            </button>

            <button
              onClick={() => setShowSettings(true)}
              className="px-3 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg flex items-center gap-2 transition-colors text-sm font-medium"
              title="Output Folder Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      ) : (
        /* Original two-row layout for standalone mode */
        <>
          {/* Row 1: Project Title + Settings */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <Film className="w-6 h-6 text-primary" />
              <h1 className="text-lg font-semibold">
                {project ? project.name : 'Video Editor Prototype'}
              </h1>
            </div>

            <div className="flex items-center gap-3">
              {/* Voice Selector */}
              <VoiceSelector
                selectedVoice={selectedVoice}
                onVoiceChange={handleVoiceChange}
                disabled={!project || loading}
              />

              {/* Target Language Selector */}
              <select
                value={targetLanguage}
                onChange={handleLanguageChange}
                disabled={!project || loading}
                className="px-3 py-2 bg-dark border border-gray-600 rounded-lg text-sm hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="auto">🌐 Auto (No Translation)</option>
                <option value="de">🇩🇪 Deutsch</option>
                <option value="en">🇬🇧 English</option>
                <option value="es">🇪🇸 Español</option>
                <option value="fr">🇫🇷 Français</option>
                <option value="it">🇮🇹 Italiano</option>
                <option value="pt">🇵🇹 Português</option>
                <option value="pl">🇵🇱 Polski</option>
                <option value="nl">🇳🇱 Nederlands</option>
                <option value="tr">🇹🇷 Türkçe</option>
                <option value="ru">🇷🇺 Русский</option>
                <option value="ja">🇯🇵 日本語</option>
                <option value="zh">🇨🇳 中文</option>
              </select>

              {/* AI Image Model Selector */}
              <select
                value={aiImageModel}
                onChange={handleAiImageModelChange}
                disabled={!project || loading}
                className="px-3 py-2 bg-dark border border-gray-600 rounded-lg text-sm hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="AI Model for Scene Backgrounds"
              >
                <option value="flux-pro-1.1">🎨 Flux Pro 1.1 - $0.04/img (Best Quality)</option>
                <option value="flux-pro">🎨 Flux Pro - $0.055/img (Very Good)</option>
                <option value="flux-dev">🎨 Flux Dev - $0.025/img (Balanced)</option>
                <option value="flux-schnell">⚡ Flux Schnell - $0.003/img (Fast)</option>
                <option value="ideogram-v3">📝 Ideogram V3 - $0.09/img (Text in Images)</option>
                <option value="recraft-v3">🎭 Recraft V3 - $0.04/img (Style Variety)</option>
                <option value="sdxl">💰 SDXL - $0.003/img (Cheap)</option>
              </select>

              {/* Background Music Manager */}
              {project && (
                <MusicManager
                  project={project}
                  onUpdate={() => fetchProject?.(project.id)}
                />
              )}
            </div>
          </div>

          {/* Row 2: Action Buttons */}
          <div className="flex items-center justify-end gap-3">
            <button
              onClick={handleGeneratePreview}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!project || loading || scenes.length === 0 || generating}
            >
              <Play className="w-4 h-4" />
              {generating ? 'Generating...' : 'Preview'}
            </button>

            <button
              onClick={handleExport}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!project || loading || scenes.length === 0 || generating}
            >
              <Download className="w-4 h-4" />
              {generating ? 'Exporting...' : 'Export'}
            </button>

            <button
              onClick={handleUploadToQueue}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!project || loading || scenes.length === 0 || generating}
            >
              <Upload className="w-4 h-4" />
              Upload to Queue
            </button>

            <button
              onClick={() => setShowSettings(true)}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg flex items-center gap-2 transition-colors"
              title="Output Folder Settings"
            >
              <Settings className="w-4 h-4" />
              Settings
            </button>
          </div>
        </>
      )}

      {/* Settings Modal */}
      <OutputFolderSettings
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
      />
    </header>
  )
}

export default Header
