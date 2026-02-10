import fs from 'fs';
import path from 'path';
import axios from 'axios';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;

if (!TOKEN || !CHAT_ID) {
  console.error('TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is missing.');
  process.exit(1);
}

const dashboardPath = path.resolve(__dirname, '..', 'dashboard_data.json');

let dashboard;
try {
  dashboard = JSON.parse(fs.readFileSync(dashboardPath, 'utf-8'));
} catch (error) {
  console.error('Failed to read dashboard_data.json:', error.message || error);
  process.exit(1);
}

const todos = Array.isArray(dashboard.todo_list) ? dashboard.todo_list : [];
if (!todos.length) {
  console.log('No todos found.');
}

const lines = todos.map((t) => {
  const status = t.completed ? '✅' : '⭕';
  const text = String(t.text || '').trim();
  const idText = typeof t.id !== 'undefined' ? `[#${t.id}] ` : '';
  return `${status} ${idText}${text}`.trim();
});

const header = '📋 [오늘의 할일 업데이트]';
const body = lines.length ? lines.join('\n') : '할일이 없습니다.';
const message = `${header}\n\n${body}`;

try {
  await axios.post(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
    chat_id: CHAT_ID,
    text: message
  });
  console.log('Telegram todo update sent.');
} catch (error) {
  console.error('Telegram send failed:', error.message || error);
  process.exit(1);
}
