"""
Video Effects Module
Generates FFmpeg filter chains for various video effects
"""

class VideoEffects:
    """Handles generation of FFmpeg video filter strings"""

    @staticmethod
    def build_filter_chain(scene, width, height, duration):
        """
        Build complete FFmpeg filter chain for a scene

        Args:
            scene: Scene dict with effect parameters
            width: Video width
            height: Video height
            duration: Video duration in seconds

        Returns:
            str: FFmpeg filter chain string (or None if no effects)
        """
        filters = []

        # Get effect parameters with defaults
        effect_zoom = scene.get('effect_zoom', 'none')
        effect_pan = scene.get('effect_pan', 'none')
        effect_speed = scene.get('effect_speed', 1.0)
        effect_shake = scene.get('effect_shake', 0)
        effect_fade = scene.get('effect_fade', 'none')
        effect_intensity = scene.get('effect_intensity', 0.5)

        # NEW EFFECTS
        effect_vignette = scene.get('effect_vignette', 'none')
        effect_color_temp = scene.get('effect_color_temp', 'none')
        # Saturation: Frontend sends FLOAT 0.0-2.0 (stored as FLOAT 1.0 in DB), use directly for FFmpeg
        effect_saturation = scene.get('effect_saturation', 1.0)  # Direct FFmpeg value (1.0 = 100% = normal)
        effect_film_grain = scene.get('effect_film_grain', 0)
        effect_glitch = scene.get('effect_glitch', 0)
        effect_chromatic = scene.get('effect_chromatic', 0)
        effect_blur = scene.get('effect_blur', 'none')
        effect_rotate = scene.get('effect_rotate', 'none')
        effect_bounce = scene.get('effect_bounce', 0)
        effect_tilt_3d = scene.get('effect_tilt_3d', 'none')
        effect_light_leaks = scene.get('effect_light_leaks', 0)
        effect_lens_flare = scene.get('effect_lens_flare', 0)
        effect_kaleidoscope = scene.get('effect_kaleidoscope', 0)

        # Apply speed effect first (affects timing)
        if effect_speed != 1.0:
            speed_filter = VideoEffects._speed_filter(effect_speed)
            if speed_filter:
                filters.append(speed_filter)

        # Handle zoom and pan together (both use zoompan)
        # If both are present, we need to combine them into one zoompan filter
        if effect_zoom != 'none' or effect_pan != 'none':
            zoompan_filter = VideoEffects._combined_zoompan_filter(
                effect_zoom, effect_pan, width, height, duration, effect_intensity
            )
            if zoompan_filter:
                filters.append(zoompan_filter)

        # Apply motion effects (rotate, bounce, tilt)
        if effect_rotate != 'none':
            rotate_filter = VideoEffects._rotate_filter(effect_rotate, duration)
            if rotate_filter:
                filters.append(rotate_filter)

        if effect_bounce > 0:  # FIXED: Changed from == 1 to > 0
            bounce_filter = VideoEffects._bounce_filter(duration, effect_intensity)
            if bounce_filter:
                filters.append(bounce_filter)

        if effect_tilt_3d != 'none':
            tilt_filter = VideoEffects._tilt_3d_filter(effect_tilt_3d, duration, effect_intensity)
            if tilt_filter:
                filters.append(tilt_filter)

        # Apply shake effect (uses crop, so can be separate)
        if effect_shake > 0:  # FIXED: Changed from == 1 to > 0
            shake_filter = VideoEffects._shake_filter(effect_intensity)
            if shake_filter:
                filters.append(shake_filter)

        # Apply color/visual effects
        if effect_saturation != 1.0:  # FIXED: Now FLOAT (was INTEGER before migration)
            print(f"🔍 DEBUG: Applying saturation filter: value={effect_saturation} (type={type(effect_saturation).__name__})", flush=True)
            saturation_filter = VideoEffects._saturation_filter(effect_saturation)
            if saturation_filter:
                filters.append(saturation_filter)
                print(f"   FFmpeg saturation filter: {saturation_filter}", flush=True)

        if effect_color_temp != 'none':
            print(f"🔍 DEBUG: Applying color_temp filter: value={effect_color_temp} (type={type(effect_color_temp).__name__})", flush=True)
            color_temp_filter = VideoEffects._color_temp_filter(effect_color_temp, effect_intensity)
            if color_temp_filter:
                filters.append(color_temp_filter)
                print(f"   FFmpeg color_temp filter: {color_temp_filter}", flush=True)

        if effect_chromatic > 0:  # FIXED: Changed from == 1 to > 0
            chromatic_filter = VideoEffects._chromatic_aberration_filter(effect_intensity)
            if chromatic_filter:
                filters.append(chromatic_filter)

        if effect_blur != 'none':
            blur_filter = VideoEffects._blur_filter(effect_blur, effect_intensity)
            if blur_filter:
                filters.append(blur_filter)

        if effect_glitch > 0:  # FIXED: Changed from == 1 to > 0
            glitch_filter = VideoEffects._glitch_filter(effect_intensity)
            if glitch_filter:
                filters.append(glitch_filter)

        if effect_vignette != 'none':
            print(f"🔍 DEBUG: Applying vignette filter: value={effect_vignette} (type={type(effect_vignette).__name__})", flush=True)
            vignette_filter = VideoEffects._vignette_filter(effect_vignette, effect_intensity)
            if vignette_filter:
                filters.append(vignette_filter)
                print(f"   FFmpeg vignette filter: {vignette_filter}", flush=True)

        if effect_film_grain > 0:  # FIXED: Changed from == 1 to > 0
            film_grain_filter = VideoEffects._film_grain_filter(effect_intensity)
            if film_grain_filter:
                filters.append(film_grain_filter)

        if effect_light_leaks > 0:  # FIXED: Changed from == 1 to > 0
            light_leaks_filter = VideoEffects._light_leaks_filter(effect_intensity)
            if light_leaks_filter:
                filters.append(light_leaks_filter)

        if effect_lens_flare > 0:  # FIXED: Changed from == 1 to > 0
            lens_flare_filter = VideoEffects._lens_flare_filter(effect_intensity)
            if lens_flare_filter:
                filters.append(lens_flare_filter)

        if effect_kaleidoscope > 0:  # FIXED: Changed from == 1 to > 0
            kaleidoscope_filter = VideoEffects._kaleidoscope_filter()
            if kaleidoscope_filter:
                filters.append(kaleidoscope_filter)

        # Apply fade effect (should be last)
        if effect_fade != 'none':
            fade_filter = VideoEffects._fade_filter(effect_fade, duration)
            if fade_filter:
                filters.append(fade_filter)

        # Join all filters with comma
        return ','.join(filters) if filters else None

    @staticmethod
    def _combined_zoompan_filter(zoom_type, pan_type, width, height, duration, intensity):
        """Combine zoom and pan using scale + crop for reliable movement"""
        # Protect against zero or negative duration
        if duration <= 0:
            duration = 0.1  # Minimum 0.1 seconds
        frames = int(duration * 30)
        if frames <= 0:
            frames = 3  # Minimum 3 frames
        max_scale = 1.0 + (intensity * 0.5)

        # Scale input to 3.5x size to give room for panning and zooming
        # Using 3.5x provides maximum headroom while maintaining quality
        scale_factor = 3.5
        scaled_width = int(width * scale_factor)
        scaled_height = int(height * scale_factor)

        # Pan distance: 100% of output width for maximum movement at intensity 1.0
        # At intensity 0.5, this gives 50% movement (half the screen width)
        pan_distance = int(width * intensity)

        # CENTER POSITIONS (where crop window starts when centered)
        center_x = int((scaled_width - width) / 2)
        center_y = int((scaled_height - height) / 2)

        # If we have BOTH zoom and pan, use zoompan filter (complex effects)
        if zoom_type and zoom_type != 'none' and pan_type and pan_type != 'none':
            # Determine zoom expression
            if zoom_type == 'zoom_in':
                zoom_expr = f"1+({max_scale}-1)*on/{frames}"
            elif zoom_type == 'zoom_out':
                zoom_expr = f"{max_scale}-({max_scale}-1)*on/{frames}"
            elif zoom_type == 'ken_burns':
                zoom_expr = f"1+({max_scale}-1)*on/{frames}"
            elif zoom_type == 'pulse':
                pulse_intensity = 0.1 + (intensity * 0.1)
                zoom_expr = f"1+{pulse_intensity}*sin(on/{frames}*3.14159*4)"
            else:
                zoom_expr = "1"

            # Pan expressions for zoompan
            x_expr = "floor(iw/2-(iw/zoom/2))"
            y_expr = "floor(ih/2-(ih/zoom/2))"

            if pan_type == 'left':
                x_expr = f"floor(iw/2-(iw/zoom/2)-on/{frames}*{pan_distance})"
            elif pan_type == 'right':
                x_expr = f"floor(iw/2-(iw/zoom/2)+on/{frames}*{pan_distance})"
            elif pan_type == 'up':
                y_expr = f"floor(ih/2-(ih/zoom/2)-on/{frames}*{pan_distance})"
            elif pan_type == 'down':
                y_expr = f"floor(iw/2-(ih/zoom/2)+on/{frames}*{pan_distance})"

            return f"scale={scaled_width}:{scaled_height}:flags=lanczos,setsar=1,zoompan=z='{zoom_expr}':d={frames}:x='{x_expr}':y='{y_expr}':s={width}x{height}:fps=30"

        # If we have PAN ONLY (no zoom), use crop filter for reliable movement
        elif pan_type and pan_type != 'none':
            # Crop expressions: move the crop window across the scaled image
            # Using 'n' (frame number) variable for smooth animation
            if pan_type == 'left':
                # Move crop window left (decreasing x)
                crop_x = f"'{center_x}-n/{frames}*{pan_distance}'"
                crop_y = f"'{center_y}'"
            elif pan_type == 'right':
                # Move crop window right (increasing x)
                crop_x = f"'{center_x}+n/{frames}*{pan_distance}'"
                crop_y = f"'{center_y}'"
            elif pan_type == 'up':
                # Move crop window up (decreasing y)
                crop_x = f"'{center_x}'"
                crop_y = f"'{center_y}-n/{frames}*{pan_distance}'"
            elif pan_type == 'down':
                # Move crop window down (increasing y)
                crop_x = f"'{center_x}'"
                crop_y = f"'{center_y}+n/{frames}*{pan_distance}'"
            else:
                crop_x = f"'{center_x}'"
                crop_y = f"'{center_y}'"

            # Scale to 3.5x, then crop a moving window, then scale to output size
            return f"scale={scaled_width}:{scaled_height}:flags=lanczos,setsar=1,crop={width}:{height}:{crop_x}:{crop_y},scale={width}:{height}:flags=lanczos"

        # If we have ZOOM ONLY, use zoompan
        elif zoom_type and zoom_type != 'none':
            if zoom_type == 'zoom_in':
                zoom_expr = f"1+({max_scale}-1)*on/{frames}"
            elif zoom_type == 'zoom_out':
                zoom_expr = f"{max_scale}-({max_scale}-1)*on/{frames}"
            elif zoom_type == 'ken_burns':
                zoom_expr = f"1+({max_scale}-1)*on/{frames}"
                # Ken Burns has built-in horizontal drift
                x_expr = f"floor(iw/2-(iw/zoom/2)+sin(on/{frames}*3.14159)*50)"
                return f"scale={scaled_width}:{scaled_height}:flags=lanczos,setsar=1,zoompan=z='{zoom_expr}':d={frames}:x='{x_expr}':y='floor(ih/2-(ih/zoom/2))':s={width}x{height}:fps=30"
            elif zoom_type == 'pulse':
                pulse_intensity = 0.1 + (intensity * 0.1)
                zoom_expr = f"1+{pulse_intensity}*sin(on/{frames}*3.14159*4)"
            else:
                zoom_expr = "1"

            return f"scale={scaled_width}:{scaled_height}:flags=lanczos,setsar=1,zoompan=z='{zoom_expr}':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps=30"

        # NO EFFECTS: just scale and return
        return f"scale={width}:{height}:flags=lanczos,setsar=1"

    @staticmethod
    def _zoom_filter(zoom_type, width, height, duration, intensity):
        """Generate zoom filter"""
        # Protect against zero or negative duration
        if duration <= 0:
            duration = 0.1  # Minimum 0.1 seconds
        # Calculate frame count (30fps)
        frames = int(duration * 30)
        if frames <= 0:
            frames = 3  # Minimum 3 frames

        # Scale factor based on intensity (0.5 = 1.2x max, 1.0 = 1.5x max)
        max_scale = 1.0 + (intensity * 0.5)

        if zoom_type == 'zoom_in':
            # Start at 100%, zoom to max_scale
            # Use linear interpolation: 1 + (max_scale-1) * (frame/total_frames)
            zoom_expr = f"'1+({max_scale}-1)*on/{frames}'"
            return f"zoompan=z={zoom_expr}:d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps=30"

        elif zoom_type == 'zoom_out':
            # Start at max_scale, zoom out to 100%
            # Use linear interpolation: max_scale - (max_scale-1) * (frame/total_frames)
            zoom_expr = f"'{max_scale}-({max_scale}-1)*on/{frames}'"
            return f"zoompan=z={zoom_expr}:d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps=30"

        elif zoom_type == 'ken_burns':
            # Ken Burns: Slow zoom with slight pan
            # Gradual zoom in with horizontal drift
            zoom_expr = f"'1+({max_scale}-1)*on/{frames}'"
            x_expr = f"'iw/2-(iw/zoom/2)+sin(on/{frames}*3.14159)*50'"  # Gentle horizontal pan
            return f"zoompan=z={zoom_expr}:d={frames}:x={x_expr}:y='ih/2-(ih/zoom/2)':s={width}x{height}:fps=30"

        elif zoom_type == 'pulse':
            # Pulse: Zoom in and out rhythmically using sine wave
            pulse_intensity = 0.1 + (intensity * 0.1)  # 0.1 to 0.2 range
            # Complete 2 cycles during duration
            zoom_expr = f"'1+{pulse_intensity}*sin(on/{frames}*3.14159*4)'"
            return f"zoompan=z={zoom_expr}:d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps=30"

        return None

    @staticmethod
    def _pan_filter(pan_type, width, height, duration, intensity):
        """Generate pan filter - integrated into zoompan if zoom is also present"""
        # Protect against zero or negative duration
        if duration <= 0:
            duration = 0.1  # Minimum 0.1 seconds
        # Pan distance based on intensity (pixels to move)
        frames = int(duration * 30)
        if frames <= 0:
            frames = 3  # Minimum 3 frames
        pan_distance = int(width * 0.15 * intensity)  # 15% to 30% of width

        # If this is called without zoom, we use zoompan with z=1 (no zoom)
        if pan_type == 'left':
            # Pan from right to left
            x_expr = f"'iw/2-(iw/zoom/2)-on/{frames}*{pan_distance}'"
            return f"zoompan=z=1:d={frames}:x={x_expr}:y='ih/2-(ih/zoom/2)':s={width}x{height}:fps=30"

        elif pan_type == 'right':
            # Pan from left to right
            x_expr = f"'iw/2-(iw/zoom/2)+on/{frames}*{pan_distance}'"
            return f"zoompan=z=1:d={frames}:x={x_expr}:y='ih/2-(ih/zoom/2)':s={width}x{height}:fps=30"

        elif pan_type == 'up':
            # Pan from bottom to top
            y_expr = f"'ih/2-(ih/zoom/2)-on/{frames}*{pan_distance}'"
            return f"zoompan=z=1:d={frames}:x='iw/2-(iw/zoom/2)':y={y_expr}:s={width}x{height}:fps=30"

        elif pan_type == 'down':
            # Pan from top to bottom
            y_expr = f"'ih/2-(ih/zoom/2)+on/{frames}*{pan_distance}'"
            return f"zoompan=z=1:d={frames}:x='iw/2-(iw/zoom/2)':y={y_expr}:s={width}x{height}:fps=30"

        return None

    @staticmethod
    def _speed_filter(speed):
        """Generate speed filter (setpts)"""
        # Protect against division by zero
        if speed <= 0:
            speed = 1.0

        if speed == 1.0:
            return None

        # Inverse of speed for setpts (0.5x speed = 2.0 PTS multiplier)
        pts_multiplier = 1.0 / speed
        return f"setpts={pts_multiplier}*PTS"

    @staticmethod
    def _shake_filter(intensity):
        """Generate shake/vibrate filter"""
        # Shake amount based on intensity (1-5 pixels)
        shake_amount = int(1 + (intensity * 4))

        # Use crop with random movement
        # Note: FFmpeg's random function creates subtle shake
        return f"crop=w='iw-{shake_amount*2}':h='ih-{shake_amount*2}':x='{shake_amount}+{shake_amount}*sin(n/10)':y='{shake_amount}+{shake_amount}*cos(n/10)'"

    @staticmethod
    def _fade_filter(fade_type, duration):
        """Generate fade filter"""
        # Protect against zero or negative duration
        if duration <= 0:
            duration = 0.1  # Minimum 0.1 seconds
        # Fade duration: 0.5 seconds for in/out
        fade_duration = min(0.5, duration / 4)  # Max 25% of clip duration

        if fade_type == 'in':
            return f"fade=t=in:st=0:d={fade_duration}"

        elif fade_type == 'out':
            fade_start = duration - fade_duration
            return f"fade=t=out:st={fade_start}:d={fade_duration}"

        elif fade_type in ['both', 'in_out']:  # FIXED: Support both 'both' and 'in_out' for combined fade
            fade_start = duration - fade_duration
            return f"fade=t=in:st=0:d={fade_duration},fade=t=out:st={fade_start}:d={fade_duration}"

        return None

    @staticmethod
    def _vignette_filter(vignette_type, intensity):
        """Generate vignette filter (dark/light edges)"""
        if vignette_type == 'dark':
            # Dark vignette - darken edges
            strength = 0.3 + (intensity * 0.4)  # 0.3 to 0.7
            return f"vignette=PI/{strength}:mode=forward"
        elif vignette_type == 'light':
            # Light vignette - lighten edges
            strength = 0.3 + (intensity * 0.4)
            return f"vignette=PI/{strength}:mode=backward"
        return None

    @staticmethod
    def _color_temp_filter(temp_type, intensity):
        """Generate color temperature filter (warm/cool)"""
        if temp_type == 'warm':
            # Warm tones - increase red/yellow
            r_strength = 1.0 + (intensity * 0.3)  # 1.0 to 1.3
            b_strength = 1.0 - (intensity * 0.2)  # 1.0 to 0.8
            return f"eq=gamma_r={r_strength}:gamma_b={b_strength}"
        elif temp_type == 'cool':
            # Cool tones - increase blue
            r_strength = 1.0 - (intensity * 0.2)
            b_strength = 1.0 + (intensity * 0.3)
            return f"eq=gamma_r={r_strength}:gamma_b={b_strength}"
        return None

    @staticmethod
    def _saturation_filter(saturation):
        """Generate saturation filter"""
        if saturation != 1.0:
            return f"eq=saturation={saturation}"
        return None

    @staticmethod
    def _film_grain_filter(intensity):
        """Generate film grain filter (vintage look)"""
        # Grain strength based on intensity
        grain_strength = int(20 + (intensity * 40))  # 20 to 60
        return f"noise=alls={grain_strength}:allf=t"

    @staticmethod
    def _glitch_filter(intensity):
        """Generate glitch effect (digital artifacts)"""
        # Random displacement based on intensity
        strength = int(5 + (intensity * 15))  # 5 to 20 pixels
        # Use random function with noise to create glitch
        return f"noise=alls=10:allf=t+u,eq=contrast=1.2"

    @staticmethod
    def _chromatic_aberration_filter(intensity):
        """Generate chromatic aberration (RGB color shift)"""
        # Split RGB channels and shift them slightly
        shift = int(2 + (intensity * 6))  # 2 to 8 pixels
        # FIXED: Ensure shift is even for H.264 compatibility (width must be divisible by 2)
        if shift % 2 != 0:
            shift = shift - 1  # Make it even
        half_shift = shift // 2
        # Red shifts left, green centered, blue shifts right
        return f"split=3[r][g][b];[r]lutrgb=g=0:b=0,crop=iw-{shift}:ih:0:0[r1];[g]lutrgb=r=0:b=0,crop=iw-{shift}:ih:{half_shift}:0[g1];[b]lutrgb=r=0:g=0,crop=iw-{shift}:ih:{shift}:0[b1];[r1][g1]blend=all_mode=addition[rg];[rg][b1]blend=all_mode=addition"

    @staticmethod
    def _blur_filter(blur_type, intensity):
        """Generate blur filter"""
        if blur_type == 'gaussian':
            # Gaussian blur
            strength = 2 + (intensity * 8)  # 2 to 10
            return f"gblur=sigma={strength}"
        elif blur_type == 'motion':
            # Motion blur (horizontal)
            strength = int(5 + (intensity * 15))  # 5 to 20
            return f"boxblur={strength}:1"
        elif blur_type == 'radial':
            # Radial blur (zoom blur from center)
            return "zoompan=z='zoom+0.002':d=1:fps=30"
        return None

    @staticmethod
    def _rotate_filter(rotate_type, duration):
        """Generate rotation filter"""
        # Protect against zero or negative duration
        if duration <= 0:
            duration = 0.1  # Minimum 0.1 seconds
        frames = int(duration * 30)
        if frames <= 0:
            frames = 3  # Minimum 3 frames

        if rotate_type == 'clockwise':
            # Full 360° rotation clockwise - FFmpeg auto-calculates output size
            return f"rotate='2*PI*t/{duration}':c=none"
        elif rotate_type == 'counter_clockwise':
            # Full 360° rotation counter-clockwise - FFmpeg auto-calculates output size
            return f"rotate='-2*PI*t/{duration}':c=none"
        elif rotate_type == 'wobble':
            # Wobble back and forth
            return f"rotate='sin(t)*0.2':c=none"
        elif rotate_type == 'rotate_90':  # FIXED: Support rotate_90 as alias for static 90° rotation
            # Static 90° clockwise rotation
            return f"rotate=PI/2:c=none"
        elif rotate_type == 'rotate_180':  # Support 180° rotation
            # Static 180° rotation
            return f"rotate=PI:c=none"
        elif rotate_type == 'rotate_270':  # Support 270° rotation
            # Static 270° rotation
            return f"rotate=3*PI/2:c=none"
        return None

    @staticmethod
    def _bounce_filter(duration, intensity):
        """Generate bounce effect (rhythmic vertical movement)"""
        # Protect against zero or negative duration
        if duration <= 0:
            duration = 0.1  # Minimum 0.1 seconds
        # Bounce up and down using sine wave
        bounce_height = int(20 + (intensity * 40))  # 20 to 60 pixels
        frequency = 3  # 3 bounces during duration
        return f"crop=iw:ih-{bounce_height}:0:'{bounce_height}*abs(sin({frequency}*2*PI*t/{duration}))'"

    @staticmethod
    def _tilt_3d_filter(tilt_type, duration, intensity):
        """Generate 3D tilt/perspective effect"""
        # Protect against zero or negative duration
        if duration <= 0:
            duration = 0.1  # Minimum 0.1 seconds
        frames = int(duration * 30)
        if frames <= 0:
            frames = 3  # Minimum 3 frames

        if tilt_type in ['left', 'tilt_left']:  # FIXED: Support both 'left' and 'tilt_left'
            # Tilt perspective to left
            strength = 0.2 * intensity
            return f"perspective=x0=0:y0=0:x1='W*{strength}':y1=0:x2='W*(1-{strength})':y2=H:x3=W:y3=H:interpolation=linear"
        elif tilt_type in ['right', 'tilt_right']:  # FIXED: Support both 'right' and 'tilt_right'
            # Tilt perspective to right
            strength = 0.2 * intensity
            return f"perspective=x0='W*{strength}':y0=0:x1=W:y1=0:x2=0:y2=H:x3='W*(1-{strength})':y3=H:interpolation=linear"
        elif tilt_type in ['forward', 'tilt_forward']:  # FIXED: Support both 'forward' and 'tilt_forward'
            # Tilt forward (top smaller)
            strength = 0.2 * intensity
            return f"perspective=x0='W*{strength}':y0=0:x1='W*(1-{strength})':y1=0:x2=0:y2=H:x3=W:y3=H:interpolation=linear"
        elif tilt_type in ['backward', 'tilt_backward']:  # FIXED: Support both 'backward' and 'tilt_backward'
            # Tilt backward (bottom smaller)
            strength = 0.2 * intensity
            return f"perspective=x0=0:y0=0:x1=W:y1=0:x2='W*{strength}':y2=H:x3='W*(1-{strength})':y3=H:interpolation=linear"
        return None

    @staticmethod
    def _light_leaks_filter(intensity):
        """Generate light leaks effect (vintage light)"""
        # Simulate light leaks with overlay and color shifts
        brightness = 0.1 + (intensity * 0.2)  # 0.1 to 0.3
        return f"eq=brightness={brightness}:contrast=1.1,hue=s={1.2}"

    @staticmethod
    def _lens_flare_filter(intensity):
        """Generate lens flare effect"""
        # Simulate lens flare with brightness and glow
        brightness = 0.15 + (intensity * 0.25)
        return f"eq=brightness={brightness}:contrast=1.15,gblur=sigma=2"

    @staticmethod
    def _kaleidoscope_filter():
        """Generate kaleidoscope effect (symmetrical mirror)"""
        # Create mirrored pattern - 4-way symmetry
        return "crop=iw/2:ih/2:0:0,split=4[tl][tr][bl][br];[tr]hflip[tr];[bl]vflip[bl];[br]hflip,vflip[br];[tl][tr]hstack[t];[bl][br]hstack[b];[t][b]vstack"

    @staticmethod
    def has_effects(scene):
        """Check if scene has any effects enabled"""
        return (
            scene.get('effect_zoom', 'none') != 'none' or
            scene.get('effect_pan', 'none') != 'none' or
            scene.get('effect_speed', 1.0) != 1.0 or
            scene.get('effect_shake', 0) == 1 or
            scene.get('effect_fade', 'none') != 'none' or
            # New effects
            scene.get('effect_vignette', 'none') != 'none' or
            scene.get('effect_color_temp', 'none') != 'none' or
            scene.get('effect_saturation', 1.0) != 1.0 or
            scene.get('effect_film_grain', 0) == 1 or
            scene.get('effect_glitch', 0) == 1 or
            scene.get('effect_chromatic', 0) == 1 or
            scene.get('effect_blur', 'none') != 'none' or
            scene.get('effect_rotate', 'none') != 'none' or
            scene.get('effect_bounce', 0) == 1 or
            scene.get('effect_tilt_3d', 'none') != 'none' or
            scene.get('effect_light_leaks', 0) == 1 or
            scene.get('effect_lens_flare', 0) == 1 or
            scene.get('effect_kaleidoscope', 0) == 1
        )

    @staticmethod
    def get_effects_summary(scene):
        """Get human-readable summary of effects"""
        effects = []

        if scene.get('effect_zoom', 'none') != 'none':
            effects.append(f"Zoom: {scene['effect_zoom']}")

        if scene.get('effect_pan', 'none') != 'none':
            effects.append(f"Pan: {scene['effect_pan']}")

        if scene.get('effect_speed', 1.0) != 1.0:
            effects.append(f"Speed: {scene['effect_speed']}x")

        if scene.get('effect_shake', 0) == 1:
            effects.append("Shake")

        if scene.get('effect_fade', 'none') != 'none':
            effects.append(f"Fade: {scene['effect_fade']}")

        # New effects
        if scene.get('effect_vignette', 'none') != 'none':
            effects.append(f"Vignette: {scene['effect_vignette']}")

        if scene.get('effect_color_temp', 'none') != 'none':
            effects.append(f"Color Temp: {scene['effect_color_temp']}")

        if scene.get('effect_saturation', 1.0) != 1.0:
            effects.append(f"Saturation: {scene['effect_saturation']}")

        if scene.get('effect_film_grain', 0) == 1:
            effects.append("Film Grain")

        if scene.get('effect_glitch', 0) == 1:
            effects.append("Glitch")

        if scene.get('effect_chromatic', 0) == 1:
            effects.append("Chromatic Aberration")

        if scene.get('effect_blur', 'none') != 'none':
            effects.append(f"Blur: {scene['effect_blur']}")

        if scene.get('effect_rotate', 'none') != 'none':
            effects.append(f"Rotate: {scene['effect_rotate']}")

        if scene.get('effect_bounce', 0) == 1:
            effects.append("Bounce")

        if scene.get('effect_tilt_3d', 'none') != 'none':
            effects.append(f"3D Tilt: {scene['effect_tilt_3d']}")

        if scene.get('effect_light_leaks', 0) == 1:
            effects.append("Light Leaks")

        if scene.get('effect_lens_flare', 0) == 1:
            effects.append("Lens Flare")

        if scene.get('effect_kaleidoscope', 0) == 1:
            effects.append("Kaleidoscope")

        return ' | '.join(effects) if effects else 'None'
