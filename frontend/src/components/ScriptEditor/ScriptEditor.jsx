import { useState } from 'react'
import { Plus, Sparkles, Wand2 } from 'lucide-react'
import { useProject } from '../../hooks/useProject'

function ScriptEditor() {
  const { project, addScene, addScenesFromScript } = useProject()
  const [scriptText, setScriptText] = useState('')
  const [loading, setLoading] = useState(false)
  const [useAiImprovement, setUseAiImprovement] = useState(false)
  const [improving, setImproving] = useState(false)
  const [targetDuration, setTargetDuration] = useState(null) // null = original length

  const handleAddScene = async () => {
    if (!scriptText.trim()) return

    try {
      await addScene({
        script: scriptText.trim(),
        duration: 5,
        background_type: 'solid',
        background_value: '#000000'
      })
      setScriptText('')
    } catch (error) {
      console.error('Failed to add scene:', error)
    }
  }

  const handleImproveScript = async (textToImprove, targetLength = null) => {
    if (!textToImprove || !textToImprove.trim()) return textToImprove

    setImproving(true)
    try {
      const response = await fetch(`/api/scripts/improve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          script: textToImprove.trim(),
          target_duration: targetLength // Send target duration to AI
        })
      })

      if (!response.ok) throw new Error('Failed to improve script')

      const data = await response.json()
      return data.improved_script
    } catch (error) {
      console.error('Failed to improve script:', error)
      alert('Failed to improve script. Using original.')
      return textToImprove
    } finally {
      setImproving(false)
    }
  }

  const handleAutoCreateScenes = async () => {
    if (!scriptText.trim()) return

    setLoading(true)
    try {
      let finalScript = scriptText.trim()

      // If AI improvement is enabled, improve first
      if (useAiImprovement) {
        finalScript = await handleImproveScript(finalScript, targetDuration)
        // Update the text area with improved script
        setScriptText(finalScript)
      }

      await addScenesFromScript(finalScript)
      setScriptText('')
    } catch (error) {
      console.error('Failed to auto-create scenes:', error)
      alert('Failed to create scenes. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-full flex flex-col p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Script Editor</h2>

        {/* AI Improvement Toggle */}
        <button
          onClick={() => setUseAiImprovement(!useAiImprovement)}
          className={`px-3 py-1.5 rounded-lg flex items-center gap-2 transition-colors ${
            useAiImprovement
              ? 'bg-purple-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
          title="Toggle AI script improvement"
        >
          <Sparkles className={`w-4 h-4 ${useAiImprovement ? 'animate-pulse' : ''}`} />
          <span className="text-xs font-semibold">
            {useAiImprovement ? 'AI: ON' : 'AI: OFF'}
          </span>
        </button>
      </div>

      {useAiImprovement && (
        <div className="mb-3 p-3 bg-purple-900/30 border border-purple-600 rounded-lg">
          <p className="text-xs text-purple-300 flex items-center gap-2 mb-2">
            <Sparkles className="w-3 h-3" />
            AI will improve your script before creating scenes (better flow, engagement, viral potential)
          </p>

          {/* Duration Selector */}
          <div className="flex items-center gap-2">
            <label className="text-xs text-purple-300 font-semibold">Target Duration:</label>
            <select
              value={targetDuration || ''}
              onChange={(e) => setTargetDuration(e.target.value ? parseInt(e.target.value) : null)}
              className="bg-purple-900/50 border border-purple-500 rounded px-2 py-1 text-xs text-white focus:outline-none focus:ring-2 focus:ring-purple-400"
            >
              <option value="">Original Length</option>
              <option value="15">15 seconds</option>
              <option value="30">30 seconds</option>
              <option value="45">45 seconds</option>
              <option value="60">60 seconds (1 min)</option>
              <option value="120">2 minutes</option>
              <option value="180">3 minutes</option>
            </select>
          </div>
        </div>
      )}

      <div className="flex-1 flex flex-col gap-3">
        <textarea
          className="flex-1 bg-dark border border-gray-600 rounded-lg p-3 resize-none focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="Write your full script here... (paste complete script for auto-scene creation)"
          value={scriptText}
          onChange={(e) => setScriptText(e.target.value)}
          disabled={!project || loading || improving}
        />

        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={handleAddScene}
            disabled={!project || !scriptText.trim() || loading || improving}
            className="py-3 bg-primary hover:bg-blue-600 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Plus className="w-4 h-4" />
            Add 1 Scene
          </button>

          <button
            onClick={handleAutoCreateScenes}
            disabled={!project || !scriptText.trim() || loading || improving}
            className="py-3 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Wand2 className={`w-4 h-4 ${(loading || improving) ? 'animate-spin' : ''}`} />
            {improving ? 'Improving...' : loading ? 'Creating...' : 'Auto-Create Scenes'}
          </button>
        </div>
      </div>

      <div className="mt-4 p-3 bg-dark rounded-lg border border-gray-700">
        <p className="text-xs text-gray-400 mb-2 font-semibold">How it works:</p>
        <ul className="text-xs text-gray-400 space-y-1">
          <li>• <strong>Add 1 Scene</strong>: Creates single scene from text</li>
          <li>• <strong>Auto-Create</strong>: Splits full script into multiple scenes automatically</li>
          <li>• <strong>AI Toggle</strong>: Enable to improve script with AI before scene creation</li>
          <li>• Separate paragraphs with double Enter for better splitting</li>
        </ul>
      </div>
    </div>
  )
}

export default ScriptEditor
