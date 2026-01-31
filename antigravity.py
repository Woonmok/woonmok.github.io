import os, requests, telebot, re, time, threading
from datetime import datetime

# 1. 지휘소 경로 설정 (운목님의 맥미니 경로)
os.chdir('/Users/seunghoonoh/woonmok.github.io')
TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
bot = telebot.TeleBot(TOKEN)

def update_system(new_tasks=None):
    try:
        # [A] 날씨 정보 실시간 수집 (wttr.in 활용)
        w_res = requests.get("https://wttr.in/Jinan,KR?format=%t|%h", timeout=10)
        raw_temp, raw_humi = w_res.text.replace('+', '').split('|')
        
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # [B] 습도 중첩 버그 수정 (정규표현식 정밀 타격)
        # "기온: ... | 습도: ..." 부분을 완전히 새로 써서 중첩 현상을 제거합니다.
        content = re.sub(
            r'기온: .*? \| 습도: .*?(?=<|</div>)', 
            f'기온: {raw_temp} | 습도: {raw_humi}', 
            content
        )

        # [C] 텔레그램 할 일 업데이트 (지휘관님이 메시지를 보냈을 때만)
        if new_tasks:
            # 오늘의 전략 과제 구역(span)을 찾아 내용을 통째로 교체합니다.
            content = re.sub(
                r'(<div class="mission-control".*?<span>)(.*?)(</span>)', 
                rf'\1{new_tasks}\3', 
                content, 
                flags=re.DOTALL
            )

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)

        # [D] 본부(GitHub) 자동 전송
        os.system("git add . && git commit -m 'Dashboard Auto-Update' && git push origin main")
        return f"🌡️ 현재 진안: {raw_temp} / 💧 습도: {raw_humi} (반영 완료)"
        
    except Exception as e:
        return f"🚨 엔진 오류 발생: {str(e)}"

# 30분마다 스스로 날씨를 갱신하는 심장박동
def heartbeat():
    while True:
        update_system()
        print(f"⏰ {datetime.now()} - 정기 업데이트 완료")
        time.sleep(1800)

# 텔레그램 명령 처리 (모든 메시지를 '할 일'로 인식)
@bot.message_handler(func=lambda m: True)
def on_telegram_message(message):
    res = update_system(message.text)
    bot.reply_to(message, f"🏛️ 지휘관님, 명을 받들었습니다!\n\n🚩 할 일 업데이트:\n{message.text}\n\n{res}")

print("📡 [Master Engine 3.0] 가동... 이제 텔레그램으로 할 일을 말씀해 주세요.")
threading.Thread(target=heartbeat, daemon=True).start()
bot.polling()