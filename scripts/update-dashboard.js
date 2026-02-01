import axios from 'axios';
import * as cheerio from 'cheerio';
import Parser from 'rss-parser';
import { google } from 'googleapis';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs/promises';

dotenv.config();

// Configuration
// ABSOLUTE PATH to the data file on Desktop
const DATA_FILE_PATH = '/Users/seunghoonoh/Desktop/farmerstree-dashboard/src/data/dashboardData.json';

const SPREADSHEET_ID = '1Rq2GPvvNowK5WxEYk2wUJTAAEkXsFPpW0u2aFVWvIMk';
const SHEET_NAME = '시트1';
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

// 4 Sections Keywords
const KW_LISTERIA = ['Listeria mushroom safety', 'enoki mushroom recall', 'FDA mushroom guidelines'];
const KW_CULTURED = ['cultured meat trends 2025', 'lab grown meat regulatory', 'Upside Foods'];
const KW_AUDIO = ['Linn Audio', 'dCS Audio', 'Audio Research amp', 'Kondo Audio'];
const KW_COMPUTER = ['NVIDIA Blackwell', 'Apple M4 Server', 'Datacenter AI trends', 'H100 cluster'];

// Curated Content (Fallback & Filler)
const CURATED_LISTERIA = [
    {
        category: 'LISTERIA FREE',
        title: '미국 CDC: 팽이버섯 섭취 시 리스테리아 주의보... "반드시 익혀 드세요"',
        link: 'https://www.cdc.gov',
        pubDate: new Date().toISOString()
    },
    {
        category: 'LISTERIA FREE',
        title: 'Wavetree 스마트팜: 공기 중 오염 99.9% 차단 무균 재배 솔루션 도입',
        link: '#',
        pubDate: new Date().toISOString()
    },
    {
        category: 'LISTERIA FREE',
        title: 'FDA: "버섯 재배 시설 위생 가이드라인" 최신 개정판 발표',
        link: 'https://www.fda.gov',
        pubDate: new Date().toISOString()
    }
];

const CURATED_CULTURED = [
    {
        category: 'CULTURED MEAT',
        title: '2025 배양육 시장 전망: 2034년까지 연평균 15% 성장 예측',
        link: '#',
        pubDate: new Date().toISOString()
    },
    {
        category: 'CULTURED MEAT',
        title: 'Farmerstree R&D: 식물성 지지체 기반 배양육 원천 기술 확보',
        link: '#',
        pubDate: new Date().toISOString()
    },
    {
        category: 'CULTURED MEAT',
        title: '글로벌 규제 완화: 싱가포르 이어 미국, 영국도 배양육 판매 승인 확대',
        link: '#',
        pubDate: new Date().toISOString()
    }
];

const CURATED_AUDIO = [
    {
        category: 'AUDIO',
        title: 'Linn Sondek LP12: 2025 Bedrok™ 플린스, 아날로그의 정점을 찍다',
        link: 'https://www.linn.co.uk',
        pubDate: new Date().toISOString()
    },
    {
        category: 'AUDIO',
        title: 'dCS Vivaldi Apex: 디지털 오디오가 도달할 수 있는 투명함의 끝',
        link: 'https://dcsaudio.com',
        pubDate: new Date().toISOString()
    },
    {
        category: 'AUDIO',
        title: 'Audio Research 160M MKII: 진공관이 선사하는 압도적 공간감',
        link: '#',
        pubDate: new Date().toISOString()
    }
];

const CURATED_COMPUTER = [
    {
        category: 'COMPUTER',
        title: 'NVIDIA Blackwell B200: AI 추론 성능 30배 향상... 데이터센터의 혁명',
        link: 'https://www.nvidia.com',
        pubDate: new Date().toISOString()
    },
    {
        category: 'COMPUTER',
        title: 'Apple M4 Server: 2025년 하반기 가동, 프라이빗 클라우드 컴퓨팅의 시작',
        link: '#',
        pubDate: new Date().toISOString()
    },
    {
        category: 'COMPUTER',
        title: '운목 Tech Center: 차세대 H100 클러스터 및 자체 LLM 서버 구축 완료',
        link: '#',
        pubDate: new Date().toISOString()
    }
];

const WEATHER_URL = 'https://search.naver.com/search.naver?query=진안군부귀면날씨';

async function fetchWeather() {
    try {
        const { data } = await axios.get(WEATHER_URL);
        const $ = cheerio.load(data);
        const temp = $('.weather_info .temperature_text').first().text().replace('현재 온도', '').trim();
        const status = $('.weather_before_sort .weather').first().text().trim();
        const humidity = $('.summary_list .sort').filter((i, el) => $(el).text().includes('습도')).find('dd').text().trim();
        return { temp: temp || 'N/A', humidity: humidity || 'N/A', status: status || 'N/A' };
    } catch (error) {
        console.error('Weather Error:', error.message);
        return { temp: 'Error', humidity: 'Error', status: 'Error' };
    }
}

async function fetchRSS(keywords, categoryName) {
    const parser = new Parser();
    const articles = [];
    for (const keyword of keywords) {
        try {
            const feedUrl = `https://news.google.com/rss/search?q=${encodeURIComponent(keyword)}&hl=ko&gl=KR&ceid=KR:ko`;
            const feed = await parser.parseURL(feedUrl);
            feed.items.slice(0, 2).forEach(item => {
                articles.push({
                    category: categoryName,
                    title: item.title,
                    link: item.link,
                    pubDate: item.pubDate
                });
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

// Telegram: Radio DJ Style
async function sendTelegramBriefing(summary) {
    if (!TELEGRAM_BOT_TOKEN) return;
    const endpoint = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
    const message = `
🎧 *[운목 AI 큐레이터]*
운목님, 오늘의 기술 및 오디오 브리핑입니다.

${summary}

오늘도 영감 가득한 하루 되십시오. 
_BGM: Rachmaninoff Piano Concerto No.2_
  `.trim();

    try {
        await axios.post(endpoint, {
            chat_id: TELEGRAM_CHAT_ID,
            text: message,
            parse_mode: 'Markdown'
        });
        console.log('Telegram briefing sent.');
    } catch (error) {
        console.error('Telegram Error:', error.message);
    }
}

async function updateDashboard() {
    console.log(`[${new Date().toLocaleString()}] Starting Update...`);

    const weather = await fetchWeather();

    const rssListeria = await fetchRSS(KW_LISTERIA, 'LISTERIA FREE');
    const rssCultured = await fetchRSS(KW_CULTURED, 'CULTURED MEAT');
    const rssAudio = await fetchRSS(KW_AUDIO, 'AUDIO');
    const rssComputer = await fetchRSS(KW_COMPUTER, 'COMPUTER');

    // Mix curated + RSS, putting Curated first for quality
    const listListeria = deduplicate([...CURATED_LISTERIA, ...rssListeria]).slice(0, 5);
    const listCultured = deduplicate([...CURATED_CULTURED, ...rssCultured]).slice(0, 5);
    const listAudio = deduplicate([...CURATED_AUDIO, ...rssAudio]).slice(0, 5);
    const listComputer = deduplicate([...CURATED_COMPUTER, ...rssComputer]).slice(0, 5);

    const dashboardData = {
        lastUpdate: new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' }),
        weather: weather,
        news: [],
        sections: {
            listeria: listListeria,
            culturedMeat: listCultured,
            audio: listAudio,
            computer: listComputer
        }
    };

    // Flatten for ticker/news array
    dashboardData.news = [
        ...listListeria.slice(0, 1), ...listCultured.slice(0, 1),
        ...listAudio.slice(0, 1), ...listComputer.slice(0, 1),
        ...listListeria.slice(1), ...listCultured.slice(1) // fill rest
    ].slice(0, 10);

    await fs.writeFile(DATA_FILE_PATH, JSON.stringify(dashboardData, null, 2), 'utf-8');
    console.log('Dashboard Data Updated.');

    // Briefing: 1 Top item from each
    const briefingLines = [
        `1. *[LISTERIA]* ${listListeria[0].title}`,
        `2. *[CULTURED]* ${listCultured[0].title}`,
        `3. *[AUDIO]* ${listAudio[0].title}`,
        `4. *[COMPUTER]* ${listComputer[0].title}`
    ].join('\n');

    await sendTelegramBriefing(briefingLines);
}

// Single run for now, loop can be handled if script is persistent, but we need immediate result
async function main() {
    await updateDashboard();
}

main();
