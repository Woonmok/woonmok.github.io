#!/usr/bin/env python3
# analyze_radar.py - Antigravity 분석 도구
"""
Project_Radar.md를 읽고 로컬 규칙 기반으로 분석하여 인사이트 생성
Antigravity가 실행하거나 대화로 요청 가능
"""

from datetime import datetime
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
RADAR_FILE = PROJECT_ROOT / "Project_Radar.md"
OUTPUT_FILE = PROJECT_ROOT / "Radar_Insights.md"

CATEGORY_KEYWORDS = {
    "배양육/푸드테크": ["배양육", "cultured meat", "cell-based", "fermentation", "균사체", "mycelium"],
    "식품 안전": ["리스테리아", "listeria", "fda", "식품 안전", "오염"],
    "하이엔드 오디오": ["오디오", "하이엔드", "dsd", "dac", "앰프"],
    "AI/컴퓨팅": ["ai", "gpu", "blackwell", "nvidia", "서버", "인프라"],
}


def _count_keywords(text):
    lower_text = text.lower()
    counts = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        counts[category] = sum(lower_text.count(keyword.lower()) for keyword in keywords)
    return counts


def _extract_relevant_lines(text, topic=None, limit=8):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    filtered = []
    if topic:
        topic_lower = topic.lower()
        for line in lines:
            if topic_lower in line.lower():
                filtered.append(line)
    else:
        filtered = lines
    return filtered[:limit]


def read_radar():
    """Project_Radar.md 읽기"""
    try:
        return RADAR_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def analyze_trends(radar_content):
    """전체 트렌드 분석 (로컬 규칙 기반)"""
    counts = _count_keywords(radar_content)
    top_categories = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    top3 = [item for item in top_categories if item[1] > 0][:3]

    if not top3:
        top3 = top_categories[:3]

    risks = []
    lower_text = radar_content.lower()
    for keyword in ["리스테리아", "listeria", "오염", "리콜", "규제", "고비용"]:
        if keyword.lower() in lower_text:
            risks.append(keyword)

    opportunities = []
    for keyword in ["절감", "효율", "발효", "자동화", "협업", "신규 시장"]:
        if keyword.lower() in lower_text:
            opportunities.append(keyword)

    lines = ["# 🔥 전체 트렌드 분석", "", "## 핵심 트렌드 (Top 3)"]
    for index, (category, score) in enumerate(top3, 1):
        lines.append(f"{index}. {category} (신호 강도: {score})")

    lines.extend(["", "## ⚠️ 주목 리스크"])
    if risks:
        lines.append("- " + ", ".join(sorted(set(risks))))
    else:
        lines.append("- 뚜렷한 리스크 키워드가 감지되지 않았습니다.")

    lines.extend(["", "## 💡 기회 요인"])
    if opportunities:
        lines.append("- " + ", ".join(sorted(set(opportunities))))
    else:
        lines.append("- 효율화/성장 키워드가 제한적입니다.")

    lines.extend(["", "## 📊 카테고리별 요약"])
    for category, score in top_categories:
        lines.append(f"- {category}: {score}")

    lines.extend([
        "",
        "## 🎯 추천 액션 아이템",
        "- 상위 카테고리 1개를 선정해 이번 주 실행 과제로 고정",
        "- 리스크 키워드 발생 항목은 별도 모니터링 섹션으로 분리",
        "- 효율/비용 절감 관련 항목은 우선순위 상향",
    ])
    return "\n".join(lines)


def search_topic(radar_content, topic):
    """특정 주제 검색 및 분석 (로컬 규칙 기반)"""
    matches = _extract_relevant_lines(radar_content, topic=topic, limit=12)
    if not matches:
        return f"## 🔍 '{topic}' 검색 결과\n\n- 관련 항목을 찾지 못했습니다."

    lines = [f"## 🔍 '{topic}' 검색 결과", "", "### 1) 관련 뉴스 목록"]
    for index, line in enumerate(matches, 1):
        lines.append(f"{index}. {line}")

    lines.extend([
        "",
        "### 2) 핵심 포인트",
        f"- '{topic}' 관련 항목 {len(matches)}건 감지",
        "- 반복 등장한 표현을 기준으로 우선순위 설정 권장",
        "",
        "### 3) 시사점",
        "- 관련 항목을 주간 실행 리스트로 전환해 추적",
    ])
    return "\n".join(lines)


def weekly_summary(radar_content):
    """주간 요약 생성 (로컬 규칙 기반)"""
    counts = _count_keywords(radar_content)
    ordered = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    highlights = [category for category, score in ordered if score > 0][:3]
    if not highlights:
        highlights = [category for category, _ in ordered[:3]]

    lines = [
        "# 📊 주간 인텔리전스 리포트",
        "",
        "## 🎯 이번 주 핵심",
    ]
    for index, category in enumerate(highlights, 1):
        lines.append(f"- {index}) {category}")

    lines.extend(["", "## 📈 카테고리별 동향"])
    for category, score in ordered:
        lines.append(f"- {category}: 신호 {score}")

    lines.extend([
        "",
        "## 💼 비즈니스 임팩트",
        "- 신호가 높은 카테고리에 리소스를 집중하는 것이 유리합니다.",
        "",
        "## 🔮 다음 주 전망",
        "- 상위 카테고리 추세 유지 여부와 리스크 키워드 재등장 여부를 추적하세요.",
    ])
    return "\n".join(lines)


def save_insights(content, mode="append"):
    """인사이트를 파일로 저장"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if mode == "overwrite" or not OUTPUT_FILE.exists():
        header = f"""# 🔍 Radar Insights - 분석 리포트

**생성 시각**: {timestamp}
    **분석 엔진**: Local Rule Engine

---

"""
        with OUTPUT_FILE.open("w", encoding="utf-8") as f:
            f.write(header + content)
    else:
        with OUTPUT_FILE.open("a", encoding="utf-8") as f:
            f.write(f"\n\n---\n## [{timestamp}] 업데이트\n\n{content}\n")


def main():
    """메인 실행"""
    print("🔍 Radar 분석 도구 시작...")
    
    # Radar 읽기
    radar_content = read_radar()
    if not radar_content:
        print("❌ Project_Radar.md를 찾을 수 없습니다.")
        return
    
    print(f"✅ Radar 데이터 로드 완료 ({len(radar_content)} 문자)")
    
    # 메뉴
    print("\n분석 모드를 선택하세요:")
    print("1. 🔥 전체 트렌드 분석")
    print("2. 📊 주간 요약 리포트")
    print("3. 🔍 특정 주제 검색")
    
    choice = input("\n선택 (1-3): ").strip()
    
    if choice == "1":
        print("\n🔄 전체 트렌드 분석 중...")
        insights = analyze_trends(radar_content)
        save_insights(insights, mode="overwrite")
        print(f"\n✅ 분석 완료!\n\n{insights}\n")
        print(f"📁 저장 위치: {OUTPUT_FILE}")
        
    elif choice == "2":
        print("\n🔄 주간 요약 생성 중...")
        summary = weekly_summary(radar_content)
        save_insights(summary, mode="overwrite")
        print(f"\n✅ 요약 완료!\n\n{summary}\n")
        print(f"📁 저장 위치: {OUTPUT_FILE}")
        
    elif choice == "3":
        topic = input("\n검색할 주제 입력 (예: 배양육, 리스테리아, GPU): ").strip()
        print(f"\n🔄 '{topic}' 검색 중...")
        result = search_topic(radar_content, topic)
        print(f"\n✅ 검색 완료!\n\n{result}\n")
        
        save = input("\n결과를 저장하시겠습니까? (y/n): ").strip().lower()
        if save == 'y':
            save_insights(f"## 🔍 '{topic}' 검색 결과\n\n{result}", mode="append")
            print(f"📁 저장 완료: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
