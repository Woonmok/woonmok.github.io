#!/usr/bin/env python3
# bridge_daily.py - Daily_Bridge → WaveTree_status 자동화

import argparse
import json
import re
from datetime import datetime
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_actionable_section(lines):
    in_section = False
    section_lines = []
    for line in lines:
        if line.strip().startswith("## 3"):
            in_section = True
            continue
        if in_section and line.strip().startswith("## "):
            break
        if in_section:
            section_lines.append(line)
    return section_lines


def extract_approved_tickets(content: str):
    lines = content.splitlines()
    target_lines = extract_actionable_section(lines)
    if not target_lines:
        target_lines = lines

    pattern = re.compile(r"^\s*[-*]\s*\[(x|X)\]\s*(.+)$")
    approved = []
    for line in target_lines:
        m = pattern.match(line)
        if m:
            approved.append(m.group(2).strip())
    return approved


def find_latest_pilot_summary(reports_dir: Path):
    if not reports_dir.exists():
        return None
    summaries = sorted(reports_dir.glob("summary_*.json"))
    if not summaries:
        return None
    latest = summaries[-1]
    try:
        return json.loads(latest.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def main():
    ap = argparse.ArgumentParser(description="Daily_Bridge → WaveTree_status.json bridge")
    ap.add_argument("--daily", default="/Users/seunghoonoh/woonmok.github.io/Daily_Bridge.md")
    ap.add_argument("--reports", default="/Users/seunghoonoh/woonmok.github.io/wave-tree-ai-pilot/reports")
    ap.add_argument("--output", default="/Users/seunghoonoh/woonmok.github.io/WaveTree_status.json")
    args = ap.parse_args()

    daily_path = Path(args.daily)
    if not daily_path.exists():
        raise SystemExit(f"Daily_Bridge not found: {daily_path}")

    content = read_text(daily_path)
    approved = extract_approved_tickets(content)

    pilot_summary = find_latest_pilot_summary(Path(args.reports))

    status = {
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "source_daily_bridge": str(daily_path),
        "approved_tickets": approved,
        "approved_count": len(approved),
        "pilot_summary": pilot_summary,
    }

    output_path = Path(args.output)
    output_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ Updated: {output_path}")
    print(f"Approved tickets: {len(approved)}")


if __name__ == "__main__":
    main()
