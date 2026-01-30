import os
import sys

# 1. 지휘소의 실제 위치로 강제 이동 (경로 오류 방지)
# 이 줄이 있어야 바탕화면 아이콘이 본부를 정확히 찾아갑니다.
os.chdir('/Users/seunghoonoh/woonmok.github.io')

import requests
import random
import urllib.parse

# 2. 예약 실행 부품(schedule) 안전장치
try:
    import schedule
except ImportError:
    # 부품이 없어도 수동 실행은 가능하게 합니다.
    schedule = None

# 3. 텔레그램 보안키
TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
CHAT_ID = "8556588810"

def run_antigravity():
    print("🚀 안티그래비티 엔진 가동 중...")
    
    # 4. 애플뮤직 & 공간음향 큐레이션
    tracks = [
        {"art": "Nils Frahm", "tit": "Says", "note": "초저역 공간감 확인"},
        {"art": "Janos Starker", "tit": "Bach Cello", "note": "첼로의 질감 확인"}
    ]
    pick = random.choice(tracks)
    m_url = f"https://music.apple.com/kr/search?term={urllib.parse.quote(pick['art'] + ' ' + pick['tit'])}"
    a_url = "https://music.apple.com/kr/curator/apple-music-spatial-audio/1564180390"

    # 5. 리포트 작성
    report = (
        f"🏛️ [운목 지휘소] 안티그래비티 리포트\n\n"
        f"✅ 오늘의 전략 과제: POM 프로젝트 도면 검토 및 일정 확인\n\n"
        f"🎵 오늘의 영감: {pick['art']} - {pick['tit']}\n"
        f"🔗 [애플뮤직 청음]: {m_url}\n"
        f"🌌 [Atmos 무대 입장]: {a_url}\n\n"
        f"🌡️ 진안 기온: -6.1°C | 💧 습도: 65%"
    )

    # 6. 발송 및 동기화
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": report})
    os.system("git add . && git commit -m 'System: Fix directory path' && git push origin main --force")
    print("🏁 지휘관님, 보고 완료!")

if __name__ == "__main__":
    run_antigravity()
    # 맥(macOS) 화면에 직접 알림 띄우기
    os.system("""osascript -e 'display notification "안티그래비티 리포트 발송 및 본부 동기화가 완료되었습니다." with title "🏛️ 안티그래비티 지휘소"'""")

if __name__ == "__main__":
    run_antigravity()