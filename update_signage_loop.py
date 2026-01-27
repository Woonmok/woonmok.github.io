import time
import random
import requests
import json
import os
import datetime
import html
import sys
import re

# =============================================================================
# Configuration
# =============================================================================
OUTPUT_FILE = 'index.html'

# Topic Configuration
TOPICS_CONFIG = [
    {
        'label': 'Listeria Free Tech',
        'query': '리스테리아 프리 기술',
        'image': 'https://images.unsplash.com/photo-1504333638930-c8787321eee0?q=80&w=2070&auto=format&fit=crop'
    },
    {
        'label': 'Cultured Meat',
        'query': '배양육 최신 동향',
        'image': 'https://images.unsplash.com/photo-1579154235602-3c2c23736671?q=80&w=2070&auto=format&fit=crop'
    },
    {
        'label': 'High-end Audio',
        'query': '하이엔드 오디오 신제품',
        'image': 'https://images.unsplash.com/photo-1558352520-435728a0d922?q=80&w=2070&auto=format&fit=crop'
    },
    {
        'label': 'COMPUTER & AI',
        'query': 'AI 기술 트렌드',
        'image': 'https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=2070&auto=format&fit=crop'
    }
]

# HTML Template
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="120">
    <title>THE WAVE TREE PROJECT</title>
    <style>
        :root {{
            --bg-color: #000000;
            --glass-bg: rgba(20, 20, 20, 0.85);
            --glass-border: rgba(255, 255, 255, 0.15);
            --text-primary: #ffffff;
            --text-secondary: #cccccc;
            --accent: #00ff88;
        }}
        body {{
            margin: 0; padding: 0; width: 100vw; height: 100vh; overflow: hidden;
            font-family: 'Pretendard', sans-serif;
            color: var(--text-primary);
            background-color: var(--bg-color);
            display: flex; flex-direction: column; justify-content: space-between;
        }}
        .overlay {{
             /* No overlay needed for pure black, but kept for compatibility if needed */
        }}
        header {{
            padding: 30px 60px;
            display: flex; justify-content: space-between; align-items: flex-start;
            border-bottom: 1px solid var(--glass-border);
        }}
        .brand {{ border-left: 4px solid var(--accent); padding-left: 20px; margin-top: 10px; }}
        .brand h1 {{ margin: 0; font-size: 2.5rem; text-transform: uppercase; letter-spacing: 2px; }}
        
        .header-right {{ display: flex; gap: 40px; text-align: right; }}
        
        .weather-widget {{ display: flex; flex-direction: column; align-items: flex-end; }}
        .weather-main {{ display: flex; align-items: center; gap: 10px; margin-bottom: 5px; font-size: 1.5rem; font-weight: 600; color: var(--accent); }}
        .weather-details {{ font-size: 1rem; opacity: 0.8; }}
        
        .datetime {{ text-align: right; }}
        .time {{ font-size: 3.2rem; font-weight: 700; line-height: 1; }}
        .date {{ font-size: 1.1rem; opacity: 0.8; margin-top: 5px; }}
        
        main {{
            padding: 40px 60px;
            display: grid; grid-template-columns: repeat(4, 1fr); gap: 30px; height: 60%;
        }}
        .news-card {{
            background: var(--glass-bg); 
            border: 1px solid var(--glass-border); border-radius: 12px; 
            display: flex; flex-direction: column; 
            position: relative; overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }}
        .news-card-bg {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-size: cover; background-position: center;
            opacity: 0.4; z-index: 0; filter: grayscale(50%) contrast(1.2);
        }}
        .news-content {{ 
            position: relative; z-index: 1; padding: 25px; 
            display: flex; flex-direction: column; height: 100%; 
            background: linear-gradient(180deg, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0.9) 100%);
        }}
        
        .category {{
            font-size: 0.9rem; font-weight: 700; color: var(--accent);
            text-transform: uppercase; margin-bottom: 20px; letter-spacing: 1px;
            border-bottom: 1px solid var(--accent); padding-bottom: 5px; display: inline-block;
        }}
        
        .news-item {{ margin-bottom: 20px; }}
        .news-item:last-child {{ margin-bottom: 0; }}
        .news-title {{ font-size: 1.15rem; font-weight: 700; margin: 0 0 8px 0; line-height: 1.4; }}
        .news-summary {{
            font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5; margin: 0;
            display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
        }}

        /* Marquee Styles */
        .marquee-container {{
            background: #111;
            border-top: 1px solid var(--glass-border);
            height: 50px;
            display: flex; align-items: center;
            overflow: hidden;
            white-space: nowrap;
            position: relative;
        }}
        .marquee-label {{
            background: var(--accent); color: #000; font-weight: 800;
            padding: 0 20px; height: 100%; display: flex; align-items: center;
            z-index: 10;
        }}
        .marquee-content {{
            display: inline-block;
            padding-left: 100%;
            animation: marquee 40s linear infinite;
            font-size: 1.1rem;
            font-weight: 500;
        }}
        .marquee-content span {{ margin-right: 50px; color: var(--text-secondary); }}
        .marquee-content span b {{ color: #fff; margin-right: 10px; }}

        @keyframes marquee {{
            0% {{ transform: translate(0, 0); }}
            100% {{ transform: translate(-100%, 0); }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <h1>THE WAVE TREE PROJECT</h1>
        </div>
        <div class="header-right">
            <div class="weather-widget">
                <div class="weather-main">
                    {weather_str}
                </div>
                <div class="weather-details">
                   진안군 부귀면
                </div>
            </div>
            <div class="datetime">
                <div class="time" id="clock">--:--</div>
                <div class="date" id="date">--.--.--</div>
            </div>
        </div>
    </header>

    <main>
        {news_sections}
    </main>

    <div class="marquee-container">
        <div class="marquee-label">NEWS FLASH</div>
        <div class="marquee-content">
            {marquee_items}
        </div>
    </div>

    <script>
        function updateTime() {{
            const now = new Date();
            const timeString = now.toLocaleTimeString('en-US', {{ hour12: false, hour: '2-digit', minute: '2-digit' }});
            const dateString = now.toLocaleDateString('en-US', {{ year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'short' }});
            document.getElementById('clock').textContent = timeString;
            document.getElementById('date').textContent = dateString.replace(/\\//g, '. ');
        }}
        setInterval(updateTime, 1000);
        updateTime();
        
        setTimeout(() => {{
            window.location.reload();
        }}, 120000);
    </script>
</body>
</html>
"""

def fetch_weather_serper(query="진안군 부귀면 날씨"):
    """Fetch weather using Serper API (Search)."""
    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        return "--°C / --% / --"
        
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "gl": "kr",
        "hl": "ko"
    })
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        data = response.json()
        
        # Default
        temp = "--°C"
        humidity = "--%"
        condition = "Unknown"
        
        if 'answerBox' in data:
            box = data['answerBox']
            if 'temperature' in box: temp = str(box.get('temperature')) + "°C"
            if 'humidity' in box: humidity = str(box.get('humidity')) + "%"
            if 'precipitation' in box: condition = f"Precip: {box.get('precipitation')}"
            
        return f"{temp} / {humidity} / {condition}"

    except Exception as e:
        print(f"Error fetching weather: {e}")
        return "--°C / --% / API Error"

def fetch_top_news_serper(query, count=2):
    """Fetch news using Serper API."""
    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        print(f"Warning: SERPER_API_KEY not found. Returning dummy data for {query}.")
        return []

    url = "https://google.serper.dev/news"
    payload = json.dumps({
        "q": query,
        "gl": "kr",
        "hl": "ko",
        "num": 5
    })
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        items = []
        if 'news' in data:
            for news in data['news']:
                if len(items) >= count: break
                
                title = news.get("title", "")
                link = news.get("link", "")
                snippet = news.get("snippet", "")
                
                items.append({
                    'title': title,
                    'link': link,
                    'summary': snippet
                })
        return items
            
    except Exception as e:
        print(f"Error fetching news for {query}: {e}")
        return []

def update_signage():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Starting Wave Tree Project update...")
    
    # 1. Fetch Weather
    print("Fetching Weather...")
    weather_str = fetch_weather_serper("진안군 부귀면 날씨")
    print(f"Weather String: {weather_str}")

    # 2. Fetch News & Build Segments
    news_sections_html = ""
    all_headlines = []
    
    for topic in TOPICS_CONFIG:
        label = topic['label']
        query = topic['query']
        card_bg_image = topic['image']
        
        print(f"Fetching news for: {label} ({query})")
        articles = fetch_top_news_serper(query)
        
        # Build Card HTML
        bg_div = ""
        if card_bg_image:
            bg_div = f'<div class="news-card-bg" style="background-image: url(\'{card_bg_image}\');"></div>'
            
        news_html = f'<article class="news-card">{bg_div}<div class="news-content"><div class="category">{label}</div>'
        
        if not articles:
            news_html += '<div class="news-item"><h2 class="news-title">데이터 수신 대기 중</h2><p class="news-summary">API 데이터를 불러올 수 없습니다.</p></div>'
        
        for art in articles:
            title = art['title']
            summary = art['summary']
            if len(summary) > 100:
                summary = summary[:100] + "..."
            
            # Clean title for simple display
            clean_title = html.escape(title)
            all_headlines.append(f"<b>[{label}]</b> {clean_title}")

            news_html += f"""
            <div class="news-item">
                <h2 class="news-title">{title}</h2>
                <p class="news-summary">{summary}</p>
            </div>
            """
        
        news_html += '</div></article>' # Close content and article
        news_sections_html += news_html

    # 3. Build Marquee Content
    if not all_headlines:
         all_headlines = ["THE WAVE TREE PROJECT - SYSTEM ONLINE"]
         
    marquee_html = ""
    for hl in all_headlines:
        marquee_html += f"<span>{hl}</span>"
        
    # 4. Generate HTML
    final_html = HTML_TEMPLATE.format(
        weather_str=weather_str,
        news_sections=news_sections_html,
        marquee_items=marquee_html
    )

    # 5. Save
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"Successfully updated: {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_signage()
