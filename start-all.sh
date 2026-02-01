#!/bin/bash

# Start both Wave Tree dashboards in background processes
# Usage: ./start-all.sh
# To stop: kill the PIDs or press Ctrl+C

set -e

echo "🚀 Starting Wave Tree Dashboards..."
echo ""

# Start jinan-dashboard (Vite dev server)
cd /Users/seunghoonoh/woonmok.github.io/jinan-dashboard
npm run dev -- --host 127.0.0.1 &
JINAN_PID=$!
echo "✅ jinan-dashboard started (PID: $JINAN_PID)"
echo "   🔗 http://127.0.0.1:5173/"
echo ""

# Start wave-tree-news-hub (Python HTTP server)
cd /Users/seunghoonoh/Desktop/wave-tree-news-hub
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
