import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const UPDATE_SCRIPT = path.join(__dirname, 'update_dashboard_real.js');

function runUpdate() {
    console.log(`[${new Date().toLocaleString()}] Running update...`);
    const child = spawn('node', [UPDATE_SCRIPT], { stdio: 'inherit' });

    child.on('close', (code) => {
        console.log(`Update process exited with code ${code}`);
    });
}

function getNextScheduledTime() {
    const now = new Date();
    const morning = new Date(now);
    morning.setHours(9, 0, 0, 0);

    const evening = new Date(now);
    evening.setHours(21, 0, 0, 0);

    // If morning is in the past, add 1 day (wait, we need to check if evening is next)
    // Actually, just find the next occurrence of either.

    let nextTime = morning;
    if (now > morning) {
        nextTime = evening;
    }
    if (now > evening) {
        // tomorow morning
        nextTime = new Date(now);
        nextTime.setDate(now.getDate() + 1);
        nextTime.setHours(9, 0, 0, 0);
    }

    return nextTime;
}

function scheduleNext() {
    const now = new Date();
    const next = getNextScheduledTime();
    const delay = next - now;

    console.log(`Next update scheduled for: ${next.toLocaleString()} (in ${Math.round(delay / 60000)} mins)`);

    setTimeout(() => {
        runUpdate();
        scheduleNext(); // Re-schedule after running
    }, delay);
}

// Run once immediately on start
runUpdate();
// Start the loop
scheduleNext();
