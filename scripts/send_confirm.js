import axios from 'axios';
const TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;

async function send() {
    await axios.post(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
        chat_id: CHAT_ID,
        text: `✅ 미션 추가 요청 확인.\n\n1. 맥미니 대시보드 연동 테스트\n2. A100 서버 상태 모니터링\n\n대시보드에 즉시 반영했습니다.`
    });
    console.log('Confirmation sent');
}
send();
