import os
import telebot # 이 부품이 필요합니다: pip install pyTelegramBotAPI
import re

# 1. 지휘소 위치 설정
os.chdir('/Users/seunghoonoh/woonmok.github.io')

TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: message.text.startswith("과제:"))
def update_task(message):
    new_tasks = message.text.replace("과제:", "").strip()
    
    # [1] index.html 업데이트 (웹 대시보드)
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 정규표현식으로 미션 바 내용만 쏙 교체
    pattern = r'(<div class="mission-control".*?<span>)(.*?)(</span>)'
    new_content = re.sub(pattern, rf'\1{new_tasks}\3', content, flags=re.DOTALL)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # [2] 본부 전송 (GitHub Push)
    os.system("git add . && git commit -m 'Telegram Update' && git push origin main")
    
    bot.reply_to(message, f"🏛️ 지휘관님, 전략 과제를 업데이트했습니다!\n\n📍 변경 내용: {new_tasks}\n🌐 웹사이트 확인: https://woonmok.github.io")

print("📡 안티그래비티 비서가 운목님의 명령을 기다리고 있습니다...")
bot.polling()