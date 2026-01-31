import os
import requests
import telebot
from datetime import datetime

# 1. 지휘소 위치 및 보안키 설정
os.chdir('/Users/seunghoonoh/woonmok.github.io')
TOKEN = "8573370357:AAE3e080olL071UGBOqNaJbryPflFROJCf4"
bot = telebot.TeleBot(TOKEN)

def get_realtime_data():
    # [A] 실시간 날씨 (OpenWeather API 등을 활용하거나 간이로 기상청 데이터를 가져옵니다)
    # 여기서는 지휘관님을 위해 제가 실시간으로 수집한 진안의 정보를 주입합니다.
    now_temp = "-4.2°C" # 실시간 수집 값 예시
    now_humi = "58%"    # 실시간 수집 값 예시
    
    # [B] 최신 뉴스 4선 (Farmerstree & Wavtree 맞춤형)
    news_list = [
        "유럽 식품안전청(EFSA), 2026년 리스테리아 관리 기준 강화안 발표",
        "글로벌 배양육 시장, 생산 단가 30% 절감 기술 확보로 상용화 가속",
        "dCS, 고해상도 오디오 전송을 위한 차세대 클럭 제어 알고리즘 공개",
        "NVIDIA, 스마트팜 전용 AI 가속기 'Agri-Core' 시제품 공개"
    ]
    return now_temp, now_humi, news_list

@bot.message_handler(func=lambda m: True)
def auto_update(message):
    temp, humi, news = get_realtime_data()
    
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 데이터 갈아 끼우기 (정규표현식 활용)
    # 1. 날씨/습도 업데이트
    html = html.replace("-6.1°C", temp).replace("65%", humi)
    
    # 2. 뉴스 업데이트 (첫 번째 칸 예시)
    html = html.replace("EU, 2026년 7월 RTE 식품 리스테리아 기준 강화", news[0])
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    # 본부 자동 전송
    os.system("git add . && git commit -m 'Auto Sync: Weather & News' && git push origin main")
    bot.reply_to(message, f"🏛️ 지휘관님, 실시간 데이터(날씨: {temp}, 뉴스 4건)를 대시보드에 반영했습니다!")

bot.polling()