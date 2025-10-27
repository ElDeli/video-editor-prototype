#!/usr/bin/env python3
"""
Mac Dropbox Sync Poller
Automatically downloads files uploaded by Railway to local Mac
Runs in background and polls sync queue every 30 seconds
"""
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import dropbox
    from services.dropbox_storage import storage
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("⚠️ Make sure you're running from the backend directory")
    sys.exit(1)


class MacSyncPoller:
    def __init__(self):
        self.storage = storage
        self.sync_queue_path = '.sync_queue.json'
        self.local_base = Path(os.path.expanduser('~/Library/CloudStorage/Dropbox/Apps/output Horoskop/output/video_editor_prototype'))
        self.poll_interval = 30  # seconds

        # Check if running on Mac with local Dropbox
        if not self.storage.use_local:
            print("❌ This script must run on a Mac with local Dropbox access!")
            print(f"❌ Dropbox path not found: {self.local_base}")
            sys.exit(1)

        # Initialize Dropbox API for downloading
        self.dbx = None
        self._init_dropbox_api()

    def _init_dropbox_api(self):
        """Initialize Dropbox API for downloads"""
        try:
            access_token = os.getenv('DROPBOX_ACCESS_TOKEN')
            refresh_token = os.getenv('DROPBOX_REFRESH_TOKEN')
            app_key = os.getenv('DROPBOX_APP_KEY')
            app_secret = os.getenv('DROPBOX_APP_SECRET')

            if not access_token:
                print("⚠️ DROPBOX_ACCESS_TOKEN not found - will try without API")
                return

            if refresh_token and app_key and app_secret:
                self.dbx = dropbox.Dropbox(
                    oauth2_access_token=access_token,
                    oauth2_refresh_token=refresh_token,
                    app_key=app_key,
                    app_secret=app_secret
                )
                print("✅ Dropbox API initialized with AUTO-REFRESH")
            else:
                self.dbx = dropbox.Dropbox(access_token)
                print("✅ Dropbox API initialized (no auto-refresh)")

        except Exception as e:
            print(f"⚠️ Dropbox API init failed: {e}")

    def read_sync_queue(self):
        """Read sync queue from Dropbox"""
        if not self.dbx:
            return {'pending': []}

        try:
            dropbox_path = f'/Apps/output Horoskop/output/video_editor_prototype/{self.sync_queue_path}'
            _, response = self.dbx.files_download(dropbox_path)
            queue = json.loads(response.content)
            return queue
        except dropbox.exceptions.ApiError as e:
            if 'not_found' in str(e):
                # Queue file doesn't exist yet
                return {'pending': []}
            print(f"⚠️ Error reading sync queue: {e}")
            return {'pending': []}
        except Exception as e:
            print(f"⚠️ Error parsing sync queue: {e}")
            return {'pending': []}

    def clear_sync_queue(self):
        """Clear sync queue after processing"""
        if not self.dbx:
            return

        try:
            dropbox_path = f'/Apps/output Horoskop/output/video_editor_prototype/{self.sync_queue_path}'
            empty_queue = json.dumps({'pending': []}, indent=2).encode('utf-8')
            self.dbx.files_upload(
                empty_queue,
                dropbox_path,
                mode=dropbox.files.WriteMode.overwrite
            )
        except Exception as e:
            print(f"⚠️ Error clearing sync queue: {e}")

    def download_file(self, rel_path):
        """Download file from Dropbox to local Mac"""
        if not self.dbx:
            print(f"⚠️ Cannot download {rel_path} - Dropbox API not initialized")
            return False

        try:
            dropbox_path = f'/Apps/output Horoskop/output/video_editor_prototype/{rel_path}'
            local_path = self.local_base / rel_path

            # Check if file already exists locally
            if local_path.exists():
                print(f"⏭️  File already exists locally: {rel_path}")
                return True

            # Download from Dropbox
            metadata, response = self.dbx.files_download(dropbox_path)
            file_data = response.content

            # Create parent directories if needed
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Save to local filesystem
            local_path.write_bytes(file_data)

            size_kb = len(file_data) / 1024
            print(f"✅ Downloaded: {rel_path} ({size_kb:.1f} KB)")
            return True

        except Exception as e:
            print(f"❌ Error downloading {rel_path}: {e}")
            return False

    def process_queue(self):
        """Process sync queue and download pending files"""
        queue = self.read_sync_queue()
        pending = queue.get('pending', [])

        if not pending:
            return 0

        print(f"\n📥 Processing {len(pending)} pending files...")

        downloaded = 0
        for item in pending:
            rel_path = item.get('path')
            if rel_path and self.download_file(rel_path):
                downloaded += 1

        # Clear queue after processing
        if downloaded > 0:
            self.clear_sync_queue()
            print(f"✅ Downloaded {downloaded}/{len(pending)} files")

        return downloaded

    def run(self):
        """Main polling loop"""
        print("=" * 80)
        print("🔄 Mac Dropbox Sync Poller")
        print("=" * 80)
        print(f"📁 Local Dropbox: {self.local_base}")
        print(f"⏱️  Poll interval: {self.poll_interval} seconds")
        print(f"🔑 Dropbox API: {'✅ Ready' if self.dbx else '❌ Not available'}")
        print("=" * 80)
        print("\n🚀 Starting polling loop (Ctrl+C to stop)...\n")

        try:
            while True:
                try:
                    self.process_queue()
                except Exception as e:
                    print(f"❌ Error in poll cycle: {e}")

                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped by user")
            print("=" * 80)


if __name__ == '__main__':
    poller = MacSyncPoller()
    poller.run()
