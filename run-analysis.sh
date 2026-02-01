#!/bin/bash
# Antigravity Radar 분석 실행 스크립트

# wave-tree-news-hub의 Python 환경 사용
PYTHON_PATH="/Users/seunghoonoh/Desktop/wave-tree-news-hub/.venv/bin/python"
SCRIPT_PATH="/Users/seunghoonoh/woonmok.github.io/analyze_radar.py"

# .env 파일에서 API 키 로드
if [ -f /Users/seunghoonoh/Desktop/wave-tree-news-hub/.env ]; then
    export $(cat /Users/seunghoonoh/Desktop/wave-tree-news-hub/.env | grep -v '^#' | xargs)
fi

echo "🔍 Antigravity Radar 분석 도구 시작..."
$PYTHON_PATH $SCRIPT_PATH
