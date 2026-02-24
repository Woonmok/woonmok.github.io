#!/bin/zsh
set -euo pipefail

BASE_DIR="/Volumes/AI_DATA_CENTRE/AI_WORKSPACE/woonmok.github.io"
SCRIPT_PATH="$BASE_DIR/antigravity.py"
STDOUT_LOG="$BASE_DIR/logs/antigravity_stdout.log"
STDERR_LOG="$BASE_DIR/logs/antigravity_error.log"

if [[ ! -f "$SCRIPT_PATH" ]]; then
  exit 0
fi

PIDS=($(pgrep -f "[a]ntigravity.py" || true))
PID_COUNT=${#PIDS[@]}

if [[ "$PID_COUNT" -gt 1 ]]; then
  KEEP_PID="${PIDS[-1]}"
  for pid in "${PIDS[@]}"; do
    if [[ "$pid" != "$KEEP_PID" ]]; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  exit 0
fi

if [[ "$PID_COUNT" -eq 1 ]]; then
  exit 0
fi

mkdir -p "$BASE_DIR/logs"
cd "$BASE_DIR"
nohup /usr/bin/python3 "$SCRIPT_PATH" >> "$STDOUT_LOG" 2>> "$STDERR_LOG" &
