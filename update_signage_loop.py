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
TOPICS_CONFIG = {
    'listeria': {
        'query': '리스테리아 프리 기술',
        'label': 'LISTERIA FREE'
    },
    'meat': {
        'query': '배양육 최신 동향',
        'label': 'CULTURED MEAT'
    },
    'audio': {
        'query': '하이엔드 오디오 신제품',
        'label': 'HIGH-END AUDIO'
    },
    'computer': {
        'query': 'AI 기술 트렌드',
        'label': 'COMPUTER & AI'
    }
}

# HTML Template (Based on digital_signage.html)
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="120">
  <title>The Wave Tree Project - Farmerstree Digital Signage</title>
  <style>
    /* Base Reset & Fonts */
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: #000;
      color: #fff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      overflow: hidden;
      /* Prevent scroll */
      height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    /* Utilities */
    .glass {{
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }}

    .text-emerald {{
      color: #34d399;
    }}

    .text-orange {{
      color: #fb923c;
    }}

    .text-blue {{
      color: #60a5fa;
    }}

    .font-mono {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}

    /* Background Ambience */
    .bg-gradient {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: radial-gradient(ellipse at top, #0f172a, #000);
      z-index: -1;
    }}

    /* Header */
    header {{
      height: 100px;
      padding: 0 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(0, 0, 0, 0.4);
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 1rem;
    }}

    .dot {{
      width: 12px;
      height: 12px;
      background-color: #10b981;
      border-radius: 50%;
      box-shadow: 0 0 10px #10b981;
      animation: pulse 2s infinite;
    }}

    .title {{
      font-size: 1.5rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      background: linear-gradient(to right, #34d399, #06b6d4);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .subtitle {{
      font-size: 1.125rem;
      font-weight: 300;
      color: rgba(255, 255, 255, 0.3);
      margin-left: 0.5rem;
    }}

    .header-info {{
      display: flex;
      gap: 2rem;
      align-items: center;
    }}

    .weather-pill {{
      display: flex;
      gap: 1.5rem;
      padding: 0.5rem 1.5rem;
      border-radius: 9999px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      font-size: 0.875rem;
      color: #d1d5db;
    }}

    .time-display {{
      text-align: right;
    }}

    #clock {{
      font-size: 1.5rem;
      font-weight: 700;
      min-width: 120px;
      min-height: 29px;
    }}

    /* Min dimensions to prevent shift */
    .last-update {{
      font-size: 0.75rem;
      color: #6b7280;
      letter-spacing: 0.05em;
      margin-top: 4px;
    }}

    /* Main Content */
    main {{
      flex: 1;
      padding: 2rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
      overflow: hidden;
    }}

    /* Mission Section */
    .mission-section {{
      padding: 1.5rem;
      border-radius: 0.75rem;
      background: linear-gradient(to right, rgba(6, 78, 59, 0.4), rgba(0, 0, 0, 0.4));
      border: 1px solid rgba(16, 185, 129, 0.3);
      display: flex;
      align-items: center;
      gap: 2rem;
    }}

    .mission-label {{
      font-size: 1.25rem;
      font-weight: 700;
      color: #34d399;
      letter-spacing: 0.05em;
      white-space: nowrap;
    }}

    .mission-items {{
      display: flex;
      gap: 2rem;
      font-size: 1.125rem;
      font-weight: 500;
    }}

    .mission-item {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .mission-dot {{
      width: 8px;
      height: 8px;
      background-color: #10b981;
      border-radius: 50%;
      opacity: 0.8;
    }}

    /* Grid */
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1.5rem;
      flex: 1;
      min-height: 0;
      /* Fix for overflow in flex item */
    }}

    .card {{
      background-color: #111827;
      /* Dark gray fallback */
      background-size: cover;
      background-position: center;
      border-radius: 0.75rem;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
      border: 1px solid rgba(255, 255, 255, 0.1);
      transition: all 0.3s;
    }}

    .card:hover {{
      border-color: rgba(255, 255, 255, 0.2);
    }}

    .card-overlay {{
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.6);
      z-index: 1;
    }}

    .card-content {{
      position: relative;
      z-index: 5;
      padding: 1.5rem;
      height: 100%;
      display: flex;
      flex-direction: column;
    }}

    .card-header {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      margin-bottom: 1rem;
    }}

    .icon-box {{
      padding: 0.5rem;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 0.5rem;
      color: #34d399;
    }}

    .card-title {{
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      font-family: monospace;
      text-transform: uppercase;
    }}

    .news-list {{
      flex: 1;
      overflow-y: hidden; /* Hide overflow for clean look, script limits items */
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}

    .news-item {{
      padding: 1rem;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 0.5rem;
      border-left: 2px solid transparent;
      text-decoration: none;
      transition: all 0.2s;
    }}

    .news-item:hover {{
      background: rgba(255, 255, 255, 0.1);
      border-left-color: #10b981;
    }}

    .news-title {{
      font-size: 0.95rem;
      font-weight: 600;
      color: #e5e7eb;
      margin-bottom: 0.5rem;
      line-height: 1.4;
      display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
    }}

    .news-meta {{
      display: flex;
      justify-content: space-between;
      font-size: 0.75rem;
      color: #9ca3af;
    }}

    /* Footer Ticker */
    footer {{
      height: 64px;
      /* h-16 */
      background: rgba(6, 78, 59, 0.9);
      border-top: 1px solid rgba(16, 185, 129, 0.3);
      display: flex;
      align-items: center;
      overflow: hidden;
      position: relative;
      z-index: 20;
    }}

    .marquee-container {{
      display: flex;
      white-space: nowrap;
      /* GPU Acceleration */
      will-change: transform;
      transform: translate3d(0, 0, 0);
      animation: marquee 240s linear infinite; /* Ultra-slow 240s */
    }}

    .marquee-content {{
      display: flex;
      gap: 3rem;
      padding: 0 1rem;
      font-size: 2rem;
      font-weight: 600;
      color: #d1fae5;
    }}

    .ticker-item {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .ticker-dot {{
      width: 6px;
      height: 6px;
      background-color: #34d399;
      border-radius: 50%;
    }}

    @keyframes marquee {{
      0% {{
        transform: translateX(0);
      }}

      100% {{
        transform: translateX(-50%);
      }}
    }}

    @keyframes pulse {{

      0%,
      100% {{
        opacity: 1;
      }}

      50% {{
        opacity: 0.5;
      }}
    }}

    /* Scrollbar Hide */
    ::-webkit-scrollbar {{
      display: none;
    }}

    * {{
      -ms-overflow-style: none;
      scrollbar-width: none;
    }}
  </style>
</head>

<body>
  <div class="bg-gradient"></div>

  <header>
    <div class="brand">
      <div class="dot"></div>
      <div class="title">The Wave Tree Project</div>
      <div class="subtitle">Farmerstree</div>
    </div>
    <div class="header-info">
      <div class="weather-pill">
        <!-- Weather Data Injected Here -->
        {weather_html}
      </div>
      <div class="time-display font-mono">
        <div id="clock">--:--:--</div>
        <div class="last-update">LIVE SYSTEM</div>
      </div>
    </div>
  </header>

  <main>
    <!-- Today's Mission -->
    <div class="mission-section">
      <div class="mission-label">TODAY'S MISSION</div>
      <div class="mission-items">
        <div class="mission-item">
          <div class="mission-dot"></div>
          지휘소 세팅 완료 기념 음악 감상
        </div>
        <div class="mission-item">
          <div class="mission-dot"></div>
          최소 장비 목록 만들기
        </div>
      </div>
    </div>

    <!-- Grid -->
    <div class="grid">
      <!-- 1. Listeria Free -->
      <div class="card"
        style="background-image: url('https://images.unsplash.com/photo-1504333638930-c8787321eee0?q=80&w=2070&auto=format&fit=crop');">
        <div class="card-overlay"></div>
        <div class="card-content">
          <div class="card-header">
            <div class="icon-box">Act</div>
            <div class="card-title">LISTERIA FREE</div>
          </div>
          <div class="news-list">
            {news_listeria}
          </div>
        </div>
      </div>

      <!-- 2. Cultured Meat -->
      <div class="card"
        style="background-image: url('https://images.unsplash.com/photo-1530893609608-32a9af3aa95c?q=80&w=2564&auto=format&fit=crop');">
        <div class="card-overlay"></div>
        <div class="card-content">
          <div class="card-header">
            <div class="icon-box">Svr</div>
            <div class="card-title">CULTURED MEAT</div>
          </div>
          <div class="news-list">
             {news_meat}
          </div>
        </div>
      </div>

      <!-- 3. Audio -->
      <div class="card"
        style="background-image: url('https://images.unsplash.com/photo-1558584673-c834fb1cc3ca?q=80&w=2535&auto=format&fit=crop');">
        <div class="card-overlay"></div>
        <div class="card-content">
          <div class="card-header">
            <div class="icon-box">Mus</div>
            <div class="card-title">HIGH-END AUDIO</div>
          </div>
          <div class="news-list">
             {news_audio}
          </div>
        </div>
      </div>

      <!-- 4. Computer -->
      <div class="card"
        style="background-image: url('https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=2070&auto=format&fit=crop');">
        <div class="card-overlay"></div>
        <div class="card-content">
          <div class="card-header">
            <div class="icon-box">Cpu</div>
            <div class="card-title">COMPUTER & AI</div>
          </div>
          <div class="news-list">
             {news_computer}
          </div>
        </div>
      </div>
    </div>
  </main>

  <footer>
    <div class="marquee-container">
      <div class="marquee-content">
        {marquee_items}
      </div>
      <!-- Duplicate for loop seamlessness (content repeated in fetch) -->
      <div class="marquee-content" aria-hidden="true">
        {marquee_items}
      </div>
    </div>
  </footer>

  <script>
    // System Clock
    function updateClock() {{
      const now = new Date();
      const timeString = now.toLocaleTimeString('ko-KR', {{ hour12: false }});
      document.getElementById('clock').innerText = timeString;
    }}
    setInterval(updateClock, 1000);
    updateClock();

    // Auto Reload for Fresh Data
    setTimeout(() => {{
        window.location.reload();
    }}, 120000); // 120s
  </script>
</body>
</html>
"""

def fetch_weather_serper(query="진안군 부귀면 날씨"):
    """Fetch weather and return formatted string."""
    api_key = os.environ.get("SERPER_API_KEY")
    # Default fallback
    temp = "-XX°C"
    humidity = "XX%"
    
    if api_key:
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": query,
            "gl": "kr",
            "hl": "ko"
        })
        headers = { 'X-API-KEY': api_key, 'Content-Type': 'application/json' }
        
        try:
            response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
            data = response.json()
            
            # Parsing Strategy (Snippet/AnswerBox)
            found = False
            
            # Strategy 1: AnswerBox (High confidence)
            if 'answerBox' in data:
                box = data['answerBox']
                # Check directly for temperature key
                if 'temperature' in box:
                    temp = str(box.get('temperature')) + "°C"
                    if 'humidity' in box: humidity = str(box.get('humidity')) + "%"
                    found = True
            
            # Strategy 2: Knowledge Graph
            if not found and 'knowledgeGraph' in data:
                kg = data['knowledgeGraph']
                if 'attributes' in kg:
                    attrs = kg['attributes']
                    if 'Temperature' in attrs: temp = attrs['Temperature']
                    elif '기온' in attrs: temp = attrs['기온']
                    
                    if 'Humidity' in attrs: humidity = attrs['Humidity']
                    elif '습도' in attrs: humidity = attrs['습도']
                    found = True

            # Strategy 3: Organic Snippet (Fallback, strictly parse only near "기온")
            if not found and 'organic' in data:
                for res in data['organic']:
                    text = (res.get('title', '') + " " + res.get('snippet', ''))
                    # Look for "기온: -5°C" or "-5도" context
                    # Avoid years like '21년' -> must have °C or 도 immediately after number
                    t_match = re.search(r'기온.*?(-?\d{1,2})\s*(°C|도)', text)
                    if t_match:
                        temp = t_match.group(1) + "°C"
                        found = True
                    
                    if found:
                        h_match = re.search(r'습도.*?(\d{1,3})%', text)
                        if h_match: humidity = h_match.group(1) + "%"
                        break
                        
        except Exception as e:
            print(f"Weather Fetch Error: {e}")

    # Return Formatted HTML (Strict Format)
    return f"""
        <span><span class="text-orange">기온</span> {temp}</span>
        <span><span class="text-blue">습도</span> {humidity}</span>
    """

def fetch_top_news_serper(query, count=5):
    """Fetch news items list. Limit to 5."""
    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        return [
            {'title': f'Data Pending for {query}', 'date': datetime.datetime.now().strftime('%Y.%m.%d')}
        ]

    # Force Korean results by adding Korean keywords to query if needed, 
    # but 'hl=ko' usually handles UI language.
    # The user insists on Korean content. 
    # Providing 'gl=kr' and 'hl=ko' is the standard way.
    
    url = "https://google.serper.dev/news"
    payload = json.dumps({
        "q": query, "gl": "kr", "hl": "ko", "num": 10 # Fetch more to filter
    })
    headers = { 'X-API-KEY': api_key, 'Content-Type': 'application/json' }

    items = []
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        data = response.json()
        
        if 'news' in data:
            for news in data['news']:
                if len(items) >= count: break
                
                title = news.get('title', 'No Title')
                
                # Filter: Prefer Korean characters?
                # Simple check: does it contain Hangul?
                if re.search(r'[가-힣]', title):
                    items.append({
                        'title': title,
                        'date': news.get('date', 'Today') # Simplified date
                    })
                
            # If we don't have enough Korean items, fill with remaining
            if len(items) < count:
                 for news in data['news']:
                    if len(items) >= count: break
                    if not any(x['title'] == news.get('title') for x in items):
                        items.append({
                            'title': news.get('title', 'No Title'),
                            'date': news.get('date', 'Today')
                        })
                        
    except Exception as e:
        print(f"News Fetch Error {query}: {e}")
        
    return items

def generate_news_html(items):
    html_output = ""
    for item in items:
        html_output += f"""
        <div class="news-item">
            <div class="news-title">{item['title']}</div>
            <div class="news-meta">
                <span>Read More →</span>
                <span>{item['date']}</span>
            </div>
        </div>
        """
    return html_output

def send_telegram_alert(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Telegram Config Missing. Skipping alert.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    
    try:
        requests.post(url, json=payload, timeout=5)
        print("Telegram notification sent.")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def update_signage():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Starting Final Tuning Update...")

    # 1. Fetch Weather
    print("Fetching Weather...")
    weather_html = fetch_weather_serper()

    # 2. Fetch News for each section
    news_content = {}
    all_headlines = []

    for key, config in TOPICS_CONFIG.items():
        print(f"Fetching {key}...")
        items = fetch_top_news_serper(config['query'], count=5) # Limit to 5
        news_content[key] = generate_news_html(items)
        
        # Collect headlines for marquee
        for item in items:
            all_headlines.append(f"[{config['label']}] {item['title']}")

    # 3. Build Marquee HTML
    # <div class="ticker-item"><div class="ticker-dot"></div> Headline... </div>
    marquee_html = ""
    if not all_headlines:
        all_headlines = ["THE WAVE TREE PROJECT - SYSTEM ONLINE"]
    
    for hl in all_headlines:
        marquee_html += f"""
        <div class="ticker-item">
            <div class="ticker-dot"></div>
            {hl}
        </div>
        """

    # 4. Generate Final HTML
    final_html = HTML_TEMPLATE.format(
        weather_html=weather_html,
        news_listeria=news_content.get('listeria', ''),
        news_meat=news_content.get('meat', ''),
        news_audio=news_content.get('audio', ''),
        news_computer=news_content.get('computer', ''),
        marquee_items=marquee_html
    )

    # 5. Save
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"Successfully updated: {OUTPUT_FILE}")
        
        # 6. Telegram Alert
        # Extract temp for message "기온: -XX°C"
        temp_match = re.search(r'기온</span>\s*(-?[\d\.]+°C)', weather_html)
        current_temp = temp_match.group(1) if temp_match else "N/A"
        
        send_telegram_alert(f"대표님, Farmerstree 지휘소 업데이트 완료되었습니다. (진안 기온: {current_temp})")
        
    except Exception as e:
        print(f"Error writing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_signage()
