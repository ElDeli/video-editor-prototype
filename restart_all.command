#!/bin/bash

# Restart All Video Editor Processes
echo "🔄 Restarting Video Editor Prototype..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Stop all processes first
echo "🛑 Stopping all processes..."
"$SCRIPT_DIR/stop_all.command"

# Wait a moment for clean shutdown
echo ""
echo "⏳ Waiting for clean shutdown..."
sleep 3

# Start all processes
echo ""
echo "🚀 Starting all processes..."
"$SCRIPT_DIR/start_all.command"
