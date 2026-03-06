#!/usr/bin/env node/usr/bin/env node

import { readFile } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const LOG_DIR = join(__dirname, 'logs');

const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

async function checkErrorLogs() {
  console.log(
    `${
      colors.cyan
    }\n═══════════════════════════════════════════════════════════════════════════════${
      colors.reset
    }`,
  );
  console.log(`${colors.yellow}                     WILSY OS ERROR DIAGNOSTIC${colors.reset}`);
  console.log(
    `${colors.cyan}═══════════════════════════════════════════════════════════════════════════════${
      colors.reset
    }`,
  );
  console.log('');

  // Check worker error logs
  for (let i = 1; i <= 4; i++) {
    const logFile = join(LOG_DIR, `worker-${i}.error.log`);
    try {
      const content = await readFile(logFile, 'utf8');
      if (content.trim()) {
        console.log(`${colors.red}\n❌ Worker ${i} Errors:${colors.reset}`);
        console.log(
          content
            .split('\n')
            .slice(0, 10)
            .map((line) => `  ${line}`)
            .join('\n'),
        );
      } else {
        console.log(`${colors.green}✅ Worker ${i}: No errors${colors.reset}`);
      }
    } catch (err) {
      console.log(`${colors.yellow}⚠️  Worker ${i}: No log file found${colors.reset}`);
    }
  }

  // Check API error log
  const apiLog = join(LOG_DIR, 'api.error.log');
  try {
    const content = await readFile(apiLog, 'utf8');
    if (content.trim()) {
      console.log(`${colors.red}\n❌ API Errors:${colors.reset}`);
      console.log(
        content
          .split('\n')
          .slice(0, 10)
          .map((line) => `  ${line}`)
          .join('\n'),
      );
    } else {
      console.log(`${colors.green}\n✅ API: No errors${colors.reset}`);
    }
  } catch (err) {
    console.log(`${colors.yellow}\n⚠️  API: No log file found${colors.reset}`);
  }

  console.log(
    `${
      colors.cyan
    }\n═══════════════════════════════════════════════════════════════════════════════${
      colors.reset
    }`,
  );
  console.log('');
}

checkErrorLogs().catch(console.error);
