import os, requests, telebot, re, time, threading
from datetime import datetime

# 1. 지휘소 경로 및 보안키 (운목님의 맥미니 환경)
os.chdir('/Users/seunghoonoh/woonmok.github.io')
TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
bot = telebot.TeleBot(TOKEN)

def deep_clean_update(new_tasks=None):
    try:
        # [A] 실시간 날씨 데이터 수집 (wttr.in)
        w_res = requests.get("https://wttr.in/Jinan,KR?format=%t|%h", timeout=10)
        raw_temp, raw_humi = w_res.text.replace('+', '').split('|')
        
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # [B] 습도 유령 제거 회로 (가장 강력한 패턴 매칭)
        # '기온'부터 태그가 닫히기 전까지의 모든 글자를 완전히 지우고 새로 씁니다.
        content = re.sub(
            r'기온: .*? \| 습도: .*?(?=</div>|</span>|<)', 
            f'기온: {raw_temp} | 습도: {raw_humi}', 
            content
        )

        # [C] 텔레그램 전략 과제 업데이트
        if new_tasks:
            # 중앙 미션 바의 <span> 태그 내부를 타격합니다.
            content = re.sub(
                r'(<div class="mission-control".*?<span>)(.*?)(</span>)', 
                rf'\1{new_tasks}\3', 
                content, 
                flags=re.DOTALL
            )

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)

        # [D] 본부 전송 (GitHub Push)
        os.system("git add . && git commit -m 'System Deep Clean & Task Update' && git push origin main")
        return f"🌡️ 진안: {raw_temp} / 💧 습도: {raw_humi}"
        
    except Exception as e:
        return f"🚨 보고드립니다! 오류 발생: {str(e)}"

# 30분 주기 자동 갱신 (지휘관님이 주무셔도 작동)
def heartbeat():
    while True:
        deep_clean_update()
        time.sleep(1800)

# 텔레그램 비서 가동 (운목님의 모든 메시지를 할 일로 인식)
@bot.message_handler(func=lambda m: True)
def handle_mission(message):
    status = deep_clean_update(message.text)
    bot.reply_to(message, f"🏛️ 지휘관님, 대시보드를 즉시 갱신했습니다!\n\n🚩 새 과제: {message.text}\n{status}\n\n🌐 확인: https://woonmok.github.io")

print("📡 [Master 3.5] 고정밀 지휘 엔진이 가동되었습니다. 이제 텔레그램으로 명령하세요.")
threading.Thread(target=heartbeat, daemon=True).start()
bot.polling()