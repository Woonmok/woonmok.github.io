import os, requests, telebot, re, time, threading
from datetime import datetime

# 1. 지휘소 설정
os.chdir('/Users/seunghoonoh/woonmok.github.io')
TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
bot = telebot.TeleBot(TOKEN)

def master_control_update(msg_text=None):
    try:
        # [A] 날씨 데이터 수집 (안정성 강화: 타임아웃 증가 및 예외 처리)
        raw_temp, raw_humi = "N/A", "N/A"
        try:
            w_res = requests.get("https://wttr.in/Jinan,KR?format=%t|%h", timeout=15)
            if w_res.status_code == 200:
                raw_temp, raw_humi = w_res.text.replace('+', '').split('|')
        except Exception as net_err:
            print(f"⚠️ 기상청 통신 지연 (할 일 업데이트는 계속 진행합니다): {net_err}")

        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # [B] 기본 업데이트: 날씨 (데이터가 있을 때만 반영)
        content = content.replace('<<header', '<header')
        if raw_temp != "N/A":
            weather_regex = r'<div>기온:.*?</div>'
            new_weather_div = f'<div>기온: {raw_temp} | 습도: {raw_humi}</div>'
            content = re.sub(weather_regex, new_weather_div, content, flags=re.DOTALL)

        # [C] 지능형 명령 분석
        if msg_text:
            if ":" in msg_text or "：" in msg_text:
                sep = ":" if ":" in msg_text else "："
                parts = msg_text.split(sep)
                if len(parts) >= 2:
                    category, value = parts[0].strip(), parts[1].strip()
                    if "곡물차" in category:
                        content = re.sub(r'<span id="tea_status">.*?</span>', f'<span id="tea_status">{value}</span>', content)
                    elif "다이소" in category or "Pick" in category:
                        content = re.sub(r'<span id="daiso_status">.*?</span>', f'<span id="daiso_status">{value}</span>', content)
                    elif "서버" in category:
                        content = re.sub(r'<span id="srv_c">.*?</span>', f'<span id="srv_c">{value}</span>', content)
            else:
                mission_regex = r'(<div class="mission-control".*?<span>)(.*?)(</span>)'
                content = re.sub(mission_regex, r'\1' + msg_text + r'\3', content, flags=re.DOTALL)

        # [D] 파일 저장 및 전송
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        os.system("git add . && git commit -m 'System Stability Update' && git push origin main")
        print(f"✅ {datetime.now()} - 업데이트 성공")
        return f"🌡️ 날씨: {raw_temp}/{raw_humi} (통신 상태에 따라 N/A 가능)"
        
    except Exception as e:
        print(f"❌ 시스템 내부 오류: {e}")
        return f"🚨 엔진 오류: {str(e)}"

def heartbeat():
    while True:
        master_control_update()
        time.sleep(1800)

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    status = master_control_update(message.text)
    bot.reply_to(message, f"🏛️ 전광판 반영 완료!\n🚩 명령: {message.text}\n{status}")

print("📡 [Master Control System v2.1] 가동 중...")
threading.Thread(target=heartbeat, daemon=True).start()
bot.polling()