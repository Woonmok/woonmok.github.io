import json
import requests

def send_unified_report():
    # 1. 실제 구글 태스크 데이터 (안티그래비티 동기화 버전)
    tasks = [
        "자료정리",
        "매일 아침 9시에 Perplexity 뉴스 주문 하기",
        "구독 결제일 확인 (4, 5, 6일)"
    ]
    
    # 2. news.json에서 최신 뉴스 제목 긁어오기
    try:
        with open('news.json', 'r') as f:
            data = json.load(f)
        news_msg = "📰 [운목 지휘소 뉴스 요약]\n"
        for cat in ['listeria_free', 'cultured_meat', 'high_end_audio', 'computer_ai']:
            news_msg += f"• {cat.upper()}: {data[cat][0]['title']}\n"
    except:
        news_msg = "뉴스 데이터를 불러올 수 없습니다."

    # 3. 통합 메시지 구성
    report = f"🔔 [운목 지휘소] 통합 리포트\n\n"
    report += news_msg
    report += f"\n✅ [오늘의 할 일]\n"
    for t in tasks:
        report += f"- {t}\n"
    report += f"\n📍 현재 진안 기온: -5.6°C" # 온도는 리포트 끝에 한 줄만!

    # 텔레그램 발송 (운목님 기존 설정값 사용)
    # 여기에 운목님의 BOT_TOKEN과 CHAT_ID를 넣어주세요.
    token = "운목님의_봇_토큰"
    chat_id = "운목님의_채팅_ID"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": report})

if __name__ == "__main__":
    send_unified_report()
