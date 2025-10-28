import { useState, useEffect } from 'react'
import { Sparkles, Zap, Move, Palette, Wand2, Clock } from 'lucide-react'
import { useProject } from '../../hooks/useProject'

function EffectsPanel({ scene, isOpen, onToggle }) {
  const { updateScene } = useProject()

  // Local state for effects
  const [effects, setEffects] = useState({
    // Original effects
    effect_zoom: scene.effect_zoom || 'none',
    effect_pan: scene.effect_pan || 'none',
    effect_speed: scene.effect_speed || 1.0,
    effect_shake: scene.effect_shake || 0,
    effect_fade: scene.effect_fade || 'none',
    effect_intensity: scene.effect_intensity || 0.5,
    // New motion effects
    effect_rotate: scene.effect_rotate || 'none',
    effect_bounce: scene.effect_bounce || 0,
    effect_tilt_3d: scene.effect_tilt_3d || 'none',
    // New color effects
    effect_vignette: scene.effect_vignette || 'none',
    effect_color_temp: scene.effect_color_temp || 'none',
    effect_saturation: scene.effect_saturation || 1.0,
    // New creative effects
    effect_film_grain: scene.effect_film_grain || 0,
    effect_glitch: scene.effect_glitch || 0,
    effect_chromatic: scene.effect_chromatic || 0,
    effect_blur: scene.effect_blur || 'none',
    effect_light_leaks: scene.effect_light_leaks || 0,
    effect_lens_flare: scene.effect_lens_flare || 0,
    effect_kaleidoscope: scene.effect_kaleidoscope || 0
  })

  const [isSaving, setIsSaving] = useState(false)
  const [activeCategory, setActiveCategory] = useState('motion') // motion, color, creative, timing

  // Update local state when scene changes (but only when scene.id changes to prevent overwriting user edits)
  useEffect(() => {
    setEffects({
      effect_zoom: scene.effect_zoom || 'none',
      effect_pan: scene.effect_pan || 'none',
      effect_speed: scene.effect_speed || 1.0,
      effect_shake: scene.effect_shake || 0,
      effect_fade: scene.effect_fade || 'none',
      effect_intensity: scene.effect_intensity || 0.5,
      effect_rotate: scene.effect_rotate || 'none',
      effect_bounce: scene.effect_bounce || 0,
      effect_tilt_3d: scene.effect_tilt_3d || 'none',
      effect_vignette: scene.effect_vignette || 'none',
      effect_color_temp: scene.effect_color_temp || 'none',
      effect_saturation: scene.effect_saturation || 1.0,
      effect_film_grain: scene.effect_film_grain || 0,
      effect_glitch: scene.effect_glitch || 0,
      effect_chromatic: scene.effect_chromatic || 0,
      effect_blur: scene.effect_blur || 'none',
      effect_light_leaks: scene.effect_light_leaks || 0,
      effect_lens_flare: scene.effect_lens_flare || 0,
      effect_kaleidoscope: scene.effect_kaleidoscope || 0
    })
  }, [scene.id])

  const handleEffectChange = (key, value) => {
    setEffects(prev => ({ ...prev, [key]: value }))
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      // DEBUG: Log effect values before saving
      const effectKeys = ['effect_vignette', 'effect_color_temp', 'effect_saturation']
      const effectValues = effectKeys.reduce((acc, key) => {
        acc[key] = { value: effects[key], type: typeof effects[key] }
        return acc
      }, {})
      console.log('🔍 DEBUG: Saving effects (Scene', scene.id, '):', effectValues)

      await updateScene(scene.id, effects)
      console.log('✅ Effects saved successfully')
    } catch (error) {
      console.error('❌ Failed to save effects:', error)
      alert('Failed to save effects')
    } finally {
      setIsSaving(false)
    }
  }

  // Check if any effects are active
  const hasActiveEffects = () => {
    return (
      effects.effect_zoom !== 'none' ||
      effects.effect_pan !== 'none' ||
      effects.effect_speed !== 1.0 ||
      effects.effect_shake === 1 ||
      effects.effect_fade !== 'none' ||
      effects.effect_rotate !== 'none' ||
      effects.effect_bounce === 1 ||
      effects.effect_tilt_3d !== 'none' ||
      effects.effect_vignette !== 'none' ||
      effects.effect_color_temp !== 'none' ||
      effects.effect_saturation !== 1 ||  // DEBUG: Changed from 1.0 to 1 (INTEGER)
      effects.effect_film_grain === 1 ||
      effects.effect_glitch === 1 ||
      effects.effect_chromatic === 1 ||
      effects.effect_blur !== 'none' ||
      effects.effect_light_leaks === 1 ||
      effects.effect_lens_flare === 1 ||
      effects.effect_kaleidoscope === 1
    )
  }

  return (
    <div className="mt-3 border-t border-gray-700 pt-3">
      {/* Toggle Button */}
      <button
        onClick={(e) => {
          e.stopPropagation()
          onToggle()
        }}
        className={`w-full flex items-center justify-between px-3 py-2 rounded transition-colors ${
          hasActiveEffects()
            ? 'bg-purple-600/20 border border-purple-500/50 hover:bg-purple-600/30'
            : 'bg-gray-800 hover:bg-gray-700'
        }`}
      >
        <div className="flex items-center gap-2">
          <Sparkles className={`w-4 h-4 ${hasActiveEffects() ? 'text-purple-400' : 'text-gray-400'}`} />
          <span className={`text-sm font-medium ${hasActiveEffects() ? 'text-purple-300' : 'text-gray-300'}`}>
            Effects {hasActiveEffects() ? '(Active)' : ''}
          </span>
        </div>
        <span className="text-xs text-gray-500">
          {isOpen ? '▲' : '▼'}
        </span>
      </button>

      {/* Effects Controls */}
      {isOpen && (
        <div
          className="mt-3 p-3 bg-dark/50 rounded border border-gray-700"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Category Tabs */}
          <div className="flex gap-1 mb-4 p-1 bg-darker rounded">
            <button
              onClick={() => setActiveCategory('motion')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-2 rounded text-xs font-medium transition-colors ${
                activeCategory === 'motion'
                  ? 'bg-primary text-white'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              <Move className="w-3.5 h-3.5" />
              Motion
            </button>
            <button
              onClick={() => setActiveCategory('color')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-2 rounded text-xs font-medium transition-colors ${
                activeCategory === 'color'
                  ? 'bg-primary text-white'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              <Palette className="w-3.5 h-3.5" />
              Color
            </button>
            <button
              onClick={() => setActiveCategory('creative')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-2 rounded text-xs font-medium transition-colors ${
                activeCategory === 'creative'
                  ? 'bg-primary text-white'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              <Wand2 className="w-3.5 h-3.5" />
              Creative
            </button>
            <button
              onClick={() => setActiveCategory('timing')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-2 rounded text-xs font-medium transition-colors ${
                activeCategory === 'timing'
                  ? 'bg-primary text-white'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              Timing
            </button>
          </div>

          <div className="space-y-3">
            {/* MOTION EFFECTS */}
            {activeCategory === 'motion' && (
              <>
                {/* Zoom Effect */}
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">
                    Zoom
                  </label>
                  <select
                    value={effects.effect_zoom}
                    onChange={(e) => handleEffectChange('effect_zoom', e.target.value)}
                    className="w-full bg-darker border border-gray-600 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="none">None</option>
                    <option value="zoom_in">Zoom In</option>
                    <option value="zoom_out">Zoom Out</option>
                    <option value="ken_burns">Ken Burns</option>
                    <option value="pulse">Pulse</option>
                  </select>
                </div>

                {/* Pan Effect */}
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">
                    Pan
                  </label>
                  <select
                    value={effects.effect_pan}
                    onChange={(e) => handleEffectChange('effect_pan', e.target.value)}
                    className="w-full bg-darker border border-gray-600 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="none">None</option>
                    <option value="left">Pan Left</option>
                    <option value="right">Pan Right</option>
                    <option value="up">Pan Up</option>
                    <option value="down">Pan Down</option>
                  </select>
                </div>

                {/* Rotate Effect */}
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">
                    Rotate
                  </label>
                  <select
                    value={effects.effect_rotate}
                    onChange={(e) => handleEffectChange('effect_rotate', e.target.value)}
                    className="w-full bg-darker border border-gray-600 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="none">None</option>
                    <option value="clockwise">Clockwise 360°</option>
                    <option value="counter_clockwise">Counter-Clockwise 360°</option>
                    <option value="wobble">Wobble</option>
                  </select>
                </div>

                {/* 3D Tilt Effect */}
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">
                    3D Tilt / Perspective
                  </label>
                  <select
                    value={effects.effect_tilt_3d}
                    onChange={(e) => handleEffectChange('effect_tilt_3d', e.target.value)}
                    className="w-full bg-darker border border-gray-600 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="none">None</option>
                    <option value="left">Tilt Left</option>
                    <option value="right">Tilt Right</option>
                    <option value="forward">Tilt Forward</option>
                    <option value="backward">Tilt Backward</option>
                  </select>
                </div>

                {/* Bounce Effect */}
                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={effects.effect_bounce === 1}
                      onChange={(e) => handleEffectChange('effect_bounce', e.target.checked ? 1 : 0)}
                      className="w-4 h-4 rounded border-gray-600 bg-darker focus:ring-2 focus:ring-primary"
                    />
                    <span className="text-xs font-medium text-gray-400">
                      Bounce Effect
                    </span>
                  </label>
                </div>

                {/* Shake Effect */}
                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={effects.effect_shake === 1}
                      onChange={(e) => handleEffectChange('effect_shake', e.target.checked ? 1 : 0)}
                      className="w-4 h-4 rounded border-gray-600 bg-darker focus:ring-2 focus:ring-primary"
                    />
                    <span className="text-xs font-medium text-gray-400">
                      Shake / Vibrate
                    </span>
                  </label>
                </div>
              </>
            )}

            {/* COLOR EFFECTS */}
            {activeCategory === 'color' && (
              <>
                {/* Vignette Effect */}
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">
                    Vignette
                  </label>
                  <select
                    value={effects.effect_vignette}
                    onChange={(e) => handleEffectChange('effect_vignette', e.target.value)}
                    className="w-full bg-darker border border-gray-600 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="none">None</option>
                    <option value="dark">Dark (Darken Edges)</option>
                    <option value="light">Light (Lighten Edges)</option>
                  </select>
                </div>

                {/* Color Temperature Effect */}
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">
                    Color Temperature
                  </label>
                  <select
                    value={effects.effect_color_temp}
                    onChange={(e) => handleEffectChange('effect_color_temp', e.target.value)}
                    className="w-full bg-darker border border-gray-600 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="none">None</option>
                    <option value="warm">Warm (Orange/Red Tones)</option>
                    <option value="cool">Cool (Blue Tones)</option>
                  </select>
                </div>

                {/* Saturation Slider */}
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">
                    Saturation: {Math.round(effects.effect_saturation * 100)}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={effects.effect_saturation}
                    onChange={(e) => handleEffectChange('effect_saturation', parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-primary"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>B&W (0%)</span>
                    <span>Normal (100%)</span>
                    <span>Vibrant (200%)</span>
                  </div>
                </div>
              </>
            )}

            {/* CREATIVE EFFECTS */}
            {activeCategory === 'creative' && (
              <>
                {/* Blur Effect */}
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">
                    Blur
                  </label>
                  <select
                    value={effects.effect_blur}
                    onChange={(e) => handleEffectChange('effect_blur', e.target.value)}
                    className="w-full bg-darker border border-gray-600 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="none">None</option>
                    <option value="gaussian">Gaussian Blur</option>
                    <option value="motion">Motion Blur</option>
                    <option value="radial">Radial Blur</option>
                  </select>
                </div>

                {/* Film Grain Effect */}
                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={effects.effect_film_grain === 1}
                      onChange={(e) => handleEffectChange('effect_film_grain', e.target.checked ? 1 : 0)}
                      className="w-4 h-4 rounded border-gray-600 bg-darker focus:ring-2 focus:ring-primary"
                    />
                    <span className="text-xs font-medium text-gray-400">
                      Film Grain (Vintage Look)
                    </span>
                  </label>
                </div>

                {/* Glitch Effect */}
                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={effects.effect_glitch === 1}
                      onChange={(e) => handleEffectChange('effect_glitch', e.target.checked ? 1 : 0)}
                      className="w-4 h-4 rounded border-gray-600 bg-darker focus:ring-2 focus:ring-primary"
                    />
                    <span className="text-xs font-medium text-gray-400">
                      Glitch Effect
                    </span>
                  </label>
                </div>

                {/* Chromatic Aberration Effect */}
                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={effects.effect_chromatic === 1}
                      onChange={(e) => handleEffectChange('effect_chromatic', e.target.checked ? 1 : 0)}
                      className="w-4 h-4 rounded border-gray-600 bg-darker focus:ring-2 focus:ring-primary"
                    />
                    <span className="text-xs font-medium text-gray-400">
                      Chromatic Aberration (RGB Split)
                    </span>
                  </label>
                </div>

                {/* Light Leaks Effect */}
                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={effects.effect_light_leaks === 1}
                      onChange={(e) => handleEffectChange('effect_light_leaks', e.target.checked ? 1 : 0)}
                      className="w-4 h-4 rounded border-gray-600 bg-darker focus:ring-2 focus:ring-primary"
                    />
                    <span className="text-xs font-medium text-gray-400">
                      Light Leaks
                    </span>
                  </label>
                </div>

                {/* Lens Flare Effect */}
                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={effects.effect_lens_flare === 1}
                      onChange={(e) => handleEffectChange('effect_lens_flare', e.target.checked ? 1 : 0)}
                      className="w-4 h-4 rounded border-gray-600 bg-darker focus:ring-2 focus:ring-primary"
                    />
                    <span className="text-xs font-medium text-gray-400">
                      Lens Flare
                    </span>
                  </label>
                </div>

                {/* Kaleidoscope Effect */}
                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={effects.effect_kaleidoscope === 1}
                      onChange={(e) => handleEffectChange('effect_kaleidoscope', e.target.checked ? 1 : 0)}
                      className="w-4 h-4 rounded border-gray-600 bg-darker focus:ring-2 focus:ring-primary"
                    />
                    <span className="text-xs font-medium text-gray-400">
                      Kaleidoscope
                    </span>
                  </label>
                </div>
              </>
            )}

            {/* TIMING EFFECTS */}
            {activeCategory === 'timing' && (
              <>
                {/* Speed Effect */}
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">
                    Speed: {effects.effect_speed}x
                  </label>
                  <select
                    value={effects.effect_speed}
                    onChange={(e) => handleEffectChange('effect_speed', parseFloat(e.target.value))}
                    className="w-full bg-darker border border-gray-600 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="0.5">0.5x (Slow Motion)</option>
                    <option value="0.75">0.75x (Slower)</option>
                    <option value="1.0">1.0x (Normal)</option>
                    <option value="1.5">1.5x (Faster)</option>
                    <option value="2.0">2.0x (Fast)</option>
                  </select>
                </div>

                {/* Fade Effect */}
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">
                    Fade
                  </label>
                  <select
                    value={effects.effect_fade}
                    onChange={(e) => handleEffectChange('effect_fade', e.target.value)}
                    className="w-full bg-darker border border-gray-600 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="none">None</option>
                    <option value="in">Fade In</option>
                    <option value="out">Fade Out</option>
                    <option value="both">Fade In + Out</option>
                  </select>
                </div>
              </>
            )}

            {/* Intensity Slider (for applicable effects) */}
            {(effects.effect_zoom !== 'none' ||
              effects.effect_pan !== 'none' ||
              effects.effect_shake === 1 ||
              effects.effect_bounce === 1 ||
              effects.effect_tilt_3d !== 'none' ||
              effects.effect_vignette !== 'none' ||
              effects.effect_color_temp !== 'none' ||
              effects.effect_film_grain === 1 ||
              effects.effect_glitch === 1 ||
              effects.effect_chromatic === 1 ||
              effects.effect_blur !== 'none' ||
              effects.effect_light_leaks === 1 ||
              effects.effect_lens_flare === 1) && (
              <div className="pt-3 border-t border-gray-700">
                <label className="block text-xs font-medium text-gray-400 mb-1">
                  Effect Intensity: {Math.round(effects.effect_intensity * 100)}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={effects.effect_intensity}
                  onChange={(e) => handleEffectChange('effect_intensity', parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-primary"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Subtle</span>
                  <span>Strong</span>
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="mt-4 space-y-2 pt-3 border-t border-gray-700">
            {/* Save Button */}
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed rounded text-sm font-medium transition-colors"
            >
              <Zap className={`w-4 h-4 ${isSaving ? 'animate-pulse' : ''}`} />
              {isSaving ? 'Saving...' : 'Apply Effects'}
            </button>

            {/* Reset Button */}
            {hasActiveEffects() && (
              <button
                onClick={() => {
                  const resetEffects = {
                    effect_zoom: 'none',
                    effect_pan: 'none',
                    effect_speed: 1.0,
                    effect_shake: 0,
                    effect_fade: 'none',
                    effect_intensity: 0.5,
                    effect_rotate: 'none',
                    effect_bounce: 0,
                    effect_tilt_3d: 'none',
                    effect_vignette: 'none',
                    effect_color_temp: 'none',
                    effect_saturation: 1.0,
                    effect_film_grain: 0,
                    effect_glitch: 0,
                    effect_chromatic: 0,
                    effect_blur: 'none',
                    effect_light_leaks: 0,
                    effect_lens_flare: 0,
                    effect_kaleidoscope: 0
                  }
                  setEffects(resetEffects)
                  updateScene(scene.id, resetEffects)
                }}
                className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
              >
                Reset All Effects
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default EffectsPanel
