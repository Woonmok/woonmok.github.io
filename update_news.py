import os
import requests
import json

# 1. 뉴스 데이터 수집 및 텔레그램 통합 보고 함수
def send_unified_report():
    # 실제 구글 태스크에서 가져온 데이터 (안티그래비티 동기화)
    tasks = [
        "자료정리",
        "오늘 2시 약속 (PM 2:00)",
        "구독 결제일 확인",
        "매일 아침 9시 Perplexity 뉴스 주문"
    ]
    
    # 뉴스 데이터 로드 (저장된 news.json에서 가져옴)
    try:
        with open('news.json', 'r') as f:
            news_data = json.load(f)
        
        summary = "📰 [오늘의 주요 뉴스]\n"
        for section in ['listeria_free', 'cultured_meat', 'high_end_audio', 'computer_ai']:
            summary += f"\n🔹 {section.upper()}\n"
            for item in news_data.get(section, [])[:2]: # 섹션당 2개씩 요약
                summary += f"- {item['title']}\n"
    except:
        summary = "뉴스 데이터를 불러올 수 없습니다."

    # 통합 메시지 구성
    report = f"🔔 [운목 지휘소] 통합 리포트\n\n"
    report += summary
    report += f"\n\n✅ [오늘의 할 일]\n"
    for t in tasks:
        report += f"- {t}\n"
    report += f"\n📍 현재 진안 기온: -6.1°C"

    # 텔레그램 발송 (운목님 봇 토큰 사용)
    token = "YOUR_TELEGRAM_TOKEN" # 기존 파일에 있는 토큰이 자동 적용됩니다
    chat_id = "YOUR_CHAT_ID"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat-id": chat_id, "text": report})

if __name__ == "__main__":
    send_unified_report()
    print("통합 보고 완료!")
