# 🏗️ Video Editor Prototype - System Architecture

**Version:** 1.0.0
**Last Updated:** 2025-01-24
**Status:** ✅ Production Ready

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Project Structure](#project-structure)
3. [Backend Architecture](#backend-architecture)
4. [Frontend Architecture](#frontend-architecture)
5. [API Endpoints](#api-endpoints)
6. [Database Schema](#database-schema)
7. [File Paths & Directories](#file-paths--directories)
8. [Data Flow](#data-flow)
9. [Service Layer](#service-layer)
10. [Configuration](#configuration)
11. [Deployment](#deployment)

---

## 🎯 System Overview

### Technology Stack

**Backend:**
- Flask 3.0.3 (Python Web Framework)
- SQLite (Database)
- FFmpeg 8.0 (Video Processing)
- MoviePy 1.0.3 (Video Composition)

**Frontend:**
- React 18 (UI Framework)
- Vite (Build Tool)
- Tailwind CSS (Styling)
- Axios (HTTP Client)

**AI Services:**
- Replicate API (7 AI Image Models)
- OpenAI API (TTS + GPT-4o-mini)
- Edge TTS 7.2.3 (Free TTS)
- ElevenLabs (Premium TTS)

### System Ports

| Service | Port | URL |
|---------|------|-----|
| Backend | 5001 | http://localhost:5001 |
| Frontend | 3000 | http://localhost:3000 |

---

## 📂 Project Structure

```
video_editor_prototype/
│
├── backend/                              # Flask Backend (Python)
│   ├── api/                             # REST API Endpoints
│   │   ├── __init__.py
│   │   ├── projects.py                  # Project CRUD + Preview + Export
│   │   ├── scenes.py                    # Scene CRUD + Regeneration
│   │   ├── tts.py                       # TTS Voice Management
│   │   ├── uploads.py                   # File Upload (Audio/Music)
│   │   └── scripts.py                   # AI Script Improvement
│   │
│   ├── services/                        # Core Business Logic
│   │   ├── replicate_image_service.py   # AI Image Generation (7 models)
│   │   ├── simple_video_generator.py    # FFmpeg Video Composition
│   │   ├── preview_generator.py         # Preview Orchestration
│   │   ├── translation_service.py       # Multi-language Translation (13 langs)
│   │   ├── keyword_extractor.py         # Visual Keyword Extraction (GPT-4o)
│   │   ├── tts_service.py              # TTS Service Orchestration
│   │   └── script_improver.py          # AI Script Enhancement
│   │
│   ├── database/                        # SQLite Database
│   │   ├── db_manager.py                # Database Manager (ORM)
│   │   └── editor_projects.db           # SQLite Database File
│   │
│   ├── previews/                        # Generated Video Files
│   │   ├── video_1_preview.mp4
│   │   ├── video_1_1080p.mp4
│   │   └── ...
│   │
│   ├── uploads/                         # User-uploaded Files
│   │   ├── audio/                       # Sound Effects
│   │   └── music/                       # Background Music
│   │
│   ├── venv/                            # Python Virtual Environment
│   ├── app.py                           # Flask App Entry Point
│   ├── requirements.txt                 # Python Dependencies
│   └── .env                             # Environment Variables (API Keys)
│
├── frontend/                            # React Frontend (Vite)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx               # Top Bar (Actions + Settings)
│   │   │   ├── Timeline/
│   │   │   │   ├── Timeline.jsx         # Scene Timeline Manager
│   │   │   │   ├── SceneCard.jsx        # Individual Scene Card
│   │   │   │   └── EffectsPanel.jsx     # Visual Effects Panel
│   │   │   ├── VideoPreview/
│   │   │   │   └── VideoPreview.jsx     # Video Player
│   │   │   ├── ScriptEditor/
│   │   │   │   └── ScriptEditor.jsx     # Bulk Script Input + AI Improve
│   │   │   ├── BackgroundMusic/
│   │   │   │   └── MusicManager.jsx     # Background Music Uploader
│   │   │   └── VoiceSelector.jsx        # TTS Voice Dropdown
│   │   │
│   │   ├── hooks/
│   │   │   └── useProject.js            # Project State Management
│   │   │
│   │   ├── services/
│   │   │   └── api.js                   # Axios API Client
│   │   │
│   │   ├── App.jsx                      # Main App Component
│   │   └── main.jsx                     # React Entry Point
│   │
│   ├── public/                          # Static Assets
│   ├── package.json                     # Node Dependencies
│   ├── vite.config.js                   # Vite Configuration
│   └── tailwind.config.js               # Tailwind CSS Config
│
├── logs/                                # Application Logs
│   ├── backend.log                      # Backend Logs
│   └── frontend.log                     # Frontend Logs
│
├── start_all.command                    # Start Script (macOS)
├── stop_all.command                     # Stop Script (macOS)
│
├── README.md                            # Project Overview
├── INSTALLATION.md                      # Installation Guide
├── HANDBUCH.md                          # User Manual (German)
├── AI_MODEL_INTEGRATION.md              # AI Model Developer Docs
└── SYSTEM_ARCHITECTURE.md               # This File

```

---

## 🔧 Backend Architecture

### Entry Point: `backend/app.py`

```python
from flask import Flask
from flask_cors import CORS
from api import projects, scenes, tts, uploads, scripts

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(projects.projects_bp, url_prefix='/api')
app.register_blueprint(scenes.scenes_bp, url_prefix='/api')
app.register_blueprint(tts.tts_bp, url_prefix='/api/tts')
app.register_blueprint(uploads.uploads_bp, url_prefix='/api/uploads')
app.register_blueprint(scripts.scripts_bp, url_prefix='/api/scripts')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

### API Layer (`backend/api/`)

| File | Purpose | Routes |
|------|---------|--------|
| `projects.py` | Project CRUD, Preview, Export | 9 endpoints |
| `scenes.py` | Scene CRUD, Reordering, Regeneration | 5 endpoints |
| `tts.py` | TTS Voice Management | 4 endpoints |
| `uploads.py` | File Upload Handling | 2 endpoints |
| `scripts.py` | AI Script Improvement | 1 endpoint |

### Service Layer (`backend/services/`)

| Service | Purpose | Key Methods |
|---------|---------|-------------|
| `replicate_image_service.py` | AI Image Generation | `generate_image(keyword, model)` |
| `simple_video_generator.py` | FFmpeg Video Composition | `generate_video(scenes, project_id)` |
| `preview_generator.py` | Preview Orchestration | `generate_preview(project_id, scenes)` |
| `translation_service.py` | Multi-language Translation | `translate(text, target_lang)` |
| `keyword_extractor.py` | Visual Keyword Extraction | `extract_visual_scenes(script)` |
| `tts_service.py` | TTS Orchestration | `generate_tts(text, voice)` |
| `script_improver.py` | AI Script Enhancement | `improve_script(text)` |

### Database Layer (`backend/database/`)

**`db_manager.py`** - Database Manager with ORM-like interface

Key Methods:
- `create_project(name)` → Create new project
- `get_project(id)` → Get project by ID
- `update_project(id, data)` → Update project settings
- `get_project_scenes(id)` → Get all scenes for project
- `add_scene(project_id, data)` → Add scene to project
- `update_scene(id, data)` → Update scene
- `reorder_scenes(project_id, scene_ids)` → Reorder scenes

---

## ⚛️ Frontend Architecture

### Component Hierarchy

```
App.jsx
├── Header.jsx
│   ├── VoiceSelector.jsx
│   └── MusicManager.jsx
├── ScriptEditor.jsx
├── Timeline.jsx
│   ├── SceneCard.jsx (multiple)
│   └── EffectsPanel.jsx
└── VideoPreview.jsx
```

### State Management (`frontend/src/hooks/useProject.js`)

**Global State:**
- `project` - Current project object
- `scenes` - Array of scene objects
- `loading` - Loading state
- `videoUrl` - Preview video URL

**Key Functions:**
- `fetchProject(id)` - Load project + scenes
- `updateScenesFromPreview(scenes)` - Sync actual durations
- `addScene(sceneData)` - Add new scene
- `updateScene(id, data)` - Update scene
- `deleteScene(id)` - Remove scene
- `reorderScenes(newOrder)` - Drag-drop reordering

### API Client (`frontend/src/services/api.js`)

Axios wrapper with base URL configuration:

```javascript
const API_BASE_URL = '/api'

export default {
  // Projects
  createProject(name)
  getProject(projectId)
  updateProject(projectId, data)
  exportVideo(projectId, format)

  // Scenes
  addScene(projectId, sceneData)
  updateScene(sceneId, data)
  deleteScene(sceneId)
  reorderScenes(projectId, sceneIds)
  bulkAddScenes(projectId, fullScript)

  // Preview
  generatePreview(projectId)

  // TTS
  getTTSVoices()
}
```

---

## 🔌 API Endpoints

### Projects Endpoints (`/api/projects`)

| Method | Endpoint | Purpose | Request Body | Response |
|--------|----------|---------|--------------|----------|
| GET | `/api/projects` | List all projects | - | `[{id, name, ...}]` |
| POST | `/api/projects` | Create project | `{name}` | `{id, name, ...}` |
| GET | `/api/projects/:id` | Get project + scenes | - | `{project, scenes}` |
| PATCH | `/api/projects/:id` | Update project | `{tts_voice, target_language, ai_image_model, ...}` | `{id, name, ...}` |
| POST | `/api/projects/:id/preview` | Generate preview | - | `{preview_path, video_url, scene_count, total_duration}` |
| POST | `/api/projects/:id/export` | Export 1080p video | `{resolution}` | `{video_path, scene_count, total_duration}` |
| GET | `/api/projects/:id/download` | Download video | `?resolution=1080p` | Binary MP4 file |
| POST | `/api/projects/:id/scenes` | Add scene | `{script, duration, background_type, background_value}` | `{id, script, ...}` |
| POST | `/api/projects/:id/scenes/bulk` | Auto-create scenes | `{full_script}` | `[{id, script, ...}]` |
| POST | `/api/projects/:id/scenes/reorder` | Reorder scenes | `{scene_ids: [1,3,2]}` | `{success: true}` |

### Scenes Endpoints (`/api/scenes`)

| Method | Endpoint | Purpose | Request Body | Response |
|--------|----------|---------|--------------|----------|
| PUT | `/api/scenes/:id` | Update scene | `{script, duration, background_value, effects, ...}` | `{id, script, ...}` |
| DELETE | `/api/scenes/:id` | Delete scene | - | `{success: true}` |
| POST | `/api/scenes/:id/regenerate-image` | Regenerate AI image | - | `{image_url}` |

### TTS Endpoints (`/api/tts`)

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| GET | `/api/tts/voices` | Get all TTS voices | `{edge: [...], openai: [...], elevenlabs: [...]}` |
| GET | `/api/tts/openai/voices` | Get OpenAI voices | `[{id, name}]` |
| GET | `/api/tts/elevenlabs/voices` | Get ElevenLabs voices | `[{id, name}]` |

### Upload Endpoints (`/api/uploads`)

| Method | Endpoint | Purpose | Request Body | Response |
|--------|----------|---------|--------------|----------|
| POST | `/api/uploads/audio` | Upload sound effect | `multipart/form-data` | `{file_path}` |
| POST | `/api/uploads/music` | Upload background music | `multipart/form-data` | `{file_path}` |

### Script Endpoints (`/api/scripts`)

| Method | Endpoint | Purpose | Request Body | Response |
|--------|----------|---------|--------------|----------|
| POST | `/api/scripts/improve` | AI script improvement | `{script}` | `{improved_script}` |

### Thumbnail Endpoints (`/api/thumbnails`)

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| GET | `/api/thumbnails/:keyword` | Get AI image thumbnail | Binary JPEG file |

---

## 🗄️ Database Schema

### SQLite Location
```
backend/database/editor_projects.db
```

### Projects Table

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    tts_voice TEXT DEFAULT 'de-DE-KatjaNeural',
    target_language TEXT DEFAULT 'auto',
    background_music_path TEXT,
    background_music_volume INTEGER DEFAULT 7,
    video_speed REAL DEFAULT 1.0,
    ai_image_model TEXT DEFAULT 'flux-schnell',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id` - Auto-increment primary key
- `name` - Project name (user-defined)
- `tts_voice` - TTS voice ID (e.g., "de-DE-KatjaNeural", "alloy")
- `target_language` - Translation target (e.g., "en", "de", "auto")
- `background_music_path` - Path to uploaded music file
- `background_music_volume` - Volume percentage (0-100, default 7)
- `video_speed` - Playback speed multiplier (0.5-2.0, default 1.0)
- `ai_image_model` - AI model for images (default "flux-schnell")
- `created_at` - Project creation timestamp
- `updated_at` - Last update timestamp

### Scenes Table

```sql
CREATE TABLE scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    scene_order INTEGER NOT NULL,
    script TEXT NOT NULL,
    duration REAL DEFAULT 5.0,
    background_type TEXT DEFAULT 'solid',
    background_value TEXT,
    audio_path TEXT,

    -- Visual Effects
    effect_zoom TEXT DEFAULT 'none',
    effect_pan TEXT DEFAULT 'none',
    effect_rotate TEXT DEFAULT 'none',
    effect_fade TEXT DEFAULT 'none',
    effect_vignette TEXT DEFAULT 'none',
    effect_saturation REAL DEFAULT 1.0,
    effect_film_grain INTEGER DEFAULT 0,
    effect_glitch INTEGER DEFAULT 0,

    -- Sound Effects
    sound_effect_path TEXT,
    sound_effect_volume INTEGER DEFAULT 50,
    sound_effect_offset INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

**Fields:**
- `id` - Auto-increment primary key
- `project_id` - Foreign key to projects table
- `scene_order` - Display order (1-based index)
- `script` - Scene narration text
- `duration` - Scene duration in seconds (auto-calculated from TTS)
- `background_type` - "solid" (color) or "keyword" (AI image)
- `background_value` - Color hex (#RRGGBB) or AI keyword
- `audio_path` - Path to generated TTS audio file
- **Visual Effects:**
  - `effect_zoom` - "none", "in", "out"
  - `effect_pan` - "none", "left", "right", "up", "down"
  - `effect_rotate` - "none", "clockwise", "counterclockwise"
  - `effect_fade` - "none", "in", "out", "inout"
  - `effect_vignette` - "none", "light", "heavy"
  - `effect_saturation` - 0.0 (grayscale) to 2.0 (vibrant)
  - `effect_film_grain` - 0 (none) to 100 (heavy)
  - `effect_glitch` - 0 (none) to 100 (heavy)
- **Sound Effects:**
  - `sound_effect_path` - Path to uploaded sound effect file
  - `sound_effect_volume` - Volume percentage (0-100)
  - `sound_effect_offset` - Start offset in milliseconds

---

## 📁 File Paths & Directories

### Backend Directories

| Path | Purpose | Auto-Created? |
|------|---------|---------------|
| `backend/database/` | SQLite database file | ✅ Yes |
| `backend/previews/` | Generated video files | ✅ Yes |
| `backend/uploads/audio/` | User-uploaded sound effects | ✅ Yes |
| `backend/uploads/music/` | User-uploaded background music | ✅ Yes |
| `backend/venv/` | Python virtual environment | ⚠️ Manual |
| `backend/.env` | Environment variables (API keys) | ⚠️ Manual |

### External Directories (Dropbox)

| Path | Purpose | Auto-Created? |
|------|---------|---------------|
| `~/Dropbox/Apps/output Horoskop/video_editor_prototype/image_cache/` | AI-generated image cache | ✅ Yes |
| `~/Dropbox/Apps/output Horoskop/video_editor_prototype/previews/` | Video output (unified) | ✅ Yes |

### Temp Directories

| Path | Purpose | Lifetime |
|------|---------|----------|
| `/var/folders/.../video_editor_simple/` | FFmpeg temp files | Per-render (auto-cleaned) |

### File Naming Conventions

**Preview Videos:**
```
video_{project_id}_preview.mp4          # 540p preview
video_{project_id}_1080p.mp4            # 1080p export
```

**TTS Audio:**
```
audio_{scene_id}.mp3                    # Generated TTS audio
```

**AI Images:**
```
{md5_hash}.jpg                          # MD5(keyword + model + dimensions)
```

**Uploaded Files:**
```
uploads/audio/{timestamp}_{filename}    # Sound effects
uploads/music/{timestamp}_{filename}    # Background music
```

---

## 🔄 Data Flow

### Preview Generation Flow

```
User clicks "Preview" Button
    ↓
Frontend: Header.jsx → handleGeneratePreview()
    ↓
API Call: POST /api/projects/{id}/preview
    ↓
Backend: projects.py → generate_preview()
    ↓
    ├─→ Get project settings (voice, language, model, music)
    ├─→ Get all scenes from database
    ├─→ PreviewGenerator.generate_preview()
    │       ├─→ Translate scripts (if target_language != 'auto')
    │       ├─→ SimpleVideoGenerator.generate_video()
    │       │       ├─→ For each scene:
    │       │       │   ├─→ TTS generation (Edge/OpenAI/ElevenLabs)
    │       │       │   ├─→ AI image generation (Replicate API)
    │       │       │   ├─→ FFmpeg: Combine image + audio + effects
    │       │       │   └─→ Output: scene_0.mp4, scene_1.mp4, ...
    │       │       ├─→ FFmpeg: Concatenate all scenes
    │       │       ├─→ FFmpeg: Add background music (if provided)
    │       │       └─→ Return: video_path + scene_timings
    │       └─→ Return: preview_path, video_url, scene_count, total_duration
    ├─→ Update scene durations in database (actual TTS duration)
    └─→ Return: {preview_path, video_url, updated_scenes, scene_timings}
    ↓
Frontend: Update scenes state with actual durations
    ↓
Frontend: Update VideoPreview component with new video_url
    ↓
User sees generated video
```

### Export Flow (1080p)

```
User clicks "Export" Button
    ↓
Frontend: Confirmation dialog
    ↓
API Call: POST /api/projects/{id}/export {resolution: "1080p"}
    ↓
Backend: projects.py → export_video()
    ↓
    ├─→ Get project + scenes
    ├─→ PreviewGenerator.generate_preview(..., resolution='1080p')
    │       └─→ Same flow as preview, but 1080p resolution
    └─→ Return: {video_path, scene_count, total_duration}
    ↓
Frontend: Trigger browser download
    ↓
Browser: GET /api/projects/{id}/download?resolution=1080p
    ↓
Backend: download_video()
    ├─→ Find video file: previews/video_{id}_1080p.mp4
    └─→ send_file(as_attachment=True, download_name="{project_name}_1080p.mp4")
    ↓
Browser: "Save As" dialog
    ↓
User selects download location
```

### Bulk Scene Creation Flow

```
User enters full script in ScriptEditor
    ↓
User clicks "Create Scenes from Script"
    ↓
Frontend: API Call POST /api/projects/{id}/scenes/bulk {full_script}
    ↓
Backend: projects.py → bulk_add_scenes()
    ↓
    ├─→ Translate full script (if target_language != 'auto')
    ├─→ KeywordExtractor.extract_visual_scenes(script)
    │       ├─→ GPT-4o-mini: Split script into sentences
    │       ├─→ For each sentence:
    │       │   ├─→ Extract visual keyword (3 attempts with different temps)
    │       │   └─→ Select best keyword (shortest, most specific)
    │       └─→ Return: [{script, visual_search, scene_type}]
    ├─→ For each visual scene:
    │   ├─→ Create scene_data object
    │   ├─→ db.add_scene(project_id, scene_data)
    │   └─→ Append to created_scenes list
    └─→ Return: created_scenes
    ↓
Frontend: Reload project → Display scenes in Timeline
    ↓
Backend: Generate AI image thumbnails for each keyword
    ↓
Frontend: Display thumbnails in SceneCards
```

### AI Image Generation Flow

```
Scene needs AI image (background_type='keyword')
    ↓
ReplicateImageService.generate_image(keyword, model, width, height)
    ↓
    ├─→ Calculate cache key: MD5(keyword + model + width + height)
    ├─→ Check image cache: ~/Dropbox/.../image_cache/{hash}.jpg
    │       └─→ If exists: Return cached path
    ├─→ If not cached:
    │   ├─→ Build Replicate API request based on model:
    │   │   ├─→ Flux models: {prompt, aspect_ratio, output_format, ...}
    │   │   ├─→ Ideogram V3: {prompt, aspect_ratio, magic_prompt_option, ...}
    │   │   ├─→ Recraft V3: {prompt, size, style, ...}
    │   │   └─→ SDXL: {prompt, width, height, ...}
    │   ├─→ replicate.run(model_version, input_params)
    │   ├─→ Download generated image
    │   ├─→ Save to cache: {hash}.jpg
    │   └─→ Return: cached path
    └─→ Return: image_path
```

### TTS Generation Flow

```
Scene needs TTS audio (script text)
    ↓
TTSService.generate_tts(text, voice)
    ↓
    ├─→ Detect voice type from voice ID:
    │   ├─→ Edge TTS: voice starts with language code (e.g., "de-DE-")
    │   ├─→ OpenAI TTS: voice in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    │   └─→ ElevenLabs: voice is custom ID
    │
    ├─→ Edge TTS:
    │   ├─→ edge_tts.Communicate(text, voice)
    │   ├─→ Save to temp file: audio_{scene_id}.mp3
    │   └─→ Return: audio_path
    │
    ├─→ OpenAI TTS:
    │   ├─→ openai.audio.speech.create(model="tts-1", voice=voice, input=text)
    │   ├─→ Save to temp file: audio_{scene_id}.mp3
    │   └─→ Return: audio_path
    │
    └─→ ElevenLabs:
        ├─→ elevenlabs.generate(text, voice_id)
        ├─→ Save to temp file: audio_{scene_id}.mp3
        └─→ Return: audio_path
```

---

## ⚙️ Service Layer Details

### ReplicateImageService (`services/replicate_image_service.py`)

**Purpose:** AI Image Generation with 7 models

**Supported Models:**

| Model ID | Cost/Image | Model String | Special Features |
|----------|-----------|--------------|------------------|
| `flux-schnell` | $0.003 | `black-forest-labs/flux-schnell` | Fast & cheap (DEFAULT) |
| `flux-dev` | $0.025 | `black-forest-labs/flux-dev` | Balanced quality |
| `flux-pro` | $0.055 | `black-forest-labs/flux-pro` | High quality |
| `flux-pro-1.1` | $0.04 | `black-forest-labs/flux-1.1-pro` | Latest Flux version |
| `ideogram-v3` | $0.09 | `ideogram-ai/ideogram-v2-turbo` | Text in images |
| `recraft-v3` | $0.04 | `recraft-ai/recraft-v3` | Style variety |
| `sdxl` | $0.003 | `stability-ai/sdxl` | Cheap alternative |

**Key Methods:**
```python
def generate_image(keyword, width=608, height=1080, model='flux-schnell')
    # Returns: image_path (cached)
```

**Cache Strategy:**
- Cache key: `MD5(keyword + model + width + height)`
- Cache location: `~/Dropbox/Apps/output Horoskop/video_editor_prototype/image_cache/`
- Cache hit = $0 cost, instant response

### SimpleVideoGenerator (`services/simple_video_generator.py`)

**Purpose:** FFmpeg Video Composition

**Key Methods:**
```python
def generate_video(scenes, project_id, resolution='preview',
                   background_music_path=None, background_music_volume=7,
                   video_speed=1.0, ai_image_model='flux-schnell')
    # Returns: (video_path, scene_timings)
```

**Resolution Modes:**

| Mode | Resolution | Use Case | Output Filename |
|------|-----------|----------|-----------------|
| `preview` | 608x1080 (540p) | Fast preview | `video_{id}_preview.mp4` |
| `1080p` | 1080x1920 (1080p) | Final export | `video_{id}_1080p.mp4` |

**Processing Steps:**

1. **Scene Video Generation:**
   - Generate TTS audio for script
   - Generate/load AI image for background
   - Apply visual effects (zoom, pan, rotate, vignette, etc.)
   - Combine image + audio with FFmpeg
   - Add sound effects (if provided)

2. **Video Concatenation:**
   - Create concat.txt file listing all scene videos
   - FFmpeg: Concatenate scenes sequentially
   - Apply video speed adjustment (if != 1.0)

3. **Background Music:**
   - Loop background music to match video duration
   - Mix music at specified volume (default 7%)
   - Combine with main video audio

4. **Output:**
   - Final video: `previews/video_{project_id}_{resolution}.mp4`
   - Scene timings: `[{id, duration, db_duration}]`

### PreviewGenerator (`services/preview_generator.py`)

**Purpose:** Preview Orchestration

**Key Methods:**
```python
def generate_preview(project_id, scenes, tts_voice='de-DE-KatjaNeural',
                    background_music_path=None, background_music_volume=7,
                    target_language='auto', video_speed=1.0,
                    ai_image_model='flux-schnell', resolution='preview')
    # Returns: {preview_path, video_url, scene_count, total_duration, scene_timings}
```

**Translation Flow:**
- If `target_language != 'auto'`:
  - Translate all scene scripts to target language
  - Use translated scripts for TTS generation
  - Keep original scripts in database unchanged

**Fallback Strategy:**
- If video generation fails: Return JSON manifest with error
- Allows frontend to display error gracefully

### KeywordExtractor (`services/keyword_extractor.py`)

**Purpose:** Visual Keyword Extraction with GPT-4o-mini

**Key Methods:**
```python
def extract_visual_scenes(full_script)
    # Returns: [{script, visual_search, scene_type}]
```

**Extraction Strategy:**

1. **Sentence Splitting:**
   - Split script by sentence boundaries (., !, ?, etc.)
   - Merge very short fragments (< 3 words) with previous sentence

2. **Keyword Extraction (per sentence):**
   - Generate 3 keyword variations with different temperatures (0.3, 0.7, 1.0)
   - Select best keyword (shortest + most specific)
   - Store as `visual_search` field

3. **Scene Creation:**
   - Each sentence → 1 scene
   - Script = original sentence
   - Visual = extracted keyword
   - Duration = auto-calculated from word count

**Example:**
```
Input: "Ein Vogel baut sein Nest. Die Sonne geht unter. Das Leben findet einen Weg."

Output:
[
  {script: "Ein Vogel baut sein Nest.", visual_search: "Vogel baut Nest im Baum"},
  {script: "Die Sonne geht unter.", visual_search: "Sonnenuntergang orange Himmel"},
  {script: "Das Leben findet einen Weg.", visual_search: "Pflanze wächst durch Riss im Beton"}
]
```

### TranslationService (`services/translation_service.py`)

**Purpose:** Multi-language Translation (13 languages)

**Supported Languages:**

| Code | Language | Example Voice |
|------|----------|---------------|
| `de` | Deutsch | de-DE-KatjaNeural |
| `en` | English | en-US-AriaNeural |
| `es` | Español | es-ES-ElviraNeural |
| `fr` | Français | fr-FR-DeniseNeural |
| `it` | Italiano | it-IT-ElsaNeural |
| `pt` | Português | pt-PT-RaquelNeural |
| `pl` | Polski | pl-PL-ZofiaNeural |
| `nl` | Nederlands | nl-NL-ColetteNeural |
| `tr` | Türkçe | tr-TR-EmelNeural |
| `ru` | Русский | ru-RU-SvetlanaNeural |
| `ja` | 日本語 | ja-JP-NanamiNeural |
| `zh` | 中文 | zh-CN-XiaoxiaoNeural |
| `auto` | No Translation | (original language) |

**Key Methods:**
```python
def translate(text, target_language)
    # Returns: translated_text
```

**Translation Provider:** OpenAI GPT-4o-mini

---

## 🔐 Configuration

### Environment Variables (`.env`)

```bash
# Replicate API (REQUIRED for AI images)
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI API (REQUIRED for TTS + keyword extraction)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ElevenLabs API (OPTIONAL for premium TTS)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

### Default Settings

**Project Defaults:**
```python
DEFAULT_TTS_VOICE = 'de-DE-KatjaNeural'  # Edge TTS German
DEFAULT_AI_MODEL = 'flux-schnell'         # Fast & cheap
DEFAULT_LANGUAGE = 'auto'                 # No translation
DEFAULT_MUSIC_VOLUME = 7                  # 7% background music
DEFAULT_VIDEO_SPEED = 1.0                 # Normal speed
```

**Scene Defaults:**
```python
DEFAULT_DURATION = 5.0                    # 5 seconds
DEFAULT_BACKGROUND_TYPE = 'solid'         # Solid color
DEFAULT_BACKGROUND_VALUE = '#000000'      # Black
DEFAULT_EFFECT_ZOOM = 'none'
DEFAULT_EFFECT_PAN = 'none'
DEFAULT_EFFECT_ROTATE = 'none'
DEFAULT_EFFECT_FADE = 'none'
DEFAULT_EFFECT_VIGNETTE = 'none'
DEFAULT_EFFECT_SATURATION = 1.0           # Normal saturation
DEFAULT_EFFECT_FILM_GRAIN = 0             # No grain
DEFAULT_EFFECT_GLITCH = 0                 # No glitch
```

### FFmpeg Configuration

**Video Encoding:**
```bash
-c:v libx264        # H.264 codec
-pix_fmt yuv420p    # Pixel format (compatibility)
-preset fast        # Encoding speed
```

**Audio Encoding:**
```bash
-c:a aac            # AAC codec
-b:a 192k           # 192 kbps bitrate
-ar 44100           # 44.1 kHz sample rate
-ac 2               # Stereo (2 channels)
```

**Frame Rate:**
```bash
-framerate 30       # 30 FPS
```

---

## 🚀 Deployment

### Local Development

**Start System:**
```bash
bash start_all.command
```

**What happens:**
1. Clear Python cache (`__pycache__`)
2. Start Backend (Flask on port 5001)
3. Start Frontend (Vite on port 3000)
4. Open browser at http://localhost:3000

**Stop System:**
```bash
bash stop_all.command
```

**What happens:**
1. Kill all Python processes
2. Kill all Node/Vite processes
3. Free ports 3000 and 5001
4. Clear Python cache

### Production Deployment (Future)

**Requirements:**
- Ubuntu 22.04 LTS or later
- 16GB RAM minimum
- 50GB+ SSD storage
- FFmpeg installed
- Python 3.9+
- Node.js 18+

**Setup Steps:**

1. **Install Dependencies:**
```bash
sudo apt update
sudo apt install -y python3.9 python3-pip ffmpeg nodejs npm
```

2. **Clone Repository:**
```bash
git clone <repository-url>
cd video_editor_prototype
```

3. **Backend Setup:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup .env
cp .env.example .env
nano .env  # Add production API keys
```

4. **Frontend Build:**
```bash
cd frontend
npm install
npm run build
```

5. **Run with PM2:**
```bash
npm install -g pm2

# Start backend
pm2 start backend/app.py --name video-editor-backend

# Serve frontend build
pm2 serve frontend/dist 3000 --name video-editor-frontend

# Save PM2 config
pm2 save
pm2 startup
```

6. **Nginx Reverse Proxy (Optional):**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:5001;
    }
}
```

---

## 📊 Performance Optimization

### Image Cache Management

**Cache Location:**
```
~/Dropbox/Apps/output Horoskop/video_editor_prototype/image_cache/
```

**Cache Strategy:**
- Cache key: MD5(keyword + model + dimensions)
- Cache hit = $0 cost + instant response
- Cache miss = API call + $0.003-$0.09 cost

**Check Cache Size:**
```bash
du -sh ~/Dropbox/Apps/output\ Horoskop/video_editor_prototype/image_cache/
```

**Clear Cache (if > 1GB):**
```bash
rm -rf ~/Dropbox/Apps/output\ Horoskop/video_editor_prototype/image_cache/*
```

**Impact:** Next preview will regenerate all images (costs $$)

### Video Rendering Performance

**Tips:**
1. Use **Flux Schnell** (13x cheaper than Flux Pro 1.1)
2. Keep scene count **under 50 scenes/project**
3. Use **preview mode** (540p) before exporting 1080p
4. Close other CPU-intensive apps during rendering

**FFmpeg Hardware Acceleration:**
```bash
# Check available hardware acceleration
ffmpeg -hwaccels
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Edge TTS 403 Error**
```bash
pip install --upgrade edge-tts  # Must be >= 7.2.3
pip show edge-tts  # Verify version
```

**2. FFmpeg Not Found**
```bash
brew install ffmpeg      # macOS
sudo apt install ffmpeg  # Ubuntu
ffmpeg -version          # Verify
```

**3. Port Already in Use**
```bash
bash stop_all.command
sleep 5
bash start_all.command
```

**4. Database Corrupted**
```bash
cd backend
cp database/editor_projects.db database/editor_projects.db.backup
rm database/editor_projects.db

python << 'EOF'
from database.db_manager import DatabaseManager
db = DatabaseManager()
db.init_db()
print("✅ Database recreated!")
EOF
```

**5. API Key Errors**
- Check `.env` file has correct keys
- Verify keys at provider websites
- Restart backend after updating `.env`

---

## 📞 Support Resources

**Documentation:**
- **README.md** - Quick overview
- **INSTALLATION.md** - Setup guide
- **HANDBUCH.md** - User manual (German)
- **AI_MODEL_INTEGRATION.md** - AI model integration
- **SYSTEM_ARCHITECTURE.md** - This file

**Logs:**
- Backend: `logs/backend.log`
- Frontend: `logs/frontend.log`

**API Documentation:**
- Replicate: https://replicate.com/docs
- OpenAI: https://platform.openai.com/docs
- ElevenLabs: https://elevenlabs.io/docs

---

**Version:** 1.0.0
**Status:** ✅ Production Ready
**Last Updated:** 2025-01-24

Made with ❤️ for the Video Editor Prototype
