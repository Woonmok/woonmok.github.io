import os, requests, telebot, re, time, threading
from datetime import datetime

# 1. 지휘소 경로 설정
os.chdir('/Users/seunghoonoh/woonmok.github.io')
TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
bot = telebot.TeleBot(TOKEN)

def final_surgical_update(new_tasks=None):
    try:
        # [A] 실시간 데이터 수집 (진안군 상전면)
        w_res = requests.get("https://wttr.in/Jinan,KR?format=%t|%h", timeout=10)
        raw_temp, raw_humi = w_res.text.replace('+', '').split('|')
        
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # [B] 오타 수정: <<header -> <header
        content = content.replace('<<header', '<header')

        # [C] 유령 박멸 타격 (중첩 div 구조 완벽 대응)
        # '진안 본부' 다음 줄에 나오는 기온/습도 줄을 통째로 갈아 끼웁니다.
        weather_regex = r'<div>기온:.*?</div>'
        new_weather_div = f'<div>기온: {raw_temp} | 습도: {raw_humi}</div>'
        content = re.sub(weather_regex, new_weather_div, content, flags=re.DOTALL)

        # [D] 텔레그램 할 일 업데이트
        if new_tasks:
            mission_regex = r'(<div class="mission-control".*?<span>)(.*?)(</span>)'
            content = re.sub(mission_regex, rf'\1{new_tasks}\3', content, flags=re.DOTALL)

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)

        # [E] 본부 전송
        os.system("git add . && git commit -m 'Final Surgical Clean' && git push origin main")
        print(f"✅ {datetime.now()} - 유령 소탕 및 업데이트 완료")
        return f"🌡️ 현재 진안: {raw_temp} / {raw_humi}"
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return f"🚨 엔진 오류: {str(e)}"

# 자동 갱신 엔진
def heartbeat():
    while True:
        final_surgical_update()
        time.sleep(1800)

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    status = final_surgical_update(message.text)
    bot.reply_to(message, f"🏛️ 지휘관님, 이제 유령은 완전히 소멸했습니다!\n\n🚩 과제: {message.text}\n{status}")

print("📡 [Surgical Mode Activated] 유령의 심장을 저격합니다...")
threading.Thread(target=heartbeat, daemon=True).start()
bot.polling()