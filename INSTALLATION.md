# 🚀 Video Editor Prototype - Installation Guide

## System Requirements

### Hardware
- **CPU:** Multi-core processor (4+ cores recommended)
- **RAM:** Minimum 8GB (16GB+ recommended for video processing)
- **Storage:** 10GB+ free space (for video cache and dependencies)
- **GPU:** Optional (speeds up video rendering with FFmpeg)

### Software Prerequisites
- **macOS:** 10.15+ (Catalina or later)
- **Homebrew:** Package manager for macOS
- **Node.js:** v18.x or later
- **Python:** 3.9.x or later
- **FFmpeg:** 8.0 or later (for video processing)

---

## 🔧 Quick Start Installation

### Step 1: Install System Dependencies

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg (CRITICAL for video generation)
brew install ffmpeg

# Install Node.js (if not installed)
brew install node

# Install Python 3.9 (if not installed)
brew install python@3.9

# Verify installations
ffmpeg -version
node --version
python3 --version
```

**Expected Output:**
```
ffmpeg version 8.0 ...
v18.x.x
Python 3.9.x
```

---

### Step 2: Navigate to Project

```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype/
```

**Note:** Project location updated to use macOS CloudStorage path (2025-10-27)

---

### Step 3: Backend Setup

```bash
cd video_editor_prototype/backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all Python dependencies
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed Flask-3.0.3 Flask-CORS-4.0.1 python-dotenv-1.0.1
replicate-0.25.1 edge-tts-7.2.3 openai-2.6.0 elevenlabs-0.2.26
moviepy-1.0.3 requests-2.31.0 Pillow-10.2.0 ...
```

---

### Step 4: Environment Variables Setup

Create `.env` file in `backend/` directory:

```bash
cd backend
nano .env
```

**Required Environment Variables:**
```env
# Replicate API (REQUIRED for AI image generation)
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI API (REQUIRED for TTS and keyword extraction)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ElevenLabs API (OPTIONAL - for premium TTS)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Dropbox API (REQUIRED for Railway cloud deployment)
DROPBOX_ACCESS_TOKEN=your_dropbox_access_token
DROPBOX_REFRESH_TOKEN=your_dropbox_refresh_token
DROPBOX_APP_KEY=your_dropbox_app_key
DROPBOX_APP_SECRET=your_dropbox_app_secret
```

**How to get API Keys:**

1. **Replicate API:**
   - Go to https://replicate.com
   - Sign up / Login
   - Go to Account → API Tokens
   - Copy your token

2. **OpenAI API:**
   - Go to https://platform.openai.com
   - Sign up / Login
   - Go to API Keys → Create new key
   - Copy your key

3. **ElevenLabs (Optional):**
   - Go to https://elevenlabs.io
   - Sign up / Login
   - Go to Profile → API Keys
   - Copy your key

4. **Dropbox API (Required for Railway):**
   - Go to https://www.dropbox.com/developers/apps
   - Create App → Scoped Access → Full Dropbox → Name your app
   - Go to Permissions tab → Enable: `files.content.write`, `files.content.read`
   - Go to Settings tab → Generate Access Token
   - Copy App Key, App Secret, Access Token
   - **Note:** For refresh token, see RAILWAY_DEPLOYMENT.md

**Save and close:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### Step 5: Initialize Database

```bash
cd backend
source venv/bin/activate

python << 'EOF'
from database.db_manager import DatabaseManager
db = DatabaseManager()
db.init_db()
print("✅ Database initialized successfully!")
EOF
```

**Expected Output:**
```
✅ Database initialized successfully!
```

**Database Location:** `backend/database/editor_projects.db`

---

### Step 6: Frontend Setup

```bash
cd ../frontend

# Install Node dependencies
npm install

# Expected packages:
# - react, react-dom
# - vite
# - tailwindcss
# - lucide-react (icons)
# - axios (HTTP client)
```

**Expected Output:**
```
added 500+ packages in 30s
```

---

### Step 7: Create Required Directories

```bash
cd ..

# Create all required directories
mkdir -p backend/replicate_cache
mkdir -p backend/output/viral_autonomous
mkdir -p backend/previews
mkdir -p backend/temp
mkdir -p logs

echo "✅ All directories created!"
```

---

## 🎬 Running the System

### Option 1: Using Start Scripts (Recommended)

```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype

# Start both backend and frontend
bash start_all.command
```

**What happens:**
1. Cleans up old processes
2. Python cache is cleared
3. Backend starts on port 5001
4. **Mac Sync Poller starts** (syncs Railway uploads every 30s)
5. Frontend starts on port 3000

**Logs:**
- Backend: `logs/backend.log`
- Frontend: `logs/frontend.log`
- **Mac Sync Poller:** `logs/mac_sync.log`

### Option 2: Manual Start (for debugging)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## 🛑 Stopping the System

```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype
bash stop_all.command
```

**What happens:**
1. All Python processes killed (backend + mac_sync_poller)
2. All Node/Vite processes killed (frontend)
3. Ports 3000 and 5001 freed

**Verify all stopped:**
```bash
lsof -ti:5001  # Should return nothing
lsof -ti:3000  # Should return nothing
pgrep -f "mac_sync_poller.py"  # Should return nothing
```

---

## 📦 System Architecture

```
video_editor_prototype/
│
├── backend/                          # Flask Backend (Python)
│   ├── api/                         # REST API Endpoints
│   │   ├── projects.py              # Project CRUD + Preview Generation
│   │   └── scenes.py                # Scene CRUD + Image Regeneration
│   │
│   ├── services/                    # Core Business Logic
│   │   ├── replicate_image_service.py   # AI Image Generation (7 models)
│   │   ├── simple_video_generator.py    # FFmpeg Video Composition
│   │   ├── preview_generator.py         # Preview Orchestration
│   │   ├── translation_service.py       # Multi-language Translation
│   │   └── keyword_extractor.py         # Visual Keyword Extraction (GPT-4o)
│   │
│   ├── database/                    # SQLite Database
│   │   ├── db_manager.py            # Database Manager
│   │   └── editor_projects.db       # SQLite Database File
│   │
│   ├── output/                      # Generated Videos (Temp)
│   │   └── viral_autonomous/        # Video Output Directory
│   │
│   ├── previews/                    # Preview Videos
│   ├── replicate_cache/             # Cached AI Images (saves $$)
│   ├── venv/                        # Python Virtual Environment
│   ├── app.py                       # Flask App Entry Point
│   ├── requirements.txt             # Python Dependencies
│   └── .env                         # Environment Variables (API Keys)
│
├── frontend/                        # React Frontend (Vite)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx           # Top Bar (Model/Voice/Language Selection)
│   │   │   ├── Timeline/
│   │   │   │   ├── Timeline.jsx     # Scene Timeline Manager
│   │   │   │   ├── SceneCard.jsx    # Individual Scene Card
│   │   │   │   └── EffectsPanel.jsx # Visual Effects Panel
│   │   │   ├── VideoPreview/
│   │   │   │   └── VideoPreview.jsx # Video Player
│   │   │   ├── ScriptEditor/
│   │   │   │   └── ScriptEditor.jsx # Bulk Script Input
│   │   │   └── BackgroundMusic/
│   │   │       └── MusicManager.jsx # Background Music Uploader
│   │   │
│   │   ├── hooks/
│   │   │   └── useProject.js        # Project State Management
│   │   │
│   │   ├── services/
│   │   │   └── api.js               # Axios API Client
│   │   │
│   │   └── App.jsx                  # Main App Component
│   │
│   ├── package.json                 # Node Dependencies
│   └── vite.config.js               # Vite Configuration
│
├── logs/                            # Application Logs
│   ├── backend.log                  # Backend Logs
│   ├── frontend.log                 # Frontend Logs
│   └── mac_sync.log                 # Mac Sync Poller Logs
│
├── mac_sync_poller.py               # Railway → Mac Auto-Sync (30s interval)
├── start_all.command                # Start Script (macOS)
├── stop_all.command                 # Stop Script (macOS)
├── system_health_check.sh           # System Health Check (28 checks)
├── HANDBUCH.md                      # User Manual (German)
├── AI_MODEL_INTEGRATION.md          # Developer Docs (AI Models)
├── RAILWAY_DEPLOYMENT.md            # Railway Cloud Deployment Guide
└── INSTALLATION.md                  # This File

```

---

## 🔑 Key Technologies

### Backend Stack
- **Flask 3.0.3** - Python web framework
- **SQLite** - Lightweight database (absolute path fix 2025-10-27)
- **Replicate API** - AI image generation (Flux, Ideogram, Recraft, SDXL)
- **OpenAI API** - TTS + GPT-4o-mini for keyword extraction
- **Edge TTS 7.2.3** - Free Microsoft TTS (fixed 403 error!)
- **ElevenLabs** - Premium TTS (optional)
- **MoviePy 1.0.3** - Python video editing library
- **FFmpeg 8.0** - Video/audio processing
- **Dropbox SDK 11.36.2** - Hybrid storage (local Mac + Railway cloud)

### Frontend Stack
- **React 18** - UI framework
- **Vite** - Build tool (fast HMR)
- **Tailwind CSS** - Utility-first CSS
- **Lucide React** - Icon library
- **Axios** - HTTP client

---

## 🎨 Supported AI Image Models

| Model | Cost/Image | Speed | Quality | Use Case |
|-------|-----------|-------|---------|----------|
| **Flux Schnell** | $0.003 | ⚡⚡⚡ | Good | **Default - Fast & Cheap** |
| Flux Dev | $0.025 | ⚡⚡ | Very Good | Balanced quality/cost |
| Flux Pro | $0.055 | ⚡ | Excellent | Premium quality |
| Flux Pro 1.1 | $0.04 | ⚡ | Excellent | Latest Flux version |
| Ideogram V3 | $0.09 | ⚡⚡ | Very Good | **Text in images!** |
| Recraft V3 | $0.04 | ⚡⚡ | Very Good | Style variety |
| SDXL | $0.003 | ⚡⚡⚡ | OK | Cheap alternative |

**Default:** Flux Schnell (13x cheaper than Flux Pro 1.1!)

---

## 🎙️ Supported TTS Services

| Service | Cost | Quality | Speed | Status |
|---------|------|---------|-------|--------|
| **Edge TTS** | FREE | Good | Fast | ✅ **Working (v7.2.3)** |
| OpenAI TTS | ~$0.015/1000 chars | Very Good | Fast | ✅ Recommended |
| ElevenLabs | ~$0.30/1000 chars | Excellent | Medium | ✅ Premium option |

**Default:** Edge TTS (kostenlos!)

**Available Voices:**
- German: Katja, Conrad, Amala
- English: Aria, Guy, Sonia
- OpenAI: alloy, echo, fable, onyx, nova, shimmer
- ElevenLabs: Custom voice IDs

---

## 🗄️ Database Schema

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
    ai_image_model TEXT DEFAULT 'flux-schnell',  -- NEW!
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Scenes Table
```sql
CREATE TABLE scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    scene_order INTEGER NOT NULL,
    script TEXT NOT NULL,
    duration REAL DEFAULT 5.0,
    background_type TEXT DEFAULT 'solid',
    background_value TEXT,  -- Keyword or color
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

---

## 🐛 Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

---

### FFmpeg not found

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**Solution:**
```bash
brew install ffmpeg
ffmpeg -version  # Verify installation
```

---

### Edge TTS 403 Error

**Error:** `WSServerHandshakeError: 403, message='Invalid response status'`

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install --upgrade edge-tts  # Must be >= 7.2.3
```

**Verify:**
```bash
pip show edge-tts
# Version: 7.2.3 or higher
```

---

### Replicate API Errors

**Error:** `Unauthorized: Invalid API token`

**Solution:**
1. Check `.env` file has correct `REPLICATE_API_TOKEN`
2. Verify token at https://replicate.com/account/api-tokens
3. Restart backend after updating `.env`

---

### Port already in use

**Error:** `Address already in use: 5001` or `3000`

**Solution:**
```bash
bash stop_all.command
# Wait 5 seconds
bash start_all.command
```

**Manual kill:**
```bash
lsof -ti:5001 | xargs kill -9  # Kill backend
lsof -ti:3000 | xargs kill -9  # Kill frontend
```

---

### Frontend not updating

**Solution:**
1. Clear browser cache (Cmd+Shift+R)
2. Restart Vite dev server
3. Delete `node_modules` and reinstall:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

### Database corrupted

**Solution:**
```bash
cd backend
# Backup old database
cp database/editor_projects.db database/editor_projects.db.backup

# Recreate database
rm database/editor_projects.db

# Initialize new database
python << 'EOF'
from database.db_manager import DatabaseManager
db = DatabaseManager()
db.init_db()
print("✅ Database recreated!")
EOF
```

---

## 📊 Performance Optimization

### Image Cache Management

The system caches AI-generated images to save costs. Cache location:
```
backend/replicate_cache/
```

**Cache size check:**
```bash
du -sh backend/replicate_cache
```

**Clear cache (if > 1GB):**
```bash
rm -rf backend/replicate_cache/*
```

**Impact:** Next preview will regenerate all images (costs $$)

---

### Video Rendering Performance

**Slow video generation?**

1. **Reduce scene count:** Keep projects under 50 scenes
2. **Use Flux Schnell:** Faster image generation
3. **Lower resolution:** Use 'preview' mode (540p) instead of '1080p'
4. **Close other apps:** FFmpeg is CPU-intensive

**FFmpeg optimization:**
```bash
# Check FFmpeg build supports hardware acceleration
ffmpeg -hwaccels
```

---

## 🔄 Updating the System

### Update Python Dependencies

```bash
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Update Node Dependencies

```bash
cd frontend
npm update
```

### Update System Tools

```bash
brew update
brew upgrade ffmpeg node python@3.9
```

---

## 🚀 Railway Cloud Deployment

**Status:** ✅ LIVE at https://video-editor.momentummind.de

### Hybrid Architecture

This system uses **HYBRID DEPLOYMENT**:

```
LOCAL MAC (Primary)              RAILWAY (Cloud Backup)
├─ Backend: localhost:5001       ├─ Backend: video-editor.momentummind.de
├─ Frontend: localhost:3000      │
├─ Direct Dropbox Access         ├─ Dropbox API Access
└─ Mac Sync Poller (30s)         └─ Writes to .sync_queue.json
       ↓                                    ↓
       └────── SHARED DROPBOX STORAGE ──────┘
               (Source of Truth)
```

### Why Hybrid?

1. **Mac** - Fast local Dropbox filesystem access
2. **Railway** - 24/7 cloud deployment for remote access
3. **Auto-Sync** - Mac Sync Poller syncs Railway uploads every 30s
4. **Shared Storage** - Both use same Dropbox folders

### Railway Deployment Guide

See **RAILWAY_DEPLOYMENT.md** for complete deployment instructions including:
- Railway project setup
- Environment variables configuration
- Dropbox API token refresh setup
- Monitoring and logs

### Health Monitoring

```bash
# Local system health (28 checks)
bash system_health_check.sh

# Railway deployment health
curl https://video-editor.momentummind.de/api/health
```

---

## 📞 Support

### Documentation
- **README:** Complete system overview
- **QUICKSTART:** 5-minute setup guide
- **SYSTEM_ARCHITECTURE:** Technical architecture
- **RAILWAY_DEPLOYMENT:** Cloud deployment guide
- **User Manual:** `HANDBUCH.md` (German)
- **AI Models:** `AI_MODEL_INTEGRATION.md`
- **Installation:** This file

### Logs
- Backend: `logs/backend.log`
- Frontend: `logs/frontend.log`
- Mac Sync Poller: `logs/mac_sync.log`

### Common Issues
- **Database errors** → FIXED with absolute paths (2025-10-27)
- **Mac Sync Poller not starting** → FIXED with venv rebuild (2025-10-27)
- FFmpeg errors → Check FFmpeg installation (`brew install ffmpeg`)
- API errors → Check `.env` file and API keys
- Performance → Clear cache, reduce scene count

### System Health Check

Run comprehensive health check (28 tests):
```bash
bash system_health_check.sh
```

Expected result: ✅ 28/28 (100%) HEALTHY

---

**Version:** 2.0.0
**Last Updated:** 2025-10-27
**System Health:** ✅ 100% (NULL BUG TOLERANCE ACHIEVED)
**Author:** Video Editor Prototype Team
