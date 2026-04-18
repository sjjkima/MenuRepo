#!/bin/bash

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

cd "$ROOT_DIR"

echo ""
echo "TableOrder Restaurant System"
echo "================================"

# Create required dirs
mkdir -p "$BACKEND_DIR/data" "$BACKEND_DIR/generated/qr_codes"

# Install Python deps
echo ""
echo "Installing Python dependencies..."
python3 -m pip install -r "$BACKEND_DIR/requirements.txt" -q

echo ""
echo "Setup complete!"
echo ""
echo "Starting servers..."
echo ""

# Start backend in background
echo "Starting FastAPI backend on :8000"
python3 -m uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

sleep 1

# Start frontend server
echo "Starting frontend server on :8080"
python3 "$FRONTEND_DIR/serve_frontend.py" &
FRONTEND_PID=$!

echo ""
echo "============================================="
echo "  System is running"
echo ""
echo "  Customer Menu (Table 1):"
echo "     http://localhost:8080/customer.html?table=1"
echo ""
echo "  Reception Dashboard:"
echo "     http://localhost:8080/admin.html"
echo ""
echo "  Analytics Dashboard:"
echo "     http://localhost:8080/analytics.html"
echo ""
echo "  API Docs (FastAPI):"
echo "     http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop all servers"
echo "============================================="

# Wait and cleanup on exit
trap "echo ''; echo 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
