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

### Step 2: Clone/Download Project

```bash
cd ~/Dropbox/Social\ Media/Video\ Editor\ Prototype/
# Project should be in: video_editor_prototype/
```

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
cd video_editor_prototype

# Start both backend and frontend
bash start_all.command
```

**What happens:**
1. Python cache is cleared
2. Backend starts on port 5001
3. Frontend starts on port 3000
4. Browser opens automatically at http://localhost:3000

**Logs:**
- Backend: `logs/backend.log`
- Frontend: `logs/frontend.log`

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
cd video_editor_prototype
bash stop_all.command
```

**What happens:**
1. All Python processes killed
2. All Node/Vite processes killed
3. Ports 3000 and 5001 freed
4. Python cache cleared

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
│   └── frontend.log                 # Frontend Logs
│
├── start_all.command                # Start Script (macOS)
├── stop_all.command                 # Stop Script (macOS)
├── HANDBUCH.md                      # User Manual (German)
├── AI_MODEL_INTEGRATION.md          # Developer Docs (AI Models)
└── INSTALLATION.md                  # This File

```

---

## 🔑 Key Technologies

### Backend Stack
- **Flask 3.0.3** - Python web framework
- **SQLite** - Lightweight database
- **Replicate API** - AI image generation (Flux, Ideogram, Recraft, SDXL)
- **OpenAI API** - TTS + GPT-4o-mini for keyword extraction
- **Edge TTS 7.2.3** - Free Microsoft TTS (fixed 403 error!)
- **ElevenLabs** - Premium TTS (optional)
- **MoviePy 1.0.3** - Python video editing library
- **FFmpeg 8.0** - Video/audio processing

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

## 🚀 Deployment (Future)

### Server Requirements

- **OS:** Ubuntu 22.04 LTS or later
- **RAM:** 16GB minimum
- **Storage:** 50GB+ SSD
- **Network:** Stable internet for API calls

### Production Setup

```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3.9 python3-pip ffmpeg nodejs npm

# Clone repository
git clone <repository-url>
cd video_editor_prototype

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
nano .env  # Add production API keys

# Frontend build
cd ../frontend
npm install
npm run build

# Run with PM2 (process manager)
npm install -g pm2
pm2 start backend/app.py --name video-editor-backend
pm2 start frontend --name video-editor-frontend
pm2 save
pm2 startup
```

---

## 📞 Support

### Documentation
- **User Manual:** `HANDBUCH.md`
- **AI Models:** `AI_MODEL_INTEGRATION.md`
- **Installation:** This file

### Logs
- Backend: `logs/backend.log`
- Frontend: `logs/frontend.log`

### Common Issues
- FFmpeg errors → Check FFmpeg installation
- API errors → Check `.env` file and API keys
- Performance → Clear cache, reduce scene count

---

**Version:** 1.0
**Last Updated:** 2025-01-24
**Author:** Video Editor Prototype Team
