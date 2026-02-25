#!/bin/bash

# Start both Wave Tree dashboards in background processes
# Usage: ./start-all.sh
# To stop: kill the PIDs or press Ctrl+C

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
WORKSPACE_ROOT="${WAVETREE_WORKSPACE_ROOT:-$(cd "$PROJECT_ROOT/.." && pwd)}"
JINAN_DIR="$PROJECT_ROOT/jinan-dashboard"
NEWS_HUB_DIR="${NEWS_HUB_DIR:-$WORKSPACE_ROOT/wave-tree-news-hub}"

if [ ! -d "$NEWS_HUB_DIR" ]; then
	NEWS_HUB_DIR="$WORKSPACE_ROOT/wave-tree-news-hub"
fi

echo "🚀 Starting Wave Tree Dashboards..."
echo ""

# Start jinan-dashboard (Vite dev server)
cd "$JINAN_DIR"
npm run dev -- --host 127.0.0.1 &
JINAN_PID=$!
echo "✅ jinan-dashboard started (PID: $JINAN_PID)"
echo "   🔗 http://127.0.0.1:5173/"
echo ""

# Start wave-tree-news-hub (Python HTTP server)
cd "$NEWS_HUB_DIR"
python3 -m http.server 8000 &
WAVE_PID=$!
echo "✅ wave-tree-news-hub started (PID: $WAVE_PID)"
echo "   🔗 http://127.0.0.1:8000/wave-tree-news-hub.html"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Both servers are running. Press Ctrl+C to stop."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Keep the script running and handle Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $JINAN_PID $WAVE_PID 2>/dev/null; exit" INT

# Wait for both processes
wait $JINAN_PID $WAVE_PID 2>/dev/null || true
