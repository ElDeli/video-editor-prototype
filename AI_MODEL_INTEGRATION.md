# 🤖 AI Model Integration - Technical Documentation

**Version:** 2.0.0
**Last Updated:** 2025-10-27
**System Status:** ✅ 7 AI Models Active

---

## Übersicht

Dieses Dokument erklärt **genau**, wie die 7 AI Image Models in den Video Editor integriert sind und wie das System funktioniert.

**Aktuelle Models:**
- Flux Schnell (DEFAULT - $0.003/img)
- Flux Dev, Flux Pro, Flux Pro 1.1
- Ideogram V3 (Text in images!)
- Recraft V3 (Style variety)
- SDXL (Budget alternative)

---

## 📂 Betroffene Dateien

### 1. Backend Core Service
- `backend/services/replicate_image_service.py` - **Hauptservice** für AI Image Generation

### 2. Video Generation
- `backend/services/simple_video_generator.py` - Übergibt Model-Parameter an Image Service
- `backend/services/preview_generator.py` - Orchestriert Preview mit Model-Parameter

### 3. API Endpoints
- `backend/api/projects.py` - Project Management + Preview Generation
- `backend/api/scenes.py` - Scene Management + Image Regeneration

### 4. Database
- `backend/database/db_manager.py` - Database Schema mit `ai_image_model` Spalte

### 5. Frontend
- `frontend/src/components/Header.jsx` - Model Selection Dropdown

---

## 🔧 **Schritt-für-Schritt Integration**

### **STEP 1: Replicate Image Service erweitern**

**Datei:** `backend/services/replicate_image_service.py`

#### **1.1 Model Registry definieren**

```python
class ReplicateImageService:
    def __init__(self):
        # Default Model (WICHTIG: flux-schnell = günstig!)
        self.default_model = 'flux-schnell'

        # Model Registry: Shortname → Replicate Model Path
        self.models = {
            # Flux Models (Black Forest Labs)
            'flux-schnell': 'black-forest-labs/flux-schnell',      # $0.003/img - FASTEST
            'flux-dev': 'black-forest-labs/flux-dev',              # $0.025/img
            'flux-pro': 'black-forest-labs/flux-pro',              # $0.055/img
            'flux-pro-1.1': 'black-forest-labs/flux-1.1-pro',      # $0.04/img

            # Ideogram (Text in Images!)
            'ideogram-v3': 'ideogram-ai/ideogram-v2-turbo',        # $0.09/img

            # Recraft (Style Variety)
            'recraft-v3': 'recraft-ai/recraft-v3',                 # $0.04/img

            # SDXL (Cheap & Fast)
            'sdxl': 'stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b'  # $0.003/img
        }
```

**WICHTIG:**
- **Shortname** (z.B. `'flux-schnell'`) = Wird in UI und Database verwendet
- **Model Path** (z.B. `'black-forest-labs/flux-schnell'`) = Replicate API Pfad

#### **1.2 Model-Specific Parameters bauen**

**KRITISCH:** Jedes Model hat **andere Parameter**! Du MUSST die Replicate API Docs checken!

```python
def generate_image(self, keyword, width=608, height=1080, model=None):
    # Model Selection
    if model is None:
        model = self.default_model

    # Get Replicate Model Path
    model_id = self.models.get(model)
    if not model_id:
        raise ValueError(f"Unknown model: {model}")

    # Build Input Parameters (MODEL-SPECIFIC!)
    if model == 'sdxl':
        # SDXL - Old Model with custom dimensions
        input_params = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_inference_steps": 25,
            "output_format": "jpg",
            "output_quality": 90
        }

    elif model == 'ideogram-v3':
        # Ideogram V3 - TEXT IN IMAGES!
        # ⚠️ NO output_format parameter!
        # ⚠️ aspect_ratio must be ENUM (not custom like "608:1080")!
        input_params = {
            "prompt": prompt,
            "aspect_ratio": "9:16",              # ← ENUM: "9:16", "16:9", "1:1"
            "magic_prompt_option": "Auto",       # Auto-enhance prompts
            "style_type": "Auto"                 # Auto-select style
        }

    elif model == 'recraft-v3':
        # Recraft V3 - STYLE VARIETY
        # ⚠️ NO output_format parameter!
        input_params = {
            "prompt": prompt,
            "aspect_ratio": "9:16",              # ← ENUM
            "style": "any"                       # Let model choose
        }

    else:
        # Flux Models (flux-pro-1.1, flux-pro, flux-dev, flux-schnell)
        # ⭐ These are the MAIN models - most flexible!
        input_params = {
            "prompt": prompt,
            "aspect_ratio": "9:16",              # Vertical format
            "output_format": "jpg",              # ⭐ JPEG (not WebP!)
            "output_quality": 90,
            "prompt_upsampling": True            # ⭐ AUTO-ENHANCE PROMPTS!
        }

    # Run Replicate API
    output = replicate.run(model_id, input=input_params)

    # Download & Cache Image
    # ... (siehe unten)
```

**KEY LEARNINGS:**

1. **aspect_ratio vs width/height:**
   - Neue Models (Flux, Ideogram, Recraft): `aspect_ratio: "9:16"` (ENUM!)
   - Alte Models (SDXL): `width: 608, height: 1080` (Custom)

2. **output_format:**
   - Flux Models: `output_format: "jpg"` ✅
   - Ideogram/Recraft: **KEIN** output_format Parameter! ❌

3. **Prompt Enhancement:**
   - Flux: `prompt_upsampling: True` → AI verbessert Prompt automatisch!
   - Ideogram: `magic_prompt_option: "Auto"` → Ähnliche Funktion
   - Recraft: Keine Prompt Enhancement

---

### **STEP 2: Cache System**

**KRITISCH:** Cache muss **Model** in Hash einbeziehen!

```python
def _get_cache_key(self, keyword, width, height, model):
    """
    Generate cache key including MODEL parameter

    This ensures same keyword with different models
    generates DIFFERENT images!
    """
    cache_string = f"{keyword}_{width}_{height}_{model}"
    return hashlib.md5(cache_string.encode()).hexdigest()

def _check_cache(self, cache_key):
    """Check if image exists in cache"""
    cache_file = self.cache_dir / f"{cache_key}.jpg"
    if cache_file.exists():
        return str(cache_file)
    return None
```

**Beispiel:**
- `"Pferd"` + `608` + `1080` + `"flux-schnell"` → Hash: `abc123.jpg`
- `"Pferd"` + `608` + `1080` + `"flux-pro-1.1"` → Hash: `xyz789.jpg`

→ **2 verschiedene Bilder** im Cache!

---

### **STEP 3: Database Schema**

**Datei:** `backend/database/db_manager.py`

#### **3.1 Projects Table erweitern**

```python
def init_db(self):
    # Add ai_image_model column to projects table
    try:
        cursor.execute("ALTER TABLE projects ADD COLUMN ai_image_model TEXT DEFAULT 'flux-schnell'")
        conn.commit()
    except sqlite3.OperationalError:
        # Column already exists
        pass
```

#### **3.2 Update Function erweitern**

```python
def update_project(self, project_id, project_data):
    # Allowed fields for updates
    fields = []
    values = []

    # Add ai_image_model to allowed fields
    for key in ['tts_voice', 'background_music_path', 'ai_image_model']:  # ← HIER!
        if key in project_data:
            fields.append(f'{key} = ?')
            values.append(project_data[key])

    # Execute update
    if fields:
        query = f'UPDATE projects SET {", ".join(fields)} WHERE id = ?'
        cursor.execute(query, values)
```

---

### **STEP 4: API Endpoints**

#### **4.1 Project Update Endpoint**

**Datei:** `backend/api/projects.py`

```python
@projects_bp.route('/projects/<int:project_id>', methods=['PATCH', 'PUT'])
def update_project(project_id):
    data = request.get_json()

    # Build updates dict
    updates = {}

    # Add ai_image_model if present
    if 'ai_image_model' in data:
        updates['ai_image_model'] = data['ai_image_model']

    # Apply updates
    if updates:
        db.update_project(project_id, updates)

    return jsonify(db.get_project(project_id))
```

#### **4.2 Preview Generation mit Model**

```python
@projects_bp.route('/projects/<int:project_id>/preview', methods=['POST'])
def generate_preview(project_id):
    project = db.get_project(project_id)
    scenes = db.get_project_scenes(project_id)

    # Get AI image model from project (DEFAULT: flux-schnell)
    ai_image_model = project.get('ai_image_model', 'flux-schnell')

    # Pass to preview generator
    result = preview_gen.generate_preview(
        project_id,
        scenes,
        ai_image_model=ai_image_model  # ← HIER!
    )

    return jsonify(result)
```

#### **4.3 Scene Image Regeneration**

**Datei:** `backend/api/scenes.py`

```python
@scenes_bp.route('/scenes/<int:scene_id>/regenerate-image', methods=['POST'])
def regenerate_scene_image(scene_id):
    scene = db.get_scene(scene_id)
    project = db.get_project(scene.get('project_id'))

    # Get AI model from project
    ai_image_model = project.get('ai_image_model', 'flux-schnell')

    # Add variation to force new image
    original_keyword = scene.get('background_value', 'cosmic')
    variation_num = random.randint(1, 100)
    new_keyword = f"{original_keyword} variation {variation_num}"

    # Generate new image with current model
    image_path = image_service.generate_image(
        new_keyword,
        width=608,
        height=1080,
        model=ai_image_model  # ← HIER!
    )

    # Update scene
    db.update_scene(scene_id, {'background_value': new_keyword})

    return jsonify({'success': True, 'new_keyword': new_keyword})
```

---

### **STEP 5: Video Generator Integration**

**Datei:** `backend/services/simple_video_generator.py`

```python
class SimpleVideoGenerator:
    def generate_video(self, scenes, project_id, resolution='preview',
                      ai_image_model='flux-schnell'):  # ← DEFAULT PARAMETER

        scene_videos = []

        for idx, scene in enumerate(scenes):
            # Create scene video with AI model
            scene_video = self._create_scene_video(
                scene,
                width,
                height,
                idx,
                ai_image_model=ai_image_model  # ← ÜBERGABE
            )
            scene_videos.append(scene_video)

        # ... rest of video composition

    def _create_scene_video(self, scene, width, height, idx,
                           ai_image_model='flux-schnell'):

        # Get background keyword
        background_value = scene.get('background_value', 'cosmic energy')

        # Generate AI image with specified model
        bg_image = self.image_service.generate_image(
            background_value,
            width=width,
            height=height,
            model=ai_image_model  # ← HIER!
        )

        # ... rest of scene video creation
```

---

### **STEP 6: Frontend Integration**

**Datei:** `frontend/src/components/Header.jsx`

#### **6.1 State Management**

```javascript
function Header({ onPreviewGenerated }) {
  const { project } = useProject()

  // AI Model State (DEFAULT: flux-schnell)
  const [aiImageModel, setAiImageModel] = useState('flux-schnell')

  // Load from project when available
  useEffect(() => {
    if (project && project.ai_image_model) {
      setAiImageModel(project.ai_image_model)
    }
  }, [project])

  // Handle model change
  const handleAiImageModelChange = async (e) => {
    const newModel = e.target.value
    setAiImageModel(newModel)

    if (project) {
      try {
        await api.updateProject(project.id, { ai_image_model: newModel })
      } catch (error) {
        console.error('Failed to update AI image model:', error)
      }
    }
  }

  // ... rest of component
}
```

#### **6.2 Dropdown UI**

```jsx
<select
  value={aiImageModel}
  onChange={handleAiImageModelChange}
  disabled={!project || loading}
  className="px-3 py-2 bg-dark border border-gray-600 rounded-lg text-sm"
  title="AI Model for Scene Backgrounds"
>
  <option value="flux-pro-1.1">🎨 Flux Pro 1.1 - $0.04/img (Best Quality)</option>
  <option value="flux-pro">🎨 Flux Pro - $0.055/img (Very Good)</option>
  <option value="flux-dev">🎨 Flux Dev - $0.025/img (Balanced)</option>
  <option value="flux-schnell">⚡ Flux Schnell - $0.003/img (Fast)</option>
  <option value="ideogram-v3">📝 Ideogram V3 - $0.09/img (Text in Images)</option>
  <option value="recraft-v3">🎭 Recraft V3 - $0.04/img (Style Variety)</option>
  <option value="sdxl">💰 SDXL - $0.003/img (Cheap)</option>
</select>
```

---

## 🎯 **Integration für Batch Creator**

### **Wo du Änderungen machen musst:**

#### **1. Viral Trend Creator (`viral_trend_creator_autonomous.py`)**

Suche nach der Image Generation Funktion:

```python
# VORHER:
def generate_background_image(keyword):
    # Hardcoded SDXL
    image_path = replicate_service.generate_image(keyword, width=608, height=1080)
    return image_path

# NACHHER:
def generate_background_image(keyword, ai_model='flux-schnell'):
    # Model-aware generation
    image_path = replicate_service.generate_image(
        keyword,
        width=608,
        height=1080,
        model=ai_model  # ← PARAMETER ÜBERGEBEN
    )
    return image_path
```

#### **2. Batch Queue Processor (`viral_queue_processor.py`)**

```python
# VORHER:
def process_batch(batch):
    for scene in batch['scenes']:
        image = generate_background_image(scene['keyword'])

# NACHHER:
def process_batch(batch):
    # Read AI model from batch config
    ai_model = batch.get('ai_image_model', 'flux-schnell')  # DEFAULT!

    for scene in batch['scenes']:
        image = generate_background_image(
            scene['keyword'],
            ai_model=ai_model  # ← ÜBERGEBEN
        )
```

#### **3. Web Frontend Batch Creator (`web_frontend/app.py`)**

```python
@app.route('/create_batch', methods=['POST'])
def create_batch():
    data = request.json

    # NEW: Get AI model from form
    ai_model = data.get('ai_image_model', 'flux-schnell')

    batch = {
        'script': data['script'],
        'tts_voice': data.get('tts_voice', 'de-DE-KatjaNeural'),
        'ai_image_model': ai_model,  # ← NEU!
        'created_at': datetime.now().isoformat()
    }

    # Save to Dropbox State
    save_batch_to_queue(batch)

    return jsonify({'success': True})
```

#### **4. Batch Creator UI (HTML)**

```html
<!-- Add AI Model Selector to Batch Creator Form -->
<div class="form-group">
    <label for="aiModel">AI Image Model:</label>
    <select id="aiModel" name="ai_image_model" class="form-control">
        <option value="flux-schnell" selected>⚡ Flux Schnell - $0.003/img (Fast)</option>
        <option value="flux-dev">🎨 Flux Dev - $0.025/img (Balanced)</option>
        <option value="flux-pro-1.1">🎨 Flux Pro 1.1 - $0.04/img (Premium)</option>
        <option value="ideogram-v3">📝 Ideogram V3 - $0.09/img (Text in Images)</option>
        <option value="recraft-v3">🎭 Recraft V3 - $0.04/img (Styles)</option>
        <option value="sdxl">💰 SDXL - $0.003/img (Cheap)</option>
    </select>
    <small class="form-text text-muted">
        Default: Flux Schnell (günstig & schnell)
    </small>
</div>
```

---

## 🔍 **Replicate API Docs checken**

**KRITISCH:** Bevor du ein neues Model hinzufügst, MUSST du die Docs lesen!

### **Beispiel: Flux Schnell Docs**

1. Gehe zu: https://replicate.com/black-forest-labs/flux-schnell
2. Scrolle zu "API"
3. Schaue "Inputs":

```json
{
  "prompt": "...",
  "aspect_ratio": "9:16",       // ← ENUM! Nicht custom!
  "num_outputs": 1,
  "output_format": "jpg",       // ← "jpg", "png", "webp"
  "output_quality": 90,
  "prompt_upsampling": true
}
```

### **Beispiel: Ideogram V3 Docs**

1. Gehe zu: https://replicate.com/ideogram-ai/ideogram-v2-turbo
2. Schaue "Inputs":

```json
{
  "prompt": "...",
  "aspect_ratio": "9:16",       // ← ENUM!
  "magic_prompt_option": "Auto", // ← Unique to Ideogram!
  "style_type": "Auto"          // ← Unique to Ideogram!
  // ⚠️ NO output_format!
}
```

---

## ⚠️ **Häufige Fehler & Lösungen**

### **Error 1: Invalid aspect_ratio**
```
Error: aspect_ratio must be one of: 1:1, 16:9, 9:16, ...
```

**Problem:** Du hast `"608:1080"` übergeben statt `"9:16"`

**Lösung:**
```python
# FALSCH:
input_params = {"aspect_ratio": "608:1080"}

# RICHTIG:
input_params = {"aspect_ratio": "9:16"}
```

### **Error 2: Unknown parameter 'output_format'**
```
Error: Unexpected parameter: output_format
```

**Problem:** Ideogram/Recraft unterstützen kein `output_format`

**Lösung:**
```python
# FALSCH:
if model == 'ideogram-v3':
    input_params = {"output_format": "jpg"}  # ❌

# RICHTIG:
if model == 'ideogram-v3':
    input_params = {"aspect_ratio": "9:16"}  # ✅ Kein output_format!
```

### **Error 3: Cache-Miss trotz gleichem Keyword**
```
Expected cached image, but generated new one
```

**Problem:** Model nicht in Cache-Key einbezogen

**Lösung:**
```python
# FALSCH:
cache_key = f"{keyword}_{width}_{height}"

# RICHTIG:
cache_key = f"{keyword}_{width}_{height}_{model}"
```

---

## 📊 **Testing Checklist**

Bevor du ein neues Model ins Production nimmst:

- [ ] Replicate API Docs gelesen
- [ ] Input Parameters korrekt (Docs checken!)
- [ ] Cache-Key enthält Model-Name
- [ ] Test-Image generiert (1 Bild)
- [ ] Cache funktioniert (2x selbes Keyword = 1x API Call)
- [ ] Model-Wechsel funktioniert (Dropdown → Preview)
- [ ] Kosten korrekt (Check Replicate Dashboard)
- [ ] Database Default gesetzt
- [ ] Frontend Dropdown aktualisiert
- [ ] Error Handling implementiert

---

## 💡 **Best Practices**

### 1. **Default Model = flux-schnell**
- Günstig ($0.003/img)
- Schnell (~2-5s pro Bild)
- Gute Qualität für Prototyping

### 2. **Model Registry zentral**
- Alle Models in `replicate_image_service.py`
- Shortnames konsistent (lowercase, kebab-case)
- Kommentare mit Kosten

### 3. **Cache immer mit Model**
- `cache_key = f"{keyword}_{width}_{height}_{model}"`
- Verhindert falsche Bilder
- Ermöglicht A/B Testing

### 4. **Error Handling**
```python
try:
    output = replicate.run(model_id, input=input_params)
except Exception as e:
    print(f"✗ Error generating image with {model}: {e}")
    # Fallback to default model?
    return None
```

### 5. **Logging für Debugging**
```python
print(f"🎨 Generating image with {model}")
print(f"   Keyword: {keyword}")
print(f"   Params: {input_params}")
print(f"   Cost: ${cost}/img")
```

---

## 📝 **Zusammenfassung für Batch Creator**

### **Minimal Changes:**

1. **`replicate_image_service.py`** - Bereits done! ✅
2. **`viral_trend_creator_autonomous.py`**:
   ```python
   def generate_scene_video(scene, ai_model='flux-schnell'):
       image = image_service.generate_image(
           scene['keyword'],
           width=608,
           height=1080,
           model=ai_model
       )
   ```

3. **`viral_queue_processor.py`**:
   ```python
   batch = load_batch_from_queue()
   ai_model = batch.get('ai_image_model', 'flux-schnell')

   for scene in batch['scenes']:
       generate_scene_video(scene, ai_model=ai_model)
   ```

4. **`web_frontend/app.py`**:
   ```python
   @app.route('/create_batch', methods=['POST'])
   def create_batch():
       batch = {
           'script': data['script'],
           'ai_image_model': data.get('ai_image_model', 'flux-schnell')
       }
   ```

5. **UI HTML**: Dropdown hinzufügen (siehe oben)

**Das war's!** 🎉

---

**Version:** 1.0
**Letzte Aktualisierung:** 2025-01-24
