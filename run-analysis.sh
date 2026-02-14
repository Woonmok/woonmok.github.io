#!/bin/bash
# Antigravity Radar 분석 실행 스크립트

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
NEWS_HUB_DIR="/Volumes/AI_DATA_CENTRE/AI_WORKSPACE/wave-tree-news-hub"

if [ ! -d "$NEWS_HUB_DIR" ]; then
    NEWS_HUB_DIR="$WORKSPACE_ROOT/wave-tree-news-hub"
fi

if [ -x "$NEWS_HUB_DIR/.venv312/bin/python" ]; then
    PYTHON_PATH="$NEWS_HUB_DIR/.venv312/bin/python"
elif [ -x "$NEWS_HUB_DIR/.venv/bin/python" ]; then
    PYTHON_PATH="$NEWS_HUB_DIR/.venv/bin/python"
else
    PYTHON_PATH="python3"
fi

SCRIPT_PATH="$SCRIPT_DIR/analyze_radar.py"

# .env 파일에서 API 키 로드
if [ -f "$NEWS_HUB_DIR/.env" ]; then
    export $(cat "$NEWS_HUB_DIR/.env" | grep -v '^#' | xargs)
fi

echo "🔍 Antigravity Radar 분석 도구 시작..."
$PYTHON_PATH $SCRIPT_PATH
