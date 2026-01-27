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
OUTPUT_FILE = 'index.html'  # Relative path for GitHub Actions
BG_KEYWORDS = ['misty mountain', 'forest', 'analog audio', 'minimalist architecture', 'nature']
TOPICS = {
    'Listeria Free Tech': '리스테리아 프리 기술',
    'Cultured Meat': '배양육 최신 동향',
    'High-end Audio': '하이엔드 오디오 신제품',
    'Jinan-gun Issue': '전북 진안군 소식'
}

# HTML Template
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="120">
    <title>POM & Farmerstree Live Signage</title>
    <style>
        :root {{
            --glass-bg: rgba(0, 0, 0, 0.65);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-primary: #ffffff;
            --text-secondary: #e0e0e0;
            --accent: #00ff88;
        }}
        body {{
            margin: 0; padding: 0; width: 100vw; height: 100vh; overflow: hidden;
            font-family: 'Pretendard', sans-serif;
            color: var(--text-primary);
            background: url('{bg_url}') no-repeat center center fixed;
            background-size: cover;
            display: flex; flex-direction: column; justify-content: space-between;
        }}
        .overlay {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.4); z-index: 0;
        }}
        header {{
            position: relative; z-index: 10; padding: 40px 60px;
            display: flex; justify-content: space-between; align-items: flex-end;
            background: linear-gradient(180deg, rgba(0,0,0,0.8) 0%, transparent 100%);
        }}
        .brand {{ border-left: 4px solid var(--accent); padding-left: 20px; }}
        .brand h1 {{ margin: 0; font-size: 2.5rem; text-transform: uppercase; }}
        .brand span {{ font-size: 1.2rem; color: var(--accent); }}
        .datetime {{ text-align: right; }}
        .time {{ font-size: 3.5rem; font-weight: 700; }}
        .date {{ font-size: 1.2rem; opacity: 0.8; margin-top: 5px; }}
        main {{
            position: relative; z-index: 10; padding: 0 60px 40px 60px;
            display: grid; grid-template-columns: repeat(4, 1fr); gap: 30px; height: 65%;
        }}
        .news-card {{
            background: var(--glass-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border); border-radius: 20px; padding: 30px;
            display: flex; flex-direction: column; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3);
        }}
        .category {{
            font-size: 0.9rem; font-weight: 600; color: var(--accent);
            text-transform: uppercase; margin-bottom: 20px; display: flex; align-items: center;
        }}
        .category::before {{
            content: ''; display: block; width: 8px; height: 8px;
            background-color: var(--accent); border-radius: 50%; margin-right: 10px;
        }}
        .news-item {{ margin-bottom: 25px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 20px; }}
        .news-item:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
        .news-title {{ font-size: 1.3rem; font-weight: 700; margin: 0 0 10px 0; line-height: 1.3; }}
        .news-summary {{
            font-size: 0.95rem; color: var(--text-secondary); line-height: 1.6; margin: 0;
            display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden;
        }}
        footer {{
            position: relative; z-index: 10; background: linear-gradient(0deg, rgba(0,0,0,0.9) 0%, transparent 100%);
            padding: 20px 60px; display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; opacity: 0.7;
        }}
    </style>
</head>
<body>
    <div class="overlay"></div>
    <header>
        <div class="brand">
            <h1>Pom & Farmerstree</h1>
            <span>Live Signage Director</span>
        </div>
        <div class="datetime">
            <div class="time" id="clock">--:--</div>
            <div class="date" id="date">--.--.--</div>
        </div>
    </header>

    <main>
        {news_sections}
    </main>

    <footer>
        <div>Weather: Check Local Data</div>
        <div>
            <span style="color: #ffeb3b; font-weight: bold; margin-right: 15px;">🎉 Mission Complete: Command Center Online</span>
            <a href="https://www.youtube.com/watch?v=lTRiuFIWV54" target="_blank" style="color: var(--accent); text-decoration: none;">▶ Play Celebration Music</a>
        </div>
        <div>System Status: Online | Auto-refresh: 2min | Source: Serper API</div>
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
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Starting update cycle...")
    
    # 1. Select Random Background
    bg_keyword = random.choice(BG_KEYWORDS)
    bg_url = f"https://source.unsplash.com/featured/1920x1080/?{requests.utils.quote(bg_keyword)}"
    print(f"Selected Background: {bg_keyword}")

    # 2. Fetch News
    news_sections_html = ""
    
    for category_en, query_kr in TOPICS.items():
        print(f"Fetching news for: {category_en} ({query_kr})")
        articles = fetch_top_news_serper(query_kr)
        
        news_html = f'<article class="news-card"><div class="category">{category_en}</div>'
        
        if not articles:
            news_html += '<div class="news-item"><h2 class="news-title">데이터 수신 대기 중</h2><p class="news-summary">API 키가 없거나 뉴스를 불러올 수 없습니다. Serper API Key를 확인해주세요.</p></div>'
        
        for art in articles:
            summary = art['summary']
            if len(summary) > 150:
                summary = summary[:150] + "..."
                
            news_html += f"""
            <div class="news-item">
                <h2 class="news-title">{art['title']}</h2>
                <p class="news-summary">{summary}</p>
            </div>
            """
        
        news_html += '</article>'
        news_sections_html += news_html

    # 3. Generate HTML
    final_html = HTML_TEMPLATE.format(
        bg_url=bg_url,
        news_sections=news_sections_html
    )

    # 4. Save
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"Successfully updated: {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_signage()
