# 🚂 Video Editor Prototype - Railway Cloud Deployment Guide

**Version:** 2.0.0
**Last Updated:** 2025-10-27
**Deployment Status:** ✅ LIVE at https://video-editor.momentummind.de

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Hybrid Architecture](#hybrid-architecture)
3. [Deployment Steps](#deployment-steps)
4. [Environment Variables](#environment-variables)
5. [Dropbox API Setup](#dropbox-api-setup)
6. [Mac Sync Poller](#mac-sync-poller)
7. [Monitoring & Logs](#monitoring--logs)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview

### Current Production Deployment

- **URL:** https://video-editor.momentummind.de
- **Status:** ✅ Live and responding
- **Deployment:** Hybrid Mac + Railway
- **Database:** SQLite with absolute paths
- **Storage:** Dropbox API + Local Mac filesystem

### Why Hybrid Deployment?

This system uses **BOTH** local Mac AND Railway cloud deployment:

```
LOCAL MAC (Primary - Fast)        RAILWAY (Cloud - 24/7)
├─ Direct Dropbox filesystem      ├─ Dropbox API access
├─ Instant image access           ├─ Remote availability
├─ Backend: localhost:5001        ├─ Backend: video-editor.momentummind.de
├─ Frontend: localhost:3000       │
└─ Mac Sync Poller (30s)          └─ Writes to .sync_queue.json
       ↓                                    ↓
       └────── SHARED DROPBOX STORAGE ──────┘
```

**Benefits:**
- ✅ Fast local development (Mac uses filesystem)
- ✅ 24/7 cloud access (Railway always online)
- ✅ Auto-sync (Mac Sync Poller every 30s)
- ✅ Shared image cache (cost savings)

---

## 🔄 Hybrid Architecture

### Storage Structure

**Code Location:**
```
~/Library/CloudStorage/Dropbox/Social Media/video_editor_prototype/
```

**Output Location:**
```
~/Library/CloudStorage/Dropbox/Apps/output Horoskop/output/video_editor_prototype/
├─ image_cache/         # AI-generated images (1088 cached)
├─ uploads/             # User-uploaded files
└─ .sync_queue.json     # Railway → Mac sync notifications
```

### How Sync Works

1. **Railway uploads file** → Writes to Dropbox via API
2. **Railway updates** `.sync_queue.json` → Adds file path
3. **Mac Sync Poller reads** `.sync_queue.json` every 30s
4. **Mac downloads file** from Dropbox to local filesystem
5. **Both systems** now have same files

---

## 🚀 Deployment Steps

### Step 1: Push to GitHub

```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype

# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit"

# Push to GitHub
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Login with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose `video_editor_prototype` repository
6. Railway auto-detects Python/Node.js project

### Step 3: Configure Build Settings

Railway should automatically detect:
- **Build Command:** `cd frontend && npm install && npm run build`
- **Start Command:** `cd backend && gunicorn app:app`
- **Port:** Auto-assigned (usually 8080)

If not, manually set in Railway project settings.

### Step 4: Set Environment Variables

See [Environment Variables](#environment-variables) section below.

### Step 5: Deploy & Get URL

1. Railway automatically deploys
2. Get your URL from Railway dashboard
3. Example: `https://video-editor-production-abc123.up.railway.app`
4. Set custom domain: `video-editor.momentummind.de` (if available)

---

## 🔑 Environment Variables

### Required Variables (Railway Dashboard)

```bash
# Replicate API (AI Image Generation)
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI API (TTS + Keyword Extraction)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ElevenLabs API (Optional Premium TTS)
ELEVENLABS_API_KEY=your_elevenlabs_key

# Dropbox API (CRITICAL for Railway storage)
DROPBOX_ACCESS_TOKEN=sl.xxxxxxxxxxxxxxxxxxxxxxxxxxxx
DROPBOX_REFRESH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DROPBOX_APP_KEY=your_app_key
DROPBOX_APP_SECRET=your_app_secret

# Port (Railway sets automatically)
PORT=8080
```

### How to Get Dropbox API Credentials

See [Dropbox API Setup](#dropbox-api-setup) section below.

---

## 📦 Dropbox API Setup

### Step 1: Create Dropbox App

1. Go to https://www.dropbox.com/developers/apps
2. Click **"Create App"**
3. Choose:
   - **API:** Scoped Access
   - **Access:** Full Dropbox
   - **Name:** `video-editor-production` (or similar)
4. Click **"Create App"**

### Step 2: Set Permissions

In the **Permissions** tab, enable:
- ✅ `files.content.write`
- ✅ `files.content.read`
- ✅ `files.metadata.write`
- ✅ `files.metadata.read`

Click **"Submit"** to save.

### Step 3: Generate Access Token

In the **Settings** tab:
1. Find **"Generated access token"** section
2. Click **"Generate"**
3. Copy the token (starts with `sl.`)
4. **Important:** This token expires in 4 hours!

### Step 4: Get Refresh Token (Long-term Auth)

For long-term access, generate a refresh token:

```bash
# Get authorization code
curl -X POST https://www.dropbox.com/oauth2/authorize \
  -d "client_id=YOUR_APP_KEY" \
  -d "response_type=code" \
  -d "token_access_type=offline"

# Exchange code for refresh token
curl -X POST https://api.dropboxapi.com/oauth2/token \
  -d "code=YOUR_AUTH_CODE" \
  -d "grant_type=authorization_code" \
  -d "client_id=YOUR_APP_KEY" \
  -d "client_secret=YOUR_APP_SECRET"
```

Response includes `refresh_token` - save this for Railway!

### Step 5: Add to Railway

Add all 4 Dropbox variables to Railway:
- `DROPBOX_ACCESS_TOKEN`
- `DROPBOX_REFRESH_TOKEN`
- `DROPBOX_APP_KEY`
- `DROPBOX_APP_SECRET`

With refresh token, Railway can auto-refresh expired access tokens!

---

## 🔄 Mac Sync Poller

### What It Does

The Mac Sync Poller ensures files uploaded via Railway are automatically synced to your local Mac.

### How to Run

Mac Sync Poller is automatically started by `start_all.command`:

```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype
bash start_all.command
```

This starts:
1. Backend (Port 5001)
2. Frontend (Port 3000)
3. **Mac Sync Poller** (background process)

### Check if Running

```bash
pgrep -f "mac_sync_poller.py"
# Returns process ID if running
```

### View Logs

```bash
tail -f logs/mac_sync.log
```

**Expected output:**
```
📁 Storage Mode: LOCAL FILESYSTEM
🔄 Polling for new files from Railway...
✅ No new files to sync
```

### Manual Start (if needed)

```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype
./backend/venv/bin/python mac_sync_poller.py &
```

---

## 📊 Monitoring & Logs

### Railway Logs

View Railway logs:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs
```

### Health Checks

**Railway Backend:**
```bash
curl https://video-editor.momentummind.de/api/health
```

**Expected response:**
```json
{"status": "healthy", "storage_mode": "DROPBOX API"}
```

**Local Mac Backend:**
```bash
curl http://localhost:5001/api/health
```

**Expected response:**
```json
{"status": "healthy", "storage_mode": "LOCAL FILESYSTEM"}
```

### System Health Check

Run comprehensive check (28 tests):
```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype
bash system_health_check.sh
```

---

## 🐛 Troubleshooting

### Railway Build Fails

**Error:** `Build failed`

**Solutions:**
1. Check Railway build logs
2. Verify all environment variables are set
3. Check `requirements.txt` and `package.json` are valid
4. Ensure Python 3.9+ and Node 18+ in Railway

### Dropbox API Errors on Railway

**Error:** `401 Unauthorized` or `Invalid access token`

**Solutions:**
1. Check `DROPBOX_ACCESS_TOKEN` is valid
2. Generate new access token if expired
3. Set `DROPBOX_REFRESH_TOKEN` for auto-refresh
4. Verify Dropbox App permissions are set correctly

### Mac Sync Poller Not Working

**Error:** `ModuleNotFoundError: No module named 'dropbox'`

**Solution:** Rebuild venv (fixed 2025-10-27)
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Errors

**Error:** `unable to open database file`

**Solution:** FIXED with absolute paths (2025-10-27)
- Database now uses `os.path.dirname(os.path.abspath(__file__))`
- Works from any working directory
- Railway and Mac both work correctly

### Railway Not Syncing to Mac

**Check `.sync_queue.json`:**
```bash
cat ~/Library/CloudStorage/Dropbox/Apps/output\ Horoskop/output/video_editor_prototype/.sync_queue.json
```

**Should contain:**
```json
{
  "pending": [
    {
      "path": "uploads/music/song.mp3",
      "timestamp": "2025-10-27T12:00:00",
      "source": "railway"
    }
  ]
}
```

**If empty:** Railway isn't writing notifications
**If full but not syncing:** Mac Sync Poller not running

---

## 📞 Support & Documentation

### Related Documentation
- **README.md** - System overview
- **INSTALLATION.md** - Local setup guide
- **SYSTEM_ARCHITECTURE.md** - Hybrid architecture details
- **QUICKSTART.md** - 5-minute setup

### Logs
- Railway logs: `railway logs`
- Local backend: `logs/backend.log`
- Local frontend: `logs/frontend.log`
- Mac Sync Poller: `logs/mac_sync.log`

---

**Version:** 2.0.0
**Last Updated:** 2025-10-27
**Deployment:** ✅ LIVE at https://video-editor.momentummind.de
**System Health:** ✅ 100% (NULL BUG TOLERANCE ACHIEVED)
