# Quick Start Guide

Get the Video Editor Prototype running in 5 minutes.

## 1. Backend Setup (Terminal 1)

```bash
cd video_editor_prototype/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your paths
# PORT=5001
# DATABASE_PATH=./database/editor_projects.db
# DROPBOX_CUSTOM_MEDIA_PATH=/path/to/your/dropbox/custom_media

# Run backend
python app.py
```

Backend running at: http://localhost:5001

## 2. Frontend Setup (Terminal 2)

```bash
cd video_editor_prototype/frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

Frontend running at: http://localhost:3000

## 3. Open Browser

Navigate to: http://localhost:3000

## 4. Test the Editor

1. Create a new project (backend will auto-initialize DB on first run)
2. Type some text in the Script Editor
3. Click "Add Scene"
4. See the scene appear in the Timeline
5. Edit/Delete scenes as needed

## Troubleshooting

### Backend won't start?
- Check Python version: `python3 --version` (need 3.10+)
- Check virtual environment is activated (you should see `(venv)` in terminal)
- Check port 5001 is not in use: `lsof -i :5001`

### Frontend won't start?
- Check Node version: `node --version` (need 18+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check port 3000 is not in use: `lsof -i :3000`

### API requests failing?
- Ensure backend is running on port 5001
- Check browser console for errors
- Verify CORS is enabled in Flask (should be by default)

### Database issues?
- Delete the database and restart: `rm backend/database/editor_projects.db`
- Backend will auto-create fresh DB on startup

## Next Steps

- Read full README.md for detailed architecture
- Check API endpoints in backend/api/
- Explore component structure in frontend/src/components/
- Review development roadmap for upcoming features
