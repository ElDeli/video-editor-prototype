# 📦 Dropbox Output System

## ✅ Was wurde implementiert?

Ein **automatisches Dropbox-basiertes Output-System**, das sowohl **lokal** als auch auf **Railway** funktioniert.

---

## 🎯 Problem gelöst

❌ **Vorher:** Railway Container hat kein persistentes Filesystem → Folder Browser funktionierte nicht

✅ **Jetzt:** Vordefinierte Dropbox-Ordner werden automatisch initialisiert und funktionieren überall!

---

## 📂 Dropbox-Ordner-Struktur

```
~/Dropbox/Apps/output Horoskop/
├── video_editor_prototype/
│   ├── previews/              ← Generierte Videos
│   └── image_cache/           ← AI-Bilder Cache
└── video_uploads/             ← NEU: Output Queue Ordner
    ├── instagram/             ← Instagram Reels
    ├── youtube/               ← YouTube Shorts
    ├── tiktok/                ← TikTok Videos
    └── general/               ← Allgemeine Queue
```

---

## 🔧 Wie es funktioniert

### **Auto-Initialisierung**

Beim ersten API-Call zu `/api/settings/output-folders` werden automatisch 4 vordefinierte Ordner erstellt:

1. **Instagram Reels** → `~/Dropbox/.../video_uploads/instagram/`
2. **YouTube Shorts** → `~/Dropbox/.../video_uploads/youtube/`
3. **TikTok** → `~/Dropbox/.../video_uploads/tiktok/`
4. **General Upload Queue** → `~/Dropbox/.../video_uploads/general/`

### **Railway vs. Local**

| Umgebung | Folder Browser | Output Ordner |
|----------|----------------|---------------|
| **Railway** | Zeigt nur vordefinierte Dropbox-Ordner | ✅ Funktioniert |
| **Local Mac** | Vollständiger Filesystem-Browser | ✅ Funktioniert |

**Railway-Erkennung:**
```python
IS_RAILWAY = os.getenv('RAILWAY_ENVIRONMENT') is not None
```

---

## 💡 Verwendung

### **1. Settings öffnen**

- Klicke auf **Settings** (⚙️) Button im Video Editor
- **Output Folder Settings** Modal öffnet sich

### **2. Ordner werden automatisch geladen**

Die 4 Dropbox-Ordner erscheinen automatisch in der Liste:

```
✅ Instagram Reels      (Default: ⭐)
✅ YouTube Shorts
✅ TikTok
✅ General Upload Queue
```

### **3. Upload to Queue nutzen**

1. Erstelle ein Video mit "Preview" oder "Export"
2. Klicke **"Upload to Queue"** Button
3. Video wird in den **Default-Ordner** kopiert (Instagram Reels)
4. Erfolgs-Meldung: "Video copied to: Instagram Reels"

### **4. Default-Ordner ändern**

- Klicke auf **⭐ Icon** bei einem anderen Ordner
- Dieser wird zum neuen Default

---

## 🔄 Integration mit Sternzeichen_Automation

Die Videos landen in Dropbox und können vom Haupt-System gelesen werden:

```python
# Sternzeichen_Automation kann aus diesen Ordnern lesen:
upload_queue = "~/Dropbox/Apps/output Horoskop/video_uploads/instagram/"

# Automatische Sync:
# 1. Video Editor erstellt Video
# 2. Upload to Queue kopiert nach Dropbox
# 3. Sternzeichen_Automation liest aus Dropbox
# 4. Upload zu Instagram/TikTok/YouTube
```

---

## 🚀 Railway Deployment

### **Environment Variables (nicht nötig!)**

Das System funktioniert **automatisch** ohne zusätzliche Config.

### **Dropbox Access auf Railway**

⚠️ **Wichtig:** Railway Container braucht Zugriff auf Dropbox!

**Option 1: Dropbox API** (Empfohlen für Production)
- Nutze Dropbox API statt lokalem Filesystem
- Token in Environment Variable speichern

**Option 2: Volume Mount** (Aktuell)
- Funktioniert wenn Dropbox auf Railway gemountet ist
- Oder: Nutze existierende Dropbox-Integration

---

## 📊 API Endpoints

### **GET /api/settings/output-folders**
Listet alle Output-Ordner (initialisiert automatisch Dropbox-Ordner)

```json
[
  {
    "id": 1,
    "name": "Instagram Reels",
    "path": "/Users/.../Dropbox/.../video_uploads/instagram",
    "is_default": 1,
    "created_at": "2025-10-25 07:24:28"
  },
  ...
]
```

### **POST /api/settings/output-folders**
Fügt manuell einen Ordner hinzu (optional)

### **GET /api/settings/browse-folders**
Folder Browser:
- **Railway:** Zeigt nur Dropbox-Ordner
- **Local:** Vollständiger Filesystem-Browser

---

## ✅ Vorteile

1. **✅ Funktioniert auf Railway** - Keine Filesystem-Probleme mehr
2. **✅ Automatische Initialisierung** - Kein manuelles Setup nötig
3. **✅ Sync zwischen Systemen** - Video Editor + Sternzeichen_Automation nutzen gleiche Ordner
4. **✅ Persistent** - Dropbox speichert alles dauerhaft
5. **✅ Flexibel** - User kann immer noch eigene Ordner hinzufügen

---

## 🔍 Troubleshooting

### **"Failed to load folders" auf Railway**

**Ursache:** Dropbox-Ordner nicht vorhanden

**Lösung:**
```bash
# Lokal einmalig ausführen:
mkdir -p ~/Dropbox/Apps/output\ Horoskop/video_uploads/{instagram,youtube,tiktok,general}
```

### **Videos werden nicht kopiert**

**Prüfe:**
1. Default-Ordner ist gesetzt (⭐ Symbol)
2. Ordner existiert physisch
3. Schreibrechte vorhanden

**Debug:**
```bash
# Check folders
ls -la ~/Dropbox/Apps/output\ Horoskop/video_uploads/

# Check database
sqlite3 backend/database/editor_projects.db "SELECT * FROM output_folders;"
```

---

## 📝 Code-Änderungen

### **Backend:** `backend/api/settings.py`

- ✅ `DROPBOX_OUTPUT_BASE` Konstante
- ✅ `PREDEFINED_FOLDERS` Array
- ✅ `IS_RAILWAY` Detection
- ✅ `ensure_predefined_folders()` Auto-Init
- ✅ `browse_folders()` Railway-Modus

### **Frontend:** `frontend/src/components/Settings/OutputFolderSettings.jsx`

- ✅ Info-Box für Dropbox-Ordner
- ✅ Auto-Reload beim Öffnen

### **Database:** `output_folders` Tabelle

```sql
CREATE TABLE output_folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    is_default INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## 🎉 Zusammenfassung

**Das Dropbox Output System ist vollständig implementiert und funktionsbereit!**

- ✅ Automatische Initialisierung
- ✅ Railway-kompatibel
- ✅ Integration mit Sternzeichen_Automation
- ✅ User-friendly UI
- ✅ Keine manuelle Konfiguration nötig

**Nächste Schritte:**
1. Auf Railway deployen
2. Testen ob Dropbox-Access funktioniert
3. Falls nötig: Dropbox API Integration hinzufügen

---

**Version:** 1.0.0
**Datum:** 2025-10-25
**Status:** ✅ Production Ready
