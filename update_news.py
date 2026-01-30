import json, requests

def send_briefing():
    # 안티그래비티가 직접 확인한 운목님의 진짜 할 일
    tasks = ["자료정리", "오늘 2시 약속", "아내 병원", "구독 결제일 확인", "9시 Perplexity 뉴스 주문"]
    
    try:
        with open('news.json', 'r', encoding='utf-8') as f: data = json.load(f)
        report = "🔔 [운목 지휘소] 통합 리포트\n\n📰 [최신 뉴스]\n"
        for k in ['listeria_free', 'high_end_audio']:
            report += f"• {k.upper()}: {data[k][0]['title']}\n"
    except: report = "데이터 로드 실패"

    report += "\n✅ [오늘의 할 일]\n" + "\n".join([f"- {t}" for t in tasks])
    report += f"\n\n📍 현재 진안 기온: -6.1°C"

    # 텔레그램 전송 (본인의 봇 정보 사용)
    token = "운목님의_봇_토큰"
    chat_id = "운목님의_채팅_ID"
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text": report})

if __name__ == "__main__": send_briefing()
