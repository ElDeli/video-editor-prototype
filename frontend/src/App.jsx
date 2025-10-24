import { useState, useEffect } from 'react'
import EditorPage from './pages/EditorPage'
import { ProjectProvider, useProject } from './hooks/useProject'

function AppContent() {
  const { project, createProject, loading } = useProject()

  useEffect(() => {
    // Auto-create default project if none exists
    if (!project && !loading) {
      createProject('My Video Project')
    }
  }, [project, loading])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-darker text-gray-400">
        Loading...
      </div>
    )
  }

  return <EditorPage />
}

function App() {
  return (
    <ProjectProvider>
      <AppContent />
    </ProjectProvider>
  )
}

export default App
