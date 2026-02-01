import axios from 'axios';
import * as cheerio from 'cheerio';
import Parser from 'rss-parser';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const DASHBOARD_DATA_PATH = path.join(__dirname, '../src/data/dashboardData.json');

const KEYWORDS = [
    '리스테리아', // Broaden search to get more results
    '배양육',
    'High End Audio'
];

async function fetchWeather() {
    try {
        const url = 'https://search.naver.com/search.naver?query=진안군부귀면날씨';
        const { data } = await axios.get(url);
        const $ = cheerio.load(data);

        // Naver Weather Selectors (Subject to change, need robust fallback)
        const temp = $('.temperature_text').first().text().replace('현재 온도', '').trim();
        const status = $('.weather_before_sort .weather').first().text().trim();
        // Humidity is often in a list
        let humidity = '';
        $('.summary_list .sort').each((i, el) => {
            if ($(el).text().includes('습도')) {
                humidity = $(el).find('dd').text().trim();
            }
        });

        // Fallback for English speakers / Formatting
        return {
            temp: temp || 'N/A',
            humidity: humidity || '50%',
            status: status || 'Clear'
        };
    } catch (error) {
        console.error('Weather fetch failed:', error.message);
        return { temp: 'N/A', humidity: 'N/A', status: 'N/A' };
    }
}

async function fetchNews(keyword) {
    const parser = new Parser();
    const encoded = encodeURIComponent(keyword);
    const rssUrl = `https://news.google.com/rss/search?q=${encoded}&hl=ko&gl=KR&ceid=KR:ko`;

    try {
        const feed = await parser.parseURL(rssUrl);
        return feed.items.map(item => ({
            category: keyword,
            title: item.title,
            link: item.link,
            pubDate: item.pubDate
        }));
    } catch (error) {
        console.error(`News fetch failed for ${keyword}:`, error.message);
        return [];
    }
}

async function main() {
    console.log('Fetching real-time data...');

    // 1. Weather
    const weather = await fetchWeather();
    console.log('Weather:', weather);

    // 2. News
    let allNews = [];

    // Specific High End Audio Brands
    const audioKeywords = ['Linn Audio', 'dCS Audio', 'Wilson Audio'];
    const audioNewsPromises = audioKeywords.map(k => fetchNews(k));
    const audioNewsResults = await Promise.all(audioNewsPromises);
    const audioNews = audioNewsResults.flat();

    // Listeria & Cultured Meat
    const listeriaNews = await fetchNews('리스테리아');
    const culturedMeatNews = await fetchNews('배양육');

    // Jinan News
    const jinanNews = await fetchNews('진안군');

    // AI/Computer News (Filling the gap)
    const aiNews = await fetchNews('인공지능 기술');

    // Combine for ticker
    allNews = [...listeriaNews, ...culturedMeatNews, ...audioNews, ...jinanNews, ...aiNews];

    // 3. Construct Data
    const dashboardData = {
        lastUpdate: new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' }),
        weather: weather,
        news: allNews.slice(0, 15), // Top 15 for ticker
        sections: {
            listeria: listeriaNews.slice(0, 5),
            culturedMeat: culturedMeatNews.slice(0, 5),
            audio: audioNews.slice(0, 5),
            computer: aiNews.slice(0, 5)
        }
    };

    // 4. Save
    await fs.writeFile(DASHBOARD_DATA_PATH, JSON.stringify(dashboardData, null, 2), 'utf-8');
    console.log(`Updated ${DASHBOARD_DATA_PATH}`);
}

main();
