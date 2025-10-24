# 🎬 Video Editor Prototype

> AI-powered video creation tool with 7 AI image models, 3 TTS services, and advanced visual effects.

[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)]()
[![Version](https://img.shields.io/badge/Version-1.0.0-blue)]()
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

---

## 📋 Quick Start

### Prerequisites
```bash
# Install system dependencies
brew install ffmpeg node python@3.9
```

### Installation
```bash
cd video_editor_prototype

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
EOF

# Frontend Setup
cd ../frontend
npm install
```

### Run
```bash
# From project root
bash start_all.command
```

Open http://localhost:3000

### Stop
```bash
bash stop_all.command
```

---

## 📚 Complete Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| **README.md** | Quick overview (this file) | Everyone |
| **INSTALLATION.md** | Detailed installation guide | Developers |
| **HANDBUCH.md** | Complete user manual (German) | End users |
| **AI_MODEL_INTEGRATION.md** | AI model integration guide | Developers |

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────┐
│           React Frontend (Vite + Tailwind)         │
│  • Timeline Editor with drag-drop                  │
│  • Visual Effects Panel                            │
│  • Video Preview Player                            │
│  • Multi-language Script Editor                    │
└────────────────────┬───────────────────────────────┘
                     │ REST API (HTTP)
┌────────────────────▼───────────────────────────────┐
│              Flask Backend (Python)                │
│  • Project/Scene CRUD operations                   │
│  • AI Image Generation (Replicate API)             │
│  • TTS (Edge/OpenAI/ElevenLabs)                    │
│  • Video Composition (FFmpeg + MoviePy)            │
│  • Translation Service (13 languages)              │
│  • Keyword Extraction (GPT-4o-mini)                │
└────────────────────┬───────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────┐
│          SQLite Database + File Cache              │
│  • projects table (settings, metadata)             │
│  • scenes table (script, effects, timing)          │
│  • Image cache (MD5-based, saves $$)               │
└────────────────────────────────────────────────────┘
```

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

### Cost Explosion Example (avoid!)
```
AI Images:  20 × $0.09 (Ideogram V3)    = $1.80
TTS:        ElevenLabs                  = $1.50
────────────────────────────────────────────────
Total:                                   $3.30
```

**💡 Tip:** Use Flux Schnell + Edge TTS for lowest costs!

---

## 🛠️ Tech Stack

### Backend
- **Flask 3.0.3** - Python web framework
- **SQLite** - Lightweight database
- **Replicate API** - AI image generation
- **OpenAI API** - TTS + GPT-4o-mini
- **Edge TTS 7.2.3** - Free TTS (403 error fixed!)
- **MoviePy 1.0.3** - Video editing library
- **FFmpeg 8.0** - Media processing

### Frontend
- **React 18** - UI framework
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first CSS
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client

---

## 🎯 Usage Example

### 1. Create Project via API
```bash
curl -X POST http://localhost:5001/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "My Awesome Video"}'
```

### 2. Bulk Add Scenes (Auto-Extract Keywords)
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
2. **Enable Image Caching** - Reuse AI-generated images
3. **Limit Scene Count** - Keep under 50 scenes/project
4. **Use Preview Mode** - Test with 540p before 1080p export
5. **Close Other Apps** - FFmpeg is CPU-intensive

---

## 🐛 Common Issues & Solutions

### Edge TTS 403 Error
```bash
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

### Clear Image Cache (if > 1GB)
```bash
rm -rf backend/replicate_cache/*
```

---

## 🔄 Recent Updates (2025-01-24)

✅ **Edge TTS Fixed** - v7.2.3 resolves 403 errors
✅ **7 AI Models** - Flux, Ideogram, Recraft, SDXL
✅ **Flux Schnell Default** - 13x cost savings
✅ **Complete Docs** - Installation, manual, API guides
✅ **Multi-language** - 13 language support
✅ **Enhanced Effects** - Film grain, glitch, vignette
✅ **Sound Effects** - Per-scene audio control

---

## 📂 Project Structure

```
video_editor_prototype/
├── backend/                    # Flask API
│   ├── api/                   # REST endpoints
│   ├── services/              # Business logic
│   ├── database/              # SQLite DB
│   ├── replicate_cache/       # AI image cache
│   ├── previews/              # Generated videos
│   └── requirements.txt       # Python deps
│
├── frontend/                   # React app
│   ├── src/components/        # UI components
│   ├── src/hooks/             # Custom hooks
│   └── package.json           # Node deps
│
├── logs/                       # Application logs
├── start_all.command          # Start script
├── stop_all.command           # Stop script
├── README.md                  # This file
├── INSTALLATION.md            # Setup guide
├── HANDBUCH.md                # User manual
└── AI_MODEL_INTEGRATION.md    # Developer docs
```

---

## 🚀 Roadmap

### Planned Features
- [ ] Export to 1080p/4K
- [ ] Custom aspect ratios (9:16, 16:9, 1:1)
- [ ] Watermark support
- [ ] Batch rendering queue
- [ ] Direct social media upload
- [ ] Cloud deployment (Docker + K8s)
- [ ] Multi-user collaboration
- [ ] Template marketplace

---

## 📞 Support

### Logs
- Backend: `logs/backend.log`
- Frontend: `logs/frontend.log`

### Resources
- User Manual: `HANDBUCH.md`
- Installation Guide: `INSTALLATION.md`
- AI Models Guide: `AI_MODEL_INTEGRATION.md`

---

## 📄 License

Proprietary - Video Editor Prototype Team

---

**Version:** 1.0.0
**Status:** ✅ Production Ready
**Last Updated:** 2025-01-24

Made with ❤️ for the Sternzeichen Automation System
