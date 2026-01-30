import os, json, requests, random, urllib.parse

# 1. 지휘관 보안 주소
TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
CHAT_ID = "8556588810"

def run_antigravity():
    print("🚀 안티그래비티 '애플뮤직 & 아토스' 엔진 가동...")

    # 2. 애플뮤직 및 공간음향 선곡 로직
    tracks = [
        {"artist": "Nils Frahm", "title": "Says", "note": "초저역 텍스처 테스트"},
        {"artist": "Keith Jarrett", "title": "The Köln Concert", "note": "피아노 타건 잔향 확인"}
    ]
    pick = random.choice(tracks)
    music_link = f"https://music.apple.com/kr/search?term={urllib.parse.quote(pick['artist'] + ' ' + pick['title'])}"
    atmos_link = "https://music.apple.com/kr/curator/apple-music-spatial-audio/1567115160"

    # 3. 텔레그램 리포트 구성 (운목 지휘관 전용)
    report = (
        f"🏛️ [운목 지휘소] 통합 브리핑\n\n"
        f"✅ 오늘의 할 일:\n- 자료정리\n- 오늘 2시 약속\n- 아내 병원 동행\n\n"
        f"🎵 [오늘의 영감: High-Res]\n{pick['artist']} - {pick['title']}\n"
        f"🔗 애플뮤직: {music_link}\n\n"
        f"🌌 [공간 음향 체크]\n🔗 Atmos 무대 입장: {atmos_link}\n\n"
        f"📍 진안 기온: -6.1°C"
    )

    # 4. 텔레그램 발송
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": report})
    print("✅ 텔레그램 리포트 발송 완료 (폰을 확인하세요).")

    # 5. 시스템 동기화 (GitHub)
    os.system("git add .")
    os.system('git commit -m "Antigravity: Full Intelligence Sync"')
    os.system("git push origin main --force")
    print("🏁 본부 동기화 완료. 대시보드 화면이 갱신되었습니다.")

if __name__ == "__main__":
    run_antigravity()
