#!/usr/bin/env node/usr/bin/env node

/*
 * WILSY OS: QUANTUM FORENSIC ENGINE SHUTDOWN (ES Module Version)
 * ============================================================================
 */

import fs from 'fs/promises';
import { execSync } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PID_DIR = join(__dirname, '.pids');

const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

console.log('');
console.log(
  `${colors.blue}═══════════════════════════════════════════════════════════════════════════════${
    colors.reset
  }`,
);
console.log(`${colors.yellow}                 SHUTTING DOWN WILSY OS${colors.reset}`);
console.log(
  `${colors.blue}═══════════════════════════════════════════════════════════════════════════════${
    colors.reset
  }`,
);
console.log('');

async function stopProcess(pidFile, name) {
  try {
    const pid = parseInt(await fs.readFile(join(PID_DIR, pidFile), 'utf8'));
    try {
      process.kill(pid);
      console.log(`Stopping ${name}... ${colors.green}✓${colors.reset}`);
    } catch (error) {
      console.log(`Stopping ${name}... ${colors.yellow}⚠️  Not running${colors.reset}`);
    }
  } catch (error) {
    // PID file doesn't exist
  }
  try {
    await fs.unlink(join(PID_DIR, pidFile));
  } catch (error) {
    // Ignore
  }
}

async function main() {
  // Stop API
  await stopProcess('api.pid', 'API Gateway');

  // Stop Monitoring
  await stopProcess('monitoring.pid', 'Monitoring');

  // Stop Workers
  for (let i = 1; i <= 4; i++) {
    await stopProcess(`worker-${i}.pid`, `Worker ${i}`);
  }

  // Final cleanup
  try {
    execSync(
      'pkill -f "node.*(server|precedentVectorizer|MonitoringDashboard)" 2>/dev/null || true',
    );
  } catch (error) {
    // Ignore
  }

  console.log('');
  console.log(`${colors.green}✓ Shutdown complete${colors.reset}`);
  console.log('');
}

main().catch(console.error);
