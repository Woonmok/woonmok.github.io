#!/usr/bin/env python3
import os
import json
from dotenv import load_dotenv

base_dir = "/Volumes/AI_DATA_CENTRE/AI_WORKSPACE/woonmok.github.io"
os.chdir(base_dir)

print(f"Working: {base_dir}")
print(f"Dashboard: {os.path.exists('dashboard_data.json')}")
print(f"News: {os.path.exists('daily_news.json')}")

with open('dashboard_data.json') as f:
    dash = json.load(f)
print(f"Todos: {len(dash.get('todo_list', []))}")
for t in dash.get('todo_list', []):
    print(f"  {t['text']}")

with open('daily_news.json') as f:
    news = json.load(f)
print(f"News cats: {list(news.keys())}")

load_dotenv('.env')
print(f"Token OK: {bool(os.getenv('TELEGRAM_BOT_TOKEN'))}")
print(f"ChatID OK: {bool(os.getenv('TELEGRAM_CHAT_ID'))}")

import telebot
print("Telebot OK")
