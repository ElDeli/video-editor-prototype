# 🎬 Video Editor Prototype

> AI-powered video creation tool with 7 AI image models, 3 TTS services, advanced visual effects, and hybrid Mac + Railway deployment.

[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)]()
[![Version](https://img.shields.io/badge/Version-2.0.0-blue)]()
[![Health](https://img.shields.io/badge/System%20Health-100%25-brightgreen)]()
[![License](https://img.shields.io/badge/License-Proprietary-red)]()

---

## ✨ Key Features

### 🎨 **7 AI Image Models**
- **Flux Schnell** ($0.003/img) - **DEFAULT** - Fast & cheap
- Flux Dev, Flux Pro, Flux Pro 1.1 - Premium quality
- **Ideogram V3** - Text in images capability!
- **Recraft V3** - Style variety
- SDXL - Budget alternative

### 🎙️ **3 TTS Services**
- ✅ **Edge TTS (v7.2.3+)** - FREE & Working!
- **OpenAI TTS** - alloy, echo, fable, nova, shimmer
- **ElevenLabs** - Premium voice quality

### 🎬 **Video Features**
- **Auto-Scene Creation** - AI keyword extraction with GPT-4o-mini
- **13 Languages** - Auto-translation support
- **Visual Effects** - Zoom, pan, rotate, vignette, glitch, film grain, etc.
- **Sound Effects** - Per-scene audio with volume & timing control
- **Background Music** - Looping music with adjustable volume
- **Variable Speed** - 0.5x to 2.0x playback speed

### 🔄 **Hybrid Deployment**
- **Local Mac** - Fast local Dropbox filesystem access
- **Railway Cloud** - 24/7 cloud deployment at https://video-editor.momentummind.de
- **Mac Sync Poller** - Automatic sync between Railway uploads and local Mac
- **Shared Dropbox Storage** - Unified storage for images and videos

---

## 📋 Quick Start

### Prerequisites
```bash
# Install system dependencies
brew install ffmpeg node python@3.9
```

### Installation
```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype

# Backend Setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env with API keys
cat > .env << EOF
REPLICATE_API_TOKEN=your_replicate_token
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
DROPBOX_ACCESS_TOKEN=your_dropbox_token
DROPBOX_REFRESH_TOKEN=your_refresh_token
DROPBOX_APP_KEY=your_app_key
DROPBOX_APP_SECRET=your_app_secret
EOF

# Frontend Setup
cd ../frontend
npm install
```

### Run Local System
```bash
# From project root
bash start_all.command
```

Open http://localhost:3000

### Stop System
```bash
bash stop_all.command
```

### Health Check
```bash
bash system_health_check.sh
```

**Expected Result:** ✅ 28/28 (100%) - HEALTHY

---

## 🏗️ System Architecture

### Hybrid Mac + Railway Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                    HYBRID ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  LOCAL MAC (Primary)              RAILWAY (Cloud Backup)    │
│  ├─ Backend: localhost:5001       ├─ Backend: video-editor. │
│  ├─ Frontend: localhost:3000      │   momentummind.de       │
│  ├─ Direct Dropbox Access         ├─ Dropbox API Access     │
│  └─ Mac Sync Poller (30s)         └─ Writes to .sync_queue │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │     SHARED DROPBOX STORAGE (Source of Truth)     │      │
│  ├──────────────────────────────────────────────────┤      │
│  │ CODE:   ~/Dropbox/Social Media/                  │      │
│  │         video_editor_prototype/                  │      │
│  │                                                   │      │
│  │ OUTPUT: ~/Dropbox/Apps/output Horoskop/          │      │
│  │         output/video_editor_prototype/           │      │
│  │         ├─ image_cache/ (AI images)              │      │
│  │         ├─ uploads/ (user files)                 │      │
│  │         └─ .sync_queue.json (sync notifications) │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Flask 3.0.3 - Python web framework
- SQLite - Database (absolute path fix applied)
- Replicate API - 7 AI image models
- OpenAI API - TTS + GPT-4o-mini keyword extraction
- Edge TTS 7.2.3 - Free TTS
- MoviePy 1.0.3 - Video editing
- FFmpeg 8.0 - Media processing
- Dropbox SDK 11.36.2 - Cloud storage API

**Frontend:**
- React 18 - UI framework
- Vite - Build tool
- Tailwind CSS - Styling
- Lucide React - Icons

---

## 📚 Complete Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| **README.md** | System overview (this file) | Everyone |
| **PROJECT_STATUS.md** | Complete system health & status | Developers/Operations |
| **QUICKSTART.md** | 5-minute setup guide | New users |
| **INSTALLATION.md** | Detailed installation guide | Developers |
| **SYSTEM_ARCHITECTURE.md** | Technical architecture docs | Developers |
| **RAILWAY_DEPLOYMENT.md** | Railway deployment guide | DevOps |
| **HANDBUCH.md** | User manual (German) | End users |
| **AI_MODEL_INTEGRATION.md** | AI model integration guide | Developers |

---

## 🎯 Recent Critical Fixes (2025-10-27)

### ✅ Database Path Fix (CRITICAL)
**Problem:** Backend couldn't access database - "unable to open database file"
**Root Cause:** Relative path `./database/editor_projects.db` failed when backend started from project root
**Solution:** Changed to absolute path using `os.path.dirname(os.path.abspath(__file__))`
**Status:** ✅ FIXED - 960 projects loading successfully

### ✅ Virtual Environment Rebuild (CRITICAL)
**Problem:** Mac Sync Poller couldn't start - dropbox module not found
**Root Cause:** venv had hardcoded old path before Dropbox migration
**Solution:** Rebuilt venv with correct path, reinstalled all dependencies
**Status:** ✅ FIXED - Mac Sync Poller running (PID: 25287)

### ✅ Dropbox Storage Path Fix
**Problem:** Incorrect path `~/Dropbox/Apps/...` vs `~/Library/CloudStorage/Dropbox/Apps/...`
**Solution:** Updated `dropbox_storage.py` with correct macOS CloudStorage path
**Status:** ✅ FIXED - 1088 cached images accessible

### ✅ Directory Structure Cleanup
**Problem:** Triple directory structure with duplicate paths
**Solution:** Cleaned up to 2 directories (CODE + OUTPUT)
**Status:** ✅ FIXED - One source of truth

### ✅ System Health Check
**Created:** Comprehensive `system_health_check.sh` script
**Tests:** 28 critical system components
**Result:** ✅ 100% HEALTHY (28/28 passed, 0 warnings, 0 errors)

---

## 💰 Cost Examples

### Budget Project (20 scenes, 3min)
```
AI Images:  20 × $0.003 (Flux Schnell) = $0.06
TTS:        Edge TTS (FREE)             = $0.00
────────────────────────────────────────────────
Total:                                   $0.06
```

### Premium Project (20 scenes, 3min)
```
AI Images:  20 × $0.04 (Flux Pro 1.1)   = $0.80
TTS:        OpenAI TTS                  = $0.05
────────────────────────────────────────────────
Total:                                   $0.85
```

**💡 Tip:** Use Flux Schnell + Edge TTS for lowest costs!

---

## 🛠️ System Components

### Core Services
- ✅ Backend API (Flask) - localhost:5001
- ✅ Frontend (React) - localhost:3000
- ✅ Railway Deployment - https://video-editor.momentummind.de
- ✅ Mac Sync Poller - Auto-sync Railway uploads (30s interval)
- ✅ SQLite Database - 960 projects, 4 tables
- ✅ Dropbox Storage - 1088 cached images

### Health Monitoring
Run comprehensive health check:
```bash
bash system_health_check.sh
```

**Monitors:**
1. ✅ Local Backend (Port 5001)
2. ✅ Local Frontend (Port 3000)
3. ✅ Railway Deployment
4. ✅ Git Repository
5. ✅ Dropbox Storage
6. ✅ Mac Sync Poller
7. ✅ Directory Structure
8. ✅ Critical Files

---

## 🎯 Usage Example

### 1. Create Project
```bash
curl -X POST http://localhost:5001/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "My Awesome Video"}'
```

### 2. Auto-Create Scenes with AI Keyword Extraction
```bash
curl -X POST http://localhost:5001/api/projects/1/scenes/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "full_script": "A majestic horse stands in a golden field. The sun sets behind mountains. Eagles soar through the sky."
  }'
```

**Result:** 3 scenes created with AI-extracted visual keywords!

### 3. Generate Preview
```bash
curl -X POST http://localhost:5001/api/projects/1/preview
```

**Output:** `previews/video_1_preview.mp4`

---

## 📊 Performance Tips

1. **Use Flux Schnell** - 13x cheaper than Flux Pro 1.1
2. **Enable Image Caching** - Reuse AI-generated images (1088 cached)
3. **Limit Scene Count** - Keep under 50 scenes/project
4. **Use Preview Mode** - Test with 540p before 1080p export
5. **Mac Sync Poller** - Automatic sync every 30 seconds

---

## 🐛 Common Issues & Solutions

### Edge TTS 403 Error
```bash
cd backend
source venv/bin/activate
pip install --upgrade edge-tts  # Must be >= 7.2.3
```

### FFmpeg Not Found
```bash
brew install ffmpeg
ffmpeg -version  # Verify
```

### Port Already in Use
```bash
bash stop_all.command
sleep 5
bash start_all.command
```

### Database Issues
```bash
# Already fixed with absolute path!
# Database now works from any working directory
```

### Mac Sync Poller Not Running
```bash
# Check if running
pgrep -f "mac_sync_poller.py"

# Restart
bash stop_all.command
bash start_all.command
```

### Check System Health
```bash
bash system_health_check.sh
# Expected: 28/28 (100%) HEALTHY
```

---

## 📂 Project Structure

```
video_editor_prototype/
├── backend/                    # Flask API
│   ├── api/                   # REST endpoints
│   ├── services/              # Business logic
│   │   ├── dropbox_storage.py # Hybrid storage manager
│   │   ├── replicate_image_service.py # 7 AI models
│   │   └── preview_generator.py # Video generation
│   ├── database/              # SQLite DB (absolute path)
│   │   └── editor_projects.db # 960 projects, 4 tables
│   ├── venv/                  # Virtual environment (rebuilt)
│   └── requirements.txt       # Python deps
│
├── frontend/                   # React app
│   ├── src/components/        # UI components
│   └── package.json           # Node deps
│
├── logs/                       # Application logs
│   ├── backend.log
│   ├── frontend.log
│   └── mac_sync.log           # Sync poller logs
│
├── mac_sync_poller.py         # Auto-sync Railway uploads
├── start_all.command          # Start script
├── stop_all.command           # Stop script
├── system_health_check.sh     # Health check script
│
├── README.md                  # This file
├── PROJECT_STATUS.md          # System status & health
├── INSTALLATION.md            # Setup guide
├── SYSTEM_ARCHITECTURE.md     # Architecture docs
├── RAILWAY_DEPLOYMENT.md      # Deployment guide
├── HANDBUCH.md                # User manual (German)
└── AI_MODEL_INTEGRATION.md    # AI model docs
```

---

## 🚀 Deployment

### Local Development
```bash
bash start_all.command
```

### Railway Production
- **URL:** https://video-editor.momentummind.de
- **Status:** ✅ Live and responding
- **Auto-Deploy:** Enabled (pushes to main branch)

### System Health
```bash
bash system_health_check.sh
```

**Current Status:**
```
✅ PASSED:   28 / 28 (100%)
⚠️  WARNINGS: 0
❌ ERRORS:   0

🎉 SYSTEM STATUS: HEALTHY ✅
```

---

## 📞 Support

### Documentation
- **System Status:** `PROJECT_STATUS.md` - Complete health documentation
- **Quick Start:** `QUICKSTART.md` - 5-minute setup
- **Installation:** `INSTALLATION.md` - Detailed setup guide
- **Architecture:** `SYSTEM_ARCHITECTURE.md` - Technical docs
- **User Manual:** `HANDBUCH.md` - German user guide
- **AI Models:** `AI_MODEL_INTEGRATION.md` - Developer docs

### Logs
- Backend: `logs/backend.log`
- Frontend: `logs/frontend.log`
- Mac Sync: `logs/mac_sync.log`

### Health Check
```bash
bash system_health_check.sh
```

---

## 🔄 Latest Updates

### Version 2.0.0 (2025-10-27)
- ✅ **CRITICAL:** Fixed database path issue (relative → absolute)
- ✅ **CRITICAL:** Rebuilt virtual environment with correct paths
- ✅ **CRITICAL:** Fixed Dropbox storage paths (CloudStorage)
- ✅ **NEW:** Mac Sync Poller for automatic Railway → Mac sync
- ✅ **NEW:** System health check script (28 checks)
- ✅ **NEW:** 100% system health achieved (NULL BUG TOLERANCE)
- ✅ **CLEANUP:** Directory structure (removed duplicates)
- ✅ **DOCS:** Complete documentation overhaul

### Version 1.0.0 (2025-01-24)
- ✅ Edge TTS Fixed - v7.2.3 resolves 403 errors
- ✅ 7 AI Models - Flux, Ideogram, Recraft, SDXL
- ✅ Flux Schnell Default - 13x cost savings
- ✅ Multi-language - 13 language support
- ✅ Enhanced Effects - Film grain, glitch, vignette
- ✅ Sound Effects - Per-scene audio control

---

## 📄 License

Proprietary - Video Editor Prototype Team

---

**Version:** 2.0.0
**Status:** ✅ Production Ready (100% Health)
**Last Updated:** 2025-10-27
**System Health:** ✅ 28/28 PASSED (NULL BUG TOLERANCE ACHIEVED)

Made with ❤️ for the Sternzeichen Automation System
