"""
Replicate AI Image Service
Generates images using Replicate API for scene backgrounds
"""
import os
import replicate
import requests
from pathlib import Path
from typing import Optional
import hashlib
from services.dropbox_storage import storage

class ReplicateImageService:
    def __init__(self):
        self.api_token = os.getenv('REPLICATE_API_TOKEN')
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN not found in environment variables")

        # Set API token for replicate
        os.environ['REPLICATE_API_TOKEN'] = self.api_token

        # Use hybrid storage for image cache (Dropbox on Mac, /tmp cache on Railway)
        self.cache_dir = storage.get_save_dir('image_cache')

        # Available AI Models - Map from friendly names to Replicate model IDs
        self.models = {
            'flux-pro-1.1': 'black-forest-labs/flux-1.1-pro',  # BEST QUALITY (~$0.04/img, 20s)
            'flux-pro': 'black-forest-labs/flux-pro',  # Very good (~$0.055/img, 25s)
            'flux-dev': 'black-forest-labs/flux-dev',  # Good balance (~$0.025/img, 15s)
            'flux-schnell': 'black-forest-labs/flux-schnell',  # Fast & cheap (~$0.003/img, 10s)
            'ideogram-v3': 'ideogram-ai/ideogram-v3-quality',  # TEXT IN IMAGES! (~$0.09/img, 25s)
            'recraft-v3': 'recraft-ai/recraft-v3',  # STYLE VARIETY (~$0.04/img, 20s)
            'sdxl': 'stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b'  # Legacy
        }

        # Default model (Flux Dev = Best balance of quality & speed at $0.025/img)
        # Changed from flux-schnell ($0.003) for 3x better image quality
        self.default_model = 'flux-dev'

        # German to English keyword translation for better AI results
        self.translations = {
            # People & Professions
            'frau': 'woman portrait',
            'frauen': 'women',
            'mann': 'man portrait',
            'männer': 'men',
            'kind': 'child',
            'kinder': 'children',
            'baby': 'baby',
            'mädchen': 'girl',
            'junge': 'boy',
            'wissenschaftler': 'scientist in laboratory',
            'forscher': 'researcher',
            'arzt': 'doctor',
            'ärztin': 'female doctor',

            # Science & Technology
            'kernreaktor': 'nuclear reactor',
            'reaktor': 'reactor facility',
            'atom': 'atom structure',
            'radioaktiv': 'radioactive warning symbol',
            'strahlung': 'radiation',
            'rauchmelder': 'smoke detector',
            'glühbirne': 'light bulb',
            'experiment': 'scientific experiment',

            # Space & Astronomy
            'galaxie': 'spiral galaxy in space',
            'planet': 'planet in space',
            'stern': 'bright star',
            'sterne': 'starry sky',
            'universum': 'universe cosmos nebula',
            'weltall': 'outer space',
            'mond': 'moon',
            'sonne': 'sun',
            'urknall': 'big bang explosion',
            'schwarzes loch': 'black hole',

            # Nature & Elements
            'feuer': 'fire flames',
            'wasser': 'water ocean waves',
            'baum': 'tree',
            'blume': 'flower',
            'pflanze': 'plant',
            'wald': 'forest',
            'berg': 'mountain',
            'strand': 'beach',

            # Locations
            'haus': 'house',
            'gartenhaus': 'garden shed',
            'garten': 'garden',
            'stadt': 'city',
            'nachbarschaft': 'neighborhood',
            'labor': 'laboratory',

            # Emotions & Abstract
            'liebe': 'love hearts',
            'angst': 'fear',
            'freude': 'joy happiness',
            'dunkel': 'dark atmosphere',
            'licht': 'bright light',
            'explosion': 'explosion blast',

            # Energy & Movement
            'energie': 'powerful energy flowing cosmic force',
            'kraft': 'strength force power radiating',
            'macht': 'mighty power authority',
            'stärke': 'strength strong powerful',
            'bewegung': 'dynamic movement motion flowing',
            'dynamik': 'dynamic energy motion',
            'fließen': 'flowing liquid energy',

            # Generic themes for scenes without specific keywords
            'willkommen': 'welcoming open arms cosmic gateway',
            'dankbarkeit': 'gratitude appreciation golden light',
            'social-media': 'social media connection digital network',
            'leben': 'vibrant life force living energy',
            'mut': 'courage bravery strength determination',
            'schatten': 'shadows darkness mysterious',
            'kampf': 'battle warrior strength',
            'schöpfung': 'creation genesis cosmic birth',
            'pfad': 'path journey road forward',
            'wahrheit': 'truth honesty clarity light',
            'kosmisch': 'cosmic mystical universe ethereal',
        }

    def generate_image(self, keyword: str, width: int = 608, height: int = 1080, model: str = None) -> Optional[str]:
        """
        Generate image from keyword using Replicate AI

        Args:
            keyword: German keyword or visual phrase (e.g., "universum", "feuer")
            width: Image width (default 608 for preview)
            height: Image height (default 1080 for 9:16)
            model: AI model to use (flux-pro-1.1, flux-dev, flux-schnell, sdxl)

        Returns:
            Path to cached image file, or None if generation failed
        """
        try:
            # Use default model if none specified
            if not model:
                model = self.default_model

            # Validate model
            if model not in self.models:
                print(f"⚠️ Unknown model '{model}', using default: {self.default_model}")
                model = self.default_model

            # Get Replicate model ID
            model_id = self.models[model]

            # Check cache first (include model in cache key)
            cache_key = self._get_cache_key(keyword, width, height, model)
            cache_filename = f"{cache_key}.jpg"
            cache_rel_path = f"image_cache/{cache_filename}"

            # Check if cached image exists (works on both Mac and Railway)
            if storage.file_exists(cache_rel_path):
                # Get full path for local access
                cached_path = self.cache_dir / cache_filename

                # On Railway: If file exists in Dropbox but not locally, download it
                if not cached_path.exists():
                    print(f"📥 Downloading cached image from Dropbox: {cache_filename}")
                    try:
                        image_data = storage.get_file_content(cache_rel_path)
                        cached_path.parent.mkdir(parents=True, exist_ok=True)
                        cached_path.write_bytes(image_data)
                        print(f"✓ Downloaded from Dropbox to local cache")
                    except Exception as e:
                        print(f"⚠️ Failed to download from Dropbox: {e}")
                        # Continue to regenerate
                        pass
                    else:
                        print(f"✓ Using cached image for '{keyword}' (model: {model})")
                        return str(cached_path)
                else:
                    print(f"✓ Using cached image for '{keyword}' (model: {model})")
                    return str(cached_path)

            # Translate keyword to English for better results
            prompt = self._create_prompt(keyword)

            # Negative prompt for better quality
            negative_prompt = "blurry, low quality, distorted, deformed, ugly, bad anatomy, watermark, text, signature, logo, cartoon, anime, 3d render, illustration"

            print(f"🎨 Generating image for '{keyword}' (model: {model}, prompt: '{prompt[:60]}...')...")

            # Build input parameters based on model
            if model == 'sdxl':
                # SDXL uses different parameters
                input_params = {
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": width,
                    "height": height,
                    "num_outputs": 1,
                    "guidance_scale": 7.5,
                    "num_inference_steps": 25,
                    "output_format": "jpg",  # JPEG for compatibility
                    "output_quality": 90
                }
            elif model == 'ideogram-v3':
                # Ideogram V3 - TEXT IN IMAGES! (~$0.09/img)
                # Note: ideogram-v3 does NOT support output_format parameter
                input_params = {
                    "prompt": prompt,
                    "aspect_ratio": "9:16",  # Vertical format (enum only!)
                    "magic_prompt_option": "Auto",  # Auto-enhance prompts
                    "style_type": "Auto"  # Auto-select best style
                }
            elif model == 'recraft-v3':
                # Recraft V3 - STYLE VARIETY (~$0.04/img)
                input_params = {
                    "prompt": prompt,
                    "aspect_ratio": "9:16",  # Vertical format (enum only!)
                    "style": "any"  # Let model choose best style
                }
            else:
                # Flux models (flux-pro-1.1, flux-pro, flux-dev, flux-schnell)
                # Use 9:16 for vertical video format (closest to 608:1080)
                input_params = {
                    "prompt": prompt,
                    "aspect_ratio": "9:16",  # Vertical format for Instagram/TikTok
                    "output_format": "jpg",  # ⭐ JPEG for compatibility with cache system
                    "output_quality": 90,
                    "prompt_upsampling": True,  # ⭐ AUTO-ENHANCE PROMPTS FOR BETTER QUALITY!
                    "safety_tolerance": 2  # ⭐ Less restrictive filtering (1=strict, 6=permissive)
                }

                # Add guidance for Pro models (not supported on Schnell)
                if model in ['flux-pro-1.1', 'flux-pro', 'flux-dev']:
                    input_params["guidance"] = 3.5  # ⭐ Optimal prompt adherence

            # Generate image using Replicate
            output = replicate.run(model_id, input=input_params)

            # Download image
            if output and len(output) > 0:
                image_url = output[0] if isinstance(output, list) else output
                image_data = requests.get(image_url).content

                # Save to cache using hybrid storage (Dropbox + local cache on Railway)
                saved_path = storage.save_file(cache_rel_path, image_data)

                print(f"✓ Image generated and cached: {saved_path}")
                return str(saved_path)
            else:
                print(f"✗ No image generated for '{keyword}'")
                return None

        except Exception as e:
            print(f"✗ Error generating image for '{keyword}': {e}")
            return None

    def _create_prompt(self, keyword: str) -> str:
        """
        Create optimized prompt from German keyword or dynamic phrase

        DYNAMIC MODE: If keyword is not in translation dict, treat it as
        a dynamic phrase extracted from the sentence itself.

        Args:
            keyword: German keyword or dynamic visual concept phrase

        Returns:
            English prompt optimized for image generation
        """
        keyword_lower = keyword.lower().strip()

        # Check if it's a known keyword with translation
        if keyword_lower in self.translations:
            base_prompt = self.translations[keyword_lower]
        else:
            # DYNAMIC MODE: Use the phrase directly (assumed to be German)
            # The AI can understand German, but we add context to improve results
            base_prompt = f"{keyword_lower}"

            # Add contextual hints for better astrological/mystical content
            # These help guide the AI to create appropriate imagery
            if any(word in keyword_lower for word in ['widder', 'sternzeichen', 'horoskop', 'zodiac']):
                base_prompt = f"astrological zodiac sign {base_prompt} mystical cosmic symbol constellation"
            elif any(word in keyword_lower for word in ['energie', 'kraft', 'macht', 'stärke', 'power']):
                # Energy/power concepts - make them visually dramatic
                base_prompt = f"powerful {base_prompt} glowing energy radiating force dynamic movement"
            elif any(word in keyword_lower for word in ['feuer', 'fire', 'flamme']):
                # Fire concepts - vivid flames
                base_prompt = f"{base_prompt} vivid flames burning bright intense fire"
            elif any(word in keyword_lower for word in ['mut', 'courage', 'stärke', 'strength']):
                # Courage/strength - heroic imagery
                base_prompt = f"{base_prompt} heroic strong determined powerful warrior energy"
            elif len(keyword_lower.split()) > 1:
                # Multi-word phrase: enhance with visual descriptors to make it SPECIFIC
                base_prompt = f"realistic depiction of {base_prompt} cinematic detailed scene"

        # NO style modifiers needed - Flux prompt_upsampling handles this automatically!
        # Just return the clean prompt from GPT or translation
        return base_prompt

    def _get_cache_key(self, keyword: str, width: int, height: int, model: str = None) -> str:
        """Generate cache key from parameters"""
        if not model:
            model = self.default_model
        key_string = f"{keyword}_{width}_{height}_{model}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def get_thumbnail(self, keyword: str) -> Optional[str]:
        """
        Get small thumbnail for preview (faster generation)

        Args:
            keyword: German keyword

        Returns:
            Path to thumbnail image
        """
        # Generate smaller image for thumbnails
        return self.generate_image(keyword, width=304, height=540)
