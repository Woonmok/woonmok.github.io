import json, requests

def send_real_briefing():
    # 안티그래비티가 동기화한 운목님의 실제 할 일
    real_tasks = ["자료정리", "구독 결제일 확인", "오늘 2시 약속", "아내 병원", "Perplexity 뉴스 주문"]
    
    try:
        with open('news.json', 'r', encoding='utf-8') as f: data = json.load(f)
        report = "🔔 [운목 지휘소] 맥미니 통합 브리핑\n\n📰 [오늘의 핵심 뉴스]\n"
        for k in ['listeria_free', 'high_end_audio']:
            report += f"• {k.upper()}: {data[k][0]['title']}\n"
    except: report = "뉴스 로드 실패"

    report += "\n✅ [운목님의 할 일 목록]\n" + "\n".join([f"- {t}" for t in real_tasks])
    report += f"\n\n📍 진안 기온: -6.1°C"

    # 텔레그램 전송 (본인의 토큰/ID 입력)
    token = "운목님의_봇_토큰"
    chat_id = "운목님의_채팅_ID"
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text": report})

if __name__ == "__main__":
    send_real_briefing()
    print("맥미니 본부에서 통합 리포트 발송 완료!")
