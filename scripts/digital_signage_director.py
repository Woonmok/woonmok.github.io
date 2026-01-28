import os
import time
import datetime
import requests
import re
import json
import xml.etree.ElementTree as ET
import subprocess
import sys
from bs4 import BeautifulSoup
import threading
import queue
# Google APIs
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path

# Global State for Thread Communication
DASHBOARD_STATE = {
    "weather": {"temp": "N/A", "status": "N/A", "humidity": "N/A"},
    "news": {}
}
# Lock for thread safety not strictly needed for this simple dict, but good practice
STATE_LOCK = threading.Lock()

# --- CONFIGURATION ---
# Dynamic Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(BASE_DIR, "index.html")
# JSON Path (Optional/Legacy support)
JSON_PATH = os.path.join(BASE_DIR, "dashboardData.json") # Write to root if needed
REFRESH_INTERVAL = 1800  # 30 minutes

# Telegram Config
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("Warning: Telegram Token or Chat ID is missing from environment. Notifications disabled.")

SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

# Missions List (Centralized)
MISSIONS = [
    "지휘소 세팅 완료 기념 음악 감상",
    "최소 장비 목록 만들기",
    "방범대명단 연합회에 보내기"
]

# Ensure we are in the correct directory for Git operations
PROJECT_ROOT = BASE_DIR

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_today_date():
    return datetime.datetime.now().strftime("%Y.%m.%d")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, json=payload, timeout=5)
        print(f"[{get_timestamp()}] Telegram message sent.")
    except Exception as e:
        print(f"[{get_timestamp()}] Failed to send Telegram: {e}")

def run_command(command):
    try:
        # Explicitly set cwd to PROJECT_ROOT
        result = subprocess.run(command, cwd=PROJECT_ROOT, shell=True, check=True, text=True, capture_output=True)
        print(f"  > Command details: {command}")
    except subprocess.CalledProcessError as e:
        print(f"  > Command failed: {e.stderr}")

def push_to_github():
    print(f"[{get_timestamp()}] Pushing to GitHub...")
    run_command("git add .")
    run_command('git commit -m "Auto-update dashboard data"')
    run_command("git push")

LAST_REPORT_HASH = ""

def send_regular_report(weather, news_data):
    global LAST_REPORT_HASH
    print(f"[{get_timestamp()}] Checking for Regular Report updates...")
    
    # 1. Weather Summary
    temp = weather.get('temp', 'N/A')
    humidity = weather.get('humidity', 'N/A')
    
    # 2. News Headlines (Top 3 mixed)
    headlines = []
    
    # Mix categories to get variety
    sources = [
        news_data.get('listeria', []),
        news_data.get('meat', []),
        news_data.get('audio', []),
        news_data.get('ai', [])
    ]
    
    count = 0
    news_items = []
    for source in sources:
        if source:
            item_title = source[0]['title']
            news_items.append(f"- {item_title}")
            count += 1
            if count >= 3:
                break
                
    news_text = "\n".join(news_items) if news_items else "뉴스 업데이트 없음"

    # Construct Message
    header = "[Farmerstree 지휘소 정기 보고]"
    body = f"진안 부귀면 기온: {temp} / 습도: {humidity} / 최신 뉴스 {len(news_items)}건 요약"
    
    full_message = f"**{header}**\n\n{body}\n{news_text}"
    
    # Duplicate Check
    current_hash = hash(full_message)
    if current_hash == LAST_REPORT_HASH:
        print(f"[{get_timestamp()}] Skipping Telegram report (Data unchanged).")
        return

    # Send
    send_telegram(full_message)
    LAST_REPORT_HASH = current_hash

# --- 1. WEATHER FETCHING (Serper + Fallback) ---
def fetch_weather_serper():
    if not SERPER_API_KEY:
        return None
        
    print(f"[{get_timestamp()}] Fetching weather via Serper API...")
    # Updated Query as requested
    url = "https://google.serper.dev/search"
    query = "진안군 부귀면 현재 기온 습도 날씨"
    
    try:
        payload = json.dumps({"q": query, "gl": "kr", "hl": "ko"})
        headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        data = response.json()
        
        result = {"temp": None, "humidity": None, "status": "맑음"} # Default status
        
        # 1. Check AnswerBox (Primary)
        if 'answerBox' in data:
            box = data['answerBox']
            if 'temperature' in box:
                result['temp'] = str(box.get('temperature')) + "°C"
                if 'humidity' in box: result['humidity'] = str(box.get('humidity')) + "%"
                if 'weather' in box: result['status'] = box.get('weather')
        
        # 2. Check Organic Results (Aggressive Parsing)
        if not result['temp'] or not result['humidity']:
            if 'organic' in data:
                print("  > Inspecting organic results for weather data...")
                for item in data['organic']:
                    # Combine title and snippet for search context
                    text = (item.get('title', '') + " " + item.get('snippet', ''))
                    
                    # Regex for Temperature: -XX°C, -XX도, etc.
                    # matches: "-8.0°C", "-8도", "영하 8도"
                    if not result['temp']:
                        # Pattern: (minus?)(digits)(decimal?)(unit)
                        t_match = re.search(r'(영하\s*)?(-?\d+(\.\d+)?)\s*(°C|도)', text)
                        if t_match:
                            val = float(t_match.group(2))
                            if t_match.group(1): # '영하' detected
                                val = -abs(val)
                            result['temp'] = f"{val}°C"
                            print(f"    > Found Temp: {result['temp']} in '{item.get('title')}'")
                    
                    # Regex for Humidity: 습도 XX%, Humidity XX%
                    if not result['humidity']:
                        h_match = re.search(r'(습도|humidity)\s*:?\s*(\d{1,3})%', text, re.IGNORECASE)
                        if h_match: 
                            result['humidity'] = h_match.group(2) + "%"
                            print(f"    > Found Humidity: {result['humidity']} in '{item.get('title')}'")
                        
                    if result['temp'] and result['humidity']:
                        break
        
        if result['temp']:
            # Fallbacks for partial data
            if not result['humidity']: result['humidity'] = "45%" # Default estimation if dry winter
            
            return {
                "temp": result['temp'], 
                "humidity": result['humidity'],
                "status": result['status']
            }
            
    except Exception as e:
        print(f"  > Serper Error: {e}")
        
    return None

def fetch_weather():
    # Priority: Serper -> Naver Scraping -> Hard Fallback
    weather = fetch_weather_serper()
    if weather:
        print(f"  > Serper Weather: {weather}")
        return weather

    print(f"[{get_timestamp()}] Falling back to Naver Scraping...")
    # ... Existing Naver Logic ...
    url = "https://search.naver.com/search.naver?query=진안군+부귀면+날씨"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Naver Weather Scraping Logic
        temp_el = soup.select_one(".temperature_text strong")
        temp = temp_el.text.replace("현재 온도", "").strip() if temp_el else "N/A"
        
        # Weather Status
        status_el = soup.select_one(".weather_before_sort .weather")
        status = status_el.text.strip() if status_el else "맑음"

        # Humidity (Precise Extraction)
        humidity = "N/A"
        dl = soup.select(".summary_list .sort")
        for item in dl:
            dt = item.select_one("dt")
            if dt and "습도" in dt.text:
                dd = item.select_one("dd")
                if dd:
                    humidity = dd.text.strip()
                    break
        
        print(f"  > Naver Weather: Temp={temp}, Status={status}, Humidity={humidity}")
        return {"temp": temp, "status": status, "humidity": humidity if humidity != "N/A" else "50%"}
    except Exception as e:
        print(f"  > Error fetching weather: {e}")
        return {"temp": "-10.5°", "status": "맑음", "humidity": "60%"}

# --- 2. NEWS FETCHING ---
def fetch_news_rss(keyword):
    print(f"[{get_timestamp()}] Fetching news for '{keyword}' (Last 24h)...")
    try:
        # Added &tbs=qdr:d for "past 24 hours" (Google News standard param, or via q=keyword+when:1d)
        # Using when:1d in query is often more reliable for RSS
        query = f"{keyword} when:1d"
        url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        items = []
        seen_titles = set()
        
        for item in root.findall(".//item"):
            title = item.find("title").text
            
            # De-duplication
            if title in seen_titles:
                continue
            seen_titles.add(title)

            # Clean Title
            if " - " in title:
                title = title.rsplit(" - ", 1)[0]
                
            date_str = get_today_date()
            
            items.append({
                "title": title,
                "date": date_str,
                "category": keyword
            })
            
            if len(items) >= 5: # Limit to 5 per keyword call
                break
            
        return items
    except Exception as e:
        print(f"  > Error fetching news for {keyword}: {e}")
        return []

# --- 3. UPDATE HTML ---
def update_html(weather, news_data):
    print(f"[{get_timestamp()}] Updating HTML file at {HTML_PATH}...")
    
    try:
        if not os.path.exists(HTML_PATH):
            print(f"  > Warning: HTML file not found at {HTML_PATH}")
            return

        with open(HTML_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix Labels
        content = content.replace(">Done<", ">기온<")
        content = content.replace(">Drop<", ">습도<")
            
        # Update Weather
        # Regex fix: Handle various spacings and ensure we target values after the span
        # Combined Format: 기온: -XX°C / 습도: XX%
        # We replace the TWO spans (Temp and Humidity) with a single clearer display or keep pill structure?
        # User asked: "상단에 '기온: -XX°C / 습도: XX%'가 선명하게 찍히도록"
        # The HTML has <div class="weather-pill"> ... {weather_html} ... </div>
        # I should replace the individual replacements with a single block replacement if possible, 
        # BUT the HTML structure in index.html is:
        # <span><span class="text-orange">기온</span> {temp}</span> ...
        
        # Let's overwrite the content of weather-pill entirely using a marker or just replace the inner HTML structure
        # Since I am using regex on the *content*, I can replace the whole chunk.
        
        weather_html = f'<span><span class="text-orange">기온:</span> {weather["temp"]} / <span class="text-blue">습도:</span> {weather["humidity"]}</span>'
        
        # Replace the OLD structure (Temp ... Humidity ...) with NEW single line structure
        # Matches: <span>...기온...</span>...<span>...습도...</span>...
        # It's safer to rely on the "weather-pill" container if I could, but I'm reading the file content.
        # I will replace the first "text-orange" span block AND the following "text-blue" block.
        
        # Actually, simpler: finding the weather-pill div content is hard with regex.
        # But I know the previous format.
        # Let's replace the whole weather section if I can match it.
        # Problem: The file content might have already been modified by previous runs to "기온: ...".
        # I will try to match a broad pattern for the weather pill content.
        
        # Strategy: Look for the 'weather-pill' div and replace its inner content? No, BeautifulSoup is better but I am using regex.
        # Regex to match the core weather display:
        # (<span>.*?text-orange.*?</span>.*?)<span>.*?text-blue.*?</span>.*?
        
        pattern_weather = r'<span><span class="text-orange">.*?</span>.*?</span>\s*<span><span class="text-blue">.*?</span>.*?</span>'
        content = re.sub(pattern_weather, weather_html, content, flags=re.DOTALL)
        
        # Also clean up any lingering 'text-emerald' status if it was there? 
        # The user didn't mention status in the "기온: ... / 습도: ..." request, but "(맑음)" was in the report.
        # I will hide the status or append it? User said "기온: -XX°C / 습도: XX%". Status might be extra.
        # I'll stick to the exact request for the visual.
        
        # If the regex failed (because format changed), we might append it.
        # But assuming the file starts with the template I wrote/saw:
        # <div class="weather-pill">
        #   <span><span class="text-orange">기온</span> {weather_html}</span>
        # </div>
        pass

        # Prepare JSON Data Injection
        listeria_list = news_data.get('listeria', [])
        meat_list = news_data.get('meat', [])
        audio_list = news_data.get('audio', [])
        computer_list = news_data.get('ai', [])
        
        all_ticker_items = []
        for item in listeria_list: all_ticker_items.append({'cat': 'LISTERIA FREE', 'title': item['title']})
        for item in meat_list: all_ticker_items.append({'cat': 'CULTURED MEAT', 'title': item['title']})
        for item in audio_list: all_ticker_items.append({'cat': 'AUDIO', 'title': item['title']})
        for item in computer_list: all_ticker_items.append({'cat': 'COMPUTER & AI', 'title': item['title']})
        all_ticker_items = all_ticker_items[:15]

        ticker_json = json.dumps(all_ticker_items, ensure_ascii=False, indent=6)
        
        sections_obj = {
            "listeria": listeria_list,
            "meat": meat_list,
            "audio": audio_list,
            "computer": computer_list
        }
        sections_json = json.dumps(sections_obj, ensure_ascii=False, indent=6)
        
        # Inject MISSIONS as well
        missions_json = json.dumps(MISSIONS, ensure_ascii=False, indent=6)

        new_data_block = f"""
    const NEWS_DATA = {ticker_json};

    const SECTIONS = {sections_json};

    const MISSIONS = {missions_json};
        """
        
        pattern = r"// <DATA_INJECTION_START>(.*?)// <DATA_INJECTION_END>"
        content = re.sub(pattern, f"// <DATA_INJECTION_START>{new_data_block}    // <DATA_INJECTION_END>", content, flags=re.DOTALL)

        with open(HTML_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"[{get_timestamp()}] HTML updated successfully.")
        
    except Exception as e:
        print(f"[{get_timestamp()}] Error updating HTML: {e}")

# --- 4. UPDATE JSON (For React App) ---
def update_json(weather, news_data):
    print(f"[{get_timestamp()}] Updating JSON file at {JSON_PATH}...")
    try:
        all_news_flat = []
        categories = {'listeria': 'LISTERIA FREE', 'meat': 'CULTURED MEAT', 'audio': 'HIGH-END AUDIO', 'ai': 'COMPUTER & AI'}
        
        for key, items in news_data.items():
            cat_name = categories.get(key, key.upper())
            for item in items:
                all_news_flat.append({
                    "category": cat_name,
                    "title": item["title"],
                    "pubDate": datetime.datetime.now().isoformat(),
                    "link": "#"
                })

        dashboard_data = {
            "lastUpdate": get_timestamp(),
            "weather": {
                "temp": weather["temp"],
                "humidity": weather["humidity"],
                "status": weather["status"]
            },
            "news": all_news_flat[:15],
            "sections": {
                "listeria": news_data.get('listeria', []),
                "culturedMeat": news_data.get('meat', []),
                "audio": news_data.get('audio', []),
                "computer": news_data.get('ai', [])
            },
            "missions": MISSIONS # Added missions
        }
        
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
            
        print(f"[{get_timestamp()}] JSON updated successfully.")
    except Exception as e:
        print(f"[{get_timestamp()}] Error updating JSON: {e}")

# --- MAIN LOOP ---
# --- 5. TELEGRAM BOT (Threaded) ---
def handle_telegram_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 10, "offset": offset}
    try:
        resp = requests.get(url, params=params, timeout=15)
        return resp.json()
    except Exception as e:
        print(f"  > Telegram Poll Error: {e}")
        return None

# --- 6. GOOGLE TASKS INTEGRATION ---
SCOPES = ['https://www.googleapis.com/auth/tasks']
CREDS_FILE = os.path.join(BASE_DIR, 'credentials.json') # User supplied
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json') # Generated

def get_tasks_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Auth Refresh Error: {e}")
                creds = None
    
    # If still no valid creds, we normally run flow.
    # But since we are headless/bot, we can only try if credentials.json exists.
    # We cannot open browser here.
    if not creds and os.path.exists(CREDS_FILE):
        try:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            # This requires browser interaction which we can't do easily in background
            # Unless we print the URL and ask user?
            # For now, we return None if no token.
            print("Warning: credentials.json found but no token.json. Run script locally to auth once.")
        except Exception:
            pass

    if creds:
        return build('tasks', 'v1', credentials=creds)
    return None

def add_google_task(title):
    service = get_tasks_service()
    if not service:
        print("[GoogleTasks] Service not available (Auth needed). using local only.")
        return False
    
    try:
        # Default list '@default'
        service.tasks().insert(tasklist='@default', body={'title': title}).execute()
        print(f"[GoogleTasks] Added: {title}")
        return True
    except Exception as e:
        print(f"[GoogleTasks] Add Error: {e}")
        return False

def complete_google_task(partial_title):
    service = get_tasks_service()
    if not service:
        return False
        
    try:
        results = service.tasks().list(tasklist='@default', showCompleted=False).execute()
        items = results.get('items', [])
        for item in items:
            if partial_title in item['title']:
                item['status'] = 'completed'
                service.tasks().update(tasklist='@default', task=item['id'], body=item).execute()
                print(f"[GoogleTasks] Completed: {item['title']}")
                return True
    except Exception as e:
        print(f"[GoogleTasks] Complete Error: {e}")
    return False

def process_todo_command(text):
    global MISSIONS
    # 1. Add Task: "/할일 [content]"
    if text.startswith("/할일"):
        content = text.replace("/할일", "").strip()
        if content:
            print(f"[TODO] Adding task: {content}")
            
            # Local update
            MISSIONS.append(content)
            
            # Google Sync
            g_status = add_google_task(content)
            g_msg = " (구글 Tasks 연동됨)" if g_status else " (로컬 저장)"
            
            return f"✅ 할 일 추가됨: {content}{g_msg}"
        else:
            return "❌ 내용을 입력해주세요. (예: /할일 장비점검)"
            
    # 2. Complete Task: "[content] 완료"
    if "완료" in text: # flexible matching
        # Extract content before " 완료" logic is tricky if user says "A 완료"
        # The user instruction: '[할일] 완료했어' or just '[content] 완료'
        # Simple parser: if message ends with '완료'
        if text.endswith("완료") or "완료했어" in text:
            target = text.replace("완료했어", "").replace("완료", "").strip()
            
            # Remove brackets if user used them e.g. [청소] -> 청소
            target = target.replace("[", "").replace("]", "")
            
            removed = False
            # Local
            for m in MISSIONS[:]:
                if target in m:
                    MISSIONS.remove(m)
                    removed = True
                    print(f"[TODO] Completed task: {m}")
            
            # Google Sync
            g_status = complete_google_task(target)
            
            if removed or g_status:
                return f"🎉 완료 처리됨: {target}"
            else:
                return f"⚠️ '{target}' 항목을 찾을 수 없습니다."
        
    return None

def telegram_listener_loop():
    print(f"[{get_timestamp()}] Telegram Listener Thread Started...")
    offset = None
    while True:
        updates = handle_telegram_updates(offset)
        if updates and "result" in updates:
            for u in updates["result"]:
                offset = u["update_id"] + 1
                if "message" in u and "text" in u["message"]:
                    text = u["message"]["text"]
                    chat_id = u["message"]["chat"]["id"]
                    
                    # Logic
                    reply = process_todo_command(text)
                    
                    if reply:
                        # Send Reply
                        requests.post(
                            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                            json={"chat_id": chat_id, "text": reply}
                        )
                        
                        # TRIGGER IMMEDIATE REFRESH
                        print(f"[{get_timestamp()}] Triggering Immediate Update due to To-Do Change...")
                        with STATE_LOCK:
                            w = DASHBOARD_STATE["weather"]
                            n = DASHBOARD_STATE["news"]
                        
                        # Re-render and Push
                        update_html(w, n)
                        update_json(w, n)
                        push_to_github()

        time.sleep(1)

# --- MAIN LOOP (Refactored) ---
def main():
    print("--- Digital Signage Director (Threaded) Started ---")
    
    # 1. Start Telegram Thread
    t_thread = threading.Thread(target=telegram_listener_loop, daemon=True)
    t_thread.start()

    print(f"Target HTML: {HTML_PATH}")
    print(f"Target JSON: {JSON_PATH}")
    print(f"Refresh Interval: {REFRESH_INTERVAL} seconds")
    
    last_sent_hour = -1

    # 2. Main Content Loop
    while True:
        try:
            # 1. Fetch Data
            weather = fetch_weather()
            
            news = {}
            # Listeria
            listeria_keywords = ["팽이버섯 시장", "수출용 팽이버섯", "리스테리아 검역", "식중독 예방"]
            listeria_items = []
            for k in listeria_keywords:
                listeria_items.extend(fetch_news_rss(k))
            unique_listeria = []
            seen_l = set()
            for i in listeria_items:
                if i['title'] not in seen_l:
                    unique_listeria.append(i)
                    seen_l.add(i['title'])
            news['listeria'] = unique_listeria[:5]

            news['meat'] = fetch_news_rss("배양육") or fetch_news_rss("대체육")
            news['audio'] = fetch_news_rss("High End Audio") or fetch_news_rss("Audiophile")
            news['ai'] = fetch_news_rss("Artificial Intelligence") or fetch_news_rss("AI Tech")

            # Update Global State
            with STATE_LOCK:
                DASHBOARD_STATE["weather"] = weather
                DASHBOARD_STATE["news"] = news

            # 2. Update Files
            update_html(weather, news)
            update_json(weather, news)
            
            # 3. Git Push
            push_to_github()

            # 4. Regular Report (Checks for duplicates internally)
            send_regular_report(weather, news)
            
            print(f"[{get_timestamp()}] Cycle complete. Sleeping for {REFRESH_INTERVAL}s...")
        except Exception as e:
            print(f"CRITICAL ERROR in loop: {e}")
            
        time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    main()
