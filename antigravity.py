import warnings
from urllib3.exceptions import NotOpenSSLWarning
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# --- 모든 import를 맨 위로 이동 ---


import os, requests, telebot, re, time, threading, fcntl, json, warnings
from datetime import datetime
from dotenv import load_dotenv
import urllib3
from urllib3.exceptions import NotOpenSSLWarning
# 모든 경고 완전 억제 (환경변수 + 코드)
os.environ['PYTHONWARNINGS'] = 'ignore'
warnings.filterwarnings('ignore')
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)

# --- 환경 변수 및 상수 ---
OPENWEATHER_API_KEY = "73522ad14e4276bdf715f0e796fc623f"
OPENWEATHER_CITY = "Jinan,KR"  # 진안, 대한민국

load_dotenv()
os.chdir('/Users/seunghoonoh/woonmok.github.io')
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("⚠️ TELEGRAM_BOT_TOKEN 환경 변수가 설정되지 않았습니다!")
bot = telebot.TeleBot(TOKEN)

# --- 파일 입출력 함수 ---
def load_dashboard_data():
    try:
        with open('dashboard_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"todo_list": [], "system_status": "NORMAL"}

def save_dashboard_data(data):
    path = 'dashboard_data.json'
    try:
        with open(path, 'w', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"[save_dashboard_data] 기록 성공: {path}")
                print(f"[save_dashboard_data] 데이터: {data}")
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        print(f"[save_dashboard_data] 기록 실패: {path}, 에러: {e}")
        with open("logs/antigravity_error.log", "a", encoding="utf-8") as logf:
            logf.write(f"[save_dashboard_data][EXCEPTION] {datetime.now()} {e}\n")

# --- 날씨 API ---
def get_weather():
    print("get_weather() called")
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={OPENWEATHER_CITY}&appid={OPENWEATHER_API_KEY}&units=metric&lang=kr"
        print(f"Requesting: {url}")
        resp = requests.get(url, timeout=10)
        print(f"Response status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Weather data: {data}")
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            desc = data['weather'][0]['description']
            result = {
                "text": f"진안 실시간 날씨: {desc}, 온도 {temp}°C, 습도 {humidity}%",
                "temp": temp,
                "humidity": humidity,
                "desc": desc
            }
        else:
            result = {"text": f"[날씨] API 오류: {resp.status_code}"}
        print(f"get_weather result: {result}")
        with open("logs/antigravity_error.log", "a", encoding="utf-8") as logf:
            logf.write(f"[get_weather] {datetime.now()} {result}\n")
        return result
    except Exception as e:
        print(f"get_weather exception: {e}")
        err = {"text": f"[날씨] 연결 오류: {e}"}
        with open("logs/antigravity_error.log", "a", encoding="utf-8") as logf:
            logf.write(f"[get_weather][EXCEPTION] {datetime.now()} {e}\n")
        return err

# --- 날씨 자동 업데이트 스레드 ---
def weather_updater():
    print("weather_updater thread started")
    def update_once():
        try:
            print("weather_updater: update_once called")
            weather = get_weather()
            data = load_dashboard_data()
            # weather dict에 temp가 없더라도 반드시 weather 필드 기록
            if isinstance(weather, dict) and "temp" in weather:
                data["weather"] = {
                    "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "temp": weather["temp"],
                    "humidity": weather["humidity"],
                    "desc": weather["desc"]
                }
            else:
                data["weather"] = {
                    "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error": str(weather.get('text', weather))
                }
            save_dashboard_data(data)
            print(f"weather field written: {data['weather']}")
        except Exception as e:
            print(f"weather_updater exception: {e}")
            data = load_dashboard_data()
            data["weather"] = {
                "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": f"weather_updater exception: {e}"
            }
            save_dashboard_data(data)
            with open("logs/antigravity_error.log", "a", encoding="utf-8") as logf:
                logf.write(f"[weather_updater][EXCEPTION] {datetime.now()} {e}\n")
    # 최초 1회 즉시 실행
    update_once()
    while True:
        time.sleep(600)
        update_once()

if __name__ == "__main__":
    print("antigravity.py main started")
    threading.Thread(target=weather_updater, daemon=True).start()
threading.Thread(target=weather_updater, daemon=True).start()

OPENWEATHER_API_KEY = "73522ad14e4276bdf715f0e796fc623f"
OPENWEATHER_CITY = "Jinan,KR"  # 진안, 대한민국

load_dotenv()
os.chdir('/Users/seunghoonoh/woonmok.github.io')
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("⚠️ TELEGRAM_BOT_TOKEN 환경 변수가 설정되지 않았습니다!")
bot = telebot.TeleBot(TOKEN)

def load_dashboard_data():
    try:
        with open('dashboard_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"todo_list": [], "system_status": "NORMAL"}

def save_dashboard_data(data):
    with open('dashboard_data.json', 'w', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            json.dump(data, f, ensure_ascii=False, indent=2)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def get_weather():
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={OPENWEATHER_CITY}&appid={OPENWEATHER_API_KEY}&units=metric&lang=kr"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            desc = data['weather'][0]['description']
            return {
                "text": f"진안 실시간 날씨: {desc}, 온도 {temp}°C, 습도 {humidity}%",
                "temp": temp,
                "humidity": humidity,
                "desc": desc
            }
        else:
            return {"text": f"[날씨] API 오류: {resp.status_code}"}
    except Exception as e:
        return {"text": f"[날씨] 연결 오류: {e}"}


# --- 텔레그램 명령 처리 ---
def handle_telegram_command(msg_text, message):
    try:
        if msg_text.strip() in ["/날씨", "날씨", "/weather"]:
            weather = get_weather()
            return weather["text"] if isinstance(weather, dict) else str(weather)

        data = load_dashboard_data()

        if msg_text == "/start":
            return "👋 안녕하세요! Wave Tree 할일 관리 봇입니다.\n\n사용 가능한 명령어:\n- /todo 또는 '목록' - 할일 목록\n- 추가: 작업명 - 할일 추가\n- 완료: ID - 할일 완료\n- 삭제: ID - 할일 삭제\n- 할일: 1. xxx, 2. yyy - 할일 덮어쓰기"

        elif msg_text in ["/todo", "/목록", "/list"]:
            todos = data.get("todo_list", [])
            if not todos:
                return "📋 오늘의 할일이 없습니다."
            msg = "📋 오늘의 할일\n\n"
            for item in todos:
                status = "✅" if item["completed"] else "⭕"
                msg += f"{status} [{item['id']}] {item['text']}\n"
            return msg

        elif msg_text in ["/help", "/도움말"]:
            return "📚 **명령어 도움말**\n\n▪️ /todo - 할일 목록 보기\n▪️ 추가: 작업명 - 새 할일 추가\n▪️ 완료: 1 - ID로 완료 처리\n▪️ 삭제: 1 - ID로 삭제\n▪️ 목록 - 할일 목록 보기\n▪️ 할일: 1. xxx, 2. yyy - 할일 덮어쓰기"

        if msg_text.startswith("추가:"):
            task = msg_text.replace("추가:", "").strip()
            max_id = max([item.get("id", 0) for item in data.get("todo_list", [])] or [0])
            new_todo = {"text": task, "completed": False, "id": max_id + 1}
            data["todo_list"].append(new_todo)
            save_dashboard_data(data)
            return f"✅ '{task}' 이 오늘의 할일에 추가되었습니다! (ID: {max_id + 1})"

        elif msg_text.startswith("완료:"):
            target = msg_text.replace("완료:", "").strip()
            for item in data.get("todo_list", []):
                if item["text"] == target or str(item["id"]) == target:
                    item["completed"] = True
                    save_dashboard_data(data)
                    return f"🎉 '{item['text']}' 완료했습니다!"
            return "❌ 해당 할일을 찾을 수 없습니다."

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

        elif msg_text in ["목록", "오늘", "할일"]:
            todos = data.get("todo_list", [])
            if not todos:
                return "📋 오늘의 할일이 없습니다."
            msg = "📋 **오늘의 할일**\n\n"
            for item in todos:
                status = "✅" if item["completed"] else "⭕"
                msg += f"{status} [{item['id']}] {item['text']}\n"
            return msg

        elif msg_text.startswith("상태:"):
            status_msg = msg_text.replace("상태:", "").strip()
            data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_dashboard_data(data)
            return f"📊 대시보드 상태: {status_msg}"

        elif msg_text.startswith("할일"):
            task_text = msg_text.replace("할일:", "").replace("할일 :", "").strip()
            if not task_text:
                bot.send_message(message.chat.id, "❌ 할일을 입력해주세요! 예) 할일: 1. 회의 준비")
                return None
            tasks = [t.strip() for t in task_text.split(",")]
            parsed_tasks = []
            for task in tasks:
                if task:
                    parts = task.split(".", 1)
                    if len(parts) == 2 and parts[0].strip().isdigit():
                        task_id = int(parts[0].strip())
                        task_text_content = parts[1].strip()
                        if 1 <= task_id <= 3:
                            parsed_tasks.append({"id": task_id, "text": task})
            if not parsed_tasks:
                bot.send_message(message.chat.id, "❌ 형식이 맞지 않습니다. 예) 할일: 1. 대시보드, 2. 리스트")
                return None
            current_todo = {item["id"]: item for item in data.get("todo_list", [])}
            for new_item in parsed_tasks:
                task_id = new_item["id"]
                if task_id in current_todo:
                    current_todo[task_id]["text"] = new_item["text"]
                else:
                    current_todo[task_id] = {"text": new_item["text"], "completed": False, "id": task_id}
            data["todo_list"] = sorted(current_todo.values(), key=lambda x: x["id"])
            data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_dashboard_data(data)
            task_list = "\n".join([f"✓ {item['text']}" for item in data["todo_list"]])
            response = f"✅ 할일이 업데이트되었습니다!\n\n현재 할일 목록:\n{task_list}"
            bot.send_message(message.chat.id, response)
            return None
        return None
    except Exception as e:
        # 모든 예외를 로그에 남김
        with open("logs/antigravity_error.log", "a", encoding="utf-8") as logf:
            logf.write(f"[telegram_command] {datetime.now()} {e}\n")
        return f"🚨 에러 발생: {str(e)}"

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    result = handle_telegram_command(message.text, message)
    if result:
        # parse_mode 제거 (마크다운 파싱 오류 방지)
        bot.reply_to(message, result)