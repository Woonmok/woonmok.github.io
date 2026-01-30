import os, json, requests

# [세팅: 운목님의 고유 주소]
TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
CHAT_ID = "8556588810"

def run_antigravity():
    print("🚀 안티그래비티 엔진 가동: 지휘소 전체 정비를 시작합니다...")

    # 1. 텔레그램 리포트 구성 (할 일 동기화)
    tasks = ["자료정리", "오늘 2시 약속", "아내 병원", "9시 Perplexity 뉴스 주문"]
    briefing = f"🔔 [운목 지휘소] 안티그래비티 통합 브리핑\n\n✅ 오늘의 할 일:\n" + "\n".join([f"- {t}" for t in tasks])

    # 2. 텔레그램 발송
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": briefing})
    print("✅ 텔레그램 리포트 발송 완료.")

    # 3. 깃허브 자동 업데이트 (터미널 명령어 자동화)
    print("📡 본부(GitHub) 데이터 동기화 중...")
    os.system("git add .")
    os.system('git commit -m "Antigravity: System Auto-Sync"')
    os.system("git push origin main --force")
    print("🏁 모든 정비가 완료되었습니다. 이제 지휘소 화면을 확인하세요.")

if __name__ == "__main__":
    run_antigravity()
