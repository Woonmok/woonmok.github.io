import time
import random
import requests
import json
import os
import datetime
import html
import sys

# =============================================================================
# Configuration
# =============================================================================
OUTPUT_FILE = 'index.html'
# Specific Card Backgrounds (Unsplash Keywords)
TOPIC_CONFIG = {
    'LISTERIA FREE': {
        'query': '팽이버섯 리스테리아 예방 기술',
        'bg_keyword': 'enoki mushroom farm',
        'fallback_bg': 'https://images.unsplash.com/photo-1626202378942-e1d033722e92?auto=format&fit=crop&q=80' # Enoki specific
    },
    'CULTURED MEAT': {
        'query': '배양육 세포배양 최신 연구',
        'bg_keyword': 'microscope science lab',
        'fallback_bg': 'https://images.unsplash.com/photo-1579165466741-7f35a4755657?auto=format&fit=crop&q=80' # Microscope
    },
    'HIGH-END AUDIO': {
        'query': '하이엔드 오디오 시스템 앰프',
        'bg_keyword': 'hifi audio vacuum tube',
        'fallback_bg': 'https://images.unsplash.com/photo-1558485203-b5417ae4a43b?auto=format&fit=crop&q=80' # Valve amp
    },
    'COMPUTER & AI': {
        'query': '인공지능 LLM 최신 뉴스',
        'bg_keyword': 'artificial intelligence chip',
        'fallback_bg': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80' # AI Chip
    }
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="120">
    <title>The Wave Tree Project Dashboard</title>
    <style>
        :root {{
            --bg-dark: #0a0a0a;
            --card-bg: rgba(20, 20, 20, 0.85); /* Darker, less transparent */
            --text-primary: #ffffff;
            --text-secondary: #cccccc;
            --accent: #00ff88;
            --accent-glow: rgba(0, 255, 136, 0.3);
        }}
        body {{
            margin: 0; padding: 0; width: 100vw; height: 100vh; overflow: hidden;
            font-family: 'Pretendard', sans-serif;
            color: var(--text-primary);
            background-color: var(--bg-dark);
            /* Global simple dark bg */
            background-image: radial-gradient(circle at 50% 50%, #1a1a1a 0%, #000000 100%);
            display: flex; flex-direction: column; justify-content: space-between;
        }}
        header {{
            padding: 30px 50px;
            display: flex; justify-content: space-between; align-items: flex-start;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            background: rgba(0,0,0,0.5);
        }}
        .brand {{ border-left: 5px solid var(--accent); padding-left: 20px; }}
        .brand h1 {{ margin: 0; font-size: 2.4rem; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 0 20px var(--accent-glow); }}
        .brand span {{ font-size: 1.2rem; color: var(--accent); font-weight: 600; letter-spacing: 3px; }}
        
        .header-right {{ display: flex; gap: 40px; text-align: right; }}
        .weather-widget {{ display: flex; flex-direction: column; }}
        .weather-info {{ display: flex; gap: 15px; justify-content: flex-end; font-size: 1.1rem; margin-bottom: 5px; }}
        .weather-label {{ color: var(--accent); font-weight: 600; margin-right: 5px; }}
        .weather-temp {{ font-size: 2.5rem; font-weight: 700; color: #fff; }}

        .datetime {{ text-align: right; }}
        .time {{ font-size: 3.2rem; font-weight: 700; line-height: 1; color: #fff; }}
        .date {{ font-size: 1.1rem; opacity: 0.7; margin-top: 5px; }}
        
        main {{
            padding: 30px 50px;
            display: grid; grid-template-columns: repeat(4, 1fr); gap: 25px; height: 68%;
        }}
        .news-card {{
            border-radius: 16px; padding: 25px;
            display: flex; flex-direction: column;
            border: 1px solid rgba(255,255,255,0.15);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            position: relative; overflow: hidden;
            /* Default dark bg */
            background-color: #111;
            transition: transform 0.3s ease;
        }}
        /* Background Image overlay logic handled inline */
        .news-card::before {{
            content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(180deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.9) 100%);
            z-index: 1;
        }}
        .card-content {{ position: relative; z-index: 2; height: 100%; display: flex; flex-direction: column; }}
        
        .category {{
            font-size: 0.9rem; font-weight: 800; color: var(--accent);
            text-transform: uppercase; margin-bottom: 20px; 
            border-bottom: 2px solid var(--accent); padding-bottom: 10px;
            display: inline-block; width: fit-content;
        }}
        
        .news-item {{ margin-bottom: 20px; flex-grow: 1; }}
        .news-title {{ font-size: 1.3rem; font-weight: 700; margin: 0 0 10px 0; line-height: 1.4; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }}
        .news-summary {{
            font-size: 0.95rem; color: var(--text-secondary); line-height: 1.6;
            display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical; overflow: hidden;
        }}
        .news-date {{ font-size: 0.8rem; opacity: 0.6; margin-top: 5px; display: block; }}

        footer {{
            padding: 15px 50px; background: #000; border-top: 1px solid #333;
            display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; color: #888;
        }}
        a {{ color: inherit; text-decoration: none; }}
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <h1>The Wave Tree Project</h1>
            <span>Farmerstree</span>
        </div>
        <div class="header-right">
            <div class="weather-widget">
                <div class="weather-temp">{weather_temp}</div>
                <div class="weather-info">
                   <span><span class="weather-label">날씨</span>{weather_condition}</span>
                   <span><span class="weather-label">습도</span>{weather_humidity}</span>
                </div>
                <div class="weather-info">
                    <span><span class="weather-label">기온</span>{weather_temp_label}</span>
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

    <footer>
        <div>System: Online (Farmerstree HQ)</div>
        <div>
            <span style="color: #ffeb3b; font-weight: bold; margin-right: 15px;">🎉 Mission Complete</span>
            <a href="https://www.youtube.com/watch?v=lTRiuFIWV54" target="_blank" style="color: var(--accent);">▶ Celebration Music</a>
        </div>
        <div>Source: Serper / Google News RSS</div>
    </footer>

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
    </script>
</body>
</html>
"""

def clean_html(raw_html):
    """Remove HTML tags and entities."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return html.unescape(cleantext).strip()

def fetch_weather_serper(location="서울 날씨"):
    api_key = os.environ.get("SERPER_API_KEY")
    default_weather = {'temp': '--°C', 'condition': '데이터 없음', 'humidity': '--%', 'temp_label': '--'}
    
    if not api_key: 
        return default_weather

    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": location, "gl": "kr", "hl": "ko"})
        headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
        resp = requests.post(url, headers=headers, data=payload, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        
        if 'answerBox' in data:
            box = data['answerBox']
            return {
                'temp': f"{box.get('temperature', 0)}°C",
                'condition': box.get('weather', '맑음'),
                'humidity': f"{box.get('humidity', '50%')}",
                'temp_label': f"{box.get('temperature', 0)}°C" 
            }
    except:
        pass
    return default_weather

def fetch_news_rss(query, count=2):
    """Fallback: Fetch from Google News RSS (No API Key needed)"""
    encoded_query = requests.utils.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    try:
        # SSL context workaround often needed for Mac
        import ssl
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context
            
        import xml.etree.ElementTree as ET
        import urllib.request
        
        with urllib.request.urlopen(rss_url, timeout=5) as response:
            tree = ET.parse(response)
            root = tree.getroot()
            items = []
            for item in root.findall('.//item')[:count]:
                items.append({
                    'title': item.find('title').text,
                    'link': item.find('link').text,
                    'summary': clean_html(item.find('description').text or ""),
                    'date': ""
                })
            return items
    except Exception as e:
        print(f"RSS Fallback failed for {query}: {e}")
        return []

def fetch_news_smart(query, count=2):
    """Try Serper, then RSS."""
    # 1. Try Serper
    api_key = os.environ.get("SERPER_API_KEY")
    if api_key:
        try:
            url = "https://google.serper.dev/news"
            payload = json.dumps({"q": query, "gl": "kr", "hl": "ko", "num": count})
            headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
            resp = requests.post(url, headers=headers, data=payload, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if 'news' in data and data['news']:
                    return [{
                        'title': n.get('title'),
                        'link': n.get('link'),
                        'summary': n.get('snippet', '') + f" ({n.get('date', '')})",
                        'date': n.get('date', '')
                    } for n in data['news']]
        except Exception as e:
            print(f"Serper error: {e}")
    
    # 2. Fallback to RSS
    print(f"Using RSS Fallback for {query}")
    return fetch_news_rss(query, count)

def update_signage():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Updating Dashboard...")
    
    weather_data = fetch_weather_serper()
    news_sections_html = ""
    
    for category, config in TOPIC_CONFIG.items():
        articles = fetch_news_smart(config['query'])
        
        # Resolve background image
        bg_image_url = config['fallback_bg']
        # Optionally we could use Serper Images API to find a fresh one using config['bg_keyword']
        # But for stability as requested (Enoki/Microscope), fixed high-quality URLs or specific queries are safer.
        # Let's use the provided fallback URLs which act as specific seeds.
        
        card_style = f"background-image: url('{bg_image_url}'); background-size: cover; background-position: center;"
        
        content_html = ""
        if not articles:
            content_html = '<div class="news-item"><h2 class="news-title">데이터 수신 중...</h2><p class="news-summary">잠시 후 업데이트 됩니다.</p></div>'
        else:
            # Only show 1 top article per card to fit layout better? Or 2? 
            # Template designed for vertical space. Let's show 1 main one with long summary.
            art = articles[0]
            content_html = f"""
            <div class="news-item">
                <a href="{art['link']}" target="_blank">
                    <h2 class="news-title">{art['title']}</h2>
                </a>
                <p class="news-summary">{art['summary']}</p>
                <span class="news-date">{art['date']}</span>
            </div>
            """

        news_sections_html += f"""
        <article class="news-card" style="{card_style}">
            <div class="card-content">
                <div class="category">{category}</div>
                {content_html}
            </div>
        </article>
        """

    final_html = HTML_TEMPLATE.format(
        weather_temp=weather_data['temp'],
        weather_condition=weather_data['condition'],
        weather_humidity=weather_data['humidity'],
        weather_temp_label=weather_data['temp_label'],
        news_sections=news_sections_html
    )

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print("Update Complete.")
    except Exception as e:
        print(f"Write Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_signage()
