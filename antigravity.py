import os, requests, telebot, re, time, threading
from datetime import datetime

# 1. 지휘소 설정
os.chdir('/Users/seunghoonoh/woonmok.github.io')
TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
bot = telebot.TeleBot(TOKEN)

def master_control_update(msg_text=None):
    try:
        # [A] 날씨 수집
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

        # [C] 텔레그램 명령 처리 (To-Do 및 상태 제어)
        if msg_text:
            # 1. To-Do 추가 (예: "추가: 시온마켓 샘플 챙기기")
            if msg_text.startswith("추가:"):
                task = msg_text.replace("추가:", "").strip()
                new_li = f'<li class="todo-item">{task}</li>\n    '
                content = content.replace('', new_li)

            # 2. To-Do 완료 (예: "완료: 미국 출장 준비")
            elif msg_text.startswith("완료:"):
                task = msg_text.replace("완료:", "").strip()
                content = content.replace(f'<li class="todo-item">{task}</li>', f'<li class="todo-item completed">{task}</li>')

            # 3. To-Do 삭제 (예: "삭제: 옛날 과제")
            elif msg_text.startswith("삭제:"):
                task = msg_text.replace("삭제:", "").strip()
                content = re.sub(rf'<li class="todo-item.*?">{task}</li>\n?', '', content)

            # 4. To-Do 초기화 (예: "리스트 초기화")
            elif msg_text == "리스트 초기화":
                content = re.sub(r'.*?', 
                                '\n    ', content, flags=re.DOTALL)

            # 5. 기존 비즈니스 상태 업데이트 (예: "곡물차: 완료")
            elif ":" in msg_text:
                cat, val = [x.strip() for x in msg_text.split(":")]
                if "곡물차" in cat:
                    content = re.sub(r'id="tea_status".*?>.*?</span>', f'id="tea_status" style="color: #00ff9d;">{val}</span>', content)
                elif "다이소" in cat or "Pick" in cat:
                    content = re.sub(r'id="daiso_status".*?>.*?</span>', f'id="daiso_status" style="color: #00ff9d;">{val}</span>', content)
                elif "브레인" in cat or "Brain" in cat:
    content = re.sub(r'id="srv_a_status".*?>.*?</span>', f'id="srv_a_status" style="color: #00ccff;">{val}</span>', content)
elif "팩토리" in cat or "Factory" in cat:
    content = re.sub(r'id="srv_b_status".*?>.*?</span>', f'id="srv_b_status" style="color: #00ccff;">{val}</span>', content)
elif "핸즈" in cat or "Hands" in cat or "서버C" in cat:
    content = re.sub(r'id="srv_c_status".*?>.*?</span>', f'id="srv_c_status" style="color: #00ccff;">{val}</span>', content)
        # [D] 저장 및 배포
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        os.system("git add . && git commit -m 'Tactical Update' && git push origin main")
        return "🎯 명령이 전광판에 즉시 반영되었습니다."

    except Exception as e:
        return f"🚨 오류: {str(e)}"

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    res = master_control_update(message.text)
    bot.reply_to(message, res)

threading.Thread(target=lambda: (time.sleep(1800) or master_control_update()) , daemon=True).start()
bot.polling()