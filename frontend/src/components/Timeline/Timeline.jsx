import { useProject } from '../../hooks/useProject'
import SceneCard from './SceneCard'
import { Plus } from 'lucide-react'

function Timeline({ onPreviewRegenerated }) {
  const { project, scenes, selectedSceneId, setSelectedSceneId } = useProject()

  if (!project) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <div className="text-center">
          <p className="text-lg mb-2">No project loaded</p>
          <p className="text-sm">Create or load a project to start editing</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Timeline</h2>
        <span className="text-sm text-gray-400">{scenes.length} scenes</span>
      </div>

      <div className="space-y-3">
        {scenes.map((scene, index) => (
          <SceneCard
            key={scene.id}
            scene={scene}
            index={index}
            isSelected={selectedSceneId === scene.id}
            onSelect={() => setSelectedSceneId(scene.id)}
            onPreviewRegenerated={onPreviewRegenerated}
          />
        ))}

        {scenes.length === 0 && (
          <div className="py-12 text-center text-gray-500">
            <Plus className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No scenes yet</p>
            <p className="text-sm mt-1">Add your first scene using the Script Editor</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Timeline
