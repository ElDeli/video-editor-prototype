import { useState, useEffect, useRef } from 'react'
import { Volume2, Play, Pause, X, Sparkles } from 'lucide-react'
import api from '../services/api'

function VoiceSelector({ selectedVoice, onVoiceChange, disabled }) {
  const [voiceGroups, setVoiceGroups] = useState([])
  const [elevenLabsVoices, setElevenLabsVoices] = useState([])
  const [openAIVoices, setOpenAIVoices] = useState([])
  const [loadingVoices, setLoadingVoices] = useState(false)
  const [loadingElevenLabs, setLoadingElevenLabs] = useState(false)
  const [loadingOpenAI, setLoadingOpenAI] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [playingVoice, setPlayingVoice] = useState(null)
  const [audioElement, setAudioElement] = useState(null)

  // Refs for scrolling to premium sections
  const elevenLabsRef = useRef(null)
  const openAIRef = useRef(null)

  // Load available voices (Edge TTS)
  useEffect(() => {
    const loadVoices = async () => {
      setLoadingVoices(true)
      try {
        const data = await api.getTTSVoices()
        setVoiceGroups(data.voice_groups || [])
      } catch (error) {
        console.error('Failed to load voices:', error)
      } finally {
        setLoadingVoices(false)
      }
    }
    loadVoices()
  }, [])

  // Load ElevenLabs Premium Voices
  useEffect(() => {
    const loadElevenLabsVoices = async () => {
      setLoadingElevenLabs(true)
      try {
        const response = await fetch('/api/tts/elevenlabs/voices')
        const data = await response.json()
        setElevenLabsVoices(data.voices || [])
      } catch (error) {
        console.error('Failed to load ElevenLabs voices:', error)
        // Silently fail - premium voices are optional
      } finally {
        setLoadingElevenLabs(false)
      }
    }
    loadElevenLabsVoices()
  }, [])

  // Load OpenAI TTS Voices
  useEffect(() => {
    const loadOpenAIVoices = async () => {
      setLoadingOpenAI(true)
      try {
        const response = await fetch('/api/tts/openai/voices')
        const data = await response.json()
        setOpenAIVoices(data.voices || [])
      } catch (error) {
        console.error('Failed to load OpenAI voices:', error)
        // Silently fail - OpenAI voices are optional
      } finally {
        setLoadingOpenAI(false)
      }
    }
    loadOpenAIVoices()
  }, [])

  // Get currently selected voice info
  const getSelectedVoiceInfo = () => {
    // Check Edge TTS voices
    for (const group of voiceGroups) {
      const voice = group.options.find(v => v.value === selectedVoice)
      if (voice) return voice
    }
    // Check ElevenLabs voices
    const elevenLabsVoice = elevenLabsVoices.find(v => v.value === selectedVoice)
    if (elevenLabsVoice) return elevenLabsVoice

    // Check OpenAI voices
    const openAIVoice = openAIVoices.find(v => v.value === selectedVoice)
    if (openAIVoice) return openAIVoice

    return null
  }

  const handlePlayPreview = async (voiceValue) => {
    // Stop currently playing audio
    if (audioElement) {
      audioElement.pause()
      setAudioElement(null)
    }

    if (playingVoice === voiceValue) {
      setPlayingVoice(null)
      return
    }

    try {
      setPlayingVoice(voiceValue)

      // Determine voice type and construct appropriate URL
      const isElevenLabs = voiceValue.startsWith('elevenlabs:')
      const isOpenAI = voiceValue.startsWith('openai:')
      let audioUrl

      if (isElevenLabs) {
        // Extract voice ID from "elevenlabs:VOICE_ID" format
        const voiceId = voiceValue.split(':')[1]
        audioUrl = `/api/tts/elevenlabs/preview/${voiceId}`
      } else if (isOpenAI) {
        // Extract voice ID from "openai:VOICE_ID" format
        const voiceId = voiceValue.split(':')[1]
        audioUrl = `/api/tts/openai/preview/${voiceId}`
      } else {
        // Edge TTS voice
        audioUrl = `/api/tts/preview/${voiceValue}`
      }

      const audio = new Audio(audioUrl)

      audio.onended = () => {
        setPlayingVoice(null)
        setAudioElement(null)
      }

      audio.onerror = () => {
        setPlayingVoice(null)
        setAudioElement(null)
        alert('Failed to play voice preview')
      }

      setAudioElement(audio)
      await audio.play()
    } catch (error) {
      console.error('Failed to play preview:', error)
      setPlayingVoice(null)
    }
  }

  const handleVoiceSelect = (voiceValue) => {
    onVoiceChange(voiceValue)
    setShowModal(false)

    // Stop any playing audio
    if (audioElement) {
      audioElement.pause()
      setAudioElement(null)
      setPlayingVoice(null)
    }
  }

  const scrollToPremium = () => {
    if (elevenLabsRef.current) {
      elevenLabsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  const selectedVoiceInfo = getSelectedVoiceInfo()

  return (
    <>
      {/* Voice Selector Button */}
      <button
        onClick={() => setShowModal(true)}
        disabled={disabled || loadingVoices}
        className="flex items-center gap-2 bg-dark border border-gray-600 rounded-lg px-3 py-2 hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Volume2 className="w-4 h-4 text-gray-400" />
        <span className="text-sm">
          {selectedVoiceInfo ? selectedVoiceInfo.label : 'Select Voice'}
        </span>
      </button>

      {/* Voice Selector Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gradient-to-br from-purple-900/20 via-blue-900/20 to-pink-900/20 backdrop-blur-md flex items-center justify-center z-50 p-4 animate-fadeIn">
          <div className="bg-gradient-to-br from-slate-900/95 via-purple-900/30 to-blue-900/30 backdrop-blur-xl border border-purple-500/30 rounded-3xl shadow-2xl shadow-purple-500/20 max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-purple-500/30 bg-gradient-to-r from-purple-600/20 via-blue-600/20 to-pink-600/20">
              <h2 className="text-3xl font-bold flex items-center gap-3 bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
                <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl shadow-lg shadow-purple-500/50">
                  <Volume2 className="w-7 h-7 text-white" />
                </div>
                Wähle deine Stimme
              </h2>

              {/* Jump to Premium Button */}
              <div className="flex items-center gap-3">
                {(elevenLabsVoices.length > 0 || openAIVoices.length > 0) && (
                  <button
                    onClick={scrollToPremium}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-400 hover:to-orange-400 text-white rounded-xl font-semibold shadow-lg shadow-yellow-500/30 hover:shadow-yellow-500/50 transition-all duration-300 hover:scale-105"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span className="text-sm">Premium Stimmen</span>
                  </button>
                )}

                <button
                  onClick={() => {
                    setShowModal(false)
                    if (audioElement) {
                      audioElement.pause()
                      setAudioElement(null)
                      setPlayingVoice(null)
                    }
                  }}
                  className="p-2 hover:bg-purple-500/20 rounded-xl transition-all hover:rotate-90 duration-300 group"
                >
                  <X className="w-6 h-6 text-purple-300 group-hover:text-white" />
                </button>
              </div>
            </div>

            {/* Voice List */}
            <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-transparent via-purple-900/10 to-slate-900">
              {loadingVoices ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-14 w-14 border-4 border-purple-500 border-t-transparent mx-auto mb-4 shadow-lg shadow-purple-500/50"></div>
                  <p className="text-purple-300 text-lg font-medium">Lade Stimmen...</p>
                </div>
              ) : (
                <>
                  {/* Edge TTS Free Voices - DISPLAYED FIRST */}
                  {voiceGroups.map((group) => (
                  <div key={group.label} className="mb-8">
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2 pb-2 border-b border-gradient-to-r from-purple-500 via-pink-500 to-blue-500">
                      <span className="text-2xl drop-shadow-lg">{group.label.split(' ')[0]}</span>
                      <span className="text-purple-300 font-normal text-base">{group.label.split(' ').slice(1).join(' ')}</span>
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                      {group.options.map((voice) => {
                        const isSelected = voice.value === selectedVoice
                        const isPlaying = playingVoice === voice.value
                        const chars = voice.characteristics

                        return (
                          <div
                            key={voice.value}
                            className={`relative group rounded-xl p-3 transition-all duration-300 cursor-pointer transform hover:scale-[1.02] ${
                              isSelected
                                ? 'bg-gradient-to-br from-purple-600 via-pink-600 to-blue-600 shadow-xl shadow-purple-500/40 border-2 border-purple-400/50'
                                : 'bg-gradient-to-br from-slate-800/80 via-slate-700/50 to-slate-800/80 hover:from-purple-800/50 hover:via-pink-800/30 hover:to-blue-800/50 border border-purple-500/20 hover:border-purple-400/40 shadow-md hover:shadow-purple-500/20 backdrop-blur-sm'
                            }`}
                            onClick={() => handleVoiceSelect(voice.value)}
                          >
                            {/* Selection Indicator */}
                            {isSelected && (
                              <div className="absolute -top-1.5 -right-1.5">
                                <div className="relative">
                                  <div className="w-4 h-4 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full animate-pulse shadow-md shadow-yellow-500/50"></div>
                                  <div className="absolute inset-0 w-4 h-4 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full animate-ping opacity-75"></div>
                                </div>
                              </div>
                            )}

                            {/* Voice Info */}
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex-1 pr-2 min-w-0">
                                <div className={`font-bold text-base mb-0.5 truncate ${isSelected ? 'text-white drop-shadow-lg' : 'text-white'}`}>
                                  {voice.label.split('(')[0].trim()}
                                </div>
                                <div className={`text-xs font-medium ${isSelected ? 'text-pink-200' : 'text-purple-300'}`}>
                                  {voice.label.match(/\((.*?)\)/)?.[1]}
                                </div>
                                <div className={`text-[10px] mt-0.5 line-clamp-1 ${isSelected ? 'text-white/90' : 'text-gray-400'}`}>
                                  {chars.description}
                                </div>
                              </div>

                              {/* Play Button */}
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handlePlayPreview(voice.value)
                                }}
                                className={`p-2.5 rounded-xl transition-all duration-300 flex-shrink-0 ${
                                  isPlaying
                                    ? 'bg-gradient-to-br from-yellow-400 to-orange-500 text-white shadow-xl shadow-yellow-500/50 scale-110 animate-pulse'
                                    : isSelected
                                    ? 'bg-white/20 text-white hover:bg-white/30 shadow-md backdrop-blur-sm'
                                    : 'bg-gradient-to-br from-purple-600 to-pink-600 text-white hover:from-purple-500 hover:to-pink-500 shadow-md hover:shadow-purple-500/50 group-hover:scale-105'
                                }`}
                              >
                                {isPlaying ? (
                                  <Pause className="w-4 h-4" />
                                ) : (
                                  <Play className="w-4 h-4 ml-0.5" />
                                )}
                              </button>
                            </div>

                            {/* Voice Characteristics */}
                            <div className="flex flex-wrap gap-1.5">
                              <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold backdrop-blur-sm ${
                                isSelected
                                  ? 'bg-white/25 text-white shadow-md'
                                  : 'bg-gradient-to-r from-purple-600/40 to-pink-600/40 text-purple-200 border border-purple-400/30'
                              }`}>
                                💫 {chars.tone}
                              </span>
                              <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold backdrop-blur-sm ${
                                isSelected
                                  ? 'bg-white/25 text-white shadow-md'
                                  : 'bg-gradient-to-r from-blue-600/40 to-cyan-600/40 text-blue-200 border border-blue-400/30'
                              }`}>
                                🎵 {chars.pitch}
                              </span>
                              <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold backdrop-blur-sm ${
                                isSelected
                                  ? 'bg-white/25 text-white shadow-md'
                                  : 'bg-gradient-to-r from-pink-600/40 to-rose-600/40 text-pink-200 border border-pink-400/30'
                              }`}>
                                ✨ {chars.style}
                              </span>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                ))}

                  {/* ElevenLabs Premium Voices Section - DISPLAYED SECOND */}
                  {elevenLabsVoices.length > 0 && (
                    <div className="mb-8" ref={elevenLabsRef}>
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2 pb-2 border-b border-gradient-to-r from-yellow-500 via-orange-500 to-pink-500">
                        <span className="text-2xl drop-shadow-lg">🌟</span>
                        <span className="bg-gradient-to-r from-yellow-400 via-orange-400 to-pink-400 bg-clip-text text-transparent">Premium (ElevenLabs)</span>
                      </h3>
                      {loadingElevenLabs ? (
                        <div className="text-center py-8">
                          <div className="animate-spin rounded-full h-10 w-10 border-4 border-yellow-500 border-t-transparent mx-auto mb-3"></div>
                          <p className="text-yellow-300 text-sm">Loading premium voices...</p>
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                          {elevenLabsVoices.map((voice) => {
                            const isSelected = voice.value === selectedVoice
                            const isPlaying = playingVoice === voice.value
                            const chars = voice.characteristics

                            return (
                              <div
                                key={voice.value}
                                className={`relative group rounded-xl p-3 transition-all duration-300 cursor-pointer transform hover:scale-[1.02] ${
                                  isSelected
                                    ? 'bg-gradient-to-br from-yellow-600 via-orange-600 to-pink-600 shadow-xl shadow-yellow-500/40 border-2 border-yellow-400/50'
                                    : 'bg-gradient-to-br from-slate-800/80 via-slate-700/50 to-slate-800/80 hover:from-yellow-800/50 hover:via-orange-800/30 hover:to-pink-800/50 border border-yellow-500/20 hover:border-yellow-400/40 shadow-md hover:shadow-yellow-500/20 backdrop-blur-sm'
                                }`}
                                onClick={() => handleVoiceSelect(voice.value)}
                              >
                                {/* Premium Badge */}
                                <div className="absolute -top-1.5 -left-1.5">
                                  <div className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white text-[9px] font-bold px-1.5 py-0.5 rounded-full shadow-md">
                                    PREMIUM
                                  </div>
                                </div>

                                {/* Selection Indicator */}
                                {isSelected && (
                                  <div className="absolute -top-1.5 -right-1.5">
                                    <div className="relative">
                                      <div className="w-4 h-4 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full animate-pulse shadow-md shadow-yellow-500/50"></div>
                                      <div className="absolute inset-0 w-4 h-4 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full animate-ping opacity-75"></div>
                                    </div>
                                  </div>
                                )}

                                {/* Voice Info */}
                                <div className="flex items-start justify-between mb-2 mt-1">
                                  <div className="flex-1 pr-2 min-w-0">
                                    <div className={`font-bold text-base mb-0.5 truncate ${isSelected ? 'text-white drop-shadow-lg' : 'text-white'}`}>
                                      {voice.label.split('(')[0].trim()}
                                    </div>
                                    <div className={`text-xs font-medium ${isSelected ? 'text-yellow-200' : 'text-yellow-300'}`}>
                                      {voice.label.match(/\((.*?)\)/)?.[1]}
                                    </div>
                                    <div className={`text-[10px] mt-0.5 line-clamp-1 ${isSelected ? 'text-white/90' : 'text-gray-400'}`}>
                                      {chars.description}
                                    </div>
                                  </div>

                                  {/* Play Button */}
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      handlePlayPreview(voice.value)
                                    }}
                                    className={`p-2.5 rounded-xl transition-all duration-300 flex-shrink-0 ${
                                      isPlaying
                                        ? 'bg-gradient-to-br from-yellow-400 to-orange-500 text-white shadow-xl shadow-yellow-500/50 scale-110 animate-pulse'
                                        : isSelected
                                        ? 'bg-white/20 text-white hover:bg-white/30 shadow-md backdrop-blur-sm'
                                        : 'bg-gradient-to-br from-yellow-600 to-orange-600 text-white hover:from-yellow-500 hover:to-orange-500 shadow-md hover:shadow-yellow-500/50 group-hover:scale-105'
                                    }`}
                                  >
                                    {isPlaying ? (
                                      <Pause className="w-4 h-4" />
                                    ) : (
                                      <Play className="w-4 h-4 ml-0.5" />
                                    )}
                                  </button>
                                </div>

                                {/* Voice Characteristics */}
                                <div className="flex flex-wrap gap-1.5">
                                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold backdrop-blur-sm ${
                                    isSelected
                                      ? 'bg-white/25 text-white shadow-md'
                                      : 'bg-gradient-to-r from-yellow-600/40 to-orange-600/40 text-yellow-200 border border-yellow-400/30'
                                  }`}>
                                    💫 {chars.tone}
                                  </span>
                                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold backdrop-blur-sm ${
                                    isSelected
                                      ? 'bg-white/25 text-white shadow-md'
                                      : 'bg-gradient-to-r from-orange-600/40 to-pink-600/40 text-orange-200 border border-orange-400/30'
                                  }`}>
                                    🎵 {chars.pitch}
                                  </span>
                                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold backdrop-blur-sm ${
                                    isSelected
                                      ? 'bg-white/25 text-white shadow-md'
                                      : 'bg-gradient-to-r from-pink-600/40 to-rose-600/40 text-pink-200 border border-pink-400/30'
                                  }`}>
                                    ✨ {chars.style}
                                  </span>
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      )}
                    </div>
                  )}

                  {/* OpenAI TTS Voices Section - DISPLAYED THIRD */}
                  {openAIVoices.length > 0 && (
                    <div className="mb-8">
                      <h3 className="text-xl font-bold mb-4 flex items-center gap-2 pb-2 border-b border-gradient-to-r from-green-500 via-teal-500 to-cyan-500">
                        <span className="text-2xl drop-shadow-lg">⚡</span>
                        <span className="bg-gradient-to-r from-green-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">Premium (OpenAI)</span>
                      </h3>
                      {loadingOpenAI ? (
                        <div className="text-center py-8">
                          <div className="animate-spin rounded-full h-10 w-10 border-4 border-green-500 border-t-transparent mx-auto mb-3"></div>
                          <p className="text-green-300 text-sm">Loading OpenAI voices...</p>
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                          {openAIVoices.map((voice) => {
                            const isSelected = voice.value === selectedVoice
                            const isPlaying = playingVoice === voice.value
                            const chars = voice.characteristics

                            return (
                              <div
                                key={voice.value}
                                className={`relative group rounded-xl p-3 transition-all duration-300 cursor-pointer transform hover:scale-[1.02] ${
                                  isSelected
                                    ? 'bg-gradient-to-br from-green-600 via-teal-600 to-cyan-600 shadow-xl shadow-green-500/40 border-2 border-green-400/50'
                                    : 'bg-gradient-to-br from-slate-800/80 via-slate-700/50 to-slate-800/80 hover:from-green-800/50 hover:via-teal-800/30 hover:to-cyan-800/50 border border-green-500/20 hover:border-green-400/40 shadow-md hover:shadow-green-500/20 backdrop-blur-sm'
                                }`}
                                onClick={() => handleVoiceSelect(voice.value)}
                              >
                                {/* Premium Badge */}
                                <div className="absolute -top-1.5 -left-1.5">
                                  <div className="bg-gradient-to-r from-green-400 to-teal-500 text-white text-[9px] font-bold px-1.5 py-0.5 rounded-full shadow-md">
                                    PREMIUM
                                  </div>
                                </div>

                                {/* Selection Indicator */}
                                {isSelected && (
                                  <div className="absolute -top-1.5 -right-1.5">
                                    <div className="relative">
                                      <div className="w-4 h-4 bg-gradient-to-br from-green-400 to-teal-500 rounded-full animate-pulse shadow-md shadow-green-500/50"></div>
                                      <div className="absolute inset-0 w-4 h-4 bg-gradient-to-br from-green-400 to-teal-500 rounded-full animate-ping opacity-75"></div>
                                    </div>
                                  </div>
                                )}

                                {/* Voice Info */}
                                <div className="flex items-start justify-between mb-2 mt-1">
                                  <div className="flex-1 pr-2 min-w-0">
                                    <div className={`font-bold text-base mb-0.5 truncate ${isSelected ? 'text-white drop-shadow-lg' : 'text-white'}`}>
                                      {voice.label.split('(')[0].trim()}
                                    </div>
                                    <div className={`text-xs font-medium ${isSelected ? 'text-green-200' : 'text-green-300'}`}>
                                      {voice.label.match(/\((.*?)\)/)?.[1]}
                                    </div>
                                    <div className={`text-[10px] mt-0.5 line-clamp-1 ${isSelected ? 'text-white/90' : 'text-gray-400'}`}>
                                      {chars.description}
                                    </div>
                                  </div>

                                  {/* Play Button */}
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      handlePlayPreview(voice.value)
                                    }}
                                    className={`p-2.5 rounded-xl transition-all duration-300 flex-shrink-0 ${
                                      isPlaying
                                        ? 'bg-gradient-to-br from-green-400 to-teal-500 text-white shadow-xl shadow-green-500/50 scale-110 animate-pulse'
                                        : isSelected
                                        ? 'bg-white/20 text-white hover:bg-white/30 shadow-md backdrop-blur-sm'
                                        : 'bg-gradient-to-br from-green-600 to-teal-600 text-white hover:from-green-500 hover:to-teal-500 shadow-md hover:shadow-green-500/50 group-hover:scale-105'
                                    }`}
                                  >
                                    {isPlaying ? (
                                      <Pause className="w-4 h-4" />
                                    ) : (
                                      <Play className="w-4 h-4 ml-0.5" />
                                    )}
                                  </button>
                                </div>

                                {/* Voice Characteristics */}
                                <div className="flex flex-wrap gap-1.5">
                                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold backdrop-blur-sm ${
                                    isSelected
                                      ? 'bg-white/25 text-white shadow-md'
                                      : 'bg-gradient-to-r from-green-600/40 to-teal-600/40 text-green-200 border border-green-400/30'
                                  }`}>
                                    💫 {chars.tone}
                                  </span>
                                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold backdrop-blur-sm ${
                                    isSelected
                                      ? 'bg-white/25 text-white shadow-md'
                                      : 'bg-gradient-to-r from-teal-600/40 to-cyan-600/40 text-teal-200 border border-teal-400/30'
                                  }`}>
                                    🎵 {chars.pitch}
                                  </span>
                                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold backdrop-blur-sm ${
                                    isSelected
                                      ? 'bg-white/25 text-white shadow-md'
                                      : 'bg-gradient-to-r from-cyan-600/40 to-blue-600/40 text-cyan-200 border border-cyan-400/30'
                                  }`}>
                                    ✨ {chars.style}
                                  </span>
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default VoiceSelector
