#!/bin/bash

# Start All Video Editor Processes
echo "🚀 Starting Video Editor Prototype..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Kill any existing processes first (clean start)
echo "🧹 Cleaning up old processes..."
pkill -f "python app.py" 2>/dev/null
pkill -f "vite" 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:5001 | xargs kill -9 2>/dev/null
sleep 2

# Clear Python cache for fresh start
echo "🗑️  Clearing Python cache..."
cd "$SCRIPT_DIR/backend"
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
echo "✅ Python cache cleared - loading fresh code"
sleep 1

# Start Backend (Python Flask)
echo "🐍 Starting Backend (Port 5001)..."
cd "$SCRIPT_DIR/backend" || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Start backend in background with nohup
nohup ./venv/bin/python app.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 3

# Start Frontend (Vite React)
echo "⚛️  Starting Frontend (Port 3000)..."
cd "$SCRIPT_DIR/frontend" || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Error: node_modules not found!"
    echo "Please run: npm install"
    exit 1
fi

# Start frontend in background with nohup
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

# Wait for services to fully start
echo ""
echo "⏳ Waiting for services to initialize..."
sleep 5

# Check if services are running
echo ""
echo "🔍 Checking services..."

if lsof -ti:5001 > /dev/null 2>&1; then
    echo "✅ Backend running on http://localhost:5001"
else
    echo "❌ Backend failed to start! Check logs/backend.log"
fi

if lsof -ti:3000 > /dev/null 2>&1; then
    echo "✅ Frontend running on http://localhost:3000"
else
    echo "❌ Frontend failed to start! Check logs/frontend.log"
fi

echo ""
echo "🎉 Video Editor Prototype is ready!"
echo ""
echo "📝 Logs:"
echo "   Backend:  $SCRIPT_DIR/logs/backend.log"
echo "   Frontend: $SCRIPT_DIR/logs/frontend.log"
echo ""
echo "🌐 Open in browser: http://localhost:3000"
echo ""
