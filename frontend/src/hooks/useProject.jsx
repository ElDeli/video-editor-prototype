import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const ProjectContext = createContext()

export function ProjectProvider({ children }) {
  const [project, setProject] = useState(null)
  const [scenes, setScenes] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedSceneId, setSelectedSceneId] = useState(null)
  const [scriptText, setScriptText] = useState('')
  const [aiImageModel, setAiImageModel] = useState('flux-dev')

  // Create new project
  const createProject = async (name) => {
    setLoading(true)
    try {
      const newProject = await api.createProject(name)
      setProject(newProject)
      setScenes([])
      return newProject
    } catch (error) {
      console.error('Failed to create project:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  // Load existing project
  const loadProject = async (projectId) => {
    setLoading(true)
    try {
      const data = await api.getProject(projectId)
      setProject(data.project)
      setScenes(data.scenes || [])
      return data
    } catch (error) {
      console.error('Failed to load project:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }

  // Add scene
  const addScene = async (sceneData) => {
    try {
      const newScene = await api.addScene(project.id, sceneData)
      setScenes(prev => [...prev, newScene])
      return newScene
    } catch (error) {
      console.error('Failed to add scene:', error)
      throw error
    }
  }

  // Update scene
  const updateScene = async (sceneId, sceneData) => {
    try {
      const updatedScene = await api.updateScene(sceneId, sceneData)
      setScenes(prev => prev.map(s => s.id === sceneId ? updatedScene : s))
      return updatedScene
    } catch (error) {
      console.error('Failed to update scene:', error)
      throw error
    }
  }

  // Delete scene
  const deleteScene = async (sceneId) => {
    try {
      await api.deleteScene(sceneId)
      setScenes(prev => prev.filter(s => s.id !== sceneId))
      if (selectedSceneId === sceneId) {
        setSelectedSceneId(null)
      }
    } catch (error) {
      console.error('Failed to delete scene:', error)
      throw error
    }
  }

  // Reorder scenes
  const reorderScenes = async (newOrder) => {
    try {
      await api.reorderScenes(project.id, newOrder)
      setScenes(newOrder)
    } catch (error) {
      console.error('Failed to reorder scenes:', error)
      throw error
    }
  }

  // Bulk add scenes from full script
  const addScenesFromScript = async (fullScript) => {
    try {
      const newScenes = await api.bulkAddScenes(project.id, fullScript, aiImageModel)
      setScenes(prev => [...prev, ...newScenes])
      return newScenes
    } catch (error) {
      console.error('Failed to add scenes from script:', error)
      throw error
    }
  }

  // Update scenes from preview response (after video generation)
  const updateScenesFromPreview = (updatedScenes) => {
    console.log('🔄 Updating scenes with actual durations from preview:', updatedScenes)
    setScenes(updatedScenes)
  }

  // Fetch project (refresh project data without scenes)
  const fetchProject = async (projectId) => {
    try {
      const data = await api.getProject(projectId || project?.id)
      setProject(data.project)
      return data.project
    } catch (error) {
      console.error('Failed to fetch project:', error)
      throw error
    }
  }

  const value = {
    project,
    scenes,
    loading,
    selectedSceneId,
    setSelectedSceneId,
    scriptText,
    setScriptText,
    aiImageModel,
    setAiImageModel,
    createProject,
    loadProject,
    fetchProject,
    addScene,
    updateScene,
    deleteScene,
    reorderScenes,
    addScenesFromScript,
    updateScenesFromPreview
  }

  return (
    <ProjectContext.Provider value={value}>
      {children}
    </ProjectContext.Provider>
  )
}

export function useProject() {
  const context = useContext(ProjectContext)
  if (!context) {
    throw new Error('useProject must be used within ProjectProvider')
  }
  return context
}
