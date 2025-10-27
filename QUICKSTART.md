# 🚀 Quick Start Guide

Get the Video Editor Prototype running in 5 minutes!

## 🎯 Recommended Method: Use start_all.command

The easiest way to start the system:

```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype
bash start_all.command
```

This automatically starts:
- ✅ Backend (Port 5001)
- ✅ Frontend (Port 3000)
- ✅ Mac Sync Poller (Railway → Mac sync)

**System URLs:**
- Local Frontend: http://localhost:3000
- Local Backend: http://localhost:5001
- Railway Cloud: https://video-editor.momentummind.de

---

## 📦 First-Time Setup

If running for the first time, follow these steps:

### 1. Install System Dependencies

```bash
# macOS
brew install ffmpeg node python@3.9

# Verify installations
ffmpeg -version
node --version
python3 --version
```

### 2. Backend Setup

```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file with API keys
cat > .env << EOF
REPLICATE_API_TOKEN=your_replicate_token
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
DROPBOX_ACCESS_TOKEN=your_dropbox_token
DROPBOX_REFRESH_TOKEN=your_refresh_token
DROPBOX_APP_KEY=your_app_key
DROPBOX_APP_SECRET=your_app_secret
EOF
```

### 3. Frontend Setup

```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype/frontend

# Install Node dependencies
npm install
```

### 4. Start the System

```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype
bash start_all.command
```

---

- **Local Frontend:** http://localhost:3000
- **Local Backend:** http://localhost:5001/api/health
- **Railway Cloud:** https://video-editor.momentummind.de

---

## ✅ Verify System Health

Run the comprehensive health check:

```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype
bash system_health_check.sh
```

**Expected Output:**
```
✅ PASSED:   28 / 28 (100%)
⚠️  WARNINGS: 0
❌ ERRORS:   0

🎉 SYSTEM STATUS: HEALTHY ✅
```

---

## 🎬 Test the Editor

1. Open http://localhost:3000 in your browser
2. Create a new project (database auto-initializes with 960 existing projects)
3. Type some text in the Script Editor
4. Click "Add Scene" to create scenes
5. Generate AI images with one of 7 models (Flux Schnell is default)
6. Add TTS voiceover (Edge TTS is free!)
7. Generate preview video

---

## 🛑 Stop the System

```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype
bash stop_all.command
```

This stops:
- Backend process
- Frontend process
- Mac Sync Poller

---

## 🐛 Troubleshooting

### Backend won't start?
```bash
# Check Python version (need 3.9+)
python3 --version

# Check if venv exists
ls backend/venv

# Rebuild venv if needed
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start?
```bash
# Check Node version (need 18+)
node --version

# Check port 3000
lsof -i :3000

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database error: "unable to open database file"?
**SOLVED!** Database now uses absolute paths (fixed 2025-10-27)
- Database location: `backend/database/editor_projects.db`
- Size: 389KB with 960 projects
- Works from any working directory

### Mac Sync Poller not running?
```bash
# Check if running
pgrep -f "mac_sync_poller.py"

# Check logs
tail -f logs/mac_sync.log

# Restart system
bash stop_all.command
bash start_all.command
```

### Port already in use?
```bash
# Kill processes on port 5001
lsof -ti:5001 | xargs kill -9

# Kill processes on port 3000
lsof -ti:3000 | xargs kill -9

# Then restart
bash start_all.command
```

### Check system logs
```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# Mac Sync logs
tail -f logs/mac_sync.log
```

---

## 📚 Next Steps

- **Read README.md** - Complete system overview
- **Check SYSTEM_ARCHITECTURE.md** - Technical architecture
- **Review RAILWAY_DEPLOYMENT.md** - Cloud deployment guide
- **Read HANDBUCH.md** - User manual (German)
- **Explore AI_MODEL_INTEGRATION.md** - AI models documentation

---

## 💰 Cost-Effective Setup

**Budget Mode (FREE):**
- AI Images: Flux Schnell ($0.003/image)
- TTS: Edge TTS (FREE!)
- Cost per 20-scene video: ~$0.06

**Premium Mode:**
- AI Images: Flux Pro 1.1 ($0.04/image)
- TTS: OpenAI TTS ($0.05/video)
- Cost per 20-scene video: ~$0.85

---

**Version:** 2.0.0
**Last Updated:** 2025-10-27
**System Health:** ✅ 100% (28/28 checks passing)
