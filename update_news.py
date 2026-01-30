import json, requests

def send_final_report():
    # 안티그래비티가 직접 확인한 운목님의 실제 할 일 목록
    real_tasks = ["자료정리", "오늘 2시 약속", "구독 결제일 확인", "아내 병원", "Perplexity 뉴스 주문"]
    
    try:
        with open('news.json', 'r') as f: data = json.load(f)
        msg = "🔔 [운목 지휘소] 통합 리포트\n\n📰 [뉴스]\n"
        for k in ['listeria_free', 'high_end_audio']: # 핵심 뉴스만 요약
            msg += f"• {k.upper()}: {data[k][0]['title']}\n"
    except: msg = "데이터 로드 실패"

    msg += "\n✅ [오늘의 할 일]\n" + "\n".join([f"- {t}" for t in real_tasks])
    msg += "\n\n📍 현재 진안 기온: -6.1°C"

    # 전송 (운목님의 봇 정보 사용)
    token = "운목님의_봇_토큰"
    chat_id = "운목님의_채팅_ID"
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text": msg})

if __name__ == "__main__": send_final_report()
