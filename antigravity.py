운목 지휘관님, 이 코드는 기존에 사용하시던 antigravity.py 엔진의 핵심 부품입니다.

기존 코드를 부분적으로 수정하면 배선이 꼬일 수 있으니, 제가 날씨 업데이트 + 할 일 업데이트 + 비즈니스 상태 업데이트를 하나로 통합한 **'풀 옵션 엔진'**을 다시 조립해 드립니다.

🛠️ 통합 관제 엔진 (antigravity.py) 최종본
기존 antigravity.py의 내용을 모두 지우고, 아래 코드를 통째로 복사해서 덮어쓰기 하세요. 가장 안전하고 확실한 방법입니다.

Python

import os, requests, telebot, re, time, threading
from datetime import datetime

# 1. 지휘소 경로 및 봇 설정
os.chdir('/Users/seunghoonoh/woonmok.github.io')
TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
bot = telebot.TeleBot(TOKEN)

def master_control_update(msg_text=None):
    try:
        # [A] 기본 날씨 데이터 수집
        w_res = requests.get("https://wttr.in/Jinan,KR?format=%t|%h", timeout=10)
        raw_temp, raw_humi = w_res.text.replace('+', '').split('|')
        
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # [B] 기본 업데이트: 날씨 및 오타 수정
        content = content.replace('<<header', '<header')
        weather_regex = r'<div>기온:.*?</div>'
        new_weather_div = f'<div>기온: {raw_temp} | 습도: {raw_humi}</div>'
        content = re.sub(weather_regex, new_weather_div, content, flags=re.DOTALL)

        # [C] 지능형 명령 분석 (텔레그램 메시지가 있을 경우)
        if msg_text:
            # 1. 카테고리 업데이트 (예: "곡물차: 완료" 라고 보냈을 때)
            if ":" in msg_text or "：" in msg_text:
                parts = msg_text.split(':') if ":" in msg_text else msg_text.split("：")
                category, value = parts[0].strip(), parts[1].strip()
                
                if "곡물차" in category:
                    content = re.sub(r'<span id="tea_status">.*?</span>', f'<span id="tea_status">{value}</span>', content)
                elif "다이소" in category or "Pick" in category:
                    content = re.sub(r'<span id="daiso_status">.*?</span>', f'<span id="daiso_status">{value}</span>', content)
                elif "서버" in category:
                    content = re.sub(r'<span id="srv_c">.*?</span>', f'<span id="srv_c">{value}</span>', content)
            
            # 2. 일반 할 일 업데이트 (중앙 미션 바)
            else:
                mission_regex = r'(<div class="mission-control".*?<span>)(.*?)(</span>)'
                content = re.sub(mission_regex, rf'\1{msg_text}\3', content, flags=re.DOTALL)

        # [D] 파일 저장 및 서버 전송
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        os.system("git add . && git commit -m 'Master Control Update' && git push origin main")
        print(f"✅ {datetime.now()} - 지휘소 업데이트 완료")
        return f"🌡️ {raw_temp}/{raw_humi} 반영 완료"
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return f"🚨 엔진 오류: {str(e)}"

# 백그라운드 자동 갱신 (30분 주기)
def heartbeat():
    while True:
        master_control_update()
        time.sleep(1800)

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    status = master_control_update(message.text)
    bot.reply_to(message, f"🏛️ 지휘관님, 명령을 전광판에 즉시 반영했습니다!\n\n🚩 내용: {message.text}\n{status}")

print("📡 [Master Control System] 가동... 지휘관님의 명령을 기다립니다.")
threading.Thread(target=heartbeat, daemon=True).start()
bot.polling()