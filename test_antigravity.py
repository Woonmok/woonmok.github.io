#!/usr/bin/env python3
import os
import json
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent

print(f"Working: {PROJECT_ROOT}")
print(f"Dashboard: {(PROJECT_ROOT / 'dashboard_data.json').exists()}")
print(f"News: {(PROJECT_ROOT / 'daily_news.json').exists()}")

with (PROJECT_ROOT / 'dashboard_data.json').open() as f:
    dash = json.load(f)
print(f"Todos: {len(dash.get('todo_list', []))}")
for t in dash.get('todo_list', []):
    print(f"  {t['text']}")

with (PROJECT_ROOT / 'daily_news.json').open() as f:
    news = json.load(f)
print(f"News cats: {list(news.keys())}")

load_dotenv(PROJECT_ROOT / '.env')
print(f"Token OK: {bool(os.getenv('TELEGRAM_BOT_TOKEN'))}")
print(f"ChatID OK: {bool(os.getenv('TELEGRAM_CHAT_ID'))}")

import telebot
print("Telebot OK")
