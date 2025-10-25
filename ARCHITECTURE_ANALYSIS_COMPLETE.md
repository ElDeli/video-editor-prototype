# VIDEO EDITOR PROTOTYPE - COMPLETE ARCHITECTURE ANALYSIS

**Analysis Date:** October 25, 2025  
**Codebase Location:** /Users/marcoglamngiw/video_editor_prototype  
**Status:** Production Ready - v1.0.0  

---

## EXECUTIVE SUMMARY

The Video Editor Prototype is a **full-stack AI-powered video creation platform** that enables users to generate professional short-form videos with AI-generated images, text-to-speech, visual effects, and music. It follows a **hybrid architecture** with local development on Mac and cloud deployment on Railway.

**Key Characteristics:**
- 7 AI image models (Flux Schnell - 13x cheaper, Ideogram, Recraft, SDXL)
- 3 TTS services (Edge TTS - free, OpenAI, ElevenLabs - premium)
- 13-language translation support
- Advanced visual effects (zoom, pan, rotate, glitch, film grain, vignette, etc.)
- Per-scene sound effects and looping background music
- Multi-platform deployment (Mac local + Railway cloud)

---

## TABLE OF CONTENTS

1. [Flask API Endpoints](#flask-api-endpoints)
2. [Complete Directory Structure](#complete-directory-structure)
3. [Dropbox Paths (Hybrid Storage)](#dropbox-paths-hybrid-storage)
4. [Railway Deployment Configuration](#railway-deployment-configuration)
5. [Database Schema](#database-schema)
6. [Python Services](#python-services)
7. [Frontend Architecture](#frontend-architecture)
8. [AI Service Integration Points](#ai-service-integration-points)

---

## FLASK API ENDPOINTS

### Authentication & Health
| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| GET | `/` | Serve React frontend (index.html) | ✓ |
| GET | `/api/health` | Health check endpoint | ✓ |
| GET | `/<path:path>` | Serve static assets (JS, CSS) | ✓ |

### Projects API (`/api/projects*`)
| Method | Endpoint | Purpose | Returns |
|--------|----------|---------|---------|
| GET | `/api/projects` | List all projects | `[{id, name, tts_voice, ...}]` |
| POST | `/api/projects` | Create new project | `{id, name, created_at}` |
| GET | `/api/projects/<id>` | Get project + all scenes | `{project: {...}, scenes: [...]}` |
| PATCH/PUT | `/api/projects/<id>` | Update project settings | `{updated_project}` |
| POST | `/api/projects/<id>/scenes` | Add single scene | `{id, project_id, script, ...}` |
| POST | `/api/projects/<id>/scenes/bulk` | Auto-extract scenes from full script | `[{scene1}, {scene2}, ...]` |
| POST | `/api/projects/<id>/scenes/reorder` | Reorder scenes by ID array | `{success: true}` |
| POST | `/api/projects/<id>/preview` | Generate 540p preview video | `{preview_id, video_path, total_duration, ...}` |
| POST | `/api/projects/<id>/export` | Generate 1080p final video | `{video_path, scene_count, total_duration}` |
| GET | `/api/projects/<id>/download` | Download exported video file | Binary MP4 file |
| POST | `/api/projects/<id>/upload-to-queue` | Copy video to output folder | `{destination_path, folder_name}` |
| GET | `/api/thumbnails/<keyword>` | Generate thumbnail for keyword | JPEG image |

**Project Settings (updatable via PATCH):**
- `tts_voice`: Selected voice (default: `de-DE-KatjaNeural`)
- `background_music_path`: Path to background music file
- `background_music_volume`: Volume 0-100 (default: 7)
- `target_language`: Translation language or 'auto' (default: 'auto')
- `video_speed`: Playback speed 0.5x-2.0x (default: 1.0)
- `ai_image_model`: AI model to use (default: `flux-schnell`)

### Scenes API (`/api/scenes*`)
| Method | Endpoint | Purpose | Returns |
|--------|----------|---------|---------|
| GET | `/api/scenes/<id>` | Get scene by ID | `{id, project_id, script, duration, ...}` |
| PUT | `/api/scenes/<id>` | Update scene data | Updated scene object |
| DELETE | `/api/scenes/<id>` | Delete scene | `{success: true}` |
| POST | `/api/scenes/<id>/regenerate-image` | Regenerate AI image for scene | `{success: true, new_keyword}` |

**Scene Properties:**
- `script`: Text content for TTS
- `duration`: Scene duration in seconds
- `background_type`: 'solid' or 'keyword' (AI-generated)
- `background_value`: Color (#000000) or AI keyword
- `effect_zoom`: zoom-in, zoom-out, none
- `effect_pan`: pan-left, pan-right, none
- `effect_rotate`: rotate-cw, rotate-ccw, none
- `effect_speed`: Playback speed multiplier
- `effect_shake`: Boolean (camera shake effect)
- `effect_fade`: fade-in, fade-out, none
- `effect_vignette`: dark, light, none
- `effect_glitch`: Boolean (digital glitch effect)
- `effect_film_grain`: Boolean (analog film effect)
- `sound_effect_path`: Path to per-scene sound effect MP3
- `sound_effect_volume`: Volume 0-100

### Scripts API (`/api/scripts*`)
| Method | Endpoint | Purpose | Returns |
|--------|----------|---------|---------|
| POST | `/api/scripts/improve` | Improve script with GPT-4o-mini | `{improved_script, original_script, message}` |

**Improvements Applied:**
- Hook: Attention-grabbing opening
- Flow: Conversational tone
- Emotion: Emotional triggers (curiosity, inspiration)
- Pacing: Short, punchy sentences
- CTA: Strong call-to-action
- Duration: Optional targeting of specific duration
- Emoji removal: All emojis stripped (TTS incompatible)

### TTS (Text-to-Speech) API (`/api/tts*`)
| Method | Endpoint | Purpose | Returns |
|--------|----------|---------|---------|
| GET | `/api/tts/voices` | List Edge TTS voices (free) | `{voice_groups: [{language, options: [{voice_id, label, gender}]}]}` |
| GET | `/api/tts/preview/<voice_name>` | Get voice sample (cached) | MP3 audio stream |
| GET | `/api/tts/elevenlabs/voices` | List ElevenLabs voices (premium) | `{voices: [{voice_id, label, characteristics}]}` |
| GET | `/api/tts/elevenlabs/preview/<voice_id>` | Get ElevenLabs voice sample | MP3 audio stream |
| GET | `/api/tts/openai/voices` | List OpenAI TTS voices | `{voices: [voiceOptions]}` |
| GET | `/api/tts/openai/preview/<voice_id>` | Get OpenAI voice sample | MP3 audio stream |

**Available Voices:**
- **Edge TTS (Free):** 15 German voices, 6 US English, 4 UK English, + Spanish, French, Italian, Portuguese, Polish, Dutch, Turkish, Russian, Japanese, Chinese, Arabic, Hindi
- **ElevenLabs (Premium):** Premium voices with accent/age/gender metadata
- **OpenAI TTS:** alloy, echo, fable, nova, shimmer (monolingual support)

### Sound Effects API (`/api/sound-effects*`)
| Method | Endpoint | Purpose | Returns |
|--------|----------|---------|---------|
| POST | `/api/sound-effects/generate` | Generate sound effect (ElevenLabs) | `{path, text_prompt}` |
| POST | `/api/scenes/<id>/sound-effect` | Add sound effect to scene | Updated scene object |
| DELETE | `/api/scenes/<id>/sound-effect` | Remove sound effect from scene | Updated scene object |
| GET | `/api/scenes/<id>/sound-effect/audio` | Serve sound effect preview | MP3 audio stream |
| POST | `/api/scenes/<id>/sound-effect/generate` | Generate and add sound effect in one call | Updated scene object |

**ElevenLabs Sound Effects:** AI-generated sounds from text prompts (0.5-22 seconds)

### Music API (`/api/music*`)
| Method | Endpoint | Purpose | Returns |
|--------|----------|---------|---------|
| POST | `/api/music/generate` | Generate background music (ElevenLabs) | `{path, filename, duration}` |
| GET | `/api/music/test` | Test if Music API is configured | `{configured: bool}` |

**Music Generation:**
- Automatic duration calculation from project scenes
- Max 22 seconds (loops in video if shorter than total duration)
- ElevenLabs API required

### Uploads API (`/api/uploads*`)
| Method | Endpoint | Purpose | Returns |
|--------|----------|---------|---------|
| POST | `/api/uploads/audio` | Upload background music file | `{filename, path, original_name, size}` |
| POST | `/api/uploads/image` | Upload scene background image | `{filename, path, original_name, size}` |
| GET | `/api/uploads/audio/<filename>` | Serve uploaded audio file | Audio stream |
| GET | `/api/uploads/image/<filename>` | Serve uploaded image file | Image stream |
| DELETE | `/api/uploads/audio/<filename>` | Delete audio file | `{success: true}` |
| DELETE | `/api/uploads/image/<filename>` | Delete image file | `{success: true}` |

**File Constraints:**
- Audio: MP3, WAV, M4A, AAC, OGG (max 50MB)
- Images: JPG, JPEG, PNG, WEBP (max 10MB)

### Settings API (`/api/settings*`)
| Method | Endpoint | Purpose | Returns |
|--------|----------|---------|---------|
| GET | `/api/settings/output-folders` | List output folders | `[{id, name, path, is_default}]` |
| POST | `/api/settings/output-folders` | Add output folder | New folder object |
| DELETE | `/api/settings/output-folders/<id>` | Delete output folder | `{success: true}` |
| POST | `/api/settings/output-folders/<id>/set-default` | Set default output folder | `{success: true}` |
| GET | `/api/settings/output-folders/default` | Get default output folder | Default folder object |
| GET | `/api/settings/browse-folders` | Browse filesystem folders | `{currentPath, parentPath, folders: [{name, path}]}` |

### Preview API
| Method | Endpoint | Purpose | Returns |
|--------|----------|---------|---------|
| GET | `/api/previews/<filename>` | Serve generated preview video from Dropbox | MP4 video stream |

---

## COMPLETE DIRECTORY STRUCTURE

```
/Users/marcoglamngiw/video_editor_prototype/
│
├── 📁 backend/                          # Flask Python Backend
│   ├── 📁 api/                         # REST API Endpoints (8 modules)
│   │   ├── __init__.py                 # Package init
│   │   ├── projects.py                 # 477 lines - Project/Scene/Preview/Export CRUD
│   │   ├── scenes.py                   # 113 lines - Scene edit/delete/regenerate
│   │   ├── scripts.py                  # 128 lines - AI Script Improvement (GPT-4o-mini)
│   │   ├── tts.py                      # 291 lines - 3 TTS services (Edge/OpenAI/ElevenLabs)
│   │   ├── uploads.py                  # 170 lines - Audio/Image upload handling
│   │   ├── sound_effects.py            # 168 lines - Sound effect generation/management
│   │   ├── music.py                    # 109 lines - Background music generation
│   │   └── settings.py                 # 108 lines - Output folder configuration
│   │
│   ├── 📁 services/                    # Business Logic Layer (13 modules)
│   │   ├── replicate_image_service.py  # AI Image generation (7 models)
│   │   │   └── Models: flux-schnell ($0.003), flux-dev, flux-pro, flux-pro-1.1,
│   │   │     ideogram-v3, recraft-v3, sdxl
│   │   │   └── Cache: ~/Dropbox/.../image_cache (MD5-based)
│   │   │
│   │   ├── simple_video_generator.py   # FFmpeg video composition
│   │   │   └── Output: ~/Dropbox/.../previews/ (540p & 1080p)
│   │   │
│   │   ├── preview_generator.py        # Preview orchestration (50 lines)
│   │   │
│   │   ├── video_generator.py          # Legacy video generator (if exists)
│   │   │
│   │   ├── elevenlabs_voice_service.py # Premium TTS voices
│   │   ├── openai_tts_service.py       # OpenAI TTS API wrapper
│   │   ├── elevenlabs_sound_service.py # Sound effect generation
│   │   ├── elevenlabs_music_service.py # Background music generation
│   │   │
│   │   ├── translation_service.py      # Multi-language translation (13 languages)
│   │   │
│   │   ├── keyword_extractor.py        # Visual keyword extraction (GPT-4o-mini)
│   │   │
│   │   ├── video_effects.py            # Visual effects library
│   │   │
│   │   ├── dropbox_storage.py          # Hybrid storage (local/Dropbox API)
│   │   │
│   │   └── __init__.py                 # Package init
│   │
│   ├── 📁 database/                    # Data Layer
│   │   ├── db_manager.py               # SQLite ORM (all CRUD operations)
│   │   ├── __init__.py
│   │   └── editor_projects.db          # SQLite database file
│   │
│   ├── 📁 previews/                    # Generated video cache (local)
│   │   └── (preview MP4 files during development)
│   │
│   ├── 📁 voice_samples/               # Cached voice samples
│   │   └── (MP3 files, one per voice for preview)
│   │
│   ├── 📁 uploads/                     # User uploaded files (local backup)
│   │   └── (mirrors Dropbox upload structure)
│   │
│   ├── 📁 replicate_cache/             # AI image cache (local backup)
│   │   └── (MD5-hashed image files)
│   │
│   ├── 📁 venv/                        # Python Virtual Environment
│   │   └── (dependencies installed via pip)
│   │
│   ├── app.py                          # Flask app entry point (72 lines)
│   ├── requirements.txt                # Python dependencies (12 packages)
│   └── .env                            # Environment variables (API keys)
│
├── 📁 frontend/                        # React Frontend (Vite + Tailwind)
│   ├── 📁 src/
│   │   ├── 📁 components/              # Reusable React components
│   │   │   ├── Header.jsx              # Top navigation bar
│   │   │   ├── VoiceSelector.jsx       # TTS voice dropdown
│   │   │   ├── ScriptEditor/
│   │   │   │   └── ScriptEditor.jsx    # Multi-line script input
│   │   │   ├── Timeline/
│   │   │   │   ├── Timeline.jsx        # Drag-drop scene timeline
│   │   │   │   ├── SceneCard.jsx       # Individual scene item
│   │   │   │   └── EffectsPanel.jsx    # Visual effects editor
│   │   │   ├── VideoPreview/
│   │   │   │   └── VideoPreview.jsx    # Video preview player
│   │   │   ├── BackgroundMusic/
│   │   │   │   └── MusicManager.jsx    # Music upload/generation
│   │   │   ├── SceneImage/
│   │   │   │   └── SceneImageUploader.jsx # Image upload
│   │   │   └── Settings/
│   │   │       ├── OutputFolderSettings.jsx
│   │   │       └── FolderBrowser.jsx
│   │   │
│   │   ├── 📁 hooks/
│   │   │   └── useProject.jsx          # Project state management hook
│   │   │
│   │   ├── 📁 pages/
│   │   │   └── EditorPage.jsx          # Main editor page layout
│   │   │
│   │   ├── 📁 services/
│   │   │   └── api.js                  # Axios API client (all endpoints)
│   │   │
│   │   ├── App.jsx                     # Root React component
│   │   └── main.jsx                    # React entry point
│   │
│   ├── index.html                      # HTML entry point
│   ├── tailwind.config.js              # Tailwind CSS configuration
│   ├── vite.config.js                  # Vite build configuration
│   ├── postcss.config.js               # PostCSS configuration
│   ├── package.json                    # Node dependencies
│   ├── package-lock.json               # Dependency lock file
│   └── 📁 node_modules/                # npm packages
│
├── 📁 logs/                            # Application logs
│   ├── backend.log
│   └── frontend.log
│
├── 📁 .git/                            # Git repository
│
├── 📄 Dockerfile                       # Multi-stage Docker build
│   ├── Stage 1: Node 18 → Build React (Vite)
│   └── Stage 2: Python 3.11 → Run Flask + serve static
│
├── 📄 Procfile                         # Railway deployment config
├── 📄 railway.json                     # Railway build settings
├── 📄 start_all.command                # Local dev startup script
├── 📄 stop_all.command                 # Local dev shutdown script
│
├── 📚 DOCUMENTATION
│   ├── README.md                       # Quick start & feature overview
│   ├── INSTALLATION.md                 # Detailed installation guide
│   ├── HANDBUCH.md                     # German user manual
│   ├── SYSTEM_ARCHITECTURE.md          # This detailed architecture
│   ├── AI_MODEL_INTEGRATION.md         # AI model configuration guide
│   ├── QUICKSTART.md                   # Quick start guide
│   ├── RAILWAY_DEPLOYMENT.md           # Railway deployment guide
│   └── claude_chat_notes_videoeditor.md # Dev notes

└── 📄 Configuration Files
    ├── .gitignore                      # Git ignore patterns
    └── .env.example                    # Environment template

TOTAL: ~100+ files (excluding node_modules and venv)
```

### Key Directories Not in Project Root
These are created dynamically in Dropbox:
- `~/Dropbox/Apps/output Horoskop/video_editor_prototype/previews/` - Generated videos
- `~/Dropbox/Apps/output Horoskop/video_editor_prototype/image_cache/` - AI image cache
- `~/Dropbox/Apps/output Horoskop/video_editor_prototype/uploads/` - User files
  - `audio/` - Background music files
  - `images/` - Scene background images
  - `sound_effects/` - Per-scene sound effects

---

## DROPBOX PATHS (HYBRID STORAGE)

### Storage Architecture
The system uses a **hybrid approach**:
- **Local (Mac):** Direct filesystem access to Dropbox folder
- **Cloud (Railway):** Dropbox API when local folder not available

### All Dropbox Paths Used

| Component | Path | Purpose | Size |
|-----------|------|---------|------|
| **Previews** | `~/Dropbox/Apps/output Horoskop/video_editor_prototype/previews/` | Generated videos (540p & 1080p) | Varies |
| **Image Cache** | `~/Dropbox/Apps/output Horoskop/video_editor_prototype/image_cache/` | MD5-hashed AI images | ~500MB+ |
| **Audio Uploads** | `~/Dropbox/Apps/output Horoskop/video_editor_prototype/uploads/audio/` | User-uploaded music | ~1GB |
| **Image Uploads** | `~/Dropbox/Apps/output Horoskop/video_editor_prototype/uploads/images/` | User-uploaded images | ~500MB |
| **Sound Effects** | `~/Dropbox/Apps/output Horoskop/video_editor_prototype/uploads/sound_effects/` | ElevenLabs-generated effects | ~300MB |

### Path References in Code

```python
# backend/api/projects.py (lines 57, 366, 419)
dropbox_path = os.path.expanduser("~/Dropbox/Apps/output Horoskop/video_editor_prototype/previews")

# backend/api/uploads.py (line 10)
DROPBOX_BASE = Path(os.path.expanduser('~/Dropbox/Apps/output Horoskop/video_editor_prototype/uploads'))

# backend/services/replicate_image_service.py (line 22)
dropbox_path = os.path.expanduser("~/Dropbox/Apps/output Horoskop/video_editor_prototype/image_cache")

# backend/services/elevenlabs_sound_service.py
self.sound_dir = Path(os.path.expanduser('~/Dropbox/Apps/output Horoskop/video_editor_prototype/uploads/sound_effects'))

# backend/services/dropbox_storage.py (line 11)
self.dropbox_base = '~/Dropbox/Apps/output Horoskop/output/video_editor_prototype'

# backend/app.py (line 57)
previews_dir = Path(os.path.expanduser('~/Dropbox/Apps/output Horoskop/video_editor_prototype/previews'))
```

### Database Location
- **Local:** `./backend/database/editor_projects.db` (or `DATABASE_PATH` env var)
- **Railway:** Creates in container working directory

---

## RAILWAY DEPLOYMENT CONFIGURATION

### Build Configuration (railway.json)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Procfile

```
web: cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

### Dockerfile (Multi-stage Build)

**Stage 1: Frontend Build (Node 18)**
- Copy `frontend/package*.json`
- Run `npm ci` (clean install)
- Copy frontend source
- Run `npm run build` → outputs to `frontend/dist/`

**Stage 2: Backend Runtime (Python 3.11)**
- Install system deps: `ffmpeg`, `libmagic1`
- Copy backend code
- Install Python requirements from `backend/requirements.txt`
- Install gunicorn 21.2.0
- Copy built frontend dist → `backend/static/`
- Set `PYTHONUNBUFFERED=1`
- Expose port (from `$PORT` env var)
- Run: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

### Environment Variables Required

```
# Required
REPLICATE_API_TOKEN=xxx
OPENAI_API_KEY=xxx
ELEVENLABS_API_KEY=xxx
PORT=5001

# Optional (Railway)
DROPBOX_ACCESS_TOKEN=xxx  # For Railway, when local Dropbox unavailable
DATABASE_PATH=/app/backend/database/editor_projects.db
```

### Deployment Flow

1. **Push to GitHub** → Railway detects push
2. **Build Phase:**
   - Read Dockerfile
   - Build frontend with Vite
   - Install Python deps
   - Copy static assets to backend
3. **Run Phase:**
   - Start gunicorn on `$PORT`
   - Backend serves both API and static frontend
4. **Auto-restart:** ON_FAILURE (up to 10 retries)

### Performance Tuning

```
--workers 2       # 2 worker processes (Railway small size)
--timeout 120     # 120s timeout for video generation
--bind 0.0.0.0    # Listen on all interfaces
```

---

## DATABASE SCHEMA

### SQLite Database: `editor_projects.db`

```sql
-- Projects Table (main container)
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    tts_voice TEXT DEFAULT 'de-DE-KatjaNeural',
    background_music_path TEXT,
    background_music_volume INTEGER DEFAULT 7,
    target_language TEXT DEFAULT 'auto',
    video_speed REAL DEFAULT 1.0,
    ai_image_model TEXT DEFAULT 'flux-schnell',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Scenes Table (video timeline)
CREATE TABLE IF NOT EXISTS scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    scene_order INTEGER NOT NULL,
    script TEXT NOT NULL,
    duration REAL DEFAULT 5.0,
    background_type TEXT DEFAULT 'solid',  -- 'solid' or 'keyword' (AI)
    background_value TEXT,  -- Color (#000000) or AI keyword
    audio_path TEXT,  -- Legacy TTS audio
    
    -- Motion Effects
    effect_zoom TEXT DEFAULT 'none',  -- zoom-in, zoom-out
    effect_pan TEXT DEFAULT 'none',   -- pan-left, pan-right
    effect_rotate TEXT DEFAULT 'none', -- rotate-cw, rotate-ccw
    effect_speed REAL DEFAULT 1.0,     -- Playback speed
    effect_shake INTEGER DEFAULT 0,    -- Boolean camera shake
    effect_bounce INTEGER DEFAULT 0,   -- Boolean bounce effect
    effect_tilt_3d TEXT DEFAULT 'none',-- 3D tilt effect
    
    -- Color Effects
    effect_fade TEXT DEFAULT 'none',   -- fade-in, fade-out
    effect_vignette TEXT DEFAULT 'none', -- dark, light
    effect_color_temp TEXT DEFAULT 'none', -- warm, cool
    effect_saturation REAL DEFAULT 1.0,   -- 0.0-2.0
    
    -- Creative Effects
    effect_film_grain INTEGER DEFAULT 0,  -- Boolean
    effect_glitch INTEGER DEFAULT 0,      -- Boolean
    effect_chromatic INTEGER DEFAULT 0,   -- Boolean chromatic aberration
    effect_blur TEXT DEFAULT 'none',      -- blur intensity
    effect_light_leaks INTEGER DEFAULT 0, -- Boolean
    effect_lens_flare INTEGER DEFAULT 0,  -- Boolean
    effect_kaleidoscope INTEGER DEFAULT 0,-- Boolean
    effect_intensity REAL DEFAULT 0.5,    -- General effect intensity
    
    -- Sound Effects
    sound_effect_path TEXT,  -- Path to scene-specific sound effect
    sound_effect_volume INTEGER DEFAULT 50,  -- 0-100
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
)

-- Settings Table (app configuration)
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- Output Folders Table (export destinations)
CREATE TABLE IF NOT EXISTS output_folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    is_default INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Database Relationships
- **1:Many** - One Project has Many Scenes
- **1:1** - One Project has default output folder (via settings)

### Database Statistics
- Typical project: 1-50 scenes
- Row size: ~2KB per scene
- Typical database: 1-50MB for 1000+ projects

---

## PYTHON SERVICES

### 1. ReplicateImageService (`services/replicate_image_service.py`)

**Purpose:** AI image generation for scene backgrounds

**Supported Models:**
- `flux-schnell` (DEFAULT) - $0.003/img, 10s - **13x cheaper**
- `flux-dev` - $0.025/img, 15s
- `flux-pro` - $0.055/img, 25s
- `flux-pro-1.1` - $0.04/img, 20s - Best quality
- `ideogram-v3` - $0.09/img, 25s - Text in images!
- `recraft-v3` - $0.04/img, 20s - Style variety
- `sdxl` - Budget alternative

**Features:**
- MD5-based image cache (saves API calls)
- German-to-English keyword translation
- Automatic image sizing (608x1080 for video)
- Variation suffix for forced regeneration

**API Usage:**
```python
image_service = ReplicateImageService()
image_path = image_service.generate_image("majestic mountain at sunset", 
                                         model="flux-schnell")
```

### 2. SimpleVideoGenerator (`services/simple_video_generator.py`)

**Purpose:** Compose video from scenes using FFmpeg

**Inputs:**
- List of scenes (script, duration, effects)
- TTS voice
- Background music (optional)
- Video speed multiplier
- AI image model selection

**Outputs:**
- MP4 video file (540p or 1080p)
- Scene timing data (actual duration for sync)

**Processing Pipeline:**
1. Generate TTS audio for each scene
2. Generate AI image for each scene (parallel)
3. Apply visual effects to images
4. Mix audio (TTS + sound effect + background music)
5. Compose final video with FFmpeg/MoviePy

**Key Features:**
- Automatic duration calculation from script length
- Volume mixing (TTS + sound + music)
- Scene-specific effects application
- Background music looping

### 3. PreviewGenerator (`services/preview_generator.py`)

**Purpose:** Orchestrate preview/export generation

**Features:**
- Translation support (13 languages)
- Delegates to SimpleVideoGenerator
- Syncs actual durations back to database
- Supports multiple resolutions (preview/1080p)

### 4. KeywordExtractor (`services/keyword_extractor.py`)

**Purpose:** Extract visual keywords from script (auto-scene creation)

**Uses:** OpenAI GPT-4o-mini API

**Process:**
1. Parse full script into sentences
2. Use GPT-4o-mini to identify key visual moments
3. Extract one keyword per scene
4. Return scene list with visual keywords

### 5. TranslationService (`services/translation_service.py`)

**Supported Languages (13):**
- German (de)
- English (en)
- French (fr)
- Spanish (es)
- Italian (it)
- Portuguese (pt)
- Polish (pl)
- Dutch (nl)
- Turkish (tr)
- Russian (ru)
- Japanese (ja)
- Chinese (zh)
- Hindi (hi)

**Uses:** Google Translate or OpenAI Translate

### 6. ElevenLabsVoiceService (`services/elevenlabs_voice_service.py`)

**Purpose:** Premium TTS voice management

**Features:**
- Get available voices list
- Cache voice metadata
- Download voice samples
- Characteristics: accent, age, gender, use_case

### 7. OpenAITTSService (`services/openai_tts_service.py`)

**Purpose:** OpenAI TTS integration

**Voices:** alloy, echo, fable, nova, shimmer

### 8. ElevenLabsSoundService (`services/elevenlabs_sound_service.py`)

**Purpose:** AI sound effect generation

**Features:**
- Generate sounds from text prompts
- Duration range: 0.5-22 seconds
- Save to Dropbox sound_effects folder

### 9. ElevenLabsMusicService (`services/elevenlabs_music_service.py`)

**Purpose:** AI background music generation

**Features:**
- Generate from text description
- Auto-calculate duration from project
- Max 22 seconds (loops in video)
- Save to output folder

### 10. DropboxStorage (`services/dropbox_storage.py`)

**Purpose:** Hybrid storage abstraction

**Logic:**
- Check if local Dropbox folder exists
  - YES → Use filesystem directly (Mac)
  - NO → Use Dropbox API (Railway)

**Methods:**
- `save_file(rel_path, data)` - Save file
- `file_exists(rel_path)` - Check existence
- `get_file_content(rel_path)` - Read file

---

## FRONTEND ARCHITECTURE

### Tech Stack
- **Framework:** React 18
- **Build Tool:** Vite 5.3
- **Styling:** Tailwind CSS 3.4
- **HTTP Client:** Axios 1.7
- **Icons:** Lucide React
- **Video Playback:** react-player

### Component Tree

```
App.jsx (root)
├── EditorPage.jsx (main layout)
│   ├── Header.jsx
│   │   ├── Project title & buttons
│   │   ├── Export/Download controls
│   │   └── Settings menu
│   │
│   ├── Timeline.jsx (left panel, 50% width)
│   │   ├── SceneCard[] (drag-drop)
│   │   │   ├── Scene number
│   │   │   ├── Thumbnail
│   │   │   ├── Script text
│   │   │   ├── Duration display
│   │   │   └── Delete button
│   │   ├── Add Scene button
│   │   └── Bulk import from script
│   │
│   └── RightPanel (50% width, tabs)
│       ├── Script Editor Tab
│       │   ├── ScriptEditor.jsx
│       │   ├── Script improvement button
│       │   └── Language selector
│       │
│       ├── Settings Tab
│       │   ├── VoiceSelector.jsx (TTS voice dropdown)
│       │   ├── Music Manager
│       │   ├── Output folder selector
│       │   ├── Video speed slider
│       │   └── AI model selector
│       │
│       ├── Effects Tab
│       │   └── EffectsPanel.jsx
│       │       ├── Effect toggles (zoom, pan, rotate, etc.)
│       │       ├── Effect intensity sliders
│       │       └── Sound effect upload
│       │
│       └── Preview Tab
│           └── VideoPreview.jsx
│               ├── Video player
│               ├── Generate preview button
│               ├── Export button
│               └── Download button
```

### Key Components

#### EditorPage.jsx
- Main layout manager
- Project state from `useProject()` hook
- Tab management
- Layout panels

#### Timeline.jsx
- Drag-drop scene reordering
- Scene card rendering
- Add/bulk import buttons
- Visual feedback during drag

#### SceneCard.jsx
- Individual scene display
- Thumbnail generation
- Duration display
- Delete functionality
- Click to edit effects

#### EffectsPanel.jsx
- 20+ visual effect toggles
- Intensity sliders
- Sound effect upload
- Real-time preview

#### VoiceSelector.jsx
- Voice dropdown with groups (by language)
- Voice characteristics display
- Voice sample playback (clicking on voice)

#### ScriptEditor.jsx
- Multi-line text input
- Character counter
- Improve script button
- Language selector

#### MusicManager.jsx
- Upload background music
- Generate music with ElevenLabs
- Volume slider (0-100)
- Duration display

#### VideoPreview.jsx
- Video player (react-player)
- Generate preview button (640p or 540p)
- Export button (1080p)
- Download button
- Progress indicator

### State Management

#### useProject() Hook
```javascript
const {
  project,           // Current project data
  scenes,            // Array of scenes
  addScene,          // Add scene function
  updateScene,       // Update scene
  deleteScene,       // Delete scene
  reorderScenes,     // Reorder scenes
  updateProject,     // Update project settings
  generatePreview,   // Generate preview
  exportVideo,       // Export final video
  downloadVideo,     // Download exported video
} = useProject(projectId)
```

#### Global State
- Project: Redux would be overkill; using React Context or local state
- Scenes: Managed in EditorPage, passed down as props
- UI State: Local component state (tabs, loading, etc.)

### API Integration (api.js)

All requests go to `/api` (relative path, proxied through Flask):

```javascript
// Example calls
await api.getTTSVoices()
await api.generatePreview(projectId)
await api.exportVideo(projectId, '1080p')
```

### Build Output

```
frontend/
├── dist/                      # Vite build output
│   ├── index.html            # Main HTML (served by Flask)
│   ├── assets/
│   │   ├── index-xxx.js      # Main JS bundle
│   │   ├── index-xxx.css     # Tailwind CSS
│   │   └── vendor-xxx.js     # React + dependencies
│   └── ...
```

Copied to `backend/static/` during Docker build → Flask serves at `/`

### Performance Optimizations

1. **Component Memoization:** React.memo on SceneCard
2. **Code Splitting:** Dynamic imports for large components
3. **Image Lazy Loading:** Scene thumbnails only on scroll
4. **Request Debouncing:** Script improve, effects changes
5. **Video Player Optimization:** react-player with streaming

---

## AI SERVICE INTEGRATION POINTS

### 1. Replicate API (Image Generation)

**Integration Points:**
- `POST /api/projects/<id>/preview` (generates images for scenes)
- `POST /api/projects/<id>/export` (generates images for final video)
- `GET /api/thumbnails/<keyword>` (on-demand image generation)
- Scene regeneration: `POST /api/scenes/<id>/regenerate-image`

**Flow:**
```
User selects AI model (ui)
  ↓
frontend sends project settings with ai_image_model
  ↓
PreviewGenerator passes to SimpleVideoGenerator
  ↓
SimpleVideoGenerator.generate_video() → ReplicateImageService.generate_image()
  ↓
API call: replicate.run("black-forest-labs/flux-schnell", 
                        input={"prompt": keyword, "width": 608, "height": 1080})
  ↓
Image saved to ~/Dropbox/.../image_cache/ with MD5 hash
  ↓
Used in video composition
```

**Cost Tracking:**
- Flux Schnell: $0.003/image
- Flux Pro 1.1: $0.04/image
- Ideogram V3: $0.09/image
- Typical project (20 scenes): $0.06 - $1.80

### 2. OpenAI API

**Integration Points:**

A) **Script Improvement (GPT-4o-mini)**
- `POST /api/scripts/improve`
- Improves viral potential, fixes duration
- Cost: ~$0.001 per script

B) **Keyword Extraction (GPT-4o-mini)**
- Used in bulk scene creation
- Extracts visual keywords from full script
- One API call per bulk import

C) **TTS (OpenAI)**
- `GET /api/tts/openai/voices`
- Voice options: alloy, echo, fable, nova, shimmer
- Cost: ~$0.03 per 1M characters

**Flow:**
```
User improves script (ui)
  ↓
frontend POST /api/scripts/improve with original script
  ↓
Backend: from openai import OpenAI
  ↓
client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a viral content creator..."},
        {"role": "user", "content": f"Improve this script:\n{script}"}
    ],
    temperature=0.8
)
  ↓
Response contains improved script
  ↓
Emojis stripped (TTS incompatible)
  ↓
Return to frontend
```

### 3. Edge TTS (Free Text-to-Speech)

**Integration Points:**
- `GET /api/tts/voices` (list available voices)
- `GET /api/tts/preview/<voice_name>` (get voice sample)
- Used in video generation for TTS audio

**Available Voices:** 50+ (German, English, French, Spanish, Italian, etc.)

**Flow:**
```
User selects voice from dropdown (ui)
  ↓
frontend GET /api/tts/voices
  ↓
Backend: asyncio.run(edge_tts.list_voices())
  ↓
Group by language, return to frontend
  ↓
User clicks voice preview button
  ↓
frontend GET /api/tts/preview/de-DE-KatjaNeural
  ↓
Backend checks cache: ./voice_samples/{voice_name}.mp3
  ↓
If not cached: edge_tts.Communicate(sample_text, voice_name).save()
  ↓
Return MP3 stream
```

**Cost:** FREE ✓

### 4. ElevenLabs API

**Integration Points:**

A) **Premium TTS Voices**
- `GET /api/tts/elevenlabs/voices` (list voices)
- `GET /api/tts/elevenlabs/preview/<voice_id>` (voice sample)
- Cost: ~$0.30 per 10K characters

B) **Sound Effects (Sound Effects Generation)**
- `POST /api/sound-effects/generate`
- `POST /api/scenes/<id>/sound-effect/generate`
- Cost: ~$0.03-0.10 per sound
- Duration: 0.5-22 seconds

C) **Background Music (Music Generation)**
- `POST /api/music/generate`
- Cost: ~$0.10 per music generation
- Duration: up to 22 seconds (loops in video)

**Flow (Sound Effects):**
```
User inputs text prompt: "explosion sound"
  ↓
frontend POST /api/sound-effects/generate
  ↓
Backend: elevenlabs_sound_service.generate_sound_effect(text_prompt, duration)
  ↓
API call: elevenlabs.generate(text=text_prompt, duration_seconds=duration)
  ↓
Audio saved to ~/Dropbox/.../sound_effects/{filename}.mp3
  ↓
Return path to frontend
  ↓
Optional: Add to scene via POST /api/scenes/<id>/sound-effect
```

**Cost Tracking:**
- Premium TTS: $0.30 per 10K chars
- Sound Effects: $0.03-0.10 each
- Background Music: $0.10 each
- Typical project: $0.50 - $5.00

### 5. Environment Variables Required

```bash
# Required for all
REPLICATE_API_TOKEN=xxx          # Image generation
OPENAI_API_KEY=xxx               # Script improve + keyword extraction
ELEVENLABS_API_KEY=xxx           # Premium TTS, sounds, music (optional)

# For Railway deployment
DROPBOX_ACCESS_TOKEN=xxx         # When no local Dropbox access
DATABASE_PATH=...                # Custom database location
PORT=5001                        # Server port
```

### 6. AI Service Costs Summary

| Service | Feature | Cost | Typical Usage |
|---------|---------|------|---------------|
| Replicate | Flux Schnell | $0.003/img | 20 images = $0.06 |
| Replicate | Flux Pro 1.1 | $0.04/img | 20 images = $0.80 |
| Replicate | Ideogram V3 | $0.09/img | 5 images = $0.45 |
| OpenAI | GPT-4o-mini | $0.003 per call | Script improve = $0.003 |
| OpenAI | TTS | $0.03 per 1M chars | 60s TTS ≈ $0.02 |
| ElevenLabs | Premium TTS | $0.30 per 10K chars | Per voice per project |
| ElevenLabs | Sound Effects | $0.03-0.10 each | Per scene |
| ElevenLabs | Background Music | $0.10 per track | Per project |
| Edge TTS | All features | **FREE** | Unlimited |

**Budget-Friendly Recommendation:**
- AI Images: Flux Schnell ($0.003)
- TTS: Edge TTS (FREE)
- **Total per 20-scene project: ~$0.06** ✓

---

## INTEGRATION SUMMARY

### Frontend to Backend Flow

```
React Component (EditorPage)
  ↓
User Action (click "Generate Preview")
  ↓
api.generatePreview(projectId)
  ↓
axios.post('/api/projects/1/preview')
  ↓
Flask API (projects.py:242)
  ↓
PreviewGenerator.generate_preview()
  ↓
SimpleVideoGenerator.generate_video()
  ↓
For each scene:
    1. Keyword Extractor → visual keyword
    2. Replicate API → AI image
    3. Edge TTS → audio file
    4. Video Effects → apply filters
    5. Audio Mix → TTS + sound + music
  ↓
FFmpeg → Compose final video
  ↓
Save to ~/Dropbox/.../previews/
  ↓
Response: {video_path, scene_count, total_duration}
  ↓
Frontend displays preview player
```

### Error Handling

- **Replicate API Down:** Fallback to solid color background
- **TTS Unavailable:** Fallback to different TTS service
- **FFmpeg Missing:** JSON manifest fallback
- **Dropbox Path Not Found:** Auto-create directory
- **Database Error:** Return 500 with error message

### Logging

- Backend logs: `logs/backend.log`
- Frontend logs: Browser console + `logs/frontend.log`
- Print statements: Routed to stderr (captured by Railway)

---

## SUMMARY TABLE

| Aspect | Details |
|--------|---------|
| **Language** | Python (backend), JavaScript (frontend) |
| **API Routes** | 35+ endpoints |
| **Database** | SQLite with 4 tables |
| **Storage** | Hybrid (local + Dropbox API) |
| **AI Models** | 7 image models, 3 TTS services, ChatGPT |
| **Deployment** | Docker on Railway, development on Mac |
| **Performance** | Video generation: 30-120s depending on scenes |
| **Cost/Video** | $0.06 (budget) to $3.30 (premium) |
| **Frontend Framework** | React 18 + Vite |
| **Video Quality** | 540p preview, 1080p export |
| **Languages** | 13 (German default) |
| **File Formats** | MP4 video, MP3 audio, JPEG/PNG images |
| **User Limit** | Unlimited projects (database only) |

---

## DEPLOYMENT CHECKLIST

- [ ] Railway project created
- [ ] Environment variables set (REPLICATE, OPENAI, ELEVENLABS tokens)
- [ ] GitHub repo connected
- [ ] Dockerfile builds successfully
- [ ] Frontend assets embedded in static/
- [ ] Database initialization runs on first boot
- [ ] Dropbox folder permissions set (or DROPBOX_ACCESS_TOKEN provided)
- [ ] Test `POST /api/projects` creates new project
- [ ] Test preview generation creates video
- [ ] Test export downloads video

