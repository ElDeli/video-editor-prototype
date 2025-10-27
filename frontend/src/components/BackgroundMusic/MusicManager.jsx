import { useState, useEffect } from 'react'
import { Music, Upload, X, Wand2, Loader, Volume2, Gauge } from 'lucide-react'
import axios from 'axios'

const API_BASE = 'http://localhost:5001/api'

export default function MusicManager({ project, onUpdate }) {
    const [showModal, setShowModal] = useState(false)
    const [activeTab, setActiveTab] = useState('generate')
    const [musicPrompt, setMusicPrompt] = useState('')
    const [selectedGenre, setSelectedGenre] = useState('hip-hop')
    const [uploading, setUploading] = useState(false)
    const [generating, setGenerating] = useState(false)
    const [musicVolume, setMusicVolume] = useState(project?.background_music_volume || 7)
    const [videoSpeed, setVideoSpeed] = useState(project?.video_speed || 1.0)

    // Sync volume and speed state when project prop changes
    useEffect(() => {
        setMusicVolume(project?.background_music_volume || 7)
        setVideoSpeed(project?.video_speed || 1.0)
    }, [project?.background_music_volume, project?.video_speed])

    // Music genres for better AI generation
    const musicGenres = [
        { value: 'hip-hop', label: 'Hip-Hop / Trap', example: 'hard hitting 808 bass, trap hi-hats' },
        { value: 'electronic', label: 'Electronic / EDM', example: 'energetic synths, electronic drums' },
        { value: 'lo-fi', label: 'Lo-Fi / Chill', example: 'relaxing lo-fi beats, chill atmosphere' },
        { value: 'phonk', label: 'Phonk', example: 'dark phonk beats, memphis style' },
        { value: 'drill', label: 'Drill', example: 'aggressive drill beats, sliding 808s' },
        { value: 'ambient', label: 'Ambient / Cinematic', example: 'atmospheric pads, cinematic sounds' },
        { value: 'rock', label: 'Rock / Guitar', example: 'electric guitar riffs, rock drums' },
        { value: 'pop', label: 'Pop', example: 'catchy melodies, upbeat pop rhythm' },
        { value: 'jazz', label: 'Jazz', example: 'smooth jazz piano, walking bass' },
        { value: 'classical', label: 'Classical', example: 'orchestral strings, piano' },
        { value: 'reggaeton', label: 'Reggaeton / Latin', example: 'reggaeton dembow rhythm, latin percussion' },
    ]

    const currentMusic = project?.background_music_path

    // DEBUG: Log project data
    console.log('🎵 MusicManager - Project:', project)
    console.log('🎵 MusicManager - currentMusic:', currentMusic)

    // Extract filename from path
    const getMusicFileName = () => {
        if (!currentMusic) return null
        const parts = currentMusic.split('/')
        return parts[parts.length - 1]
    }

    const handleGenerateMusic = async () => {
        setGenerating(true)
        try {
            // Build genre-enhanced prompt
            const selectedGenreData = musicGenres.find(g => g.value === selectedGenre)
            const genreExample = selectedGenreData ? selectedGenreData.example : ''

            // Combine genre template with user additions
            const fullPrompt = musicPrompt.trim()
                ? `${genreExample}, ${musicPrompt}`.trim()
                : genreExample

            console.log('🎵 Generating music with prompt:', fullPrompt)

            // Generate music using ElevenLabs
            // Include project_id so backend can calculate video duration and generate music of matching length
            const response = await axios.post(`${API_BASE}/music/generate`, {
                text_prompt: fullPrompt,
                project_id: project.id  // Backend will calculate total scene duration
            })

            console.log('✓ Music generated:', response.data.duration, 'seconds')

            // Apply generated music to project
            await axios.put(`${API_BASE}/projects/${project.id}`, {
                background_music_path: response.data.path
            })

            onUpdate?.()
            setShowModal(false)
            setMusicPrompt('')
            alert('AI Music generated successfully!')
        } catch (error) {
            console.error('Music generation error:', error)
            alert(error.response?.data?.error || 'Failed to generate music')
        } finally {
            setGenerating(false)
        }
    }

    const handleFileUpload = async (e) => {
        const file = e.target.files?.[0]
        if (!file) return

        setUploading(true)
        try {
            const formData = new FormData()
            formData.append('file', file)

            const response = await axios.post(`${API_BASE}/uploads/audio`, formData)

            await axios.put(`${API_BASE}/projects/${project.id}`, {
                background_music_path: response.data.path
            })

            onUpdate?.()
            setShowModal(false)
            alert('Music uploaded successfully!')
        } catch (error) {
            console.error('Upload error:', error)
            alert(error.response?.data?.error || 'Failed to upload music')
        } finally {
            setUploading(false)
        }
    }

    const removeMusic = async () => {
        if (!confirm('Hintergrundmusik entfernen?')) return

        try {
            await axios.put(`${API_BASE}/projects/${project.id}`, {
                background_music_path: null
            })
            onUpdate?.()
            alert('Musik entfernt!')
        } catch (error) {
            console.error('Remove error:', error)
            alert('Failed to remove music')
        }
    }

    const handleMusicVolumeChange = async (e) => {
        const newVolume = parseInt(e.target.value)
        setMusicVolume(newVolume)

        try {
            await axios.put(`${API_BASE}/projects/${project.id}`, {
                background_music_volume: newVolume
            })
        } catch (error) {
            console.error('Failed to update music volume:', error)
        }
    }

    const handleVideoSpeedChange = async (e) => {
        const newSpeed = parseFloat(e.target.value)
        setVideoSpeed(newSpeed)

        try {
            await axios.put(`${API_BASE}/projects/${project.id}`, {
                video_speed: newSpeed
            })
        } catch (error) {
            console.error('Failed to update video speed:', error)
        }
    }

    return (
        <>
            <div className="flex items-center gap-2">
                <button
                    onClick={() => setShowModal(true)}
                    className={`flex items-center gap-2 px-3 py-2 rounded text-sm ${
                        currentMusic
                            ? 'bg-primary text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                >
                    <Music className="w-4 h-4" />
                    {currentMusic ? 'Change Music' : 'Add Music'}
                </button>

                {currentMusic && (
                    <div className="text-sm text-gray-300 max-w-[150px] truncate overflow-hidden whitespace-nowrap" title={getMusicFileName()}>
                        🎵 {getMusicFileName()}
                    </div>
                )}

                {/* Volume Control - Always visible but disabled if no music */}
                <div className={`flex items-center gap-2 px-3 py-2 rounded ${currentMusic ? 'bg-gray-700' : 'bg-gray-800 opacity-50'}`}>
                    <Volume2 className="w-4 h-4 text-gray-300" />
                    <input
                        type="range"
                        min="0"
                        max="100"
                        value={musicVolume}
                        onChange={handleMusicVolumeChange}
                        disabled={!currentMusic}
                        className="w-24 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer disabled:cursor-not-allowed"
                        style={{
                            background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${musicVolume}%, #4b5563 ${musicVolume}%, #4b5563 100%)`
                        }}
                        title={currentMusic ? `Music Volume: ${musicVolume}%` : 'Add music to adjust volume'}
                    />
                    <span className="text-gray-300 text-xs w-8">{musicVolume}%</span>
                </div>

                {/* Video Speed Control - Always visible */}
                <div className="flex items-center gap-2 bg-gray-700 px-3 py-2 rounded">
                    <Gauge className="w-4 h-4 text-gray-300" />
                    <input
                        type="range"
                        min="0.5"
                        max="2.0"
                        step="0.05"
                        value={videoSpeed}
                        onChange={handleVideoSpeedChange}
                        className="w-24 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                        style={{
                            background: `linear-gradient(to right, #10b981 0%, #10b981 ${((videoSpeed - 0.5) / 1.5) * 100}%, #4b5563 ${((videoSpeed - 0.5) / 1.5) * 100}%, #4b5563 100%)`
                        }}
                        title={`Video Speed: ${videoSpeed}x`}
                    />
                    <span className="text-gray-300 text-xs w-12">{videoSpeed.toFixed(2)}x</span>
                </div>

                {currentMusic && (
                    <button
                        onClick={removeMusic}
                        className="p-2 bg-red-600 hover:bg-red-700 rounded text-white"
                        title="Remove music"
                    >
                        <X className="w-4 h-4" />
                    </button>
                )}
            </div>

            {showModal && (
                <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
                    <div className="bg-darker rounded-lg w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
                        <div className="flex items-center justify-between p-4 border-b border-gray-700">
                            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                                <Music className="w-6 h-6" />
                                Add Background Music
                            </h2>
                            <button
                                onClick={() => setShowModal(false)}
                                className="p-2 hover:bg-gray-700 rounded"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="flex border-b border-gray-700">
                            <button
                                onClick={() => setActiveTab('generate')}
                                className={`flex-1 px-4 py-3 text-sm font-medium transition ${
                                    activeTab === 'generate'
                                        ? 'bg-gray-700 text-white border-b-2 border-primary'
                                        : 'text-gray-400 hover:text-gray-300 hover:bg-gray-800'
                                }`}
                            >
                                <div className="flex items-center justify-center gap-2">
                                    <Wand2 className="w-4 h-4" />
                                    Generate AI Music
                                </div>
                            </button>
                            <button
                                onClick={() => setActiveTab('upload')}
                                className={`flex-1 px-4 py-3 text-sm font-medium transition ${
                                    activeTab === 'upload'
                                        ? 'bg-gray-700 text-white border-b-2 border-primary'
                                        : 'text-gray-400 hover:text-gray-300 hover:bg-gray-800'
                                }`}
                            >
                                <div className="flex items-center justify-center gap-2">
                                    <Upload className="w-4 h-4" />
                                    Upload Your Own
                                </div>
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto p-6">
                            {activeTab === 'generate' && (
                                <div className="space-y-4">
                                    <div className="bg-blue-900/30 border border-blue-700 rounded p-4">
                                        <p className="text-sm text-blue-200">
                                            <strong>ElevenLabs AI Music Generation</strong>
                                            <br />
                                            Select a genre and optionally add more details. The AI will generate custom music based on your selection.
                                            Examples: "fast tempo", "with piano", "dark atmosphere", "140 BPM"
                                        </p>
                                    </div>

                                    <div className="space-y-3">
                                        {/* Genre Selector */}
                                        <div>
                                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                                Genre / Style
                                            </label>
                                            <select
                                                value={selectedGenre}
                                                onChange={(e) => setSelectedGenre(e.target.value)}
                                                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                                                disabled={generating}
                                            >
                                                {musicGenres.map(genre => (
                                                    <option key={genre.value} value={genre.value}>
                                                        {genre.label}
                                                    </option>
                                                ))}
                                            </select>
                                            <p className="text-xs text-gray-400 mt-1">
                                                🎯 Select genre for better AI results
                                            </p>
                                        </div>

                                        {/* Additional Description */}
                                        <div>
                                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                                Additional Details (Optional)
                                            </label>
                                            <textarea
                                                value={musicPrompt}
                                                onChange={(e) => setMusicPrompt(e.target.value)}
                                                placeholder="e.g., fast tempo, with strings, dark atmosphere..."
                                                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm min-h-[100px] focus:outline-none focus:ring-2 focus:ring-primary"
                                                disabled={generating}
                                            />
                                        </div>

                                        {/* Generate Button */}
                                        <button
                                            onClick={handleGenerateMusic}
                                            disabled={generating}
                                            className={`w-full px-4 py-3 rounded text-white font-medium flex items-center justify-center gap-2 transition-colors ${
                                                generating
                                                    ? 'bg-gray-600 cursor-not-allowed'
                                                    : 'bg-primary hover:bg-primary-dark'
                                            }`}
                                        >
                                            {generating ? (
                                                <>
                                                    <Loader className="w-5 h-5 animate-spin" />
                                                    Generating Music...
                                                </>
                                            ) : (
                                                <>
                                                    <Wand2 className="w-5 h-5" />
                                                    Generate Music
                                                </>
                                            )}
                                        </button>
                                    </div>

                                    <div className="text-xs text-gray-500 mt-4">
                                        <strong>Note:</strong> Generation may take 10-30 seconds. ElevenLabs Creator Plan includes 100 minutes of music generation per month.
                                    </div>
                                </div>
                            )}

                            {activeTab === 'upload' && (
                                <div className="space-y-4">
                                    <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center">
                                        <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                                        <p className="text-gray-300 mb-4">
                                            Upload your own music file
                                        </p>
                                        <p className="text-xs text-gray-500 mb-4">
                                            Supported formats: MP3, WAV, M4A, AAC, OGG (Max 50MB)
                                        </p>
                                        <input
                                            type="file"
                                            accept=".mp3,.wav,.m4a,.aac,.ogg"
                                            onChange={handleFileUpload}
                                            disabled={uploading}
                                            className="hidden"
                                            id="music-upload"
                                        />
                                        <label
                                            htmlFor="music-upload"
                                            className={`inline-block px-6 py-3 rounded cursor-pointer ${
                                                uploading
                                                    ? 'bg-gray-600 text-gray-400'
                                                    : 'bg-primary hover:bg-primary-dark text-white'
                                            }`}
                                        >
                                            {uploading ? (
                                                <span className="flex items-center gap-2">
                                                    <Loader className="w-4 h-4 animate-spin" />
                                                    Uploading...
                                                </span>
                                            ) : (
                                                'Choose File'
                                            )}
                                        </label>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}
