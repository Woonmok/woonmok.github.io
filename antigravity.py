#!/usr/bin/env python3
"""
antigravity.py - Wave Tree 통합 텔레그램 봇
- 매일 아침 9시 자동 브리핑 (할일 + 뉴스 + 날씨)
- 할일 관리 (추가/완료/삭제/목록)
- 실시간 날씨 조회
- 10분 간격 날씨 자동 업데이트
"""

import os
import sys
import json
import time
import threading
import fcntl
import warnings
import requests
import telebot
from datetime import datetime, timedelta

# 경고 억제
os.environ['PYTHONWARNINGS'] = 'ignore'
warnings.filterwarnings('ignore')

# --- 환경 변수 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))
os.chdir(BASE_DIR)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_CITY = "Jinan,KR"
AUTO_BRIEFING_ENABLED = os.getenv("ANTIGRAVITY_AUTO_BRIEFING", "false").strip().lower() in {"1", "true", "yes", "on"}

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN 환경 변수가 설정되지 않았습니다!")

bot = telebot.TeleBot(TOKEN)

# --- 파일 경로 ---
DASHBOARD_JSON = os.path.join(BASE_DIR, "dashboard_data.json")
DAILY_NEWS_JSON = os.path.join(BASE_DIR, "daily_news.json")
TODO_STORAGE_JSON = os.path.join(BASE_DIR, "todo_storage.json")
LOG_FILE = os.path.join(BASE_DIR, "logs", "antigravity.log")

os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ===== 데이터 로드/저장 =====

def load_dashboard():
    try:
        with open(DASHBOARD_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"todo_list": [], "system_status": "NORMAL"}


def save_dashboard(data):
    try:
        with open(DASHBOARD_JSON, 'w', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        sync_todo_storage_from_dashboard(data)
    except Exception as e:
        log(f"dashboard 저장 실패: {e}")


def sync_todo_storage_from_dashboard(dashboard_data):
    try:
        todos = dashboard_data.get("todo_list", [])
        tasks = []
        now_iso = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        for idx, item in enumerate(todos, 1):
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            task_id = item.get("id")
            if isinstance(task_id, int):
                mapped_id = task_id
            else:
                mapped_id = idx
            tasks.append({
                "id": mapped_id,
                "text": text,
                "completed": bool(item.get("completed", False)),
                "date": now_iso
            })

        payload = {
            "tasks": tasks,
            "lastMsgId": 0,
            "synced_from": "dashboard_data.json",
            "synced_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(TODO_STORAGE_JSON, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"todo_storage 동기화 실패: {e}")


def load_daily_news():
    try:
        with open(DAILY_NEWS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


# ===== 날씨 =====

def get_weather():
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={OPENWEATHER_CITY}&appid={OPENWEATHER_API_KEY}"
            f"&units=metric&lang=kr"
        )
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            d = resp.json()
            return {
                "temp": d['main']['temp'],
                "humidity": d['main']['humidity'],
                "desc": d['weather'][0]['description'],
                "text": f"진안 날씨: {d['weather'][0]['description']}, {d['main']['temp']}\u00b0C, 습도 {d['main']['humidity']}%"
            }
        return {"text": f"날씨 API 오류: {resp.status_code}"}
    except Exception as e:
        return {"text": f"날씨 조회 실패: {e}"}


def weather_updater():
    """10분마다 날씨를 dashboard_data.json에 기록"""
    while True:
        try:
            w = get_weather()
            data = load_dashboard()
            if "temp" in w:
                data["weather"] = {
                    "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "temp": w["temp"],
                    "humidity": w["humidity"],
                    "desc": w["desc"]
                }
            save_dashboard(data)
        except Exception as e:
            log(f"날씨 업데이트 실패: {e}")
        time.sleep(600)


# ===== 매일 아침 9시 브리핑 =====

def build_briefing():
    """대시보드 데이터로 브리핑 메시지 생성"""
    now = datetime.now()
    dashboard = load_dashboard()
    news_data = load_daily_news()

    lines = []
    lines.append(f"\U0001f514 [운목 지휘소] 통합 브리핑")
    lines.append(f"\U0001f4c5 {now.strftime('%Y년 %m월 %d일')} 오전 {now.strftime('%H:%M')}")
    lines.append("")

    # 1) 날씨
    w = get_weather()
    if "temp" in w:
        lines.append(f"\U0001f4cd 진안 기온: {w['temp']}\u00b0C ({w['desc']})")
    else:
        lines.append(f"\U0001f4cd {w.get('text', '날씨 정보 없음')}")
    lines.append("")

    # 2) 할일 목록 (dashboard_data.json)
    todos = dashboard.get("todo_list", [])
    if todos:
        lines.append("\u2705 [오늘의 할 일 목록]")
        for item in todos:
            status = "\u2705" if item.get("completed") else "\u2b55"
            text = item.get("text", "")
            lines.append(f"{status} {text}")
    else:
        lines.append("\U0001f4cb 등록된 할일이 없습니다.")
    lines.append("")

    # 3) 뉴스 헤드라인 요약 (daily_news.json)
    category_icons = {
        "listeria": "\U0001f9a0",
        "cultured_meat": "\U0001f969",
        "audio": "\U0001f3b5",
        "computer_ai": "\U0001f916",
        "global_biz": "\U0001f30d"
    }
    category_names = {
        "listeria": "Listeria Free",
        "cultured_meat": "Cultured Meat",
        "audio": "High-End Audio",
        "computer_ai": "Computer & AI",
        "global_biz": "Global Biz"
    }

    has_news = False
    for cat_key, icon in category_icons.items():
        items = news_data.get(cat_key, [])
        if items:
            if not has_news:
                lines.append("\U0001f4f0 [뉴스 헤드라인]")
                has_news = True
            name = category_names.get(cat_key, cat_key)
            title = items[0].get("title", "")
            if len(title) > 50:
                title = title[:50] + "..."
            lines.append(f"{icon} {name}: {title}")

    if not has_news:
        lines.append("\U0001f4f0 뉴스 데이터 없음")

    return "\n".join(lines)


def send_briefing():
    """브리핑 메시지를 텔레그램으로 전송"""
    if not CHAT_ID:
        log("CHAT_ID 미설정, 브리핑 전송 불가")
        return
    try:
        msg = build_briefing()
        bot.send_message(CHAT_ID, msg)
        log("아침 브리핑 전송 완료")
    except Exception as e:
        log(f"브리핑 전송 실패: {e}")


def briefing_scheduler():
    """매일 아침 9시에 브리핑 전송"""
    log("브리핑 스케줄러 시작 (매일 09:00)")
    while True:
        now = datetime.now()
        # 다음 9시 계산
        target = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)

        wait_sec = (target - now).total_seconds()
        log(f"다음 브리핑까지 {wait_sec:.0f}초 대기 ({target.strftime('%Y-%m-%d %H:%M')})")
        time.sleep(wait_sec)

        # 브리핑 전송
        send_briefing()

        # 같은 시각 중복 방지
        time.sleep(60)


# ===== 텔레그램 명령 처리 =====

@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.reply_to(message,
        "\U0001f44b 안녕하세요! Wave Tree 통합 봇입니다.\n\n"
        "\U0001f4cb 명령어:\n"
        "/todo - 할일 목록 보기\n"
        "/weather - 진안 날씨\n"
        "/briefing - 브리핑 즉시 받기\n"
        "/help - 도움말\n\n"
        "\U0001f4ac 텍스트 명령:\n"
        "추가: 작업명\n"
        "완료: ID\n"
        "삭제: ID\n"
        "할일: 1. xxx, 2. yyy"
    )


@bot.message_handler(commands=['todo', 'list'])
def cmd_todo(message):
    data = load_dashboard()
    todos = data.get("todo_list", [])
    if not todos:
        bot.reply_to(message, "\U0001f4cb 등록된 할일이 없습니다.")
        return
    msg = "\U0001f4cb 오늘의 할일\n\n"
    for item in todos:
        status = "\u2705" if item.get("completed") else "\u2b55"
        msg += f"{status} [{item.get('id', '?')}] {item.get('text', '')}\n"
    bot.reply_to(message, msg)


@bot.message_handler(commands=['weather'])
def cmd_weather(message):
    w = get_weather()
    bot.reply_to(message, w.get("text", str(w)))


@bot.message_handler(commands=['briefing'])
def cmd_briefing(message):
    msg = build_briefing()
    bot.reply_to(message, msg)


@bot.message_handler(commands=['help'])
def cmd_help(message):
    bot.reply_to(message,
        "\U0001f4da 명령어 도움말\n\n"
        "/start - 시작\n"
        "/todo - 할일 목록\n"
        "/weather - 진안 날씨\n"
        "/briefing - 브리핑 즉시 받기\n"
        "/help - 이 도움말\n\n"
        "\U0001f4ac 텍스트 명령:\n"
        "추가: 작업명 - 할일 추가\n"
        "완료: ID - 완료 처리\n"
        "삭제: ID - 삭제\n"
        "목록 - 할일 보기\n"
        "할일: 1. xxx, 2. yyy - 덮어쓰기"
    )


@bot.message_handler(func=lambda m: True)
def handle_text(message):
    text = message.text.strip()
    data = load_dashboard()

    # 추가
    if text.startswith("추가:"):
        task = text.replace("추가:", "").strip()
        if not task:
            bot.reply_to(message, "\u274c 작업명을 입력해주세요.")
            return
        max_id = max([item.get("id", 0) for item in data.get("todo_list", [])] or [0])
        new_id = max_id + 1
        data.setdefault("todo_list", []).append({"text": task, "completed": False, "id": new_id})
        data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_dashboard(data)
        bot.reply_to(message, f"\u2705 '{task}' 추가됨 (ID: {new_id})")
        return

    # 완료
    if text.startswith("완료:"):
        target = text.replace("완료:", "").strip()
        for item in data.get("todo_list", []):
            if str(item.get("id")) == target or item.get("text") == target:
                item["completed"] = True
                data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_dashboard(data)
                bot.reply_to(message, f"\U0001f389 '{item['text']}' 완료!")
                return
        bot.reply_to(message, "\u274c 해당 할일을 찾을 수 없습니다.")
        return

    # 삭제
    if text.startswith("삭제:"):
        target = text.replace("삭제:", "").strip()
        original = len(data.get("todo_list", []))
        data["todo_list"] = [
            item for item in data.get("todo_list", [])
            if str(item.get("id")) != target and item.get("text") != target
        ]
        if len(data["todo_list"]) < original:
            data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_dashboard(data)
            bot.reply_to(message, "\U0001f5d1\ufe0f 삭제 완료.")
        else:
            bot.reply_to(message, "\u274c 해당 할일을 찾을 수 없습니다.")
        return

    # 목록
    if text in ["목록", "오늘", "할일", "내가 할 일", "내가할일"]:
        cmd_todo(message)
        return

    # 날씨
    if text in ["날씨", "기온"]:
        cmd_weather(message)
        return

    # 할일 덮어쓰기: "할일: 1. xxx, 2. yyy"
    if (
        text.startswith("할일:")
        or text.startswith("할일 :")
        or text.startswith("내가 할 일:")
        or text.startswith("내가할일:")
    ):
        task_text = text.split(":", 1)[1].strip()
        if not task_text:
            bot.reply_to(message, "\u274c 할일을 입력해주세요! 예) 할일: 1. 회의 준비, 2. 자료 정리")
            return
        tasks = [t.strip() for t in task_text.split(",")]
        new_list = []
        for task in tasks:
            if not task:
                continue
            parts = task.split(".", 1)
            if len(parts) == 2 and parts[0].strip().isdigit():
                tid = int(parts[0].strip())
                ttext = f"{parts[0].strip()}. {parts[1].strip()}"
                new_list.append({"id": tid, "text": ttext, "completed": False})
            else:
                new_list.append({"id": len(new_list)+1, "text": task, "completed": False})

        if not new_list:
            bot.reply_to(message, "\u274c 형식이 맞지 않습니다. 예) 할일: 1. 대시보드, 2. 리포트")
            return

        data["todo_list"] = sorted(new_list, key=lambda x: x["id"])
        data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_dashboard(data)

        items = "\n".join([f"\u2713 {item['text']}" for item in data["todo_list"]])
        bot.reply_to(message, f"\u2705 할일 업데이트 완료!\n\n{items}")
        return


# ===== 메인 =====

def main():
    log("antigravity.py 시작")

    # 1) 날씨 자동 업데이트 스레드
    t1 = threading.Thread(target=weather_updater, daemon=True)
    t1.start()
    log("날씨 업데이터 스레드 시작")

    # 2) 아침 9시 브리핑 스케줄러 스레드 (기본 비활성화)
    if AUTO_BRIEFING_ENABLED:
        t2 = threading.Thread(target=briefing_scheduler, daemon=True)
        t2.start()
        log("브리핑 스케줄러 스레드 시작")
    else:
        log("브리핑 스케줄러 비활성화 (ANTIGRAVITY_AUTO_BRIEFING=false)")

    # 3) 텔레그램 폴링
    log("텔레그램 폴링 시작")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except BaseException as e:
            log(f"텔레그램 폴링 오류: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
