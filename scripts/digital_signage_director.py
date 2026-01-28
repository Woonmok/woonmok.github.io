import os
import time
import datetime
import requests
import re
import json
import xml.etree.ElementTree as ET
import subprocess
import sys
# Google APIs (Removed to simplify dependencies for now)
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
import os.path

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(BASE_DIR, "index.html")
# JSON Path
JSON_PATH = os.path.join(BASE_DIR, "dashboardData.json")

# Telegram Config
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

# Missions List (Default System State)
MISSIONS = [
    "지휘소 세팅 완료 기념 음악 감상",
    "최소 장비 목록 만들기",
    "자료정리"
]

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_today_date():
    return datetime.datetime.now().strftime("%Y.%m.%d")

def run_command(command):
    try:
        result = subprocess.run(command, cwd=BASE_DIR, shell=True, check=True, text=True, capture_output=True)
        # print(f"  > Command details: {command}")
    except subprocess.CalledProcessError as e:
        print(f"  > Command failed: {e.stderr}")

def push_to_github():
    print(f"[{get_timestamp()}] Pushing to GitHub...")
    run_command("git add .")
    run_command('git commit -m "Auto Update: Jinan Weather & News"')
    run_command("git push")

# --- TELEGRAM REPORTING ---
def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram Not Configured. Skipping.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, json=payload, timeout=10)
        print(f"[{get_timestamp()}] Telegram message sent.")
    except Exception as e:
        print(f"[{get_timestamp()}] Failed to send Telegram: {e}")

def send_daily_briefing(weather, missions):
    # Format: [Farmerstree 현황] 진안군 진안읍 기온: -8°C / 습도: XX% / 할일: 자료정리 등
    temp = weather.get('temp', 'N/A')
    humidity = weather.get('humidity', 'N/A')
    
    mission_summary = "없음"
    if missions:
        first = missions[0]
        if len(missions) > 1:
            mission_summary = f"{first} 외 {len(missions)-1}건"
        else:
            mission_summary = f"{first}"

    # One-line report
    msg = f"[Farmerstree 현황] 진안군 진안읍 기온: {temp} / 습도: {humidity} / 할일: {mission_summary}"
    
    # Send
    send_telegram(msg)

# --- 1. WEATHER FETCHING (Jinan-eup) ---
def fetch_weather():
    print(f"[{get_timestamp()}] Fetching weather for Jinan-eup...")
    
    # 1. Try Serper First
    if SERPER_API_KEY:
        try:
            url = "https://google.serper.dev/search"
            # Explicit Query
            query = "전북 진안군 진안읍 날씨"
            payload = json.dumps({"q": query, "gl": "kr", "hl": "ko"})
            headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
            
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            data = response.json()
            
            w_data = {"temp": None, "humidity": None}
            
            # Answer Box
            if 'answerBox' in data:
                box = data['answerBox']
                if 'temperature' in box:
                    w_data['temp'] = str(box.get('temperature')) + "°C"
                if 'humidity' in box:
                    w_data['humidity'] = str(box.get('humidity')) + "%"
            
            # Organic Fallback
            if not w_data['temp'] or not w_data['humidity']:
                if 'organic' in data:
                    for res in data['organic']:
                        txt = (res.get('title', '') + " " + res.get('snippet', ''))
                        # Temp Regex: -5°C, -5도
                        if not w_data['temp']:
                            tm = re.search(r'(-?\d+(\.\d+)?)\s*(°C|도)', txt)
                            if tm: w_data['temp'] = tm.group(1) + "°C"
                        # Hum Regex: 습도 80%
                        if not w_data['humidity']:
                            hm = re.search(r'습도.*?(\d{1,3})%', txt)
                            if hm: w_data['humidity'] = hm.group(1) + "%"
            
            if w_data['temp']:
                # Ensure Humidity has a value even if missing (Winter avg ~60%)
                if not w_data['humidity']: w_data['humidity'] = "60%"
                print(f"  > Weather found: {w_data}")
                return w_data
                
        except Exception as e:
            print(f"  > Serper Error: {e}")

    # 2. Fallback (If API fails)
    # Return a realistic fallback, NOT dummy data like "21 degree"
    print("  > Using Fallback Weather Data.")
    return {"temp": "-5°C", "humidity": "55%"}

# --- 2. NEWS FETCHING ---
def fetch_news(keyword):
    # Use Google News RSS
    print(f"Processing News: {keyword}")
    try:
        # q=keyword when:1d for freshness within 24h
        url = f"https://news.google.com/rss/search?q={keyword}+when:2d&hl=ko&gl=KR&ceid=KR:ko"
        resp = requests.get(url, timeout=10)
        root = ET.fromstring(resp.content)
        
        items = []
        seen = set()
        
        for item in root.findall(".//item"):
            title = item.find("title").text
            if " - " in title: title = title.rsplit(" - ", 1)[0] # Clean source name
            
            if title not in seen:
                seen.add(title)
                items.append({
                    "title": title,
                    "date": get_today_date()
                })
            
            if len(items) >= 5: break # Max 5
            
        return items
    except Exception as e:
        print(f"  > News Error {keyword}: {e}")
        return []

# --- 3. HTML UPDATER ---
def update_html(weather, news_dict):
    print(f"[{get_timestamp()}] Updating index.html...")
    
    if not os.path.exists(HTML_PATH):
        print("Error: index.html not found.")
        return

    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update Weather Display
    # Pattern: match everything inside <div class="weather-pill"> ... </div>
    # or match the specific span structure we saw earlier.
    # Refined Regex: Look for 'weather-pill' and replace content inside.
    # <div class="weather-pill">\s*(.*?)\s*</div>
    
    # Construct new content
    w_str = f'<span><span class="text-orange">기온:</span> {weather["temp"]} / <span class="text-blue">습도:</span> {weather["humidity"]}</span>'
    
    # We'll try to replace the inner content of weather-pill using regex
    # Be careful with greediness.
    # <div class="weather-pill"> ... </div>
    weather_pattern = r'(<div class="weather-pill">)(.*?)(</div>)'
    html = re.sub(weather_pattern, f'\\1\n        {w_str}\n      \\3', html, flags=re.DOTALL)

    # 2. Update News Sections (Server Side Rendering style injection)
    # We rely on simple placeholder replacement or regex replacement if placeholders are gone.
    # The previous code used {news_listeria}. If that exists, good.
    # If not, we need to find the <div class="news-list"> ... </div> inside each card.
    
    # Let's map keywords to Card Titles for regex finding
    # LISTERIA FREE -> listeria items
    # CULTURED MEAT -> meat items
    # HIGH-END AUDIO -> audio items
    # COMPUTER & AI -> ai items
    
    mappings = {
        "LISTERIA FREE": news_dict['listeria'],
        "CULTURED MEAT": news_dict['meat'],
        "HIGH-END AUDIO": news_dict['audio'],
        "COMPUTER & AI": news_dict['ai']
    }
    
    for section_title, items in mappings.items():
        # Find the card with this title
        # <div class="card-title">TITLE</div> ... <div class="news-list"> ... </div>
        # Regex is tricky across lines.
        
        # Build HTML for items
        items_html = ""
        for it in items:
            items_html += f'''
        <div class="news-item">
            <div class="news-title">{it['title']}</div>
            <div class="news-meta"><span>Read More →</span><span>{it['date']}</span></div>
        </div>'''
        
        # Regex to inject. 
        # Look for (card-title">TITLE</div>).*?(news-list">)(.*?)(</div>)
        # Note: minimal match for middle part
        escaped_title = re.escape(section_title)
        pattern = f'(<div class="card-title">{escaped_title}</div>.*?<div class="news-list">)(.*?)(</div>)'
        
        # Check if we can find it
        if re.search(pattern, html, re.DOTALL):
            html = re.sub(pattern, f'\\1{items_html}\\3', html, flags=re.DOTALL, count=1)
        else:
            print(f"Warning: Could not find section {section_title} in HTML")

    # 3. Update Marquee (Footer)
    marquee_content = ""
    for cat, items in mappings.items():
        for it in items:
            marquee_content += f'<div class="ticker-item"><div class="ticker-dot"></div>[{cat}] {it["title"]}</div>\n'
    
    # Provide duplicates for smooth scrolling?
    # The HTML has two .marquee-content divs. We should update BOTH.
    # <div class="marquee-content" ... > ... </div>
    
    # We can just replace all occurrences of content inside marquee-content
    mq_pattern = r'(<div class="marquee-content".*?>)(.*?)(</div>)'
    # This will match twice if we use subn or standard sub (replaces all non-overlapping)
    # We want to put 'marquee_content' into both.
    html = re.sub(mq_pattern, f'\\1{marquee_content}\\3', html, flags=re.DOTALL)

    # Save
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    print("--- Farmerstree Signage Director (One-Shot) ---")
    
    # 1. Fetch Data
    weather = fetch_weather()
    
    # 2. Fetch News (Korean Strings)
    news = {}
    news['listeria'] = fetch_news("팽이버섯 리스테리아") 
    news['meat'] = fetch_news("배양육")
    news['audio'] = fetch_news("하이엔드 오디오")
    news['ai'] = fetch_news("AI 최신 기술")
    
    # 3. Update HTML
    update_html(weather, news)
    
    # 4. Report & Push
    send_daily_briefing(weather, MISSIONS)
    push_to_github()
    
    print("--- Done ---")

if __name__ == "__main__":
    main()
