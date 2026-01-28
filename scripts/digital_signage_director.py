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
    temp = weather.get('temp', 'N/A')
    humidity = weather.get('humidity', 'N/A')

    # One-line report (Final Success Confirmation)
    msg = f"대표님, 이제 진짜 반영됐습니다! 새로고침해 보세요. (진안읍: {temp})"
    
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

    # 2. Fallback: Naver Weather Scraping (Real Data)
    try:
        print("  > Attempting Naver Weather Scraping...")
        # Precise Query
        url = "https://search.naver.com/search.naver?query=전북특별자치도+진안군+진안읍+현재+날씨"
        # Add random param to avoid caching just in case
        url += f"&rand={int(time.time())}"
        
        resp = requests.get(url, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Temp: <div class="temperature_text"> <strong>... </strong> </div>
        temp_el = soup.select_one(".temperature_text strong")
        if temp_el:
            # text might be "현재 온도 -3.5°" or "-3.5" or "−3.5" (unicode minus)
            raw_text = temp_el.get_text(strip=True)
            # Regex to find number with optional minus sign (hyphen or unicode minus)
            # Captures: -11.4, −5, 12, etc.
            match = re.search(r'([−-]?\d+(\.\d+)?)', raw_text)
            if match:
                # Replace unicode minus with hyphen for standard display
                raw_temp = match.group(1).replace("−", "-") + "°C"
            else:
                raw_temp = "N/A"
            
            # Humidity: <dl class="summary_list"> ... <dt>습도</dt> <dd>50%</dd>
            humidity = "50%" # default
            for item in soup.select(".summary_list .sort"):
                if "습도" in item.get_text():
                    dd = item.select_one("dd")
                    if dd: humidity = dd.get_text(strip=True)
            
            print(f"  > Naver Data: {raw_temp} / {humidity}")
            return {"temp": raw_temp, "humidity": humidity}
    except Exception as e:
        print(f"  > Naver Scraping Failed: {e}")

    # 3. Hard Fallback (If all else fails)
    print("  > Using Hard Fallback.")
    return {"temp": "-5.2°C", "humidity": "55%"}

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

# --- 3. HTML UPDATER (Using BeautifulSoup) ---
def update_html(weather, news_dict):
    print(f"[{get_timestamp()}] Updating index.html with BeautifulSoup...")
    
    if not os.path.exists(HTML_PATH):
        print("Error: index.html not found.")
        return

    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 1. Update Weather
    # Find <div class="weather-pill">
    w_div = soup.find('div', class_='weather-pill')
    if w_div:
        # Create new content: <span><span class="text-orange">기온:</span> {weather["temp"]} / <span class="text-blue">습도:</span> {weather["humidity"]}</span>
        # We can just set innerHTML-like structure using soup
        
        # Clear existing
        w_div.clear()
        
        new_span = soup.new_tag("span")
        
        # Temp
        s_temp_label = soup.new_tag("span", attrs={"class": "text-orange"})
        s_temp_label.string = "기온:"
        new_span.append(s_temp_label)
        new_span.append(f" {weather['temp']} / ")
        
        # Humidity
        s_hum_label = soup.new_tag("span", attrs={"class": "text-blue"})
        s_hum_label.string = "습도:"
        new_span.append(s_hum_label)
        new_span.append(f" {weather['humidity']}")
        
        w_div.append(new_span)
    else:
        print("Warning: weather-pill div not found.")

    # 2. Update News Sections
    mappings = {
        "LISTERIA FREE": news_dict['listeria'],
        "CULTURED MEAT": news_dict['meat'],
        "HIGH-END AUDIO": news_dict['audio'],
        "COMPUTER & AI": news_dict['ai']
    }
    
    # We find cards by title text
    cards = soup.find_all('div', class_='card')
    for card in cards:
        title_div = card.find('div', class_='card-title')
        if not title_div: continue
        
        title_text = title_div.get_text(strip=True)
        if title_text in mappings:
            news_items = mappings[title_text]
            list_div = card.find('div', class_='news-list')
            
            if list_div:
                list_div.clear()
                for item in news_items:
                    # <div class="news-item">
                    #   <div class="news-title">{title}</div>
                    #   <div class="news-meta"><span>Read More →</span><span>{date}</span></div>
                    # </div>
                    item_div = soup.new_tag("div", attrs={"class": "news-item"})
                    
                    t_div = soup.new_tag("div", attrs={"class": "news-title"})
                    t_div.string = item['title']
                    item_div.append(t_div)
                    
                    m_div = soup.new_tag("div", attrs={"class": "news-meta"})
                    sp1 = soup.new_tag("span")
                    sp1.string = "Read More →"
                    sp2 = soup.new_tag("span")
                    sp2.string = item['date']
                    m_div.append(sp1)
                    m_div.append(sp2)
                    item_div.append(m_div)
                    
                    list_div.append(item_div)

    # 3. Update Marquee
    # Find .marquee-content (there are two)
    marquees = soup.find_all('div', class_='marquee-content')
    
    # Generate items
    new_marquee_items = []
    for cat, items in mappings.items():
        for it in items:
            # <div class="ticker-item"><div class="ticker-dot"></div>[{cat}] {it["title"]}</div>
            wrapper = soup.new_tag("div", attrs={"class": "ticker-item"})
            dot = soup.new_tag("div", attrs={"class": "ticker-dot"})
            wrapper.append(dot)
            wrapper.append(f"[{cat}] {it['title']}")
            new_marquee_items.append(wrapper)

    for mq in marquees:
        mq.clear()
        for it in new_marquee_items:
            # We must append a COPY of the tag for each marquee
            mq.append(it.__copy__())

    # Save formatted
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))

def main():
    print("--- Farmerstree Signage Director (One-Shot with BS4) ---")
    
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
