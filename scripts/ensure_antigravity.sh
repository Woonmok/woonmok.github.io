#!/bin/zsh
set -euo pipefail

BASE_DIR="/Volumes/AI_DATA_CENTRE/AI_WORKSPACE/woonmok.github.io"
SCRIPT_PATH="$BASE_DIR/antigravity.py"
STDOUT_LOG="$BASE_DIR/logs/antigravity_stdout.log"
STDERR_LOG="$BASE_DIR/logs/antigravity_error.log"

if [[ ! -f "$SCRIPT_PATH" ]]; then
  exit 0
fi

if pgrep -f "$SCRIPT_PATH" >/dev/null 2>&1; then
  exit 0
fi

mkdir -p "$BASE_DIR/logs"
cd "$BASE_DIR"
nohup /usr/bin/python3 "$SCRIPT_PATH" >> "$STDOUT_LOG" 2>> "$STDERR_LOG" &
