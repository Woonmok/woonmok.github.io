#!/usr/bin/env python3
# analyze_radar.py - Antigravity 분석 도구
"""
Project_Radar.md를 읽고 Gemini로 분석하여 인사이트 생성
Antigravity가 실행하거나 대화로 요청 가능
"""

import os
import google.generativeai as genai
from datetime import datetime
import json

# Gemini API 설정
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

RADAR_FILE = "/Users/seunghoonoh/woonmok.github.io/Project_Radar.md"
OUTPUT_FILE = "/Users/seunghoonoh/woonmok.github.io/Radar_Insights.md"


def read_radar():
    """Project_Radar.md 읽기"""
    try:
        with open(RADAR_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None


def analyze_trends(radar_content):
    """전체 트렌드 분석"""
    prompt = f"""당신은 '진안 Farmerstree' 프로젝트의 전략 분석가입니다.

다음 Project Radar 데이터를 분석하여:
1. 🔥 핵심 트렌드 (Top 3)
2. ⚠️ 주목해야 할 리스크
3. 💡 새로운 기회
4. 📊 카테고리별 요약 (배양육, 리스테리아, 오디오, AI/GPU)
5. 🎯 추천 액션 아이템

형식: 명확하고 실행 가능한 인사이트로 작성

데이터:
{radar_content}
"""
    
    response = model.generate_content(prompt)
    return response.text


def search_topic(radar_content, topic):
    """특정 주제 검색 및 분석"""
    prompt = f"""다음 Project Radar 데이터에서 '{topic}' 관련 내용을 찾아서:
1. 관련 뉴스 목록
2. 핵심 포인트
3. 시사점

데이터:
{radar_content}
"""
    
    response = model.generate_content(prompt)
    return response.text


def weekly_summary(radar_content):
    """주간 요약 생성"""
    prompt = f"""다음 Project Radar 데이터를 주간 리포트 형식으로 요약:

# 📊 주간 인텔리전스 리포트

## 🎯 이번 주 핵심
(가장 중요한 3가지)

## 📈 카테고리별 동향
- 배양육/푸드테크:
- 식품 안전:
- 하이엔드 오디오:
- AI/컴퓨팅:

## 💼 비즈니스 임팩트
(프로젝트에 미치는 영향)

## 🔮 다음 주 전망

데이터:
{radar_content}
"""
    
    response = model.generate_content(prompt)
    return response.text


def save_insights(content, mode="append"):
    """인사이트를 파일로 저장"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if mode == "overwrite" or not os.path.exists(OUTPUT_FILE):
        header = f"""# 🔍 Radar Insights - AI 분석 리포트

**생성 시각**: {timestamp}
**분석 엔진**: Gemini 1.5 Pro

---

"""
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(header + content)
    else:
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
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
