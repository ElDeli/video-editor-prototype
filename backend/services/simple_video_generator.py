"""
Simple Video Generator using FFmpeg directly
Bypasses MoviePy concatenation issues
"""
import os
import sys
import subprocess
from pathlib import Path
from gtts import gTTS
import tempfile
from PIL import Image, ImageDraw, ImageFont
import json
import asyncio
import edge_tts
from services.replicate_image_service import ReplicateImageService
from services.video_effects import VideoEffects
from services.elevenlabs_voice_service import ElevenLabsVoiceService
from services.openai_tts_service import OpenAITTSService
from services.dropbox_storage import storage

class SimpleVideoGenerator:
    def __init__(self, tts_voice='de-DE-KatjaNeural'):
        # Output directory for generated videos (hybrid storage)
        self.output_dir = storage.get_save_dir('previews')
        print(f"🎬 SimpleVideoGenerator initialized with output_dir: {self.output_dir}", file=sys.stderr, flush=True)

        self.temp_dir = Path(tempfile.gettempdir()) / "video_editor_simple"
        self.temp_dir.mkdir(exist_ok=True)
        self.tts_voice = tts_voice  # Can be Edge, ElevenLabs, or OpenAI voice

        # Initialize Replicate image service (REQUIRED)
        self.image_service = ReplicateImageService()

        # Initialize TTS services
        self.elevenlabs_service = ElevenLabsVoiceService()
        self.openai_tts_service = OpenAITTSService()

    def generate_video(self, scenes, project_id, resolution='preview', background_music_path=None, background_music_volume=7, video_speed=1.0, ai_image_model='flux-dev', font_size=80):
        """Generate video using FFmpeg concat demuxer"""
        if not scenes:
            raise ValueError("No scenes to generate")

        # Set resolution
        if resolution == 'preview':
            width, height = 608, 1080
        else:
            width, height = 1080, 1920

        scene_videos = []
        scene_timings = []  # Track actual timings

        print(f"\n{'='*80}", file=sys.stderr, flush=True)
        print(f"🎬 VIDEO GENERATION - Scene Order & Durations", file=sys.stderr, flush=True)
        print(f"{'='*80}", file=sys.stderr, flush=True)

        # Process each scene
        for idx, scene in enumerate(scenes):
            print(f"\n📝 Scene {idx + 1}/{len(scenes)} (ID: {scene.get('id', 'unknown')})", file=sys.stderr, flush=True)
            print(f"   Script: {scene['script'][:70]}...", file=sys.stderr, flush=True)
            print(f"   DB Duration: {scene.get('duration', 'N/A')}s", file=sys.stderr, flush=True)

            try:
                # Log effects if any
                if VideoEffects.has_effects(scene):
                    effects_summary = VideoEffects.get_effects_summary(scene)
                    print(f"   🎨 Effects: {effects_summary}", file=sys.stderr, flush=True)

                scene_video, actual_duration = self._create_scene_video(
                    scene,  # Pass full scene object instead of individual params
                    width,
                    height,
                    idx,
                    ai_image_model,  # Pass AI model from generate_video()
                    font_size  # Pass font_size from generate_video()
                )
                scene_videos.append(scene_video)
                scene_timings.append({
                    'index': idx,
                    'id': scene.get('id'),
                    'duration': actual_duration,
                    'db_duration': scene.get('duration')
                })
                print(f"   ✓ Actual Duration: {actual_duration:.2f}s", file=sys.stderr, flush=True)

            except Exception as e:
                print(f"   ✗ Error: {e}", file=sys.stderr, flush=True)
                continue

        print(f"\n{'='*80}", file=sys.stderr, flush=True)
        print(f"📊 FINAL SCENE TIMELINE", file=sys.stderr, flush=True)
        print(f"{'='*80}", file=sys.stderr, flush=True)
        cumulative = 0
        for timing in scene_timings:
            print(f"Scene {timing['index']+1} (ID: {timing['id']}) | Start: {cumulative:.2f}s | Duration: {timing['duration']:.2f}s | DB: {timing['db_duration']}s", file=sys.stderr, flush=True)
            cumulative += timing['duration']
        print(f"Total: {cumulative:.2f}s", file=sys.stderr, flush=True)
        print(f"{'='*80}\n", file=sys.stderr, flush=True)

        if not scene_videos:
            raise ValueError("No scene videos were created")

        # Concatenate using FFmpeg
        print(f"Concatenating {len(scene_videos)} videos...", file=sys.stderr, flush=True)
        output_filename = f"video_{project_id}_{resolution}.mp4"
        output_path = self.output_dir / output_filename

        self._concat_videos_ffmpeg(scene_videos, output_path, background_music_path, background_music_volume, video_speed)

        print(f"✓ Video generated: {output_path}", file=sys.stderr, flush=True)

        # Upload to Dropbox if on Railway (not local Mac)
        if not storage.use_local and storage.dbx:
            try:
                rel_path = f'previews/{output_filename}'
                dropbox_path = f'/output/video_editor_prototype/{rel_path}'
                with open(output_path, 'rb') as f:
                    import dropbox
                    storage.dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
                print(f"☁️ Uploaded preview to Dropbox: {dropbox_path}", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠️ Dropbox upload warning: {e}", file=sys.stderr, flush=True)

        # Cleanup temporary files (keep image_cache for database)
        try:
            import shutil
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleaned up temp files in {self.temp_dir}", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"⚠️ Temp cleanup warning: {e}", file=sys.stderr, flush=True)

        # Return both path and timing information
        return str(output_path), scene_timings

    def _create_scene_video(self, scene, width, height, idx, ai_image_model='flux-dev', font_size=80):
        """Create single scene video with effects"""
        text = scene['script']
        bg_type = scene.get('background_type', 'solid')
        bg_value = scene.get('background_value', '#000000')
        sound_effect_path = scene.get('sound_effect_path')

        # Generate TTS using appropriate service based on voice prefix
        tts_audio_path = self.temp_dir / f"audio_{idx}.mp3"
        self._generate_tts(text, tts_audio_path)

        # Get TTS audio duration using ffprobe
        duration = self._get_audio_duration(tts_audio_path)

        # Mix TTS with sound effect if provided
        print(f"   🔍 DEBUG: sound_effect_path = {sound_effect_path}", file=sys.stderr, flush=True)
        if sound_effect_path:
            print(f"   🔍 DEBUG: File exists? {os.path.exists(sound_effect_path)}", file=sys.stderr, flush=True)

        if sound_effect_path and os.path.exists(sound_effect_path):
            sound_effect_volume = scene.get('sound_effect_volume', 50)  # Default 50%
            sound_effect_offset = scene.get('sound_effect_offset', 0)   # Default 0% (start)
            print(f"   🎵 Mixing sound effect: {sound_effect_path} (Volume: {sound_effect_volume}%, Offset: {sound_effect_offset}%)", file=sys.stderr, flush=True)
            mixed_audio_path = self.temp_dir / f"mixed_audio_{idx}.mp3"
            self._mix_audio_with_sound_effect(tts_audio_path, sound_effect_path, mixed_audio_path, duration, sound_effect_volume, sound_effect_offset)
            audio_path = mixed_audio_path
        else:
            if sound_effect_path:
                print(f"   ⚠️ Sound effect file not found: {sound_effect_path}", file=sys.stderr, flush=True)
            else:
                print(f"   ℹ️ No sound effect for this scene", file=sys.stderr, flush=True)
            audio_path = tts_audio_path

        # Adjust duration for speed effect
        effect_speed = scene.get('effect_speed', 1.0)
        # Protect against division by zero - minimum speed is 0.1
        if effect_speed <= 0:
            effect_speed = 1.0
        if effect_speed != 1.0:
            # Speed affects video duration but not audio
            # Audio will be stretched/compressed by FFmpeg
            video_duration = duration / effect_speed
        else:
            video_duration = duration

        # Create image with text
        img_path = self.temp_dir / f"frame_{idx}.jpg"
        self._create_text_image(text, width, height, bg_type, bg_value, img_path, ai_image_model, font_size, scene)

        # Build effects filter chain
        filter_chain = VideoEffects.build_filter_chain(scene, width, height, video_duration)

        # Log the filter chain for debugging
        if filter_chain:
            print(f"   🎬 FFmpeg filter: {filter_chain}", file=sys.stderr, flush=True)

        # Create video from image + audio using FFmpeg with effects
        video_path = self.temp_dir / f"scene_{idx}.mp4"

        # Base FFmpeg command
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-framerate', '30',  # CRITICAL: Set input framerate for zoompan to work with looped images
            '-i', str(img_path),
            '-i', str(audio_path),
            '-c:v', 'libx264',
            '-t', str(video_duration),
            '-pix_fmt', 'yuv420p',
        ]

        # Add video filter if effects are present
        if filter_chain:
            cmd.extend(['-vf', filter_chain])

        # Add audio codec and speed adjustment for audio if needed
        if effect_speed != 1.0:
            # Adjust audio tempo to match video speed
            audio_filter = f"atempo={effect_speed}" if effect_speed <= 2.0 else f"atempo=2.0,atempo={effect_speed/2.0}"
            cmd.extend(['-af', audio_filter])

        cmd.extend([
            '-c:a', 'aac',
            '-b:a', '192k',
            '-ar', '44100',  # Force 44.1kHz sample rate for all scenes
            '-ac', '2',       # Force stereo for all scenes
            '-shortest',
            str(video_path)
        ])

        # Log full FFmpeg command for debugging
        print(f"   🔧 FFmpeg cmd: {' '.join(cmd)}", file=sys.stderr, flush=True)

        # Run FFmpeg command
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"   ❌ FFmpeg Error: {e.stderr}", file=sys.stderr, flush=True)
            raise

        # Return actual output duration (may differ from input due to effects)
        actual_duration = self._get_video_duration(video_path)

        return video_path, actual_duration

    async def _generate_edge_tts(self, text, output_path):
        """Generate TTS audio using Edge TTS"""
        communicate = edge_tts.Communicate(text, self.tts_voice)
        await communicate.save(str(output_path))

    def _generate_tts(self, text, output_path):
        """
        Generate TTS audio using the appropriate service based on voice prefix
        Supports: Edge TTS, ElevenLabs, OpenAI
        """
        voice = self.tts_voice

        # Detect voice service by prefix
        if voice.startswith('elevenlabs:'):
            # ElevenLabs voice
            voice_id = voice.replace('elevenlabs:', '')
            print(f"🎤 Using ElevenLabs voice: {voice_id}", file=sys.stderr, flush=True)
            self.elevenlabs_service.generate_tts(text, voice_id, str(output_path))

        elif voice.startswith('openai:'):
            # OpenAI voice
            voice_id = voice.replace('openai:', '')
            print(f"🎤 Using OpenAI voice: {voice_id}", file=sys.stderr, flush=True)
            self.openai_tts_service.generate_tts(text, voice_id, str(output_path))

        else:
            # Edge TTS (default)
            print(f"🎤 Using Edge TTS voice: {voice}", file=sys.stderr, flush=True)
            asyncio.run(self._generate_edge_tts(text, output_path))

    def _create_text_image(self, text, width, height, bg_type, bg_value, output_path, ai_image_model='flux-dev', font_size=30, scene=None):
        """Create image with text"""
        # Protect against font sizes that are too small for PIL TrueType rendering
        if font_size <= 0:
            font_size = 10  # Minimum 10px font size
        elif font_size < 10:
            print(f"   ⚠️  Font size {font_size} too small, using minimum 10px", file=sys.stderr, flush=True)
            font_size = 10

        # Always use Replicate AI image for keyword scenes
        if bg_type == 'keyword' and bg_value:
            print(f"🎨 Using AI image for keyword: '{bg_value}'", file=sys.stderr, flush=True)

            # Check if scene has existing image_path
            existing_image_path = scene.get('image_path') if scene else None

            # DEBUG: Log scene data
            print(f"🔍 DEBUG: scene = {scene}", file=sys.stderr, flush=True)
            print(f"🔍 DEBUG: existing_image_path = {existing_image_path}", file=sys.stderr, flush=True)
            if existing_image_path:
                print(f"🔍 DEBUG: os.path.exists({existing_image_path}) = {os.path.exists(existing_image_path)}", file=sys.stderr, flush=True)

            if existing_image_path and os.path.exists(existing_image_path):
                # Reuse existing image
                print(f"♻️  Reusing existing image: {existing_image_path}", file=sys.stderr, flush=True)
                ai_image_path = existing_image_path
            else:
                # Generate new image
                print(f"🆕 Generating new AI image...", file=sys.stderr, flush=True)
                ai_image_path = self.image_service.generate_image(bg_value, width, height, model=ai_image_model)

                if not ai_image_path or not os.path.exists(ai_image_path):
                    raise ValueError(f"Failed to get AI image for keyword: '{bg_value}'")

                # Save image_path to database
                if scene and scene.get('id'):
                    try:
                        from database.db_manager import DatabaseManager
                        db = DatabaseManager()
                        db.update_scene(scene['id'], {'image_path': ai_image_path})
                        print(f"💾 Saved image_path to database for scene {scene['id']}", file=sys.stderr, flush=True)
                    except Exception as e:
                        print(f"⚠️  Failed to save image_path to database: {e}", file=sys.stderr, flush=True)

            # Load AI-generated image
            img = Image.open(ai_image_path)
            img = img.resize((width, height))
            print(f"✓ Loaded AI image: {ai_image_path}", file=sys.stderr, flush=True)
        elif bg_type == 'image' and bg_value:
            # Use uploaded custom image
            print(f"📸 Using custom uploaded image: '{bg_value}'", file=sys.stderr, flush=True)

            if not os.path.exists(bg_value):
                print(f"⚠️ Custom image not found: {bg_value}, using black background", file=sys.stderr, flush=True)
                img = Image.new('RGB', (width, height), (0, 0, 0))
            else:
                try:
                    img = Image.open(bg_value)
                    img = img.resize((width, height))
                    print(f"✓ Loaded custom image: {bg_value}", file=sys.stderr, flush=True)
                except Exception as e:
                    print(f"⚠️ Failed to load custom image: {e}, using black background", file=sys.stderr, flush=True)
                    img = Image.new('RGB', (width, height), (0, 0, 0))
        else:
            # For non-keyword/non-image scenes, use solid black background
            img = Image.new('RGB', (width, height), (0, 0, 0))

        draw = ImageDraw.Draw(img)

        # Font (use font_size parameter)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

        # Word wrap
        wrapped_text = self._wrap_text(text, width - 100, font, draw)

        # Center text
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align='center')
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # Draw outline
        for adj_x in [-2, 0, 2]:
            for adj_y in [-2, 0, 2]:
                if adj_x != 0 or adj_y != 0:
                    draw.multiline_text((x + adj_x, y + adj_y), wrapped_text, font=font, fill=(0, 0, 0), align='center')

        # Draw text
        draw.multiline_text((x, y), wrapped_text, font=font, fill=(255, 255, 255), align='center')

        img.save(output_path, 'JPEG', quality=90)

    def _wrap_text(self, text, max_width, font, draw):
        """Word wrap text"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return '\n'.join(lines)


    def _get_audio_duration(self, audio_path):
        """Get audio duration using ffprobe"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(audio_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())

    def _get_video_duration(self, video_path):
        """Get video duration using ffprobe"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())

    def _concat_videos_ffmpeg(self, video_paths, output_path, background_music_path=None, background_music_volume=7, video_speed=1.0):
        """
        Concatenate videos using FFmpeg with optional speed control and background music.

        CRITICAL ORDER (like viral_trend_creator):
        1. Concat videos → temp file (WITHOUT music)
        2. Apply video speed (if != 1.0) → affects video + TTS
        3. Add background music → at NORMAL speed

        This ensures music plays at normal speed while video can be sped up/slowed down!
        """
        # Ensure temp directory exists (may have been cleaned up from previous run)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Create concat file
        concat_file = self.temp_dir / "concat.txt"
        with open(concat_file, 'w') as f:
            for video_path in video_paths:
                f.write(f"file '{video_path.absolute()}'\n")

        # STEP 1: Concat videos WITHOUT music (we'll add music later)
        temp_concat = self.temp_dir / "temp_concat.mp4"

        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',  # Just concat, no re-encoding yet
            str(temp_concat)
        ]

        print(f"📹 Step 1: Concatenating videos...", file=sys.stderr, flush=True)
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stderr:
            print(f"   ⚠️ FFmpeg stderr: {result.stderr[:500]}", file=sys.stderr, flush=True)

        # STEP 2: Apply video speed (if not 1.0) - THIS AFFECTS VIDEO + TTS!
        working_file = temp_concat

        if video_speed != 1.0:
            print(f"⚡ Step 2: Applying video speed {video_speed}x...", file=sys.stderr, flush=True)
            temp_speed = self.temp_dir / "temp_speed.mp4"

            # FFmpeg speed filters:
            # - Video: setpts=PTS/SPEED (e.g., 0.87 → slower, 1.5 → faster)
            # - Audio: atempo=SPEED (limited to 0.5-2.0, chain multiple if needed)

            # Calculate atempo filter (chain if outside 0.5-2.0 range)
            if 0.5 <= video_speed <= 2.0:
                atempo_filter = f"atempo={video_speed}"
            elif video_speed < 0.5:
                # Chain two atempo filters for speeds < 0.5
                atempo_filter = f"atempo=0.5,atempo={video_speed/0.5}"
            else:  # video_speed > 2.0
                # Chain two atempo filters for speeds > 2.0
                atempo_filter = f"atempo=2.0,atempo={video_speed/2.0}"

            cmd_speed = [
                'ffmpeg', '-y',
                '-i', str(temp_concat),
                '-filter_complex', f'[0:v]setpts=PTS/{video_speed}[v];[0:a]{atempo_filter}[a]',
                '-map', '[v]',
                '-map', '[a]',
                '-c:v', 'libx264',  # Re-encode video for speed change
                '-preset', 'veryfast',
                '-crf', '23',
                '-c:a', 'aac',  # Re-encode audio for speed change
                '-b:a', '192k',
                str(temp_speed)
            ]

            result = subprocess.run(cmd_speed, check=True, capture_output=True, text=True)
            if result.stderr:
                print(f"   ⚠️ FFmpeg stderr: {result.stderr[:500]}", file=sys.stderr, flush=True)

            working_file = temp_speed
            print(f"   ✓ Video speed adjusted to {video_speed}x", file=sys.stderr, flush=True)

        # STEP 3: Add background music (at NORMAL speed!) - AFTER speed adjustment
        if background_music_path and Path(background_music_path).exists():
            music_volume = background_music_volume / 100.0

            print(f"🎵 Step 3: Adding background music at normal speed (Volume: {background_music_volume}%)...", file=sys.stderr, flush=True)

            cmd_music = [
                'ffmpeg', '-y',
                '-i', str(working_file),  # Video with speed applied
                '-stream_loop', '-1',
                '-i', str(background_music_path),  # Music at NORMAL speed
                '-filter_complex', f'[1:a]volume={music_volume}[m];[0:a][m]amix=inputs=2:duration=first:normalize=0,volume=2.5',
                '-c:v', 'copy',  # Copy video (already encoded in step 2)
                '-c:a', 'aac',
                '-b:a', '192k',
                '-shortest',
                str(output_path)
            ]

            result = subprocess.run(cmd_music, check=True, capture_output=True, text=True)
            if result.stderr:
                print(f"   ⚠️ FFmpeg stderr: {result.stderr[:500]}", file=sys.stderr, flush=True)
        else:
            # No background music, just copy the working file
            import shutil
            shutil.copy(working_file, output_path)

        print(f"✓ Final video ready: {output_path}", file=sys.stderr, flush=True)

    def _mix_audio_with_sound_effect(self, tts_audio_path, sound_effect_path, output_path, target_duration, volume_percent=50, offset_percent=0):
        """
        Mix TTS audio with sound effect using FFmpeg

        Args:
            tts_audio_path: Path to TTS audio (voice)
            sound_effect_path: Path to sound effect
            output_path: Output path for mixed audio
            target_duration: Target duration in seconds
            volume_percent: Sound effect volume (0-100%), default 50%
            offset_percent: Sound effect timing offset (0-100%), default 0% (start)
        """
        # Convert percentage to FFmpeg volume value (0.0-1.0)
        volume = volume_percent / 100.0

        # Calculate delay in milliseconds based on offset percentage
        # 0% = start (0ms delay), 50% = middle, 100% = end
        delay_ms = int(target_duration * (offset_percent / 100.0) * 1000)

        # ROBUST APPROACH: Use amerge + pan filters to mix audio
        # This approach is more reliable than amix for different duration inputs

        # ROBUST APPROACH: Normalize both audio streams to same format before mixing
        # TTS is often mono 24kHz, sound effects can be stereo 44.1kHz
        # We need to convert both to the same format (44.1kHz stereo) before mixing
        # Output as MP3 format (not AAC) for compatibility with rest of pipeline
        cmd = [
            'ffmpeg', '-y',
            '-i', str(tts_audio_path),      # Input 0: TTS voice
            '-i', str(sound_effect_path),   # Input 1: Sound effect
            '-filter_complex',
            # Normalize TTS to 44.1kHz stereo
            '[0:a]aresample=44100,aformat=channel_layouts=stereo[tts];'
            # Normalize sound effect to 44.1kHz stereo, apply delay (timing offset), then volume
            # NO LOOP - sound effect plays once at specified timing
            f'[1:a]aresample=44100,aformat=channel_layouts=stereo,adelay={delay_ms}|{delay_ms},volume={volume}[sfx];'
            # Mix both streams WITHOUT auto-normalization (keeps TTS at 100%, SFX at specified volume)
            '[tts][sfx]amix=inputs=2:duration=first:dropout_transition=3:normalize=0[out]',
            '-map', '[out]',
            '-t', str(target_duration),     # Trim to target duration
            '-c:a', 'libmp3lame',          # Use MP3 codec for MP3 container
            '-b:a', '192k',
            '-ar', '44100',                 # Output sample rate
            str(output_path)
        ]

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"   ✓ Audio mixed successfully", file=sys.stderr, flush=True)
        except subprocess.CalledProcessError as e:
            # Log the actual error for debugging
            print(f"   ⚠️ Audio mixing failed: {e.stderr if e.stderr else str(e)}", file=sys.stderr, flush=True)
            print(f"   ℹ️ Using TTS only (without sound effect)", file=sys.stderr, flush=True)
            # Fallback: copy TTS audio as is
            import shutil
            shutil.copy(tts_audio_path, output_path)

    def cleanup_temp_files(self):
        """Clean up temp files"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            self.temp_dir.mkdir(exist_ok=True)
