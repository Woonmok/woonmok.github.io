import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import datetime
import os
import ssl

# Bypass SSL verification for legacy reasons if needed (optional, but safer to have in some envs)
ssl._create_default_https_context = ssl._create_unverified_context

# Configuration: List of RSS feeds (Example: Tech and Science)
RSS_FEEDS = [
    {
        "name": "ScienceDaily - Technology",
        "url": "https://www.sciencedaily.com/rss/matter_energy/technology.xml"
    },
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed/"
    }
]

OUTPUT_FILE = "news_input.txt"

def fetch_rss(url):
    try:
        # User-Agent is often required
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_rss(xml_content, source_name):
    items = []
    try:
        root = ET.fromstring(xml_content)
        # Handle standard RSS 2.0
        channel = root.find("channel")
        if channel is not None:
            # item search
            rss_items = channel.findall("item")
            for item in rss_items[:5]: # Top 5 per feed
                title = item.find("title").text if item.find("title") is not None else "No Title"
                description = item.find("description").text if item.find("description") is not None else ""
                
                items.append({
                    "source": source_name,
                    "title": title,
                    "summary": description[:200] + "..." if len(description) > 200 else description
                })
    except Exception as e:
        print(f"Error parsing XML from {source_name}: {e}")
    return items

def main():
    print("📡 Initializing News Intelligence Hub...")
    all_news = []

    for feed in RSS_FEEDS:
        print(f"Fetching {feed['name']}...")
        content = fetch_rss(feed['url'])
        if content:
            news_items = parse_rss(content, feed['name'])
            all_news.extend(news_items)
            print(f"  - Retrieved {len(news_items)} items.")

    # Format for output
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_text = f"News Intelligence Dump [{timestamp}]\n"
    output_text += "="*50 + "\n\n"
    
    for idx, news in enumerate(all_news, 1):
        output_text += f"{idx}. [{news['source']}] {news['title']}\n"
        output_text += f"   summary: {news['summary']}\n\n"

    # Write to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output_text)

    print(f"\n✅ Successfully saved raw news to {OUTPUT_FILE}")
    print("👉 Now open VS Code Chat and ask Copilot to summarize this file.")

if __name__ == "__main__":
    main()
