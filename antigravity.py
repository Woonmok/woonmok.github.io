import os, requests, telebot, re, time, threading
from datetime import datetime

# 1. 지휘소 경로 및 봇 설정
os.chdir('/Users/seunghoonoh/woonmok.github.io')
TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
bot = telebot.TeleBot(TOKEN)

def master_control_update(msg_text=None):
    try:
        # [A] 날씨 데이터 수집
        raw_temp, raw_humi = "N/A", "N/A"
        try:
            w_res = requests.get("https://wttr.in/Jinan,KR?format=%t|%h", timeout=10)
            if w_res.status_code == 200:
                raw_temp, raw_humi = w_res.text.replace('+', '').split('|')
        except: pass

        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # [B] 날씨 업데이트
        if raw_temp != "N/A":
            new_weather = f'기온: {raw_temp} | 습도: {raw_humi} (진안군)'
            content = re.sub(r'id="weather-info">.*?</div>', f'id="weather-info">{new_weather}</div>', content)

        # [C] 텔레그램 명령 처리
        if msg_text:
            # 1. To-Do 제어
            if msg_text.startswith("추가:"):
                task = msg_text.replace("추가:", "").strip()
                new_li = f'<li class="todo-item">{task}</li>\n            '
                content = content.replace('', new_li)
            elif msg_text.startswith("완료:"):
                task = msg_text.replace("완료:", "").strip()
                content = content.replace(f'<li class="todo-item">{task}</li>', f'<li class="todo-item completed">{task}</li>')
            elif msg_text.startswith("삭제:"):
                task = msg_text.replace("삭제:", "").strip()
                content = re.sub(rf'<li class="todo-item.*?">{re.escape(task)}</li>\n?', '', content)
            
            # 2. 상태 업데이트 (카테고리:값)
            elif ":" in msg_text or "：" in msg_text:
                sep = ":" if ":" in msg_text else "："
                cat, val = [x.strip() for x in msg_text.split(sep, 1)]
                
                # Global Biz
                if "곡물차" in cat:
                    content = re.sub(r'id="tea_status".*?>.*?</span>', f'id="tea_status" style="color: #00ff9d; font-weight:bold;">{val}</span>', content)
                elif "다이소" in cat or "Pick" in cat:
                    content = re.sub(r'id="daiso_status".*?>.*?</span>', f'id="daiso_status" style="color: #00ff9d; font-weight:bold;">{val}</span>', content)
                
                # AI Infra (브레인/팩토리/핸즈)
                elif "브레인" in cat or "Brain" in cat or "A100" in cat:
                    content = re.sub(r'id="srv_a_status".*?>.*?</span>', f'id="srv_a_status" style="color: #00ccff; font-weight:bold;">{val}</span>', content)
                elif "팩토리" in cat or "Factory" in cat or "L40S" in cat:
                    content = re.sub(r'id="srv_b_status".*?>.*?</span>', f'id="srv_b_status" style="color: #00ccff; font-weight:bold;">{val}</span>', content)
                elif "핸즈" in cat or "Hands" in cat or "6000" in cat:
                    content = re.sub(r'id="srv_c_status".*?>.*?</span>', f'id="srv_c_status" style="color: #00ccff; font-weight:bold;">{val}</span>', content)

        # [D] 저장 및 배포
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        os.system("git add . && git commit -m 'AI Infra hardware spec update' && git push origin main")
        return "🎯 지휘관님, 하드웨어 사양이 반영된 최신 전광판으로 업데이트했습니다."

    except Exception as e:
        return f"🚨 엔진 노이즈 발생: {str(e)}"

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    res = master_control_update(message.text)
    bot.reply_to(message, res)

print("📡 [The Wave Tree Project] 고성능 인프라 모드 가동...")
bot.polling()