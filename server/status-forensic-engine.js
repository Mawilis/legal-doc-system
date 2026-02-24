#!/usr/bin/env node

/*╔══════════════════════════════════════════════════════════════════════════╗
  ║           WILSY OS - FORENSIC ENGINE STATUS - 10TH GENERATION           ║
  ╚══════════════════════════════════════════════════════════════════════════╝
 */

import { readdir, readFile } from 'fs/promises';
import { join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PID_DIR = join(__dirname, '.pids');
const LOG_DIR = join(__dirname, 'logs');

const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  gold: '\x1b[38;5;220m',
};

async function status() {
  console.log(colors.gold + '\n📊 WILSY OS - FORENSIC ENGINE STATUS\n' + colors.reset);

  try {
    const files = await readdir(PID_DIR);
    const pidFiles = files.filter((f) => f.endsWith('.pid'));

    if (pidFiles.length === 0) {
      console.log(colors.yellow + '⚠️  No running processes found' + colors.reset);
      return;
    }

    console.log(colors.blue + `Found ${pidFiles.length} processes:\n` + colors.reset);

    let running = 0;
    let stopped = 0;

    for (const pidFile of pidFiles) {
      try {
        const pidPath = join(PID_DIR, pidFile);
        const pid = parseInt(await readFile(pidPath, 'utf8'));

        // Check if process is running
        try {
          process.kill(pid, 0);
          console.log(
            colors.green +
              `✅ ${pidFile.replace('.pid', '')} (PID: ${pid}) - RUNNING` +
              colors.reset
          );
          running++;
        } catch (e) {
          console.log(
            colors.red + `❌ ${pidFile.replace('.pid', '')} (PID: ${pid}) - STOPPED` + colors.reset
          );
          stopped++;
        }
      } catch (error) {
        console.log(colors.red + `❌ ${pidFile} - ERROR: ${error.message}` + colors.reset);
      }
    }

    console.log(
      colors.cyan + `\n📈 Summary: ${running} running, ${stopped} stopped` + colors.reset
    );

    // Check recent logs
    console.log(colors.blue + '\n📋 Recent log activity:' + colors.reset);

    try {
      const logFiles = await readdir(LOG_DIR);
      const recentLogs = logFiles
        .filter((f) => f.endsWith('.log'))
        .sort()
        .slice(-5);

      for (const log of recentLogs) {
        console.log(`   • ${log}`);
      }
    } catch (error) {
      console.log(colors.yellow + '   No logs found' + colors.reset);
    }
  } catch (error) {
    if (error.code === 'ENOENT') {
      console.log(colors.yellow + 'No PID directory found - engine not started\n' + colors.reset);
    } else {
      console.error(colors.red + 'Error checking status:' + colors.reset, error);
    }
  }
}

status();
