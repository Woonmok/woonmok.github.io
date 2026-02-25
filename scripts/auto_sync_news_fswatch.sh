#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_ROOT="${WAVETREE_WORKSPACE_ROOT:-$(cd "$PROJECT_ROOT/.." && pwd)}"
NEWS_HUB_DIR="${NEWS_HUB_DIR:-$WORKSPACE_ROOT/wave-tree-news-hub}"

SRC_TXT="$NEWS_HUB_DIR/data/raw/perplexity.txt"
NORMALIZED_JSON="$NEWS_HUB_DIR/data/normalized/news.json"
MIRROR_JSON="$PROJECT_ROOT/news.json"
SYNC_SCRIPT="$NEWS_HUB_DIR/sync_top_news.py"
PYTHON_BIN="$NEWS_HUB_DIR/.venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

fswatch -0 "$SRC_TXT" | while read -d "" event
 do
  echo "[auto_sync_news] 감지: $event"
  cd "$NEWS_HUB_DIR"
  node scripts/normalize.js --in "$SRC_TXT" --out "$NORMALIZED_JSON"
  cp "$NORMALIZED_JSON" "$MIRROR_JSON"
  echo "[auto_sync_news] news.json 동기화 완료"
  "$PYTHON_BIN" "$SYNC_SCRIPT"
done
