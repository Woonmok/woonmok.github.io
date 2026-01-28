
import os
import sys

# Add scripts dir to path to import director
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from digital_signage_director import fetch_weather, send_telegram, push_to_github, get_timestamp

def run():
    print(f"[{get_timestamp()}] --- Final Verification Start ---")
    
    # Check Env
    if not os.environ.get("SERPER_API_KEY"):
        print("Error: SERPER_API_KEY not found in environment.")
    if not os.environ.get("TELEGRAM_BOT_TOKEN"):
        print("Error: TELEGRAM_BOT_TOKEN not found in environment.")
        
    # 1. Test Weather (New Logic)
    print("1. Testing Weather Fetch...")
    weather = fetch_weather()
    print(f"   Result: {weather}")
    
    if not weather:
        print("   Warning: Weather returned None.")
        weather = {"temp": "확인필요", "humidity": "확인필요"}
        
    temp = weather.get('temp', 'N/A')
    humidity = weather.get('humidity', 'N/A')

    # 2. Send Telegram Report (STRICT)
    print("2. Sending Telegram Report...")
    # "[Farmerstree 현황] 진안군 진안읍 기온: -8.X°C / 습도: XX% / 할일: 5건"
    msg = f"[Farmerstree 현황] 진안군 진안읍 기온: {temp} / 습도: {humidity} / 할일: 자료정리 등"
    
    send_telegram(msg)
    
    # 3. Push Code
    print("3. Pushing changes to GitHub...")
    # We call the function from director which runs git commands
    try:
        push_to_github()
    except Exception as e:
        print(f"Git Push Error (might need manual push if no creds): {e}")

    print(f"[{get_timestamp()}] --- Verification Complete ---")

if __name__ == "__main__":
    run()
