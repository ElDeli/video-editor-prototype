import axios from 'axios'

const API_BASE_URL = '/api'

const api = {
  // Projects
  createProject: async (name) => {
    const response = await axios.post(`${API_BASE_URL}/projects`, { name })
    return response.data
  },

  getProject: async (projectId) => {
    const response = await axios.get(`${API_BASE_URL}/projects/${projectId}`)
    return response.data
  },

  listProjects: async () => {
    const response = await axios.get(`${API_BASE_URL}/projects`)
    return response.data
  },

  updateProject: async (projectId, projectData) => {
    const response = await axios.patch(`${API_BASE_URL}/projects/${projectId}`, projectData)
    return response.data
  },

  // TTS Voices
  getTTSVoices: async () => {
    const response = await axios.get(`${API_BASE_URL}/tts/voices`)
    return response.data
  },

  // Scenes
  addScene: async (projectId, sceneData) => {
    const response = await axios.post(`${API_BASE_URL}/projects/${projectId}/scenes`, sceneData)
    return response.data
  },

  updateScene: async (sceneId, sceneData) => {
    const response = await axios.put(`${API_BASE_URL}/scenes/${sceneId}`, sceneData)
    return response.data
  },

  deleteScene: async (sceneId) => {
    await axios.delete(`${API_BASE_URL}/scenes/${sceneId}`)
  },

  reorderScenes: async (projectId, sceneIds) => {
    await axios.post(`${API_BASE_URL}/projects/${projectId}/scenes/reorder`, { scene_ids: sceneIds })
  },

  bulkAddScenes: async (projectId, fullScript, aiImageModel = 'flux-dev') => {
    const response = await axios.post(`${API_BASE_URL}/projects/${projectId}/scenes/bulk`, {
      full_script: fullScript,
      ai_image_model: aiImageModel
    })
    return response.data
  },

  // Preview
  generatePreview: async (projectId, fontSize = 30) => {
    const response = await axios.post(`${API_BASE_URL}/projects/${projectId}/preview`, { fontSize })
    return response.data
  },

  // Export
  exportVideo: async (projectId, format = '1080p', fontSize = 30) => {
    const response = await axios.post(`${API_BASE_URL}/projects/${projectId}/export`, { format, fontSize })
    return response.data
  },

  // Upload to Queue
  uploadToQueue: async (projectId, folderId = null, resolution = '1080p') => {
    const response = await axios.post(`${API_BASE_URL}/projects/${projectId}/upload-to-queue`, {
      folder_id: folderId,
      resolution
    })
    return response.data
  },

  // Settings - Output Folders
  getOutputFolders: async () => {
    const response = await axios.get(`${API_BASE_URL}/settings/output-folders`)
    return response.data
  },

  addOutputFolder: async (name, path) => {
    const response = await axios.post(`${API_BASE_URL}/settings/output-folders`, { name, path })
    return response.data
  },

  deleteOutputFolder: async (folderId) => {
    await axios.delete(`${API_BASE_URL}/settings/output-folders/${folderId}`)
  },

  setDefaultOutputFolder: async (folderId) => {
    const response = await axios.post(`${API_BASE_URL}/settings/output-folders/${folderId}/set-default`)
    return response.data
  },

  getDefaultOutputFolder: async () => {
    const response = await axios.get(`${API_BASE_URL}/settings/output-folders/default`)
    return response.data
  },

  browseFolders: async (path = null) => {
    const params = path ? { path } : {}
    const response = await axios.get(`${API_BASE_URL}/settings/browse-folders`, { params })
    return response.data
  }
}

export default api
