# 📽️ Video Editor Prototype - Benutzerhandbuch

**Version:** 2.0.0
**Letzte Aktualisierung:** 2025-10-27
**System-Status:** ✅ 100% Funktionsfähig

---

## 🚀 Inhaltsverzeichnis

1. [System Starten & Stoppen](#system-starten--stoppen)
2. [Projekt erstellen](#projekt-erstellen)
3. [Scenes erstellen](#scenes-erstellen)
4. [AI Image Models](#ai-image-models)
5. [TTS Voice Selection](#tts-voice-selection)
6. [Background Music](#background-music)
7. [Video Speed & Translation](#video-speed--translation)
8. [Effects System](#effects-system)
9. [Sound Effects](#sound-effects)
10. [Preview & Export](#preview--export)
11. [Kosten-Übersicht](#kosten-übersicht)

---

## 🚀 System Starten & Stoppen

### Starten
```bash
cd ~/Library/CloudStorage/Dropbox/Social\ Media/video_editor_prototype
bash start_all.command
```

**Was passiert:**
- Backend startet auf Port 5001
- Frontend startet auf Port 3000
- **Mac Sync Poller startet** (für Railway-Sync)
- Öffne Browser: http://localhost:3000

### Stoppen
```bash
bash stop_all.command
```

**Was passiert:**
- Alle Prozesse werden beendet
- Python Cache wird geleert
- Ports 3000 und 5001 werden freigegeben

---

## 📁 Projekt erstellen

### Option 1: Über UI
1. Öffne http://localhost:3000
2. Klicke auf "New Project" (falls kein Projekt existiert)
3. Projekt wird automatisch erstellt mit Namen "My Video Project"

### Option 2: Über API
```bash
curl -X POST http://localhost:5001/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Mein Erstes Video"}'
```

**Projekt-Settings:**
- **Name**: Projekt-Name
- **TTS Voice**: Text-to-Speech Stimme (Default: de-DE-KatjaNeural)
- **Target Language**: Zielsprache für Übersetzung (Default: auto = keine Übersetzung)
- **Background Music**: Optionaler Music-Track
- **Background Music Volume**: Lautstärke 0-100% (Default: 7%)
- **Video Speed**: Geschwindigkeit 0.5x - 2.0x (Default: 1.0x)
- **AI Image Model**: Bildgenerierungs-Model (Default: flux-schnell)

---

## 🎬 Scenes erstellen

### Einzelne Scene erstellen
1. Klicke auf **"+ Add 1 Scene"**
2. Gib deinen Text ein
3. Scene wird mit Default-Einstellungen erstellt

### Bulk Scene Creation (Auto-Create)
1. Klicke auf **"✨ Auto-Create Scenes"**
2. Füge deinen **kompletten Script** ein
3. Klicke auf **"Create Scenes"**

**Was passiert:**
- Script wird automatisch in Sätze aufgeteilt
- Für jeden Satz wird eine Scene erstellt
- **AI extrahiert visuelle Keywords** aus jedem Satz
- Duration wird automatisch berechnet (~2.5 Wörter/Sekunde)

**Beispiel:**
```
Input: "Ein Pferd steht auf einer Wiese. Der Himmel ist blau. Es beginnt zu regnen."

Output:
- Scene 1: "Ein Pferd steht auf einer Wiese" → Keyword: "Pferd auf Wiese"
- Scene 2: "Der Himmel ist blau" → Keyword: "blauer Himmel"
- Scene 3: "Es beginnt zu regnen" → Keyword: "Regen"
```

---

## 🎨 AI Image Models

### Verfügbare Models

| Model | Kosten/Bild | Qualität | Geschwindigkeit | Besonderheit |
|-------|-------------|----------|-----------------|--------------|
| **⚡ Flux Schnell** | $0.003 | Gut | Sehr schnell | **DEFAULT - Empfohlen!** |
| **🎨 Flux Dev** | $0.025 | Sehr gut | Mittel | Balanced |
| **🎨 Flux Pro** | $0.055 | Exzellent | Langsam | Höchste Qualität |
| **🎨 Flux Pro 1.1** | $0.04 | Exzellent | Langsam | Verbesserte Version |
| **📝 Ideogram V3** | $0.09 | Sehr gut | Mittel | **Text in Bildern möglich!** |
| **🎭 Recraft V3** | $0.04 | Sehr gut | Mittel | Verschiedene Styles |
| **💰 SDXL** | $0.003 | OK | Schnell | Günstig wie Flux Schnell |

### Model wechseln

**Für das gesamte Projekt:**
1. Wähle Model im Dropdown (Header, rechts oben)
2. Model wird automatisch im Projekt gespeichert
3. **WICHTIG:** Bestehende Bilder bleiben im Cache!

**Cache-Logik:**
- Bilder werden gecached mit: `keyword + width + height + model`
- **Beispiel:** "Pferd" mit Flux Schnell → gecached
- Wenn du zu Flux Pro 1.1 wechselst: "Pferd" mit Flux Pro 1.1 → **neues Bild wird generiert**
- **ABER:** Nur wenn du auch Preview drückst!

### Wann werden neue Bilder generiert?

#### ❌ KEINE neuen Bilder:
- Model ändern + Preview (ohne Keyword zu ändern)
- Selben Text erneut eingeben
- Preview mehrfach drücken ohne Änderungen

#### ✅ NEUE Bilder werden generiert:
- **Keyword ändern** (Scene bearbeiten)
- **Model ändern + Keyword ändern**
- **🔄 Regenerate** Button klicken (forciert neues Bild)
- Scene komplett neu erstellen

### 🔄 Regenerate Function

**Was macht Regenerate?**
1. Fügt "variation X" (X = Random 1-100) zum Keyword hinzu
2. Umgeht dadurch den Cache
3. Generiert **garantiert ein neues Bild** mit dem **aktuellen Project Model**

**Beispiel:**
- Original Keyword: "Pferd auf Wiese"
- Nach Regenerate: "Pferd auf Wiese variation 42"
- Neues Bild wird generiert
- Keyword in Datenbank wird aktualisiert

**Kosten:**
- Abhängig vom aktuellen Model im Dropdown
- Flux Schnell: $0.003
- Flux Pro 1.1: $0.04
- Ideogram V3: $0.09

---

## 🎙️ TTS Voice Selection

### Verfügbare TTS Services

#### 1. **Microsoft Edge TTS** (Kostenlos, ✅ **FUNKTIONIERT seit v7.2.3!**)
Format: `<voice-code>` (z.B. `de-DE-KatjaNeural`)

**WICHTIG:** Edge TTS v7.2.3+ ist erforderlich (403 Error in v6.1.10 gefixt!)

**Deutsche Stimmen:**
- `de-DE-KatjaNeural` - Katja (Female) - **DEFAULT**
- `de-DE-ConradNeural` - Conrad (Male)
- `de-DE-AmalaNeural` - Amala (Female)

**Englische Stimmen:**
- `en-US-AriaNeural` - Aria (Female)
- `en-US-GuyNeural` - Guy (Male)
- `en-GB-SoniaNeural` - Sonia (Female, British)

#### 2. **OpenAI TTS** (Empfohlen, stabil, ~$0.015/1000 chars)
Format: `openai:<voice>`

**Verfügbare Stimmen:**
- `openai:alloy` - Neutral
- `openai:echo` - Male
- `openai:fable` - British
- `openai:onyx` - Deep Male
- `openai:nova` - Female
- `openai:shimmer` - Soft Female

#### 3. **ElevenLabs** (Höchste Qualität, teuer, ~$0.30/1000 chars)
Format: `elevenlabs:<voice-id>`

**Beispiel:**
```
elevenlabs:21m00Tcm4TlvDq8ikWAM
```

### Voice wechseln
1. Klicke auf Voice Selector (Header, rechts)
2. Wähle gewünschte Stimme
3. Voice wird automatisch im Projekt gespeichert
4. Nächster Preview benutzt neue Stimme

---

## 🎵 Background Music

### Music hinzufügen
1. Klicke auf **"🎵 Change Music"**
2. Wähle MP3-Datei aus
3. Music wird hochgeladen
4. Filename wird angezeigt (max. 150px, truncated)

### Music Volume einstellen
- Slider: 0% - 100%
- **Default: 7%** (empfohlen, damit TTS gut hörbar bleibt)
- Wird automatisch gespeichert

### Music entfernen
1. Klicke auf **"🎵 Change Music"**
2. Lade neue Datei hoch → überschreibt alte
3. (Momentan kein "Remove" Button)

### Wie Music funktioniert
- Music wird über **gesamte Video-Länge** geloopt
- Wenn Music kürzer als Video → Loop
- Wenn Music länger als Video → Fade out am Ende
- Volume wird konstant auf eingestellten Wert gehalten

---

## 🌐 Video Speed & Translation

### Video Speed
- **Slider:** 0.5x - 2.0x
- **Default:** 1.0x (Normal)
- **0.5x:** Halbe Geschwindigkeit (langsamer, dramatischer)
- **2.0x:** Doppelte Geschwindigkeit (schneller, dynamischer)

**Anwendungsfälle:**
- 0.8x: Entspannt, meditativ
- 1.0x: Normal
- 1.2x: Energetisch
- 1.5x: Viral TikTok Style

### Translation (Target Language)

**Verfügbare Sprachen:**
- **Auto (No Translation)** - **DEFAULT**
- 🇩🇪 Deutsch
- 🇬🇧 English
- 🇪🇸 Español
- 🇫🇷 Français
- 🇮🇹 Italiano
- 🇵🇹 Português
- 🇵🇱 Polski
- 🇳🇱 Nederlands
- 🇹🇷 Türkçe
- 🇷🇺 Русский
- 🇯🇵 日本語
- 🇨🇳 中文

**Wie Translation funktioniert:**
1. Du schreibst Script auf Deutsch
2. Wählst Target Language: "English"
3. Bei Preview wird Script automatisch übersetzt
4. TTS generiert Audio in Zielsprache
5. **WICHTIG:** Original-Script bleibt in DB gespeichert!

**Workflow Bulk Script + Translation:**
1. Paste deutschen Text in "Auto-Create Scenes"
2. Wähle Target Language: "English"
3. System übersetzt **kompletten Script** vor Scene-Creation
4. Scenes werden mit übersetztem Text erstellt

---

## ✨ Effects System

### Verfügbare Effects (Pro Scene)

#### **Motion Effects**
- **Zoom:** none, in, out, in-out
- **Pan:** none, left, right, up, down
- **Rotate:** none, clockwise, counter-clockwise
- **Bounce:** 0 (off), 1 (on)
- **Tilt 3D:** none, left, right, forward, back

#### **Color Effects**
- **Vignette:** none, light, medium, heavy
- **Color Temp:** none, warm, cold
- **Saturation:** 0.0 - 2.0 (0.0 = grayscale, 1.0 = normal, 2.0 = oversaturated)

#### **Creative Effects**
- **Film Grain:** 0 (off), 1 (on)
- **Glitch:** 0 (off), 1 (on)
- **Chromatic Aberration:** 0 (off), 1 (on)
- **Blur:** none, light, medium, heavy
- **Light Leaks:** 0 (off), 1 (on)
- **Lens Flare:** 0 (off), 1 (on)
- **Kaleidoscope:** 0 (off), 1 (on)

#### **Transition Effects**
- **Fade:** none, in, out, in-out
- **Effect Intensity:** 0.0 - 1.0

### Effects anwenden
1. Klicke auf **"✨ Effects"** bei einer Scene
2. Wähle gewünschte Effects
3. Effects werden automatisch gespeichert
4. Preview erstellen → Effects werden angewendet

---

## 🔊 Sound Effects

### Sound Effect hinzufügen
1. Klicke auf **"🎵 Add Sound Effect"** bei einer Scene
2. Wähle MP3/WAV-Datei
3. Sound wird hochgeladen
4. Path wird in Scene gespeichert

### Sound Effect Settings
- **Volume:** 0-100% (Default: 50%)
- **Offset:** 0-100% (Timing innerhalb der Scene)
  - 0% = Anfang der Scene
  - 50% = Mitte der Scene
  - 100% = Ende der Scene

**Beispiel:**
- Scene Duration: 5 Sekunden
- Sound Effect Offset: 50%
- Sound startet bei **2.5 Sekunden**

### Sound Effect entfernen
1. Klicke auf Scene bearbeiten
2. Setze `sound_effect_path` auf `null` via API
3. (Momentan kein "Remove" Button in UI)

---

## 🎥 Preview & Export

### Preview erstellen
1. Erstelle Scenes
2. Wähle Settings (Voice, Music, Model, etc.)
3. Klicke auf **"▶ Preview"**

**Was passiert:**
1. **TTS Generation:** Audio für jede Scene
2. **Image Generation:** AI-Bilder (falls nicht gecached)
3. **Video Composition:** FFmpeg kombiniert Audio + Bilder
4. **Effects Application:** Visual Effects werden angewendet
5. **Music Mixing:** Background Music wird hinzugefügt
6. **Sound Effects:** Scene-spezifische Sounds werden eingefügt
7. **Speed Adjustment:** Video-Speed wird angewendet
8. **Final Export:** Video wird gespeichert

**Output:**
- Video-Player zeigt Preview
- Scenes zeigen Thumbnails
- Durations werden automatisch synchronisiert

### Export (Final Video)
**⚠️ Noch nicht implementiert!**

Geplante Features:
- Export zu 1080p
- Export zu 4K
- Custom Aspect Ratios (9:16, 16:9, 1:1)
- Watermark hinzufügen
- Upload to Queue (für Batch Creator)

---

## 💰 Kosten-Übersicht

### AI Image Generation

| Model | Kosten pro Bild | 100 Bilder | Empfehlung |
|-------|-----------------|------------|------------|
| Flux Schnell | $0.003 | $0.30 | ✅ **Default** |
| SDXL | $0.003 | $0.30 | ✅ Günstig |
| Flux Dev | $0.025 | $2.50 | ⚠️ Balanced |
| Flux Pro 1.1 | $0.04 | $4.00 | ⚠️ Premium |
| Recraft V3 | $0.04 | $4.00 | ⚠️ Premium |
| Flux Pro | $0.055 | $5.50 | ❌ Teuer |
| Ideogram V3 | $0.09 | $9.00 | ❌ Sehr teuer |

**Cost-Saving Tips:**
- Benutze **Flux Schnell** als Default (13x günstiger als Flux Pro 1.1!)
- Ändere Keywords nur wenn nötig (Cache nutzen!)
- Benutze **Regenerate** sparsam
- Teste mit 1-2 Scenes bevor du 100 erstellst

### TTS Generation

| Service | Kosten | Qualität | Empfehlung |
|---------|--------|----------|------------|
| Edge TTS (v7.2.3+) | **Kostenlos** ✅ | Gut | ✅ **Funktioniert!** |
| OpenAI TTS | ~$0.015/1000 chars | Sehr gut | ✅ Empfohlen |
| ElevenLabs | ~$0.30/1000 chars | Exzellent | ⚠️ Teuer |

**Beispiel-Rechnung:**
- 10 Scenes × 50 Wörter = 500 Wörter ≈ 2500 chars
- OpenAI TTS: $0.0375
- ElevenLabs: $0.75

### Beispiel-Projekt Kosten

**Projekt:** 20 Scenes, 3 Minuten Video

**Szenario 1 (Günstig):**
- AI Model: Flux Schnell ($0.003)
- TTS: Edge TTS (Free)
- **Total: ~$0.06**

**Szenario 2 (Empfohlen):**
- AI Model: Flux Schnell ($0.003)
- TTS: OpenAI ($0.05)
- **Total: ~$0.11**

**Szenario 3 (Premium):**
- AI Model: Flux Pro 1.1 ($0.04)
- TTS: ElevenLabs ($1.50)
- **Total: ~$2.30**

**Szenario 4 (Kostenexplosion vermeiden!):**
- AI Model: Ideogram V3 ($0.09)
- TTS: ElevenLabs ($1.50)
- 20 Scenes × $0.09 = $1.80
- **Total: ~$3.30**

---

## 🔧 Troubleshooting

### Preview funktioniert nicht
1. Check Backend Logs: `logs/backend.log`
2. Check Frontend Logs: Browser Console (F12)
3. Restart System: `bash stop_all.command && bash start_all.command`

### Bilder werden nicht generiert
1. Check REPLICATE_API_TOKEN in `.env`
2. Check Replicate Account Credits
3. Check Logs für "403" oder "Rate limit" Errors

### TTS Errors (403 Forbidden)
- Edge TTS manchmal instabil
- **Lösung:** Wechsel zu OpenAI TTS (`openai:alloy`)

### Cache löschen
```bash
# Backend Cache
cd backend
find . -type d -name "__pycache__" -exec rm -rf {} +

# Replicate Image Cache
rm -rf backend/replicate_cache/*
```

---

## 📂 Projekt-Struktur

```
video_editor_prototype/
├── backend/
│   ├── api/                    # API Endpoints
│   │   ├── projects.py        # Project Management
│   │   └── scenes.py          # Scene Management
│   ├── database/
│   │   ├── db_manager.py      # SQLite Database
│   │   └── editor_projects.db # Database File
│   ├── services/
│   │   ├── replicate_image_service.py  # AI Image Generation
│   │   ├── simple_video_generator.py   # Video Composition
│   │   ├── preview_generator.py        # Preview Orchestration
│   │   ├── translation_service.py      # Translation
│   │   └── keyword_extractor.py        # Visual Keyword Extraction
│   ├── output/
│   │   └── viral_autonomous/   # Generated Videos
│   ├── previews/               # Preview Videos
│   ├── replicate_cache/        # Cached AI Images
│   └── app.py                  # Flask Backend
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Header.jsx      # Top Bar (Settings)
│       │   ├── SceneList.jsx   # Scene Management
│       │   ├── VideoPreview.jsx # Video Player
│       │   └── ScriptEditor.jsx # Bulk Script Input
│       └── hooks/
│           └── useProject.js    # Project State Management
├── logs/
│   ├── backend.log
│   └── frontend.log
├── start_all.command           # Start Script
├── stop_all.command            # Stop Script
└── HANDBUCH.md                 # Dieses Handbuch
```

---

## 🎓 Best Practices

### 1. Kosten minimieren
- Benutze **Flux Schnell** als Default
- Ändere Model nur für finale Version
- Teste mit 1-2 Scenes zuerst
- Nutze Cache: Keywords wiederverwenden!

### 2. Workflow optimieren
- Schreibe kompletten Script zuerst
- Benutze **Auto-Create Scenes**
- Überprüfe visuelle Keywords
- Preview erstellen
- Fine-tuning mit Regenerate

### 3. Qualität sichern
- Benutze OpenAI TTS statt Edge TTS
- Background Music auf 7% lassen
- Video Speed 1.0x - 1.2x
- Effects sparsam einsetzen

### 4. Performance
- Nicht mehr als 50 Scenes pro Projekt
- Background Music < 5 MB
- Sound Effects < 1 MB pro Scene
- Cache regelmäßig löschen (> 1 GB)

---

## 🆘 Support

Bei Problemen oder Fragen:

1. **Logs checken:**
   - Backend: `logs/backend.log`
   - Frontend: Browser Console (F12)

2. **System neu starten:**
   ```bash
   bash stop_all.command
   bash start_all.command
   ```

3. **Database Reset (ACHTUNG: Löscht alle Projekte!):**
   ```bash
   rm backend/database/editor_projects.db
   cd backend && python -c "from database.db_manager import DatabaseManager; DatabaseManager().init_db()"
   ```

4. **Cache komplett löschen:**
   ```bash
   rm -rf backend/replicate_cache/*
   rm -rf backend/__pycache__
   rm -rf backend/services/__pycache__
   ```

---

**Version:** 1.0
**Letzte Aktualisierung:** 2025-01-24
**Autor:** Video Editor Prototype Team
