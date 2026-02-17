import json, requests

def send_real_briefing():
    # ⛔ 이전 봇 토큰 비활성화됨 (2026-02-12)
    # 새 봇은 antigravity.py에서 관리합니다.
    print("⛔ 이 스크립트는 비활성화되었습니다. antigravity.py를 사용하세요.")
    return

    # 1. 텔레그램 전용 주소 (운목님 고유 주소) — 비활성화됨
    TOKEN = "REVOKED"
    CHAT_ID = "REVOKED"
    
    # 2. 안티그래비티가 동기화한 운목님의 진짜 할 일
    real_tasks = [
        "자료정리", 
        "오늘 2시 약속 (PM 2:00)", 
        "아내 병원 (1월 12일)", 
        "구독 결제일 확인", 
        "매일 아침 9시 Perplexity 뉴스 주문"
    ]
    
    # 3. 뉴스 데이터 취합
    try:
        with open('news.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        news_report = "📰 [운목 지휘소 맥미니 리포트]\n"
        for k in ['listeria_free', 'cultured_meat', 'high_end_audio', 'computer_ai']:
            if k in data and data[k]:
                news_report += f"• {k.upper()}: {data[k][0]['title']}\n"
    except:
        news_report = "뉴스 데이터를 읽어오는 데 실패했습니다.\n"

    # 4. 통합 메시지 구성
    briefing = f"🔔 [운목 지휘소] 통합 브리핑\n\n"
    briefing += news_report
    briefing += f"\n✅ [오늘의 할 일 목록]\n"
    for i, t in enumerate(real_tasks, 1):
        briefing += f"{i}. {t}\n"
    briefing += f"\n📍 진안 기온: -6.1°C"

    # 5. 전송 실행
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        response = requests.post(url, data={"chat_id": CHAT_ID, "text": briefing})
        if response.status_code == 200:
            print("🚀 지휘소 리포트 전송 성공!")
        else:
            print(f"❌ 전송 실패: {response.text}")
    except Exception as e:
        print(f"⚠️ 연결 오류: {e}")

if __name__ == "__main__":
    send_real_briefing()
