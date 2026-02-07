import axios from 'axios';
import * as cheerio from 'cheerio';
import Parser from 'rss-parser';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs/promises';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// --- CONFIGURATION ---
const TARGET_HTML_PATH = '/Users/seunghoonoh/Documents/digital_signage.html';
const TODO_FILE_PATH = path.join(__dirname, '..', 'todo_storage.json');

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

// Keywords
const KW_LISTERIA = ['Listeria mushroom safety', 'enoki mushroom recall', 'FDA mushroom guidelines'];
const KW_CULTURED = ['cultured meat trends 2025', 'lab grown meat regulatory', 'Upside Foods'];
const KW_AUDIO = ['Linn Audio', 'dCS Audio', 'Audio Research amp', 'Kondo Audio'];
const KW_COMPUTER = ['NVIDIA Blackwell', 'Apple M4 Server', 'Datacenter AI trends', 'H100 cluster'];

// Fallback Curated
const CURATED = {
  listeria: [
    { category: 'LISTERIA FREE', title: '미국 CDC: 팽이버섯 섭취 시 리스테리아 주의보... "반드시 익혀 드세요"', pubDate: new Date().toISOString() },
    { category: 'LISTERIA FREE', title: 'Wavetree 스마트팜: 공기 중 오염 99.9% 차단 무균 재배 솔루션 도입', pubDate: new Date().toISOString() },
    { category: 'LISTERIA FREE', title: 'FDA: "버섯 재배 시설 위생 가이드라인" 최신 개정판 발표', pubDate: new Date().toISOString() }
  ],
  cultured: [
    { category: 'CULTURED MEAT', title: '2025 배양육 시장 전망: 연평균 15% 성장 예측', pubDate: new Date().toISOString() },
    { category: 'CULTURED MEAT', title: 'Farmerstree R&D: 식물성 지지체 기반 배양육 원천 기술 확보', pubDate: new Date().toISOString() }
  ],
  audio: [
    { category: 'AUDIO', title: 'Linn Sondek LP12: 2025 Bedrok™ 플린스 출시', pubDate: new Date().toISOString() },
    { category: 'AUDIO', title: 'dCS Vivaldi Apex: 디지털 오디오의 정점', pubDate: new Date().toISOString() }
  ],
  computer: [
    { category: 'COMPUTER', title: 'NVIDIA Blackwell B200: AI 추론 성능 30배 향상', pubDate: new Date().toISOString() },
    { category: 'COMPUTER', title: 'Apple M4 Server: 2025년 하반기 가동 예정', pubDate: new Date().toISOString() }
  ]
};

// State
let globalData = {
  listeria: [],
  cultured: [],
  audio: [],
  computer: [],
  lastUpdate: 'Initializing...'
};

let lastUpdateId = 0; // Telegram offset

// --- FILE I/O ---
async function loadTodos() {
  try {
    const data = await fs.readFile(TODO_FILE_PATH, 'utf-8');
    return JSON.parse(data);
  } catch (e) {
    return { tasks: [], lastMsgId: 0 };
  }
}

async function saveTodos(data) {
  await fs.writeFile(TODO_FILE_PATH, JSON.stringify(data, null, 2), 'utf-8');
}

// --- TELEGRAM LOGIC ---
async function checkTelegramUpdates() {
  if (!TELEGRAM_BOT_TOKEN) return;

  try {
    // 1. Get updates with offset
    const response = await axios.get(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates`, {
      params: {
        offset: lastUpdateId + 1,
        timeout: 0 // Short poll for now, loop handles delay
      }
    });

    const updates = response.data.result;
    if (!updates || updates.length === 0) return;

    let todoData = await loadTodos();
    let tasksChanged = false;

    for (const update of updates) {
      lastUpdateId = update.update_id;
      const msg = update.message;

      // Only process text messages from the specific user
      if (msg && String(msg.chat.id) === TELEGRAM_CHAT_ID && msg.text) {
        const text = msg.text.trim();

        // Simple logic: treat ANY text as a TODO request if it looks like one, or just add it.
        // The user said: "이거 할 일에 추가해줘" -> Add to TODO.
        // We'll treat all messages as potential TODOs or simplified commands.
        // For better UX, let's look for intentions or just add everything for now as strict "Secretary" mode.

        // 명령어 파싱
        if (text.startsWith('/')) {
          // 슬래시 명령어 처리
          if (text === '/start') {
            await axios.post(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
              chat_id: TELEGRAM_CHAT_ID,
              text: `👋 안녕하세요!\n\n*할일 관리 명령어 안내*\n\n* /start - 시작 메시지 및 명령어 안내\n* /todo 또는 /목록 - 할일 목록 보기\n* /help - 도움말\n\n*추가 명령어*\n- 추가: 작업명  → 할일 추가\n- 목록  → 할일 목록 보기\n- 완료: 1  → ID로 완료 처리\n- 삭제: 1  → ID로 삭제\n- 할일: 1. xxx, 2. yyy  → 할일 전체 덮어쓰기\n\n메시지로 바로 할일을 보내도 추가됩니다!`,
              parse_mode: 'Markdown'
            });
            continue;
          }
          if (text === '/todo' || text === '/목록') {
            const list = todoData.tasks.length === 0 ? '할일이 없습니다.' : todoData.tasks.map((t, i) => `${i+1}. ${t.text}`).join('\n');
            await axios.post(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
              chat_id: TELEGRAM_CHAT_ID,
              text: `*할일 목록*\n${list}`,
              parse_mode: 'Markdown'
            });
            continue;
          }
          if (text === '/help') {
            await axios.post(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
              chat_id: TELEGRAM_CHAT_ID,
              text: `*도움말*\n\n- 할일 추가: 아무 메시지나 보내기\n- "추가: 작업명"\n- "목록"\n- "완료: 1"\n- "삭제: 1"\n- "할일: 1. xxx, 2. yyy" (전체 덮어쓰기)\n\n* /start - 안내\n* /todo 또는 /목록 - 할일 목록\n* /help - 도움말`,
              parse_mode: 'Markdown'
            });
            continue;
          }
          // 기타 슬래시 명령 무시
          continue;
        }

        // 기존 텍스트 명령어 처리
        if (/^추가[:：]/.test(text)) {
          // 추가: 작업명
          const todoText = text.replace(/^추가[:：]/, '').trim();
          if (todoText) {
            todoData.tasks.unshift({ id: Date.now(), text: todoText, date: new Date().toISOString() });
            if (todoData.tasks.length > 5) todoData.tasks = todoData.tasks.slice(0, 5);
            tasksChanged = true;
            await axios.post(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
              chat_id: TELEGRAM_CHAT_ID,
              text: `✅ 할일 추가: ${todoText}`
            });
          }
          continue;
        }
        if (/^목록$/.test(text)) {
          const list = todoData.tasks.length === 0 ? '할일이 없습니다.' : todoData.tasks.map((t, i) => `${i+1}. ${t.text}`).join('\n');
          await axios.post(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
            chat_id: TELEGRAM_CHAT_ID,
            text: `*할일 목록*\n${list}`,
            parse_mode: 'Markdown'
          });
          continue;
        }
        if (/^완료[:：]\s*([0-9]+)$/.test(text)) {
          const idx = parseInt(text.match(/^완료[:：]\s*([0-9]+)$/)[1], 10) - 1;
          if (todoData.tasks[idx]) {
            const done = todoData.tasks.splice(idx, 1)[0];
            tasksChanged = true;
            await axios.post(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
              chat_id: TELEGRAM_CHAT_ID,
              text: `✅ 완료 처리: ${done.text}`
            });
          } else {
            await axios.post(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
              chat_id: TELEGRAM_CHAT_ID,
              text: `해당 번호의 할일이 없습니다.`
            });
          }
          continue;
        }
        if (/^삭제[:：]\s*([0-9]+)$/.test(text)) {
          const idx = parseInt(text.match(/^삭제[:：]\s*([0-9]+)$/)[1], 10) - 1;
          if (todoData.tasks[idx]) {
            const del = todoData.tasks.splice(idx, 1)[0];
            tasksChanged = true;
            await axios.post(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
              chat_id: TELEGRAM_CHAT_ID,
              text: `🗑️ 삭제 완료: ${del.text}`
            });
          } else {
            await axios.post(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
              chat_id: TELEGRAM_CHAT_ID,
              text: `해당 번호의 할일이 없습니다.`
            });
          }
          continue;
        }
        if (/^할일[:：]/.test(text)) {
          // 할일: 1. xxx, 2. yyy
          const items = text.replace(/^할일[:：]/, '').split(/,|\n/).map(s => s.replace(/^[0-9]+\.?\s*/, '').trim()).filter(Boolean);
          todoData.tasks = items.map((t, i) => ({ id: Date.now() + i, text: t, date: new Date().toISOString() })).slice(0, 5);
          tasksChanged = true;
          await axios.post(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
            chat_id: TELEGRAM_CHAT_ID,
            text: `✅ 할일 목록이 새로 저장되었습니다.`
          });
          continue;
        }

        // 그 외 메시지는 할일로 추가
        todoData.tasks.unshift({
          id: Date.now(),
          text: text,
          date: new Date().toISOString()
        });
        if (todoData.tasks.length > 5) todoData.tasks = todoData.tasks.slice(0, 5);
        tasksChanged = true;
        await axios.post(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
          chat_id: TELEGRAM_CHAT_ID,
          text: `✅ 접수했습니다. 대시보드에 반영 완료!\n("${text}")`
        });
        console.log(`Added TODO: ${text}`);
      }
    }

    if (tasksChanged) {
      await saveTodos(todoData);
      // Immediate Dashboard Update using existing globalData + new Todos
      await generateAndWriteHTML(globalData, todoData.tasks);
    }

  } catch (e) {
    console.error('Telegram Poll Error:', e.message);
  }
}

async function sendBriefing(summary) {
  if (!TELEGRAM_BOT_TOKEN) return;
  const message = `
🎙 *[운목 AI 큐레이터]*
운목님, 30분 정기 브리핑입니다.

${summary}

_BGM: Rachmaninoff Piano Concerto No.2_
  `.trim();

  try {
    await axios.post(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
      chat_id: TELEGRAM_CHAT_ID,
      text: message,
      parse_mode: 'Markdown'
    });
    console.log('Briefing sent.');
  } catch (e) {
    console.error('Briefing Error:', e.message);
  }
}

// --- DATA FETCHING ---
async function fetchRSS(keywords, categoryName) {
  const parser = new Parser();
  const articles = [];
  for (const keyword of keywords) {
    try {
      const feedUrl = `https://news.google.com/rss/search?q=${encodeURIComponent(keyword)}&hl=ko&gl=KR&ceid=KR:ko`;
      const feed = await parser.parseURL(feedUrl);
      feed.items.slice(0, 2).forEach(item => {
        articles.push({ category: categoryName, title: item.title, pubDate: item.pubDate });
      });
    } catch (e) { /* ignore */ }
  }
  return articles;
}

function deduplicate(items) {
  const seen = new Set();
  return items.filter(item => {
    const normalized = item.title.replace(/\s+/g, '').toLowerCase();
    if (seen.has(normalized)) return false;
    seen.add(normalized);
    return true;
  });
}

// --- HTML GENERATOR ---
async function generateAndWriteHTML(newsData, todos) {
  const { listeria, cultured, audio, computer, lastUpdate } = newsData;

  // Prepare TODO HTML
  const todoHTML = todos.length > 0
    ? todos.map(t => `<li class="todo-item">${t.text} <span class="todo-time">${new Date(t.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span></li>`).join('')
    : `<li class="todo-empty">오늘의 새로운 도전을 입력해주세요</li>`;

  // Standard Section HTML
  const sectionHTML = (title, items, icon) => `
    <div class="section glass-panel">
      <div class="header">
        <span class="icon">${icon}</span>
        <h2>${title}</h2>
      </div>
      <div class="news-list">
        ${items.map(item => `
          <div class="news-item">
            <h3>${item.title}</h3>
            <div class="meta"><span>${new Date(item.pubDate).toLocaleDateString()}</span></div>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  const html = `
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Wavetree Digital Signage</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { 
      background: url('https://images.unsplash.com/photo-1470770841072-f978cf4d019e?q=80&w=2070&auto=format&fit=crop') no-repeat center center fixed; 
      background-size: cover;
      color: white; 
      font-family: 'Inter', system-ui, sans-serif; 
      overflow: hidden; 
      height: 100vh; 
      display: flex; 
      flex-direction: column; 
    }
    
    header {
      height: 90px; padding: 0 40px; display: flex; justify-content: space-between; align-items: center;
      background: rgba(0,0,0,0.3); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(255,255,255,0.1); z-index: 10;
    }
    h1 { font-size: 26px; font-weight: 800; letter-spacing: 2px; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
    .status-bar { display: flex; gap: 20px; align-items: center; }
    .time { font-family: monospace; font-size: 24px; font-weight: bold; }

    main { 
      flex: 1; padding: 25px; 
      display: grid; 
      grid-template-columns: 1.2fr 1fr 1fr 1fr 1fr; /* 5 Columns: TODO is wider */
      gap: 20px; 
    }
    
    /* Shared Glass Style */
    .glass-panel { 
      border-radius: 16px; 
      border: 1px solid rgba(255,255,255,0.15); 
      background: rgba(0, 0, 0, 0.45); 
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
      display: flex; flex-direction: column;
      overflow: hidden;
    }

    /* TODO Section Specifics */
    .todo-section { 
      grid-column: 1 / 2; /* First column */
      border: 1px solid rgba(255, 215, 0, 0.3); /* Gold hint */
      background: rgba(0, 0, 0, 0.6);
    }
    .todo-section .header h2 { color: #ffd700; }
    .todo-item { 
      padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); 
      font-size: 16px; font-weight: 600; list-style: none;
      display: flex; justify-content: space-between; align-items: center;
    }
    .todo-time { font-size: 12px; color: #888; font-weight: 400; }
    .todo-empty { padding: 20px; color: #888; font-style: italic; text-align: center; }
    
    /* Standard Sections */
    .section { }
    .header { padding: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; gap: 10px; }
    .header h2 { font-size: 16px; font-weight: 700; color: #fff; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    .icon { font-size: 20px; }
    
    .news-list { flex: 1; overflow-y: auto; padding: 10px; display: flex; flex-direction: column; gap: 10px; }
    .news-list::-webkit-scrollbar { display: none; }
    .news-item { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .news-item:last-child { border-bottom: none; }
    .news-item h3 { font-size: 14px; line-height: 1.4; color: #eee; margin-bottom: 5px; }
    .meta { font-size: 11px; color: #aaa; }

    footer { height: 35px; background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(10px); display: flex; align-items: center; overflow: hidden; white-space: nowrap; border-top: 1px solid rgba(255,255,255,0.1); }
    .marquee { display: flex; animation: marquee 60s linear infinite; gap: 50px; padding-left: 20px; }
    .ticker-item { font-size: 13px; color: #eee; display: flex; align-items: center; gap: 8px; }
    .dot { width: 5px; height: 5px; background: #34d399; border-radius: 50%; }

    @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
  </style>
</head>
<body>
  <header>
    <h1>WAVETREE & FARMERSTREE</h1>
    <div class="status-bar">
      <div class="time" id="clock">${new Date().toLocaleTimeString('en-US', { hour12: false })}</div>
    </div>
  </header>
  
  <main>
    <!-- 1. TODO SECTION -->
    <div class="todo-section glass-panel">
      <div class="header">
        <span class="icon">✨</span>
        <h2>TODAY'S MISSION</h2>
      </div>
      <div class="news-list">
        ${todoHTML}
      </div>
    </div>

    <!-- 2. LISTERIA -->
    ${sectionHTML('LISTERIA FREE', listeria, '🔬')}
    
    <!-- 3. CULTURED MEAT -->
    ${sectionHTML('CULTURED MEAT', cultured, '🧫')}
    
    <!-- 4. AUDIO -->
    ${sectionHTML('HIGH-END AUDIO', audio, '🎧')}
    
    <!-- 5. COMPUTER -->
    ${sectionHTML('COMPUTER & AI', computer, '💻')}
  </main>

  <footer>
    <div class="marquee">
      ${[...listeria, ...cultured, ...audio, ...computer].map(i => `
        <span class="ticker-item"><span class="dot"></span>[${i.category}] ${i.title}</span>
      `).join('')}
    </div>
  </footer>

  <script>
    setInterval(() => {
      document.getElementById('clock').innerText = new Date().toLocaleTimeString('en-US', { hour12: false });
    }, 1000);
    // Reload every 10s to reflect TODOs instantly if file updated on disk
    setTimeout(() => window.location.reload(), 10000);
  </script>
</body>
</html>
  `;

  // Write File
  try {
    await fs.writeFile(TARGET_HTML_PATH, html, 'utf-8');
    console.log(`Updated HTML at ${new Date().toLocaleTimeString()}`);
  } catch (err) {
    const desktopPath = path.join(process.env.HOME, 'Desktop', 'digital_signage.html');
    await fs.writeFile(desktopPath, html, 'utf-8');
    console.log(`Updated HTML (Desktop Fallback) at ${new Date().toLocaleTimeString()}`);
  }
}

// --- MAIN LOOP ---
async function updateContent() {
  console.log('Fetching News Content...');
  const rssListeria = await fetchRSS(KW_LISTERIA, 'LISTERIA FREE');
  const rssCultured = await fetchRSS(KW_CULTURED, 'CULTURED MEAT');
  const rssAudio = await fetchRSS(KW_AUDIO, 'AUDIO');
  const rssComputer = await fetchRSS(KW_COMPUTER, 'COMPUTER');

  // Update Global Data
  globalData.listeria = deduplicate([...CURATED.listeria, ...rssListeria]).slice(0, 5);
  globalData.cultured = deduplicate([...CURATED.cultured, ...rssCultured]).slice(0, 5);
  globalData.audio = deduplicate([...CURATED.audio, ...rssAudio]).slice(0, 5);
  globalData.computer = deduplicate([...CURATED.computer, ...rssComputer]).slice(0, 5);
  globalData.lastUpdate = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });

  const todos = await loadTodos();
  await generateAndWriteHTML(globalData, todos.tasks);

  // Create summary for briefing
  const summary = [
    `1. *[TODO]* ${todos.tasks.length > 0 ? todos.tasks[0].text : '새로운 도전 대기 중'}`,
    `2. *[LISTERIA]* ${globalData.listeria[0].title}`,
    `3. *[CULTURED]* ${globalData.cultured[0].title}`,
    `4. *[AUDIO]* ${globalData.audio[0].title}`,
    `5. *[COMPUTER]* ${globalData.computer[0].title}`
  ].join('\n');

  // await sendBriefing(summary); // Disabled to prevent duplicate/spamming. Handled by Python Director.
}

// Init
(async () => {
  // Initial Fetch
  await updateContent();

  // Loop 1: Check Telegram every 5 seconds (Fast Interactive)
  setInterval(checkTelegramUpdates, 5000);

  // Loop 2: Update Content every 30 minutes (RSS Refresh)
  setInterval(updateContent, 30 * 60 * 1000);
})();
