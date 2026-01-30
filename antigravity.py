import os
import telebot # pip3 install pyTelegramBotAPI
import re

# 1. 지휘소 위치 강제 설정
os.chdir('/Users/seunghoonoh/woonmok.github.io')

TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
bot = telebot.TeleBot(TOKEN)

# [비서 모드] 암호 없이 모든 메시지를 '과제'로 인식합니다.
@bot.message_handler(content_types=['text'])
def handle_mission(message):
    new_tasks = message.text.strip()
    
    # [1] index.html 업데이트 (웹 전광판 수정)
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 미션 컨트롤 바의 <span> 안쪽 내용만 교체하는 정밀 회로
        pattern = r'(<div class="mission-control".*?<span>)(.*?)(</span>)'
        if re.search(pattern, content, flags=re.DOTALL):
            new_content = re.sub(pattern, rf'\1{new_tasks}\3', content, flags=re.DOTALL)
            
            with open('index.html', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # [2] 본부 전송 (GitHub 자동 Push)
            os.system("git add . && git commit -m 'Telegram Update: New Mission' && git push origin main")
            
            bot.reply_to(message, f"🏛️ 지휘관님, 명을 받들었습니다!\n\n🚩 전략 과제 갱신 완료:\n{new_tasks}\n\n🌐 대시보드 전광판을 확인해 주십시오.")
        else:
            bot.reply_to(message, "⚠️ 지휘관님, 대시보드에서 '미션 바'를 찾을 수 없습니다. index.html의 레이아웃을 확인해 주세요.")
            
    except Exception as e:
        bot.reply_to(message, f"🚨 보고드립니다! 업데이트 중 오류 발생: {str(e)}")

print("📡 [Smart 2.0] 지휘관님의 모든 말씀을 전략 과제로 기록할 준비가 되었습니다...")
bot.polling()