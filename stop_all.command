#!/bin/bash

# Stop All Video Editor Processes
echo "🛑 Stopping Video Editor Prototype..."
echo ""

# Kill all Python backend processes (app.py)
echo "🔪 Killing Python backend processes..."
pkill -f "python app.py" 2>/dev/null
pkill -f "venv/bin/python app.py" 2>/dev/null
echo "✅ Python backend processes stopped"

# Kill Mac Sync Poller
echo "🔪 Killing Mac Sync Poller..."
pkill -f "mac_sync_poller.py" 2>/dev/null
echo "✅ Mac Sync Poller stopped"

# Kill all Node/Vite frontend processes
echo "🔪 Killing Node/Vite frontend processes..."
pkill -f "vite" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
echo "✅ Node/Vite frontend processes stopped"

# Kill any remaining processes on ports
echo "🔪 Freeing up ports 3000 and 5001..."
lsof -ti:5001 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

# Clear Python cache to ensure fresh start
echo "🧹 Clearing Python cache..."
cd "$(dirname "$0")/backend" 2>/dev/null
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
echo "✅ Python cache cleared"

echo ""
echo "✅ All processes stopped!"
echo "🎯 Ports 3000 and 5001 are now free"
echo ""
