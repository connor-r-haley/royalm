#!/bin/bash

echo "🚀 Starting WWIII Simulator..."

# Get absolute paths
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$ROOT_DIR/venv"

# Start backend
cd "$BACKEND_DIR"
source "$VENV_DIR/bin/activate"
echo "📡 Starting backend server..."
python -m uvicorn main:app --reload --port 8001 &
BACKEND_PID=$!

# Start frontend
cd "$FRONTEND_DIR"
echo "🌐 Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

echo "✅ Servers started in background!"
echo "📡 Backend running on: http://localhost:8001"
echo "🌐 Frontend running on: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

# Handle cleanup on script exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for either process to exit
wait