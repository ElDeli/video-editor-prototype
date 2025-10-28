import { useState, useEffect, useRef } from 'react'
import ReactPlayer from 'react-player'
import { useProject } from '../../hooks/useProject'
import { Play, RefreshCw, CheckCircle } from 'lucide-react'

function VideoPreview({ previewData, seekToScene }) {
  const { project, scenes, selectedSceneId } = useProject()
  const playerRef = useRef(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const isPlayingRef = useRef(false) // Real-time playing status
  const isPlayerReadyRef = useRef(false) // Track if player is ready for seeking

  // STABLE player key - only changes when preview data actually changes
  // Use useRef to prevent re-generating key on every render!
  const playerKeyRef = useRef(null)
  if (!playerKeyRef.current || previewData?._timestamp !== playerKeyRef.current.previewTimestamp) {
    playerKeyRef.current = {
      key: previewData?._timestamp || Date.now(),
      previewTimestamp: previewData?._timestamp
    }
    // Reset player ready status when new video loads
    isPlayerReadyRef.current = false
  }
  const playerKey = playerKeyRef.current.key

  console.log('🎥 VideoPreview render:', {
    previewData,
    playerKey,
    selectedSceneId,
    scenesCount: scenes.length,
    isPlaying,
    isPlayerReady: isPlayerReadyRef.current
  })

  // Calculate scene start time based on previous scenes' durations
  const getSceneStartTime = (sceneIndex) => {
    let totalTime = 0
    for (let i = 0; i < sceneIndex; i++) {
      totalTime += scenes[i].duration
    }
    return totalTime
  }

  // Perform seek operation
  const performSeek = (startTime) => {
    // Set seeking flag
    isSeekingRef.current = true

    // Add small delay to ensure player is ready
    setTimeout(() => {
      if (playerRef.current) {
        const seekTime = startTime + 0.1 // Small offset to ensure we're in the scene
        console.log(`⏩ Seeking to ${seekTime}s (player ready: ${isPlayerReadyRef.current})`)
        playerRef.current.seekTo(seekTime, 'seconds')
        // DO NOT auto-play - let user manually press play
        // This prevents unexpected jumps when clicking scenes during playback

        // Clear seeking flag after a delay
        setTimeout(() => {
          isSeekingRef.current = false
        }, 500)
      } else {
        console.error('❌ Player ref lost during setTimeout')
        isSeekingRef.current = false
      }
    }, 100)
  }

  // Track previous selectedSceneId to only jump when it actually changes
  const prevSelectedSceneIdRef = useRef(null)

  // Track if we're currently seeking to prevent interference with video controls
  const isSeekingRef = useRef(false)

  // Jump to selected scene when it changes
  useEffect(() => {
    // Only jump if selectedSceneId ACTUALLY changed (not just re-render)
    if (selectedSceneId === prevSelectedSceneIdRef.current) {
      return // No change, don't seek
    }

    // Prevent seeking if already seeking
    if (isSeekingRef.current) {
      console.log('⏸️ Already seeking, ignoring...')
      return
    }

    console.log('🔄 Scene selection changed:', {
      selectedSceneId,
      previousSceneId: prevSelectedSceneIdRef.current,
      hasPlayer: !!playerRef.current,
      hasPreview: !!previewData,
      scenesCount: scenes.length,
      isPlayingState: isPlaying,
      isPlayingRef: isPlayingRef.current
    })

    // Update the previous value
    prevSelectedSceneIdRef.current = selectedSceneId

    if (selectedSceneId && playerRef.current && previewData) {
      const sceneIndex = scenes.findIndex(s => s.id === selectedSceneId)
      console.log(`🔍 Scene lookup: selectedSceneId=${selectedSceneId}, found at index=${sceneIndex}`)

      if (sceneIndex >= 0) {
        const startTime = getSceneStartTime(sceneIndex)
        const sceneDurations = scenes.map((s, i) => `Scene ${i+1}: ${s.duration}s`)

        console.log(`🎬 Jumping to Scene ${sceneIndex + 1} (ID: ${selectedSceneId})`, {
          startTime: `${startTime}s`,
          sceneIndex,
          totalScenes: scenes.length,
          sceneDurations,
          isPlayerReady: isPlayerReadyRef.current
        })

        // Check if player is ready before seeking
        if (!isPlayerReadyRef.current) {
          console.warn('⚠️ Player not ready yet, waiting...')
          // Retry after player is ready
          const retryInterval = setInterval(() => {
            if (isPlayerReadyRef.current && playerRef.current) {
              clearInterval(retryInterval)
              performSeek(startTime)
            }
          }, 100)
          // Timeout after 5 seconds
          setTimeout(() => clearInterval(retryInterval), 5000)
          return
        }

        performSeek(startTime)
        // Update prevSelectedSceneIdRef after seeking
        prevSelectedSceneIdRef.current = selectedSceneId
      } else {
        console.warn(`⚠️ Scene ${selectedSceneId} not found in scenes array`)
      }
    }
    // ONLY depend on selectedSceneId - scenes/previewData are accessed via closure
    // This prevents re-running on every render when scenes array reference changes
  }, [selectedSceneId])

  return (
    <div className="h-full flex flex-col p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Preview</h2>
      </div>

      <div className="flex-1 flex flex-col">
        {previewData && previewData.preview_url ? (
          <div className="bg-black rounded-lg overflow-hidden aspect-[9/16]">
            <ReactPlayer
              ref={playerRef}
              key={playerKey}
              url={`${previewData.preview_url}?t=${playerKey}`}
              controls
              width="100%"
              height="100%"
              playing={isPlaying}
              onReady={() => {
                console.log('✅ Player is ready!')
                isPlayerReadyRef.current = true
              }}
              onPlay={() => {
                console.log('▶️ Player onPlay callback - setting refs')
                isPlayingRef.current = true
                setIsPlaying(true)
              }}
              onPause={() => {
                console.log('⏸️ Player onPause callback - setting refs')
                isPlayingRef.current = false
                setIsPlaying(false)
              }}
              onSeek={(seconds) => {
                console.log(`🎯 Player seeked to ${seconds}s`)
              }}
              onError={(error) => {
                console.error('❌ Player error:', error)
              }}
            />
          </div>
        ) : (
          <div className="flex-1 bg-dark rounded-lg border-2 border-dashed border-gray-700 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <Play className="w-16 h-16 mx-auto mb-3 opacity-50" />
              <p className="text-lg mb-2">No preview available</p>
              <p className="text-sm">
                {project && scenes.length > 0
                  ? 'Click Preview button in header to generate'
                  : 'Add scenes to generate preview'}
              </p>
            </div>
          </div>
        )}

        <div className="mt-4 space-y-2">
          <div className="p-3 bg-dark rounded-lg border border-gray-700">
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-400">Total Scenes:</span>
              <span className="font-semibold">{scenes.length}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Duration:</span>
              <span className="font-semibold">
                {scenes.reduce((sum, s) => sum + s.duration, 0)}s
              </span>
            </div>
          </div>

          {previewData && (
            <div className="p-3 bg-green-900/20 border border-green-700 rounded-lg">
              <div className="flex items-center gap-2 text-sm text-green-400 mb-2">
                <CheckCircle className="w-4 h-4" />
                <span className="font-semibold">Preview Generated</span>
              </div>
              <div className="text-xs text-gray-400 space-y-1">
                <div>Scenes: {previewData.scene_count}</div>
                <div>Duration: {previewData.total_duration}s</div>
                <div className="mt-2 p-2 bg-dark rounded text-yellow-400">
                  {previewData.message}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default VideoPreview
