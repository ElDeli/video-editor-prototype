#!/usr/bin/env python3
"""
Comprehensive Audio Test Script
Tests all audio features: TTS voices, sound effects, background music
"""
import requests
import json
import time

BASE_URL = "http://localhost:5001"

def create_test_project():
    """Create a comprehensive test project"""
    print("📦 Creating test project...")

    response = requests.post(f"{BASE_URL}/api/projects", json={
        "name": "COMPREHENSIVE AUDIO TEST",
        "script": "Scene one with clock ticking\n\nScene two with rain sounds\n\nScene three no sound effect"
    })

    if response.status_code not in [200, 201]:
        print(f"❌ Failed to create project: {response.text}")
        return None

    project = response.json()
    project_id = project['id']
    print(f"✅ Created project ID: {project_id}")
    return project_id

def update_project_settings(project_id):
    """Update project with background music and different TTS voices"""
    print(f"\n🎵 Updating project {project_id} settings...")

    # Add background music
    response = requests.patch(f"{BASE_URL}/api/projects/{project_id}", json={
        "background_music_path": "/Users/marcoglamngiw/Dropbox/Apps/output Horoskop/video_editor_prototype/uploads/music/orchestral_strings_piano_harmonic.mp3",
        "background_music_volume": 15  # 15% volume
    })

    if response.status_code == 200:
        print("✅ Background music added (15% volume)")
    else:
        print(f"❌ Failed to add background music: {response.text}")

    return response.status_code == 200

def get_scenes(project_id):
    """Get all scenes for the project"""
    response = requests.get(f"{BASE_URL}/api/projects/{project_id}/scenes")
    if response.status_code == 200:
        return response.json()['scenes']
    return []

def update_scene_with_sound_effect(project_id, scene_id, sound_effect_file, volume):
    """Add sound effect to a scene"""
    print(f"🔊 Adding sound effect to scene {scene_id} ({sound_effect_file}, {volume}% volume)...")

    response = requests.patch(f"{BASE_URL}/api/projects/{project_id}/scenes/{scene_id}", json={
        "sound_effect_path": f"/Users/marcoglamngiw/Dropbox/Apps/output Horoskop/video_editor_prototype/uploads/sound_effects/{sound_effect_file}",
        "sound_effect_volume": volume
    })

    if response.status_code == 200:
        print(f"✅ Sound effect added to scene {scene_id}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def update_scene_voice(project_id, scene_id, voice):
    """Change TTS voice for a scene"""
    print(f"🎤 Changing voice for scene {scene_id} to {voice}...")

    response = requests.patch(f"{BASE_URL}/api/projects/{project_id}/scenes/{scene_id}", json={
        "tts_voice": voice
    })

    if response.status_code == 200:
        print(f"✅ Voice changed to {voice}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def generate_preview(project_id):
    """Generate preview for the project"""
    print(f"\n🎬 Generating preview for project {project_id}...")

    response = requests.post(f"{BASE_URL}/api/projects/{project_id}/preview")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Preview generated successfully!")
        print(f"   Preview path: {result.get('preview_path', 'N/A')}")
        return True
    else:
        print(f"❌ Preview generation failed: {response.text}")
        return False

def main():
    print("=" * 70)
    print("🧪 COMPREHENSIVE AUDIO TEST")
    print("=" * 70)

    # Step 1: Create project
    project_id = create_test_project()
    if not project_id:
        return

    # Step 2: Update project settings
    if not update_project_settings(project_id):
        print("⚠️ Warning: Could not add background music")

    # Step 3: Get scenes
    print("\n📋 Fetching scenes...")
    scenes = get_scenes(project_id)
    print(f"✅ Found {len(scenes)} scenes")

    if len(scenes) >= 3:
        # Scene 1: Clock ticking + Female voice
        update_scene_with_sound_effect(project_id, scenes[0]['id'], "clock_ticking.mp3", 50)
        update_scene_voice(project_id, scenes[0]['id'], "de-DE-SeraphinaMultilingualNeural")

        # Scene 2: Rain + Male voice
        update_scene_with_sound_effect(project_id, scenes[1]['id'], "rain.mp3", 30)
        update_scene_voice(project_id, scenes[1]['id'], "de-DE-ConradNeural")

        # Scene 3: No sound effect, different voice
        update_scene_voice(project_id, scenes[2]['id'], "de-DE-KatjaNeural")

    # Step 4: Generate preview
    time.sleep(2)  # Wait a bit for updates to propagate
    success = generate_preview(project_id)

    print("\n" + "=" * 70)
    if success:
        print("✅ TEST COMPLETED SUCCESSFULLY!")
        print(f"   Project ID: {project_id}")
        print(f"   Check logs for FFmpeg stderr output")
    else:
        print("❌ TEST FAILED - Check logs for details")
    print("=" * 70)

if __name__ == "__main__":
    main()
