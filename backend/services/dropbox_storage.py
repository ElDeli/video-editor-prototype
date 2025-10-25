"""
Hybrid Dropbox Storage Manager
Automatically switches between local filesystem (Mac) and Dropbox API (Railway)
"""
import os
from pathlib import Path

# Try to import dropbox SDK (needed for Railway environment)
try:
    import dropbox
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False
    print("⚠️ Warning: Dropbox SDK not installed")

class DropboxStorage:
    def __init__(self):
        # Dropbox base paths
        self.dropbox_base = '~/Dropbox/Apps/output Horoskop/output/video_editor_prototype'
        self.local_dropbox_path = Path(os.path.expanduser(self.dropbox_base))

        # Check if local Dropbox folder exists (Mac environment)
        self.use_local = self.local_dropbox_path.exists()

        # Dropbox API credentials (only needed if not local)
        self.dbx = None
        if not self.use_local:
            self._init_dropbox_api()

        print(f"📁 Storage Mode: {'LOCAL FILESYSTEM' if self.use_local else 'DROPBOX API'}")

    def _init_dropbox_api(self):
        """Initialize Dropbox API client (Railway environment) with auto-refresh"""
        if not DROPBOX_AVAILABLE:
            print("⚠️ Warning: Dropbox SDK not available")
            return

        try:
            access_token = os.getenv('DROPBOX_ACCESS_TOKEN')
            refresh_token = os.getenv('DROPBOX_REFRESH_TOKEN')
            app_key = os.getenv('DROPBOX_APP_KEY')
            app_secret = os.getenv('DROPBOX_APP_SECRET')

            if not access_token:
                print("⚠️ Warning: DROPBOX_ACCESS_TOKEN not found, API unavailable")
                return

            # Initialize with auto-refresh if refresh token available
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
                print("✅ Dropbox API initialized (no auto-refresh - token will expire)")

        except Exception as e:
            print(f"⚠️ Dropbox API init failed: {e}")

    def save_file(self, rel_path, file_data):
        """
        Save file to storage (local or Dropbox API)

        Args:
            rel_path: Relative path from Dropbox base (e.g., 'uploads/music/song.mp3')
            file_data: File content (bytes)

        Returns:
            Full path to saved file
        """
        if self.use_local:
            # LOCAL FILESYSTEM (Mac)
            full_path = self.local_dropbox_path / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(file_data, bytes):
                full_path.write_bytes(file_data)
            else:
                # Assume file_data is a path to copy from
                import shutil
                shutil.copy2(file_data, full_path)

            return str(full_path)
        else:
            # DROPBOX API (Railway) + Local Cache
            dropbox_path = f'/Apps/output Horoskop/output/video_editor_prototype/{rel_path}'

            # Save locally in /tmp for immediate access
            local_cache_path = Path('/tmp/video_editor_cache') / rel_path
            local_cache_path.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(file_data, bytes):
                local_cache_path.write_bytes(file_data)
            else:
                # Assume file_data is a path to copy from
                import shutil
                shutil.copy2(file_data, local_cache_path)

            print(f"💾 Saved to local cache: {local_cache_path}")

            # ALSO upload to Dropbox (for permanent storage)
            if self.dbx:
                try:
                    with open(local_cache_path, 'rb') as f:
                        self.dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
                    print(f"☁️ Uploaded to Dropbox: {dropbox_path}")
                except Exception as e:
                    print(f"⚠️ Dropbox upload failed (continuing with local cache): {e}")
                    # Don't raise - we have local cache, that's enough

            # Return LOCAL path so video generation can access it
            return str(local_cache_path)

    def get_save_dir(self, rel_path):
        """
        Get directory path for saving files

        Args:
            rel_path: Relative path from Dropbox base (e.g., 'uploads/music')

        Returns:
            Path object for local filesystem, or Dropbox path string for API
        """
        if self.use_local:
            full_path = self.local_dropbox_path / rel_path
            full_path.mkdir(parents=True, exist_ok=True)
            return full_path
        else:
            # Return logical path for API (will use save_file to upload)
            return Path(rel_path)

    def file_exists(self, rel_path):
        """Check if file exists in storage"""
        if self.use_local:
            return (self.local_dropbox_path / rel_path).exists()
        else:
            if self.dbx:
                try:
                    dropbox_path = f'/Apps/output Horoskop/output/video_editor_prototype/{rel_path}'
                    self.dbx.files_get_metadata(dropbox_path)
                    return True
                except:
                    return False
            return False

    def get_file_content(self, rel_path):
        """Get file content from storage"""
        if self.use_local:
            return (self.local_dropbox_path / rel_path).read_bytes()
        else:
            if self.dbx:
                dropbox_path = f'/Apps/output Horoskop/output/video_editor_prototype/{rel_path}'
                _, response = self.dbx.files_download(dropbox_path)
                return response.content
            raise Exception("File not accessible")

# Global instance
storage = DropboxStorage()
