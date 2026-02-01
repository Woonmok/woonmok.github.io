import re
import json
import datetime
import os

LOG_FILE = "Intelligence_Log.md"
DATA_FILE = "dashboard_data.json"

def parse_log():
    if not os.path.exists(LOG_FILE):
        return []
    
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Simple regex to find entries: ## [Timestamp] [TAG] Title
    entries = []
    blocks = re.split(r'\n## ', content)
    
    # Skip preamble
    for block in blocks:
        if block.startswith("["): 
            try:
                # Extract header line
                lines = block.strip().split('\n')
                header = lines[0]
                body = "\n".join(lines[1:])
                
                # Parse header
                match = re.search(r"\[(.*?)\] \[(.*?)\] (.*)", header)
                if match:
                    timestamp, tag, title = match.groups()
                    entries.append({
                        "timestamp": timestamp,
                        "tag": tag,
                        "title": title,
                        "summary": body[:200] + "..." if len(body) > 200 else body,
                        "full_body": body
                    })
            except Exception as e:
                print(f"Error parsing block: {e}")
                
    return entries

def update_dashboard_data(entries):
    # Default State
    data = {
        "system_status": "NORMAL",
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "intelligence": [],
        "servers": {
            "A": {"name": "Server A: THE BRAIN", "param": "A100 x4", "role": "학습 엔진", "status": "연산 중", "load": 85},
            "B": {"name": "Server B: THE FACTORY", "param": "L40S x8", "role": "생산 공장", "status": "추론 가동", "load": 60},
            "C": {"name": "Server C: HANDS & EARS", "param": "6000 Ada", "role": "창작 엔진", "status": "DSD 셋업", "load": 30}
        }
    }

    # Load existing data to preserve other fields if needed (like todo_list)
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if "todo_list" in existing_data:
                    data["todo_list"] = existing_data["todo_list"]
        except:
            pass
    
    if not entries:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return

    # Check latest entries (up to 3)
    recent_entries = entries[-3:] if len(entries) >= 3 else entries
    recent_entries.reverse()
    
    data["intelligence"] = []
    for entry in recent_entries:
        data["intelligence"].append({
            "title": entry["title"],
            "summary": entry["summary"],
            "tag": entry["tag"],
            "score": "0.95" if entry["tag"] == "긴급" else ("0.90" if entry["tag"] == "중요" else "0.85")
        })
    
    # Priority Logic
    if recent_entries:
        latest = recent_entries[0]
        if "긴급" in latest["tag"]:
            data["system_status"] = "EMERGENCY"
            data["servers"]["A"]["status"] = "긴급 분석"
            data["servers"]["A"]["load"] = 98
            data["servers"]["B"]["status"] = "긴급 대기"
            data["servers"]["B"]["load"] = 20
            data["servers"]["C"]["status"] = "모니터링"
            data["servers"]["C"]["load"] = 90
        elif "우선순위 높음" in latest["tag"]:
            data["system_status"] = "HIGH_PRIORITY"
            data["servers"]["A"]["status"] = "집중 학습"
            data["servers"]["A"]["load"] = 95
        else:
            data["system_status"] = "NORMAL"
            data["servers"]["A"]["status"] = "연산 중"
            data["servers"]["A"]["load"] = 85
            data["servers"]["B"]["status"] = "추론 가동"
            data["servers"]["B"]["load"] = 60
            data["servers"]["C"]["status"] = "DSD 셋업"
            data["servers"]["C"]["load"] = 30
        
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Dashboard updated. Status: {data['system_status']}")

def update_todo_list(new_items):
    """
    Updates the todo_list in dashboard_data.json
    new_items: list of strings (task descriptions)
    """
    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    current_max_id = 0
    if "todo_list" in data and data["todo_list"]:
        current_max_id = max(item.get("id", 0) for item in data["todo_list"])

    new_todos = []
    for item in new_items:
        current_max_id += 1
        new_todos.append({
            "text": item,
            "completed": False,
            "id": current_max_id
        })
    
    # Replace active list
    data["todo_list"] = new_todos
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Updated To-Do List with {len(new_todos)} items.")

if __name__ == "__main__":
    try:
        from sync_news_to_log import sync_news
        # print("Syncing news to intelligence log...")
        # sync_news()
    except Exception as e:
        print(f"Failed to sync news: {e}")

    entries = parse_log()
    update_dashboard_data(entries)
