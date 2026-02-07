import time
import json
import os
import datetime
import sys
import re
import subprocess
import html


OUTPUT_FILE = 'index.html'
NEWS_FILE = 'news.json'
DASHBOARD_FILE = 'dashboard_data.json'

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="120">
  <title>The Wave Tree Project - Farmerstree Digital Signage</title>
  <style>
    /* ... 기존 CSS ... */
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
      <div class="weather-pill">{weather_html}</div>
      <div class="time-display font-mono">
        <div id="clock">--:--:--</div>
        <div class="last-update">LIVE SYSTEM</div>
      </div>
    </div>
  </header>
  <main>
    <div class="mission-section">
      <div class="mission-label">TODAY'S MISSION</div>
      <div class="mission-items">{mission_items_html}</div>
    </div>
    <div class="grid">
      <div class="card"><div class="card-overlay"></div><div class="card-content"><div class="card-header"><div class="icon-box">Act</div><div class="card-title">LISTERIA FREE</div></div><div class="news-list">{news_listeria}</div></div></div>
      <div class="card"><div class="card-overlay"></div><div class="card-content"><div class="card-header"><div class="icon-box">Svr</div><div class="card-title">CULTURED MEAT</div></div><div class="news-list">{news_meat}</div></div></div>
      <div class="card"><div class="card-overlay"></div><div class="card-content"><div class="card-header"><div class="icon-box">Mus</div><div class="card-title">HIGH-END AUDIO</div></div><div class="news-list">{news_audio}</div></div></div>
      <div class="card"><div class="card-overlay"></div><div class="card-content"><div class="card-header"><div class="icon-box">Cpu</div><div class="card-title">COMPUTER & AI</div></div><div class="news-list">{news_computer}</div></div></div>
    </div>
  </main>
  <footer>
    <div class="marquee-container"><div class="marquee-content">{marquee_items}</div><div class="marquee-content" aria-hidden="true">{marquee_items}</div></div>
  </footer>
  <script>
    function updateClock() {{
      const now = new Date();
      const timeString = now.toLocaleTimeString('ko-KR', {{ hour12: false }});
      document.getElementById('clock').innerText = timeString;
    }}
    setInterval(updateClock, 1000);
    updateClock();
    setTimeout(() => {{ window.location.reload(); }}, 120000);
  </script>
</body>
</html>
        # 5. Marquee (all headlines)
        all_headlines = []
        for item in news_data.get('items', []):
          all_headlines.append(f"[{item.get('category', '')}] {item.get('title', '')}")
        if not all_headlines:
          all_headlines = ["THE WAVE TREE PROJECT - SYSTEM ONLINE"]
        marquee_html = "".join([f"<div class='ticker-item'><div class='ticker-dot'></div>{hl}</div>" for hl in all_headlines])

        # 6. Mission (todo_list)
        todo_list = get_todo_list(dashboard_data)
        mission_items_html = "".join([
          f"<div class='mission-item'><div class='mission-dot'></div>{html.escape(item['text'])}</div>" for item in todo_list[:3]
        ])

        # 7. Render HTML_TEMPLATE with dynamic mission_items
        final_html = HTML_TEMPLATE.replace(
          '<div class="mission-items">\n        <div class="mission-item">\n          <div class="mission-dot"></div>\n          지휘소 세팅 완료 기념 음악 감상\n        </div>\n        <div class="mission-item">\n          <div class="mission-dot"></div>\n          최소 장비 목록 만들기\n        </div>\n        <div class="mission-item">\n          <div class="mission-dot"></div>\n          자료정리\n        </div>\n      </div>',
          f'<div class="mission-items">{mission_items_html}</div>'
        )
        final_html = final_html.format(
          weather_html=weather_html,
          news_listeria=news_listeria,
          news_meat=news_meat,
          news_audio=news_audio,
          news_computer=news_computer,
          marquee_items=marquee_html
        )

        # 8. Save & Git Push
        try:
          with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(final_html)
          print(f"Successfully updated: {OUTPUT_FILE}")
          subprocess.run("git add .", shell=True, check=True)
          subprocess.run('git commit -m "Auto Update: Weather, News, Todo"', shell=True, check=True)
          subprocess.run("git push", shell=True, check=True)
          print("[System] Push Complete.")
        except Exception as e:
          print(f"Error writing file: {e}")
          sys.exit(1)

      if __name__ == "__main__":
        update_signage()
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
      animation: marquee 360s linear infinite; /* Ultra-slow (6 mins) */
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
        <div class="mission-item">
          <div class="mission-dot"></div>
          자료정리
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

def format_weather_html(weather_data):
  temp = weather_data.get('temp', '-XX°C')
  humidity = weather_data.get('humidity', 'XX%')
  return f"<span><span class='text-orange'>기온:</span> {temp} / <span class='text-blue'>습도:</span> {humidity}</span>"

def generate_news_html(items):
  html_output = ""
  for item in items:
    html_output += f"""
    <div class='news-item'>
      <div class='news-title'>{item['title']}</div>
      <div class='news-meta'><span>Read More →</span><span>{item.get('published_at', item.get('date', 'Today'))}</span></div>
    </div>
    """
  return html_output

def get_top_news_by_category(news_data, category, count=2):
  items = [item for item in news_data.get('items', []) if item.get('category') == category]
  items = sorted(items, key=lambda x: x.get('published_at', ''), reverse=True)
  return items[:count]

def get_todo_list(dashboard_data):
  return dashboard_data.get('todo_list', [])

def send_telegram_alert(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    print(f"Telegram Config Check: Token={'Present' if token else 'Missing'}, ChatID={'Present' if chat_id else 'Missing'}")


def update_signage():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Starting Update...")

    # 1. Load dashboard_data.json
    try:
        with open(DASHBOARD_FILE, 'r', encoding='utf-8') as f:
            dashboard_data = json.load(f)
    except Exception as e:
        print(f"Error loading dashboard_data.json: {e}")
        dashboard_data = {}

    # 2. Load news.json
    try:
        with open(NEWS_FILE, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    except Exception as e:
        print(f"Error loading news.json: {e}")
        news_data = {"items": []}

    # 3. Weather
    weather_html = format_weather_html(dashboard_data.get('weather', {}))

    # 4. News (top 2 per category)
    news_listeria = generate_news_html(get_top_news_by_category(news_data, 'listeria_free', 2))
    news_meat = generate_news_html(get_top_news_by_category(news_data, 'cultured_meat', 2))
    news_audio = generate_news_html(get_top_news_by_category(news_data, 'high_end_audio', 2))
    news_computer = generate_news_html(get_top_news_by_category(news_data, 'computer_ai', 2))

    # 5. Marquee (all headlines)
    all_headlines = []
    for item in news_data.get('items', []):
        all_headlines.append(f"[{item.get('category', '')}] {item.get('title', '')}")
    if not all_headlines:
        all_headlines = ["THE WAVE TREE PROJECT - SYSTEM ONLINE"]
    marquee_html = "".join([f"<div class='ticker-item'><div class='ticker-dot'></div>{hl}</div>" for hl in all_headlines])

    # 6. Mission (todo_list)
    todo_list = get_todo_list(dashboard_data)
    mission_items_html = "".join([
        f"<div class='mission-item'><div class='mission-dot'></div>{html.escape(item['text'])}</div>" for item in todo_list[:3]
    ])

    # 7. Render HTML_TEMPLATE with dynamic mission_items
    final_html = HTML_TEMPLATE.replace(
        '<div class="mission-items">\n        <div class="mission-item">\n          <div class="mission-dot"></div>\n          지휘소 세팅 완료 기념 음악 감상\n        </div>\n        <div class="mission-item">\n          <div class="mission-dot"></div>\n          최소 장비 목록 만들기\n        </div>\n        <div class="mission-item">\n          <div class="mission-dot"></div>\n          자료정리\n        </div>\n      </div>',
        f'<div class="mission-items">{mission_items_html}</div>'
    )
    final_html = final_html.format(
        weather_html=weather_html,
        news_listeria=news_listeria,
        news_meat=news_meat,
        news_audio=news_audio,
        news_computer=news_computer,
        marquee_items=marquee_html
    )

    # 8. Save & Git Push
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"Successfully updated: {OUTPUT_FILE}")
        subprocess.run("git add .", shell=True, check=True)
        subprocess.run('git commit -m "Auto Update: Weather, News, Todo"', shell=True, check=True)
        subprocess.run("git push", shell=True, check=True)
        print("[System] Push Complete.")
    except Exception as e:
        print(f"Error writing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_signage()
        # msg = "대표님, 모든 수리가 완료되었습니다. 이제 안심하고 다녀오십시오!"
        # send_telegram_alert(msg)
