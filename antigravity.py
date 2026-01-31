import os, requests, telebot, re, time, threading
from datetime import datetime

# 1. 지휘소 경로 설정
os.chdir('/Users/seunghoonoh/woonmok.github.io')
TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
bot = telebot.TeleBot(TOKEN)

def ghost_buster_update(new_tasks=None):
    try:
        # [A] 실시간 데이터 수집
        w_res = requests.get("https://wttr.in/Jinan,KR?format=%t|%h", timeout=10)
        raw_temp, raw_humi = w_res.text.replace('+', '').split('|')
        
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # [B] 유령 제거 정밀 타격 회로
        # 기온부터 시작해서 습도 숫자가 몇 개가 붙어있든 상관없이 
        # </div> 또는 </span> 태그가 나오기 전까지의 모든 글자를 싹 지우고 새로 씁니다.
        content = re.sub(
            r'기온:.*?(?=<|</div>|</span>)', 
            f'기온: {raw_temp} | 습도: {raw_humi} ', 
            content,
            flags=re.DOTALL
        )

        # [C] 텔레그램 할 일 업데이트
        if new_tasks:
            content = re.sub(
                r'(<div class="mission-control".*?<span>)(.*?)(</span>)', 
                rf'\1{new_tasks}\3', 
                content, 
                flags=re.DOTALL
            )

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)

        # [D] 본부 전송
        os.system("git add . && git commit -m 'Ghostbuster Clean Update' && git push origin main")
        return f"🌡️ 세척 완료! 현재 진안: {raw_temp} / {raw_humi}"
        
    except Exception as e:
        return f"🚨 엔진 오류: {str(e)}"

# 자동 갱신 및 텔레그램 핸들러 (이전과 동일)
def heartbeat():
    while True:
        ghost_buster_update()
        time.sleep(1800)

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    status = ghost_buster_update(message.text)
    bot.reply_to(message, f"🏛️ 지휘관님, 유령 박멸 및 업데이트 완료!\n\n🚩 할 일: {message.text}\n{status}")

print("📡 [Ghostbusters Mode] 가동... 유령을 잡으러 갑니다.")
threading.Thread(target=heartbeat, daemon=True).start()
bot.polling()