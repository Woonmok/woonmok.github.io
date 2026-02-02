import os, requests, telebot, re, time, threading, fcntl, json
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 1. 지휘소 경로 및 봇 설정
os.chdir('/Users/seunghoonoh/woonmok.github.io')
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("⚠️ TELEGRAM_BOT_TOKEN 환경 변수가 설정되지 않았습니다!")
bot = telebot.TeleBot(TOKEN)

def load_dashboard_data():
    """dashboard_data.json 읽기"""
    try:
        with open('dashboard_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"todo_list": [], "system_status": "NORMAL"}

def save_dashboard_data(data):
    """dashboard_data.json 저장 (파일 잠금)"""
    with open('dashboard_data.json', 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            json.dump(data, f, ensure_ascii=False, indent=2)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def handle_telegram_command(msg_text):
    """텔레그램 명령 처리"""
    try:
        data = load_dashboard_data()
        
        # 1️⃣ 할일 추가: "추가: 작업명"
        if msg_text.startswith("추가:"):
            task = msg_text.replace("추가:", "").strip()
            max_id = max([item.get("id", 0) for item in data.get("todo_list", [])] or [0])
            new_todo = {"text": task, "completed": False, "id": max_id + 1}
            data["todo_list"].append(new_todo)
            save_dashboard_data(data)
            return f"✅ '{task}' 이 오늘의 할일에 추가되었습니다! (ID: {max_id + 1})"
        
        # 2️⃣ 할일 완료: "완료: 작업명" 또는 "완료: ID"
        elif msg_text.startswith("완료:"):
            target = msg_text.replace("완료:", "").strip()
            for item in data.get("todo_list", []):
                if item["text"] == target or str(item["id"]) == target:
                    item["completed"] = True
                    save_dashboard_data(data)
                    return f"🎉 '{item['text']}' 완료했습니다!"
            return "❌ 해당 할일을 찾을 수 없습니다."
        
        # 3️⃣ 할일 삭제: "삭제: 작업명" 또는 "삭제: ID"
        elif msg_text.startswith("삭제:"):
            target = msg_text.replace("삭제:", "").strip()
            original_len = len(data["todo_list"])
            data["todo_list"] = [
                item for item in data["todo_list"] 
                if item["text"] != target and str(item["id"]) != target
            ]
            if len(data["todo_list"]) < original_len:
                save_dashboard_data(data)
                return f"🗑️ 할일이 삭제되었습니다."
            return "❌ 해당 할일을 찾을 수 없습니다."
        
        # 4️⃣ 할일 목록 조회: "목록"
        elif msg_text in ["목록", "오늘", "할일"]:
            todos = data.get("todo_list", [])
            if not todos:
                return "📋 오늘의 할일이 없습니다."
            
            msg = "📋 **오늘의 할일**\n\n"
            for item in todos:
                status = "✅" if item["completed"] else "⭕"
                msg += f"{status} [{item['id']}] {item['text']}\n"
            return msg
        
        # 5️⃣ 상태 업데이트: "상태: 메시지"
        elif msg_text.startswith("상태:"):
            status_msg = msg_text.replace("상태:", "").strip()
            data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_dashboard_data(data)
            return f"📊 대시보드 상태: {status_msg}"
        
        return None  # 처리되지 않은 명령

    except Exception as e:
        return f"🚨 에러 발생: {str(e)}"

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    result = handle_telegram_command(message.text)
    
    if result:
        # 마크다운 포맷 해제 (텔레그램 마크다운 지원)
        bot.reply_to(message, result, parse_mode="markdown")

print("📡 [Wave Tree 오늘의 할일 관리 봇] 가동 중...")
print("✅ 명령어: 추가/완료/삭제/목록/상태")
bot.polling()