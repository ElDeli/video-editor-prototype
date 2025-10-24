# Video Editor Prototype - Railway Deployment Guide

## Quick Deploy to Railway

### Step 1: Push to GitHub

1. Create a new GitHub repository
2. Push this code to GitHub:
```bash
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your Video Editor repository
4. Railway will automatically detect the configuration from `railway.json`

### Step 3: Set Environment Variables

In Railway project settings, add these environment variables:

**Required:**
- `OPENAI_API_KEY` - OpenAI API key for TTS
- `ELEVENLABS_API_KEY` - ElevenLabs API key for advanced TTS
- `REPLICATE_API_TOKEN` - Replicate token for AI image generation
- `DROPBOX_ACCESS_TOKEN` - Dropbox API token for file storage

**Optional:**
- `PORT` - Railway sets this automatically (default: 8080)

### Step 4: Get Your Deployment URL

After deployment, Railway will provide a URL like: `https://video-editor-production-xxx.up.railway.app`

### Step 5: Update Main Dashboard

In your main Sternzeichen Automation Railway project, set the environment variable:

```
VIDEO_EDITOR_URL=https://video-editor-production-xxx.up.railway.app
```

Then restart the main dashboard service.

## Architecture

- **Frontend**: React + Vite (built to static files)
- **Backend**: Flask API with gunicorn
- **Storage**: Dropbox API (shared with main dashboard)
- **Database**: SQLite (persisted in Railway volume)

## Build Process

Railway automatically:
1. Installs frontend dependencies (`npm install`)
2. Builds frontend (`npm run build`)
3. Installs backend dependencies (`pip install -r requirements.txt`)
4. Starts gunicorn server on `$PORT`

## Troubleshooting

### Build fails
- Check that all environment variables are set
- Check Railway build logs

### Frontend not loading
- Ensure frontend build completed successfully
- Check that gunicorn is serving static files

### Database errors
- Railway should automatically create a volume for SQLite
- Check logs for permission issues

### Dropbox errors
- Verify `DROPBOX_ACCESS_TOKEN` is valid
- Check Dropbox paths match main dashboard paths
