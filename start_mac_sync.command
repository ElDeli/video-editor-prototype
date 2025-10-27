#!/bin/bash
# Mac Dropbox Sync Poller Starter
# Double-click this file to start the sync poller

cd "$(dirname "$0")/backend"

echo "=================================="
echo "🔄 Starting Mac Dropbox Sync Poller"
echo "=================================="
echo ""

# Load environment variables if .env exists
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
    echo "✅ Loaded environment variables from .env"
fi

# Start the poller
python3 mac_sync_poller.py

echo ""
echo "Poller stopped."
