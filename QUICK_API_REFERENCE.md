# VIDEO EDITOR PROTOTYPE - QUICK API REFERENCE

## Base URL
```
http://localhost:5001/api
```

## Quick Command Examples

### Create a Project
```bash
curl -X POST http://localhost:5001/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "My Awesome Video"}'
```

### List Projects
```bash
curl http://localhost:5001/api/projects
```

### Get Project Details
```bash
curl http://localhost:5001/api/projects/1
```

### Add a Scene
```bash
curl -X POST http://localhost:5001/api/projects/1/scenes \
  -H "Content-Type: application/json" \
  -d '{
    "script": "A majestic eagle soars through the sky",
    "duration": 5.0,
    "background_type": "keyword",
    "background_value": "eagle flying mountains"
  }'
```

### Bulk Import Scenes from Full Script
```bash
curl -X POST http://localhost:5001/api/projects/1/scenes/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "full_script": "A majestic eagle soars through the sky. Mountains stretch to the horizon. The sun sets in golden light."
  }'
```

### Generate Preview (540p)
```bash
curl -X POST http://localhost:5001/api/projects/1/preview
```

### Export Video (1080p)
```bash
curl -X POST http://localhost:5001/api/projects/1/export
```

### Download Video
```bash
curl http://localhost:5001/api/projects/1/download?resolution=1080p \
  -o my_video.mp4
```

### List TTS Voices
```bash
curl http://localhost:5001/api/tts/voices
```

### Get Voice Sample
```bash
curl http://localhost:5001/api/tts/preview/de-DE-KatjaNeural \
  -o voice_sample.mp3
```

### Improve Script with AI
```bash
curl -X POST http://localhost:5001/api/scripts/improve \
  -H "Content-Type: application/json" \
  -d '{
    "script": "An eagle. It flies. Mountains are big.",
    "target_duration": 10
  }'
```

### Update Project Settings
```bash
curl -X PATCH http://localhost:5001/api/projects/1 \
  -H "Content-Type: application/json" \
  -d '{
    "tts_voice": "de-DE-ConradNeural",
    "video_speed": 1.2,
    "ai_image_model": "flux-pro-1.1",
    "target_language": "en"
  }'
```

### Update Scene
```bash
curl -X PUT http://localhost:5001/api/scenes/5 \
  -H "Content-Type: application/json" \
  -d '{
    "script": "Updated script text",
    "duration": 6.5,
    "effect_zoom": "zoom-in",
    "effect_glitch": 1
  }'
```

### Generate Sound Effect
```bash
curl -X POST http://localhost:5001/api/sound-effects/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text_prompt": "explosion with reverb",
    "duration": 2.5
  }'
```

### Add Sound Effect to Scene
```bash
curl -X POST http://localhost:5001/api/scenes/5/sound-effect \
  -H "Content-Type: application/json" \
  -d '{
    "sound_effect_path": "/path/to/sound.mp3"
  }'
```

### Generate Background Music
```bash
curl -X POST http://localhost:5001/api/music/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text_prompt": "upbeat electronic music",
    "project_id": 1
  }'
```

### Upload Background Music
```bash
curl -X POST http://localhost:5001/api/uploads/audio \
  -F "file=@/path/to/music.mp3"
```

### Upload Scene Background Image
```bash
curl -X POST http://localhost:5001/api/uploads/image \
  -F "file=@/path/to/image.jpg"
```

### Add Output Folder
```bash
curl -X POST http://localhost:5001/api/settings/output-folders \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Final Videos",
    "path": "/Users/myname/Videos/exports"
  }'
```

### List Output Folders
```bash
curl http://localhost:5001/api/settings/output-folders
```

### Upload Video to Output Folder
```bash
curl -X POST http://localhost:5001/api/projects/1/upload-to-queue \
  -H "Content-Type: application/json" \
  -d '{
    "folder_id": 1,
    "resolution": "1080p"
  }'
```

## Response Examples

### Success Response
```json
{
  "id": 1,
  "name": "My Awesome Video",
  "tts_voice": "de-DE-KatjaNeural",
  "ai_image_model": "flux-schnell",
  "created_at": "2025-10-25T12:34:56",
  "updated_at": "2025-10-25T12:34:56"
}
```

### Preview Response
```json
{
  "preview_id": "preview_1_1729857296",
  "preview_path": "/Users/marcoglamngiw/Dropbox/Apps/output Horoskop/video_editor_prototype/previews/video_1_preview.mp4",
  "video_path": "/Users/marcoglamngiw/Dropbox/Apps/output Horoskop/video_editor_prototype/previews/video_1_preview.mp4",
  "preview_url": "/api/previews/video_1_preview.mp4",
  "total_duration": 42.5,
  "scene_count": 7,
  "status": "ready",
  "message": "Preview video generated successfully! (7 scenes, 42.5s)",
  "scene_timings": [
    {"id": 1, "duration": 6.2, "db_duration": 5.0},
    {"id": 2, "duration": 5.8, "db_duration": 5.0}
  ],
  "updated_scenes": [
    {"id": 1, "script": "Text", "duration": 6.2, ...}
  ]
}
```

### Error Response
```json
{
  "error": "Project not found"
}
```

## Available AI Models

### Image Generation (Replicate)
| Model | Cost | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| flux-schnell | $0.003 | 10s | Good | Budget videos |
| flux-dev | $0.025 | 15s | Better | Balance |
| flux-pro | $0.055 | 25s | Excellent | Professional |
| flux-pro-1.1 | $0.04 | 20s | Best | Premium quality |
| ideogram-v3 | $0.09 | 25s | Text-in-image | Text overlays |
| recraft-v3 | $0.04 | 20s | Stylized | Artistic styles |
| sdxl | Budget | 20s | Good | Alternative |

### TTS Providers
| Provider | Voices | Cost | Best For |
|----------|--------|------|----------|
| Edge TTS | 50+ | FREE | All projects |
| OpenAI | 5 | $0.03/1M chars | English |
| ElevenLabs | Premium | $0.30/10K chars | Premium voice |

### Languages Supported (13)
German, English, French, Spanish, Italian, Portuguese, Polish, Dutch, Turkish, Russian, Japanese, Chinese, Hindi

## Environment Variables
```bash
REPLICATE_API_TOKEN=your_token
OPENAI_API_KEY=your_key
ELEVENLABS_API_KEY=your_key
PORT=5001
DATABASE_PATH=./database/editor_projects.db
DROPBOX_ACCESS_TOKEN=your_token  # Railway only
```

## Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request |
| 404 | Not found |
| 500 | Server error |

## Database
**SQLite:** `backend/database/editor_projects.db`
**Tables:** projects, scenes, settings, output_folders

## Storage Paths
```
~/Dropbox/Apps/output Horoskop/video_editor_prototype/
├── previews/          # Generated videos
├── image_cache/       # AI-generated images (MD5-hashed)
└── uploads/
    ├── audio/         # Background music
    ├── images/        # Scene backgrounds
    └── sound_effects/ # Per-scene sounds
```

## Performance Tips
1. Use Flux Schnell for fastest/cheapest generation
2. Enable image caching (MD5 based, automatic)
3. Keep scenes under 50 per project
4. Preview at 540p before 1080p export
5. Use Edge TTS for free unlimited TTS

---
**Version:** 1.0.0 | **Last Updated:** Oct 25, 2025
