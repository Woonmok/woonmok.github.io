#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SCRIPT_PATH="$PROJECT_ROOT/antigravity.py"
STDOUT_LOG="$PROJECT_ROOT/logs/antigravity_stdout.log"
STDERR_LOG="$PROJECT_ROOT/logs/antigravity_error.log"
PYTHON_BIN="python3"

if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
elif [[ -x "$PROJECT_ROOT/.venv-1/bin/python" ]]; then
  PYTHON_BIN="$PROJECT_ROOT/.venv-1/bin/python"
fi

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

mkdir -p "$PROJECT_ROOT/logs"
cd "$PROJECT_ROOT"
nohup "$PYTHON_BIN" "$SCRIPT_PATH" >> "$STDOUT_LOG" 2>> "$STDERR_LOG" &
