import { useState, useRef, useEffect } from 'react'
import { Trash2, Edit, GripVertical, RefreshCw, Wand2, X, Loader, Play, Pause, Volume2, Clock } from 'lucide-react'
import { useProject } from '../../hooks/useProject'
import EffectsPanel from './EffectsPanel'
import SceneImageUploader from '../SceneImage/SceneImageUploader'
import axios from 'axios'

const API_BASE = 'http://localhost:5001/api'

function SceneCard({ scene, index, isSelected, onSelect, onPreviewRegenerated }) {
  const { updateScene, deleteScene, fetchProject } = useProject()
  const [isEditing, setIsEditing] = useState(false)
  const [editedScript, setEditedScript] = useState(scene.script)
  const [isRegenerating, setIsRegenerating] = useState(false)
  const [thumbnailTimestamp, setThumbnailTimestamp] = useState(Date.now())
  const [isEffectsOpen, setIsEffectsOpen] = useState(false)

  // Keyword editing state
  const [isEditingKeyword, setIsEditingKeyword] = useState(false)
  const [editedKeyword, setEditedKeyword] = useState(scene.background_value || '')

  // Sound Effects state
  const [showSoundEffectInput, setShowSoundEffectInput] = useState(false)
  const [soundEffectPrompt, setSoundEffectPrompt] = useState('')
  const [generatingSoundEffect, setGeneratingSoundEffect] = useState(false)
  const [isPlayingSoundEffect, setIsPlayingSoundEffect] = useState(false)
  const [soundEffectVolume, setSoundEffectVolume] = useState(scene.sound_effect_volume || 50)
  const [soundEffectOffset, setSoundEffectOffset] = useState(scene.sound_effect_offset || 0)
  const soundEffectAudioRef = useRef(null)

  // Sync volume and offset state when scene prop changes
  useEffect(() => {
    setSoundEffectVolume(scene.sound_effect_volume || 50)
    setSoundEffectOffset(scene.sound_effect_offset || 0)
  }, [scene.sound_effect_volume, scene.sound_effect_offset])

  const handleImageUpdate = () => {
    // Refresh project data to get updated scene
    if (fetchProject && scene.project_id) {
      fetchProject(scene.project_id)
    }
  }

  const handleGenerateSoundEffect = async () => {
    if (!soundEffectPrompt.trim()) {
      alert('Please enter a sound effect description')
      return
    }

    setGeneratingSoundEffect(true)
    try {
      const response = await axios.post(`${API_BASE}/scenes/${scene.id}/sound-effect/generate`, {
        text_prompt: soundEffectPrompt
      })

      // Refresh project to get updated scene
      if (fetchProject && scene.project_id) {
        await fetchProject(scene.project_id)
      }

      setShowSoundEffectInput(false)
      setSoundEffectPrompt('')
      alert('Sound Effect generiert!')
    } catch (error) {
      console.error('Failed to generate sound effect:', error)
      alert(error.response?.data?.error || 'Failed to generate sound effect')
    } finally {
      setGeneratingSoundEffect(false)
    }
  }

  const handleRemoveSoundEffect = async () => {
    if (!confirm('Sound Effect entfernen?')) return

    try {
      await axios.delete(`${API_BASE}/scenes/${scene.id}/sound-effect`)

      // Refresh project to get updated scene
      if (fetchProject && scene.project_id) {
        await fetchProject(scene.project_id)
      }

      alert('Sound Effect entfernt!')
    } catch (error) {
      console.error('Failed to remove sound effect:', error)
      alert('Failed to remove sound effect')
    }
  }

  const handleSoundEffectVolumeChange = async (e) => {
    e.stopPropagation()
    const newVolume = parseInt(e.target.value)
    setSoundEffectVolume(newVolume)

    try {
      await updateScene(scene.id, { sound_effect_volume: newVolume })
    } catch (error) {
      console.error('Failed to update sound effect volume:', error)
    }
  }

  const handleSoundEffectOffsetChange = async (e) => {
    e.stopPropagation()
    const newOffset = parseInt(e.target.value)
    setSoundEffectOffset(newOffset)

    try {
      await updateScene(scene.id, { sound_effect_offset: newOffset })
    } catch (error) {
      console.error('Failed to update sound effect offset:', error)
    }
  }

  const handleToggleSoundEffectPlayback = (e) => {
    e.stopPropagation()

    if (!soundEffectAudioRef.current) {
      // Create audio element if it doesn't exist - use API endpoint to serve the file
      soundEffectAudioRef.current = new Audio(`${API_BASE}/scenes/${scene.id}/sound-effect/audio`)
      soundEffectAudioRef.current.addEventListener('ended', () => {
        setIsPlayingSoundEffect(false)
      })
    }

    if (isPlayingSoundEffect) {
      // Pause
      soundEffectAudioRef.current.pause()
      soundEffectAudioRef.current.currentTime = 0
      setIsPlayingSoundEffect(false)
    } else {
      // Play
      soundEffectAudioRef.current.play()
      setIsPlayingSoundEffect(true)
    }
  }

  const handleSave = async () => {
    try {
      await updateScene(scene.id, { script: editedScript })
      setIsEditing(false)
    } catch (error) {
      console.error('Failed to update scene:', error)
    }
  }

  const handleSaveKeyword = async () => {
    if (!editedKeyword.trim()) {
      alert('Keyword darf nicht leer sein')
      return
    }

    try {
      // Update keyword in database
      await updateScene(scene.id, { background_value: editedKeyword })
      setIsEditingKeyword(false)

      // Ask if user wants to regenerate image with new keyword
      if (confirm('Neues Bild mit diesem Keyword generieren?')) {
        setIsRegenerating(true)
        try {
          // Call regenerate-image API (which will use the new keyword from DB)
          const response = await fetch(`${API_BASE}/scenes/${scene.id}/regenerate-image`, {
            method: 'POST'
          })

          if (!response.ok) {
            throw new Error('Failed to regenerate image')
          }

          const data = await response.json()
          console.log('Image regenerated with new keyword:', data)

          // Force thumbnail reload
          setThumbnailTimestamp(Date.now())
          alert('Bild wurde neu generiert!')
        } catch (error) {
          console.error('Failed to regenerate image:', error)
          alert('Fehler beim Generieren des Bildes')
        } finally {
          setIsRegenerating(false)
        }
      }
    } catch (error) {
      console.error('Failed to update keyword:', error)
      alert('Fehler beim Speichern des Keywords')
    }
  }

  const handleDelete = async () => {
    if (confirm('Delete this scene?')) {
      try {
        await deleteScene(scene.id)
      } catch (error) {
        console.error('Failed to delete scene:', error)
      }
    }
  }

  const handleRegenerateImage = async () => {
    console.log('🔄 Regenerate image clicked for scene:', scene.id, scene.background_value)

    if (!scene.background_value) {
      alert('This scene has no image to regenerate')
      return
    }

    // Confirmation dialog
    if (!confirm('Neues Bild generieren? Das Preview-Video wird automatisch neu generiert.')) {
      console.log('❌ Regeneration cancelled by user')
      return
    }

    console.log('✅ Starting regeneration for scene:', scene.id)
    setIsRegenerating(true)
    try {
      // Step 1: Regenerate image for this scene
      const response = await fetch(`http://localhost:5001/api/scenes/${scene.id}/regenerate-image`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error('Failed to regenerate image')
      }

      const data = await response.json()
      console.log('📦 Regenerate API response:', data)

      // Step 2: Update scene with new background value
      console.log('💾 Updating scene with new keyword:', data.new_keyword)
      await updateScene(scene.id, {
        background_value: data.new_keyword
      })

      // Step 3: Force thumbnail reload by updating timestamp state
      const newTimestamp = Date.now()
      console.log('🖼️ Updating thumbnail timestamp:', newTimestamp)
      setThumbnailTimestamp(newTimestamp)

      // Step 4: Automatically regenerate preview video
      alert('Bild wird generiert... Preview wird automatisch aktualisiert.')

      // Get project ID from scene
      const projectId = scene.project_id
      console.log('🎬 Triggering preview regeneration for project:', projectId)

      // Trigger preview regeneration
      const previewResponse = await fetch(`http://localhost:5001/api/projects/${projectId}/preview`, {
        method: 'POST'
      })

      if (!previewResponse.ok) {
        throw new Error('Failed to regenerate preview')
      }

      const previewData = await previewResponse.json()
      console.log('✅ Preview regenerated:', previewData)

      // Notify parent component to update preview video
      if (onPreviewRegenerated) {
        console.log('📡 Notifying parent component with preview data')
        onPreviewRegenerated(previewData)
      } else {
        console.warn('⚠️ No onPreviewRegenerated callback provided!')
      }

      alert('✓ Bild und Preview erfolgreich aktualisiert!')

      // Don't reload - just refresh the component
      // window.location.reload() creates a NEW project! Bug!
      // Instead, notify parent to update preview state
    } catch (error) {
      console.error('Failed to regenerate:', error)
      alert('Fehler beim Generieren. Bitte versuche es erneut.')
    } finally {
      setIsRegenerating(false)
    }
  }

  // Get thumbnail image URL with cache-busting timestamp
  const getThumbnailUrl = () => {
    if (scene.background_type === 'keyword' && scene.background_value) {
      // Generate thumbnail URL from backend API with timestamp to force reload
      return `http://localhost:5001/api/thumbnails/${encodeURIComponent(scene.background_value)}?t=${thumbnailTimestamp}`
    }
    return null
  }

  return (
    <div
      onClick={onSelect}
      className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
        isSelected
          ? 'border-primary bg-dark/50'
          : 'border-gray-700 bg-dark hover:border-gray-600'
      }`}
    >
      <div className="flex items-start gap-3">
        <GripVertical className="w-5 h-5 text-gray-500 mt-1 cursor-move flex-shrink-0" />

        {/* Thumbnail Preview with Regenerate Button */}
        <div className="relative w-16 h-24 flex-shrink-0 group">
          {getThumbnailUrl() ? (
            <>
              {/* Real AI-generated thumbnail image */}
              <img
                src={getThumbnailUrl()}
                alt={`Scene ${index + 1}`}
                className="w-full h-full rounded object-cover"
                onError={(e) => {
                  // Fallback to gray background if image fails to load
                  e.target.style.display = 'none'
                  e.target.nextSibling.style.display = 'flex'
                }}
              />
              {/* Fallback gray background */}
              <div className="hidden w-full h-full rounded bg-gray-800 items-center justify-center text-white text-xs">
                {scene.duration}s
              </div>
              {/* Duration overlay */}
              <div className="absolute bottom-1 right-1 bg-black/70 px-1 rounded text-[10px] text-white">
                {scene.duration}s
              </div>
            </>
          ) : (
            /* No thumbnail - show gray background */
            <div className="w-full h-full rounded bg-gray-800 flex items-center justify-center text-white text-xs">
              {scene.duration}s
            </div>
          )}

          {/* Regenerate Button - appears on hover */}
          <button
            onClick={(e) => {
              e.stopPropagation()
              handleRegenerateImage()
            }}
            disabled={isRegenerating}
            className="absolute inset-0 bg-black/70 rounded opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
            title="Regenerate image"
          >
            <RefreshCw className={`w-6 h-6 text-white ${isRegenerating ? 'animate-spin' : ''}`} />
          </button>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-semibold text-gray-400">
              Scene {index + 1}
            </span>
          </div>

          {isEditing ? (
            <div className="space-y-2">
              <textarea
                value={editedScript}
                onChange={(e) => setEditedScript(e.target.value)}
                className="w-full bg-darker border border-gray-600 rounded p-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                rows={3}
                onClick={(e) => e.stopPropagation()}
              />
              <div className="flex gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleSave()
                  }}
                  className="px-3 py-1 bg-primary hover:bg-blue-600 rounded text-sm"
                >
                  Save
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setIsEditing(false)
                    setEditedScript(scene.script)
                  }}
                  className="px-3 py-1 bg-gray-600 hover:bg-gray-500 rounded text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-300 line-clamp-2">
              {scene.script}
            </p>
          )}

          <div className="flex items-center gap-2 mt-2 flex-wrap">
            <span className={`text-xs px-2 py-1 rounded ${
              scene.background_type === 'keyword'
                ? 'bg-purple-600 text-white'
                : scene.background_type === 'image'
                ? 'bg-pink-600 text-white'
                : 'bg-gray-700 text-gray-300'
            }`}>
              {scene.background_type === 'keyword' ? '🖼️ Visual' : scene.background_type === 'image' ? '📸 Custom' : scene.background_type}
            </span>

            {/* Editable Keyword */}
            {scene.background_type === 'keyword' && scene.background_value && (
              isEditingKeyword ? (
                <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="text"
                    value={editedKeyword}
                    onChange={(e) => setEditedKeyword(e.target.value)}
                    className="text-xs px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-1 focus:ring-primary"
                    placeholder="Enter keyword..."
                    onClick={(e) => e.stopPropagation()}
                  />
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleSaveKeyword()
                    }}
                    className="px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-xs text-white"
                  >
                    Save
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setIsEditingKeyword(false)
                      setEditedKeyword(scene.background_value)
                    }}
                    className="px-2 py-1 bg-gray-600 hover:bg-gray-500 rounded text-xs text-white"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-1 group">
                  <span className="text-xs px-2 py-1 bg-blue-600 rounded text-white">
                    🔍 {scene.background_value}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setIsEditingKeyword(true)
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-700 rounded transition-opacity"
                    title="Edit keyword"
                  >
                    <Edit className="w-3 h-3" />
                  </button>
                </div>
              )
            )}

            {/* Image Upload Button */}
            <SceneImageUploader
              scene={scene}
              onUpdate={handleImageUpdate}
            />
          </div>

          {/* Sound Effects Section */}
          <div className="mt-2">
            {scene.sound_effect_path ? (
              // Show existing sound effect with play and remove buttons
              <div className="flex items-center gap-2 text-xs bg-green-900/30 border border-green-700 rounded px-2 py-1">
                <span className="text-green-300">🔊 Sound Effect active</span>
                <button
                  onClick={handleToggleSoundEffectPlayback}
                  className="p-1 hover:bg-green-600 rounded transition-colors"
                  title={isPlayingSoundEffect ? "Stop preview" : "Preview sound effect"}
                >
                  {isPlayingSoundEffect ? (
                    <Pause className="w-3 h-3" />
                  ) : (
                    <Play className="w-3 h-3" />
                  )}
                </button>
                {/* Volume Control */}
                <div className="flex items-center gap-1 ml-1">
                  <Volume2 className="w-3 h-3 text-green-300" />
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={soundEffectVolume}
                    onChange={handleSoundEffectVolumeChange}
                    onClick={(e) => e.stopPropagation()}
                    className="w-16 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                    style={{
                      background: `linear-gradient(to right, #4ade80 0%, #4ade80 ${soundEffectVolume}%, #4b5563 ${soundEffectVolume}%, #4b5563 100%)`
                    }}
                    title={`Volume: ${soundEffectVolume}%`}
                  />
                  <span className="text-green-300 text-[10px] w-7">{soundEffectVolume}%</span>
                </div>
                {/* Timing Control */}
                <div className="flex items-center gap-1 ml-1">
                  <Clock className="w-3 h-3 text-green-300" />
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={soundEffectOffset}
                    onChange={handleSoundEffectOffsetChange}
                    onClick={(e) => e.stopPropagation()}
                    className="w-16 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                    style={{
                      background: `linear-gradient(to right, #4ade80 0%, #4ade80 ${soundEffectOffset}%, #4b5563 ${soundEffectOffset}%, #4b5563 100%)`
                    }}
                    title={`Timing: ${soundEffectOffset}% (0%=Start, 50%=Middle, 100%=End)`}
                  />
                  <span className="text-green-300 text-[10px] w-7">{soundEffectOffset}%</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleRemoveSoundEffect()
                  }}
                  className="ml-auto p-1 hover:bg-red-600 rounded transition-colors"
                  title="Remove sound effect"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ) : showSoundEffectInput ? (
              // Show input to generate sound effect
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={soundEffectPrompt}
                  onChange={(e) => setSoundEffectPrompt(e.target.value)}
                  onClick={(e) => e.stopPropagation()}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleGenerateSoundEffect()
                    }
                  }}
                  placeholder="e.g., explosion, door closing..."
                  className="flex-1 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-primary"
                  disabled={generatingSoundEffect}
                />
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleGenerateSoundEffect()
                  }}
                  disabled={generatingSoundEffect}
                  className="px-2 py-1 bg-primary hover:bg-primary-dark rounded text-xs disabled:opacity-50"
                >
                  {generatingSoundEffect ? (
                    <Loader className="w-3 h-3 animate-spin" />
                  ) : (
                    'Generate'
                  )}
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setShowSoundEffectInput(false)
                    setSoundEffectPrompt('')
                  }}
                  className="p-1 hover:bg-gray-700 rounded transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ) : (
              // Show button to add sound effect
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setShowSoundEffectInput(true)
                }}
                className="text-xs px-2 py-1 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded flex items-center gap-1"
              >
                <Wand2 className="w-3 h-3" />
                Add Sound Effect
              </button>
            )}
          </div>

          {/* Effects Panel */}
          <EffectsPanel
            scene={scene}
            isOpen={isEffectsOpen}
            onToggle={() => setIsEffectsOpen(!isEffectsOpen)}
          />
        </div>

        <div className="flex gap-1">
          <button
            onClick={(e) => {
              e.stopPropagation()
              setIsEditing(!isEditing)
            }}
            className="p-2 hover:bg-gray-700 rounded transition-colors"
          >
            <Edit className="w-4 h-4" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              handleDelete()
            }}
            className="p-2 hover:bg-red-600 rounded transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default SceneCard
