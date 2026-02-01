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
    # pattern = r"## \[(.*?)\] \[(.*?)\] (.*?)\n(.*?)(?=\n## |\Z)"
    # Using a slightly robust pattern
    entries = []
    blocks = re.split(r'\n## ', content)
    
    # Skip preamble (index 0 usually if file starts with # header)
    for block in blocks:
        if block.startswith("["): # Check if it looks like a log entry
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
                        "summary": body[:200] + "..." if len(body) > 200 else body, # Truncate for summary
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
    
    if not entries:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return

    # Check latest entry
    latest = entries[-1]
    data["intelligence"] = [{
        "title": latest["title"],
        "summary": latest["summary"],
        "tag": latest["tag"],
        "score": "0.95" if latest["tag"] == "긴급" else "0.85"
    }]
    
    # Logic for Priority
    if "긴급" in latest["tag"]:
        data["system_status"] = "EMERGENCY"
        # Reallocate resources for Emergency
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
        
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Dashboard updated. Status: {data['system_status']}")

if __name__ == "__main__":
    entries = parse_log()
    update_dashboard_data(entries)
