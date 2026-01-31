import os, requests, telebot, re, time, threading
from datetime import datetime

# [1] 지휘소 경로 설정
os.chdir('/Users/seunghoonoh/woonmok.github.io')
TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
bot = telebot.TeleBot(TOKEN)

# [2] 실시간 데이터 수집 엔진
def update_system(news_text=None):
    try:
        # 날씨 수집 (진안군)
        w_res = requests.get("https://wttr.in/Jinan,KR?format=%t|%h", timeout=10)
        temp, humi = w_res.text.replace('+', '').split('|')
        
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # 전광판(날씨/습도) 교체
        content = re.sub(r'기온: .*? \| 습도: .*?<', f'기온: {temp} | 습도: {humi}<', content)

        # 지휘관님이 뉴스를 보냈을 경우에만 뉴스 섹션 업데이트
        if news_text:
            # 중앙 미션 바 업데이트
            content = re.sub(r'(<div class="mission-control".*?<span>)(.*?)(</span>)', rf'\1{news_text}\3', content, flags=re.DOTALL)
            # (추가: 필요시 여기서 뉴스 4개 구역을 순차적으로 교체하도록 확장 가능합니다)

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)

        # 본부(GitHub) 자동 전송
        os.system("git add . && git commit -m 'System Auto Sync' && git push origin main")
        return f"🌡️ 진안 현재: {temp} / {humi} 반영 완료"
    except Exception as e:
        return f"🚨 엔진 오류: {str(e)}"

# [3] 30분마다 스스로 돌아가는 '심장박동' 루프
def heartbeat():
    while True:
        print(f"⏰ {datetime.now()} - 정기 업데이트 시작")
        update_system()
        time.sleep(1800) # 1800초 = 30분

# [4] 텔레그램 명령 처리
@bot.message_handler(func=lambda m: True)
def on_telegram_command(message):
    res = update_system(message.text)
    bot.reply_to(message, f"🏛️ 지휘관님, 즉시 반영했습니다!\n{res}")

# 실행 시작
print("📡 [Master Engine] 가동 시작... 이제 지휘소는 자동으로 움직입니다.")
threading.Thread(target=heartbeat, daemon=True).start()
bot.polling()