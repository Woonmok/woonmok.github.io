#!/bin/bash
set -euo pipefail

SRC_TXT="/Volumes/AI_DATA_CENTRE/AI_WORKSPACE/wave-tree-news-hub/data/raw/perplexity.txt"
NORMALIZED_JSON="/Volumes/AI_DATA_CENTRE/AI_WORKSPACE/wave-tree-news-hub/data/normalized/news.json"
MIRROR_JSON="/Volumes/AI_DATA_CENTRE/AI_WORKSPACE/woonmok.github.io/news.json"
SYNC_SCRIPT="/Volumes/AI_DATA_CENTRE/AI_WORKSPACE/wave-tree-news-hub/sync_top_news.py"
PYTHON_BIN="/Volumes/AI_DATA_CENTRE/AI_WORKSPACE/wave-tree-news-hub/.venv312/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

fswatch -0 "$SRC_TXT" | while read -d "" event
 do
  echo "[auto_sync_news] 감지: $event"
  cd "/Volumes/AI_DATA_CENTRE/AI_WORKSPACE/wave-tree-news-hub"
  node scripts/normalize.js --in "$SRC_TXT" --out "$NORMALIZED_JSON"
  cp "$NORMALIZED_JSON" "$MIRROR_JSON"
  echo "[auto_sync_news] news.json 동기화 완료"
  "$PYTHON_BIN" "$SYNC_SCRIPT"
done
