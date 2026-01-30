import os, json, requests, random, urllib.parse

# 1. 지휘관 보안 주소 (운목님 고유 ID)
TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
CHAT_ID = "8556588810"

def run_antigravity():
    print("🚀 [안티그래비티] 공간 음향 회선 복구 및 엔진 가동...")

    # 2. 애플뮤직 레퍼런스 선곡 (Lossless & Atmos)
    tracks = [
        {"artist": "Nils Frahm", "title": "Says", "note": "초저역 공간감 확인"},
        {"artist": "Keith Jarrett", "title": "The Köln Concert", "note": "피아노 타건의 잔향 확인"},
        {"artist": "Janos Starker", "title": "Bach Cello Suites", "note": "현의 묵직한 질감 확인"}
    ]
    pick = random.choice(tracks)
    
    # 3. 주소 정밀 보정
    search_url = f"https://music.apple.com/kr/search?term={urllib.parse.quote(pick['artist'] + ' ' + pick['title'])}"
    # 검증된 공간 음향 마스터 큐레이터 주소
    atmos_url = "https://music.apple.com/kr/curator/apple-music-spatial-audio/1564180390"

    # 4. 프리미엄 리포트 구성
    report = (
        f"🏛️ [운목 지휘소] 안티그래비티 리포트\n\n"
        f"좋은 아침입니다, 지휘관님. 진안 본부 전선 이상 무.\n\n"
        f"✅ [오늘의 전략 과제]\n- 자료정리 및 POM 프로젝트 도면 검토\n- 아내 병원 동행 (14:00)\n\n"
        f"🎵 [오늘의 영감: High-Res]\n{pick['artist']} - {pick['title']}\n"
        f"   (체크: {pick['note']})\n"
        f"🔗 [애플뮤직 청음]: {search_url}\n\n"
        f"🌌 [공간 음향 마스터 클래스]\n"
        f"🔗 [Atmos 무대 입장]: {atmos_url}\n\n"
        f"📍 진안 기온: -6.1°C"
    )

    # 5. 전송 및 동기화
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": report})
    os.system("git add . && git commit -m 'System: Fix Atmos link' && git push origin main --force")
    print("🏁 정비 완료. 폰의 텔레그램을 확인하세요.")

if __name__ == "__main__":
    run_antigravity()
import time
import schedule

def start_schedule():
    # 매일 아침 9시에 지휘관님께 보고서를 올립니다.
    schedule.every().day.at("09:00").do(run_antigravity)
    print("⏰ 안티그래비티 자동 예약 가동: 매일 아침 9시에 뵙겠습니다.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)
        start_schedule()
        