"""
Video Generator Service
Creates actual video files from scenes using MoviePy + TTS
"""
import os
from pathlib import Path
from moviepy.editor import *
from gtts import gTTS
import tempfile
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class VideoGenerator:
    def __init__(self):
        self.output_dir = Path("./previews")
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir = Path(tempfile.gettempdir()) / "video_editor_temp"
        self.temp_dir.mkdir(exist_ok=True)

    def generate_video(self, scenes, project_id, resolution='preview'):
        """
        Generate video from scenes

        Args:
            scenes: List of scene dicts with 'script', 'duration', 'background_type', 'background_value'
            project_id: Project ID for naming
            resolution: 'preview' (540p) or 'export' (1080p)

        Returns:
            Path to generated video file
        """
        if not scenes:
            raise ValueError("No scenes to generate video from")

        # Set resolution
        if resolution == 'preview':
            width, height = 608, 1080  # 9:16 aspect ratio, lower res
        else:  # export
            width, height = 1080, 1920  # 9:16 aspect ratio, full res

        video_clips = []

        for idx, scene in enumerate(scenes):
            print(f"Processing scene {idx + 1}/{len(scenes)}: {scene['script'][:50]}...")

            try:
                # Generate TTS audio
                audio_path = self._generate_tts(scene['script'], idx)

                # Get actual audio duration
                audio_clip = AudioFileClip(audio_path)
                actual_duration = audio_clip.duration

                # Create simple black background with white text
                # For now, skip complex compositing
                bg_img = self._create_text_image(
                    scene['script'],
                    width,
                    height,
                    scene.get('background_type', 'solid'),
                    scene.get('background_value', '#000000')
                )

                # Create video clip from image
                video_clip = ImageClip(bg_img, duration=actual_duration)

                # Verify clip is valid
                if video_clip is None:
                    print(f"Warning: Scene {idx + 1} created None clip, skipping")
                    audio_clip.close()
                    continue

                # Set audio
                video_clip = video_clip.set_audio(audio_clip)

                # Verify final clip
                if video_clip is None or video_clip.duration is None:
                    print(f"Warning: Scene {idx + 1} has invalid duration, skipping")
                    audio_clip.close()
                    continue

                video_clips.append(video_clip)
                print(f"✓ Scene {idx + 1} added successfully ({actual_duration:.1f}s)")

                # Don't close audio_clip here - it's attached to video_clip

            except Exception as e:
                print(f"✗ Error processing scene {idx + 1}: {e}")
                import traceback
                traceback.print_exc()
                # Skip this scene
                continue

        # Concatenate all clips
        if not video_clips:
            raise ValueError("No video clips were created")

        print(f"Concatenating {len(video_clips)} clips...")

        # Filter out any None clips just in case
        valid_clips = [c for c in video_clips if c is not None and hasattr(c, 'duration') and c.duration is not None]

        if not valid_clips:
            raise ValueError("No valid video clips after filtering")

        print(f"Using {len(valid_clips)} valid clips")
        final_video = concatenate_videoclips(valid_clips, method="chain")

        # Export
        output_filename = f"video_{project_id}_{resolution}.mp4"
        output_path = self.output_dir / output_filename

        print(f"Exporting to {output_path}...")
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            threads=4
        )

        # Cleanup
        for clip in video_clips:
            clip.close()
        final_video.close()

        return str(output_path)

    def _generate_tts(self, text, idx):
        """Generate TTS audio using gTTS (Google TTS)"""
        audio_path = self.temp_dir / f"audio_{idx}.mp3"

        try:
            tts = gTTS(text=text, lang='de', slow=False)
            tts.save(str(audio_path))
        except Exception as e:
            print(f"TTS generation failed: {e}")
            # Fallback: create silent audio
            # For now, just re-raise
            raise

        return str(audio_path)

    def _create_text_image(self, text, width, height, bg_type, bg_value):
        """Create a single image with text overlay on background"""
        # Create background color
        if bg_type == 'solid' or bg_type == 'keyword':
            try:
                bg_color = self._hex_to_rgb(bg_value) if bg_value.startswith('#') else (0, 0, 0)
            except:
                bg_color = (0, 0, 0)
        else:
            bg_color = (0, 0, 0)

        # Create image
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Load font
        try:
            font_size = 50
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
            except:
                font = ImageFont.load_default()

        # Word wrap
        wrapped_text = self._wrap_text(text, width - 100, font, draw)

        # Get text size
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align='center')
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center text
        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # Draw outline
        for adj_x in [-2, 0, 2]:
            for adj_y in [-2, 0, 2]:
                if adj_x != 0 or adj_y != 0:
                    draw.multiline_text(
                        (x + adj_x, y + adj_y),
                        wrapped_text,
                        font=font,
                        fill=(0, 0, 0),
                        align='center'
                    )

        # Draw main text
        draw.multiline_text((x, y), wrapped_text, font=font, fill=(255, 255, 255), align='center')

        return np.array(img)

    def _create_background(self, bg_type, bg_value, width, height, duration):
        """Create background clip"""
        # Create solid color image
        if bg_type == 'solid' or bg_type == 'keyword':
            try:
                color = self._hex_to_rgb(bg_value) if bg_value.startswith('#') else (0, 0, 0)
            except:
                color = (0, 0, 0)  # Default to black
        else:
            color = (0, 0, 0)

        # Create PIL Image
        img = Image.new('RGB', (width, height), color)
        img_array = np.array(img)

        # Create clip using make_frame
        bg_clip = ImageClip(img_array, duration=duration)
        return bg_clip

    def _create_text_overlay(self, text, width, height, duration):
        """Create text overlay using PIL"""
        # Create RGB image with transparency
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Try to load a nice font, fallback to default
        try:
            font_size = 60
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font_size = 40
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

        # Word wrap text
        wrapped_text = self._wrap_text(text, width - 80, font, draw)

        # Calculate text position (centered)
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align='center')
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # Draw text with outline for better readability
        outline_color = (0, 0, 0, 255)
        text_color = (255, 255, 255, 255)

        # Draw outline
        for adj_x in [-2, 0, 2]:
            for adj_y in [-2, 0, 2]:
                if adj_x != 0 or adj_y != 0:
                    draw.multiline_text(
                        (x + adj_x, y + adj_y),
                        wrapped_text,
                        font=font,
                        fill=outline_color,
                        align='center'
                    )

        # Draw main text
        draw.multiline_text((x, y), wrapped_text, font=font, fill=text_color, align='center')

        # Convert RGBA to RGB with black background
        bg = Image.new('RGB', (width, height), (0, 0, 0))
        bg.paste(img, (0, 0), img)
        text_array = np.array(bg)

        # Create clip
        text_clip = ImageClip(text_array, duration=duration)
        return text_clip

    def _wrap_text(self, text, max_width, font, draw):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]

            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return '\n'.join(lines)

    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def cleanup_temp_files(self):
        """Clean up temporary audio files"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            self.temp_dir.mkdir(exist_ok=True)
