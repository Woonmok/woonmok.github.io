import json
import os
import datetime

NEWS_FILE = "news.json"
LOG_FILE = "Intelligence_Log.md"

# Tag mapping based on news category
TAG_MAPPING = {
    "listeria_free": "[긴급]",
    "cultured_meat": "[중요]",
    "high_end_audio": "[정보]",
    "computer_ai": "[정보]"
}

def load_news():
    if not os.path.exists(NEWS_FILE):
        return {}
    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_existing_titles():
    if not os.path.exists(LOG_FILE):
        return set()
    
    titles = set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        
    import re
    # Match title in "## [Timestamp] [TAG] Title"
    matches = re.findall(r"## \[.*?\] \[.*?\] (.*)", content)
    for title in matches:
        titles.add(title.strip())
    
    return titles

def append_to_log(new_entries):
    if not new_entries:
        return

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n")
        for entry in new_entries:
            f.write(f"## [{entry['timestamp']}] {entry['tag']} {entry['title']}\n")
            f.write(f"{entry['summary']}\n\n")
    
    print(f"Added {len(new_entries)} new entries to Intelligence Log.")

def sync_news():
    news_data = load_news()
    existing_titles = load_existing_titles()
    
    new_log_entries = []
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Iterate through categories in priority order if needed, or just all
    for category, items in news_data.items():
        if category == "last_updated" or not isinstance(items, list):
            continue
            
        tag = TAG_MAPPING.get(category, "[일반]")
        
        for item in items:
            title = item.get("title", "").strip()
            if not title:
                continue
                
            if title not in existing_titles:
                # Add to log
                summary = item.get("summary", "")
                new_log_entries.append({
                    "timestamp": current_time,
                    "tag": tag,
                    "title": title,
                    "summary": summary
                })
                # Check duplication within the current batch too
                existing_titles.add(title)
    
    append_to_log(new_log_entries)

if __name__ == "__main__":
    sync_news()
