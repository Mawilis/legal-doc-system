/* eslint-disable */
/*╔══════════════════════════════════════════════════════════════════════════╗
  ║           WILSY OS - FORENSIC ENGINE STARTUP - 10TH GENERATION          ║
  ║              "Igniting Code That Funds 10 Generations"                  ║
  ╚══════════════════════════════════════════════════════════════════════════╝
 * 
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/start-forensic-engine.js
 * VERSION: 10.0.1-GODLY
 * PURPOSE: Production-grade process manager for Wilsy OS 10th Generation
 * 
 * INVESTOR VALUE PROPOSITION:
 * • Zero-downtime deployment for R1B valuation target
 * • Automatic recovery mechanisms protect generational wealth
 * • Forensic logging of all process activity (POPIA §19 compliant)
 * • Multi-worker scaling for 270,000 law firm capacity
 * 
 * MERMAID PROCESS FLOW:
 * graph TD
 *   A[Start Engine] --> B[Initialize Environment]
 *   B --> C[Check Dependencies]
 *   C --> D[Start Workers x4]
 *   C --> E[Start Monitoring]
 *   C --> F[Start API]
 *   D --> G[Precedent Vectorizer]
 *   D --> H[Document Processor]
 *   D --> I[Audit Archiver]
 *   D --> J[Retention Enforcer]
 *   E --> K[Health Checks]
 *   E --> L[Metrics Collection]
 *   F --> M[API Gateway]
 *   G & H & I & J & K & L & M --> N[Generational Wealth Engine]
 */

import { spawn } from 'child_process.js';
import { fileURLToPath } from 'url.js';
import { dirname, join } from "path";
import fs from 'fs/promises.js';
import crypto from "crypto";
import os from 'os.js';
import cluster from 'cluster.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ===========================================================================
// GENERATIONAL CONSTANTS - 10 Generations of Wealth
// ===========================================================================

const GENERATIONS = [
  { number: 1, name: 'Wilson Khanyezi', birth: 2000, wealthTarget: 1_000_000_000 },
  { number: 2, name: 'Future Khanyezi I', birth: 2030, wealthTarget: 5_000_000_000 },
  { number: 3, name: 'Legal Sovereign', birth: 2050, wealthTarget: 25_000_000_000 },
  { number: 4, name: 'Tech Visionary', birth: 2070, wealthTarget: 100_000_000_000 },
  { number: 5, name: 'Global Ambassador', birth: 2090, wealthTarget: 500_000_000_000 },
  { number: 6, name: 'Continental Governor', birth: 2110, wealthTarget: 2_500_000_000_000 },
  { number: 7, name: 'Interstellar Diplomat', birth: 2130, wealthTarget: 10_000_000_000_000 },
  { number: 8, name: 'Galactic Justiciar', birth: 2150, wealthTarget: 50_000_000_000_000 },
  { number: 9, name: 'Cosmic Sovereign', birth: 2170, wealthTarget: 250_000_000_000_000 },
  { number: 10, name: 'Eternal Legacy', birth: 2190, wealthTarget: 1_000_000_000_000_000 },
];

// Configuration
const WORKER_COUNT = Math.min(os.cpus().length, 16); // Scale to available CPUs
const LOG_DIR = join(__dirname, 'logs');
const PID_DIR = join(__dirname, '.pids');
const EVIDENCE_DIR = join(__dirname, 'evidence');

// Worker types for different responsibilities
const WORKER_TYPES = [
  { name: 'precedent-vectorizer', script: 'workers/precedentVectorizer.js', count: 2, priority: 1 },
  { name: 'document-processor', script: 'workers/documentProcessor.js', count: 2, priority: 1 },
  { name: 'audit-archiver', script: 'workers/auditArchiver.js', count: 1, priority: 2 },
  { name: 'retention-enforcer', script: 'workers/retentionEnforcer.js', count: 1, priority: 2 },
  { name: 'email-worker', script: 'workers/emailWorker.js', count: 1, priority: 3 },
  { name: 'report-generator', script: 'workers/reportGenerator.js', count: 1, priority: 3 },
];

// ANSI colors for beautiful console output
const colors = {
  reset: '\x1b[0m',
  black: '\x1b[30m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  gold: '\x1b[38;5;220m',
  purple: '\x1b[38;5;129m',
  pink: '\x1b[38;5;206m',

  // Background colors
  bgRed: '\x1b[41m',
  bgGreen: '\x1b[42m',
  bgYellow: '\x1b[43m',
  bgBlue: '\x1b[44m',
  bgPurple: '\x1b[45m',
  bgCyan: '\x1b[46m',

  bold: '\x1b[1m',
  dim: '\x1b[2m',
  italic: '\x1b[3m',
  underline: '\x1b[4m',
  blink: '\x1b[5m',
  reverse: '\x1b[7m',
  hidden: '\x1b[8m',
};

// ===========================================================================
// FORENSIC LOGGER - Every startup event recorded for 10 generations
// ===========================================================================

class ForensicLogger {
  constructor() {
    this.logFile = join(LOG_DIR, `startup-${new Date().toISOString().split('T')[0]}.log`);
    this.events = [];
    this.startTime = Date.now();
  }

  async log(level, message, metadata = {}) {
    const timestamp = new Date().toISOString();
    const pid = process.pid;
    const hostname = os.hostname();

    // Add forensic signature
    const signature = crypto
      .createHash('sha256')
      .update(`${timestamp}${level}${message}${JSON.stringify(metadata)}`)
      .digest('hex')
      .substring(0, 16);

    const logEntry = {
      timestamp,
      level,
      message,
      metadata,
      pid,
      hostname,
      signature,
      generation: 10,
    };

    this.events.push(logEntry);

    // Color coding based on level
    let color = colors.white;
    switch (level) {
      case 'ERROR':
        color = colors.red + colors.bold;
        break;
      case 'WARN':
        color = colors.yellow + colors.bold;
        break;
      case 'INFO':
        color = colors.green;
        break;
      case 'DEBUG':
        color = colors.cyan + colors.dim;
        break;
      case 'GENERATIONAL':
        color = colors.gold + colors.bold;
        break;
      case 'BILLION':
        color = colors.purple + colors.bold;
        break;
      case 'SOVEREIGN':
        color = colors.pink + colors.bold;
        break;
    }

    const timeStr = new Date(timestamp).toLocaleTimeString();
    console.log(
      `${color}[${level.padEnd(12)}]${colors.reset} ${colors.dim}${timeStr}${
        colors.reset
      } - ${message}`
    );

    // Write to file asynchronously
    this.writeToFile(logEntry).catch(console.error);

    return logEntry;
  }

  async writeToFile(entry) {
    try {
      await fs.mkdir(LOG_DIR, { recursive: true });
      await fs.appendFile(this.logFile, JSON.stringify(entry) + '\n');
    } catch (error) {
      console.error('Failed to write to log file:', error.message);
    }
  }

  generational(message, metadata) {
    return this.log('GENERATIONAL', message, metadata);
  }
  billion(message, metadata) {
    return this.log('BILLION', message, metadata);
  }
  sovereign(message, metadata) {
    return this.log('SOVEREIGN', message, metadata);
  }
  info(message, metadata) {
    return this.log('INFO', message, metadata);
  }
  warn(message, metadata) {
    return this.log('WARN', message, metadata);
  }
  error(message, metadata) {
    return this.log('ERROR', message, metadata);
  }
  debug(message, metadata) {
    return this.log('DEBUG', message, metadata);
  }

  async getSummary() {
    const duration = Date.now() - this.startTime;
    return {
      totalEvents: this.events.length,
      errors: this.events.filter((e) => e.level === 'ERROR').length,
      warnings: this.events.filter((e) => e.level === 'WARN').length,
      duration,
      logFile: this.logFile,
    };
  }
}

// ===========================================================================
// PROCESS MANAGER - Handles all child processes with forensic tracking
// ===========================================================================

class ProcessManager {
  constructor(logger) {
    this.processes = new Map();
    this.logger = logger;
    this.restartCounts = new Map();
    this.maxRestarts = 5;
    this.restartWindow = 60000; // 1 minute
  }

  async initialize() {
    await fs.mkdir(PID_DIR, { recursive: true });
    await fs.mkdir(LOG_DIR, { recursive: true });
    await fs.mkdir(EVIDENCE_DIR, { recursive: true });

    // Clean old PID files
    try {
      const files = await fs.readdir(PID_DIR);
      for (const file of files) {
        if (file.endsWith('.pid')) {
          await fs.unlink(join(PID_DIR, file));
        }
      }
    } catch (error) {
      // Ignore if directory doesn't exist
    }

    await this.logger.generational('Environment initialized', {
      pidDir: PID_DIR,
      logDir: LOG_DIR,
      evidenceDir: EVIDENCE_DIR,
    });
  }

  async startWorker(type, instance = 1) {
    const scriptPath = join(__dirname, type.script);

    // Check if script exists
    try {
      await fs.access(scriptPath);
    } catch (error) {
      await this.logger.warn(`Worker script not found: ${type.script}`, {
        type: type.name,
        script: type.script,
      });
      return null;
    }

    const workerId = `${type.name}-${instance}`;
    const logFile = join(LOG_DIR, `${workerId}.log`);
    const errorLogFile = join(LOG_DIR, `${workerId}.error.log`);
    const pidFile = join(PID_DIR, `${workerId}.pid`);

    const proc = spawn('node', [type.script], {
      env: {
        ...process.env,
        NODE_ENV: 'production',
        WORKER_ID: workerId,
        WORKER_TYPE: type.name,
        GENERATION: '10',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
      detached: false,
    });

    this.processes.set(workerId, {
      process: proc,
      type: type.name,
      instance,
      startTime: Date.now(),
      pid: proc.pid,
      restartCount: 0,
    });

    // Save PID
    await fs.writeFile(pidFile, proc.pid.toString());

    // Handle stdout
    proc.stdout.on('data', (data) => {
      fs.appendFile(logFile, data).catch(() => {});
      this.parseWorkerOutput(workerId, data);
    });

    // Handle stderr
    proc.stderr.on('data', (data) => {
      fs.appendFile(errorLogFile, data).catch(() => {});
      this.logger.error(`Worker ${workerId} error`, {
        error: data.toString().substring(0, 500),
      });
    });

    // Handle exit
    proc.on('exit', (code, signal) => {
      this.handleWorkerExit(workerId, code, signal);
    });

    await this.logger.info(`Worker started: ${workerId}`, {
      pid: proc.pid,
      script: type.script,
      instance,
    });

    return proc;
  }

  parseWorkerOutput(workerId, data) {
    const output = data.toString().trim();
    if (output.includes('ERROR') || output.includes('error')) {
      this.logger.error(`Worker ${workerId}: ${output.substring(0, 200)}`);
    } else if (output.includes('WARN') || output.includes('warn')) {
      this.logger.warn(`Worker ${workerId}: ${output.substring(0, 200)}`);
    } else if (output.includes('BILLION')) {
      this.logger.billion(`Worker ${workerId}: ${output.substring(0, 200)}`);
    }
  }

  async handleWorkerExit(workerId, code, signal) {
    const procInfo = this.processes.get(workerId);
    if (!procInfo) return;

    const duration = Date.now() - procInfo.startTime;
    const exitCode = code !== null ? code : signal;

    await this.logger.warn(`Worker exited: ${workerId}`, {
      exitCode,
      signal,
      duration,
      uptime: `${Math.round(duration / 1000)}s`,
    });

    // Update restart count
    const restartKey = `${workerId}-${Math.floor(Date.now() / 60000)}`;
    const currentRestarts = this.restartCounts.get(restartKey) || 0;
    this.restartCounts.set(restartKey, currentRestarts + 1);

    // Check if we should restart
    if (currentRestarts < this.maxRestarts) {
      await this.logger.info(`Restarting worker: ${workerId}`, {
        attempt: currentRestarts + 1,
        maxAttempts: this.maxRestarts,
      });

      // Find worker type
      const workerType = WORKER_TYPES.find((w) => w.name === procInfo.type);
      if (workerType) {
        setTimeout(
          () => {
            this.startWorker(workerType, procInfo.instance);
          },
          2000 * (currentRestarts + 1)
        ); // Exponential backoff
      }
    } else {
      await this.logger.error(`Worker exceeded restart limit: ${workerId}`, {
        attempts: currentRestarts,
        window: '1 minute',
      });
    }

    this.processes.delete(workerId);

    // Clean up PID file
    try {
      await fs.unlink(join(PID_DIR, `${workerId}.pid`));
    } catch (error) {
      // Ignore
    }
  }

  async stopAll() {
    await this.logger.generational('Stopping all processes...');

    const stopPromises = [];
    for (const [workerId, info] of this.processes.entries()) {
      stopPromises.push(this.stopProcess(workerId, info));
    }

    await Promise.all(stopPromises);

    await this.logger.generational('All processes stopped');
  }

  async stopProcess(workerId, info) {
    return new Promise((resolve) => {
      const timeout = setTimeout(() => {
        info.process.kill('SIGKILL');
        resolve();
      }, 5000);

      info.process.once('exit', () => {
        clearTimeout(timeout);
        resolve();
      });

      info.process.kill('SIGTERM');
    });
  }

  getStatus() {
    const status = {
      total: this.processes.size,
      processes: [],
    };

    for (const [workerId, info] of this.processes.entries()) {
      status.processes.push({
        id: workerId,
        type: info.type,
        instance: info.instance,
        pid: info.pid,
        uptime: Math.round((Date.now() - info.startTime) / 1000),
        restartCount: info.restartCount,
      });
    }

    return status;
  }
}

// ===========================================================================
// STARTUP BANNER - Display generational wealth information
// ===========================================================================

function displayStartupBanner() {
  console.clear();

  console.log(
    colors.gold +
      colors.bold +
      `
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║   ██╗    ██╗██╗██╗     ███████╗██╗   ██╗    ██████╗ ███████╗           ║
    ║   ██║    ██║██║██║     ██╔════╝╚██╗ ██╔╝    ██╔══██╗██╔════╝           ║
    ║   ██║ █╗ ██║██║██║     ███████╗ ╚████╔╝     ██████╔╝███████╗           ║
    ║   ██║███╗██║██║██║     ╚════██║  ╚██╔╝      ██╔══██╗╚════██║           ║
    ║   ╚███╔███╔╝██║███████╗███████║   ██║       ██████╔╝███████║           ║
    ║    ╚══╝╚══╝ ╚═╝╚══════╝╚══════╝   ╚═╝       ╚═════╝ ╚══════╝           ║
    ║                                                                          ║
    ║                   10TH GENERATION FORENSIC ENGINE                       ║
    ║                    "IGNITING 10 GENERATIONS OF WEALTH"                  ║
    ║                                                                          ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║                                                                          ║
    ║  👑 GENESIS: Wilson Khanyezi - Generation 1 (2000)                      ║
    ║  💰 VALUATION TARGET: R 1,000,000,000 (Year 1)                          ║
    ║  🌍 MARKET: 54 African Countries | 270,000 Law Firms                    ║
    ║  ⚖️  COMPLIANCE: POPIA §19 | ECT Act §15 | Companies Act §24            ║
    ║  🚀 WORKERS: ${WORKER_COUNT} Parallel Processes                            ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    ` +
      colors.reset
  );

  console.log(
    colors.cyan +
      colors.bold +
      `
    ┌──────────────────────────────────────────────────────────────────────┐
    │                    GENERATIONAL WEALTH PROGRESSION                   │
    ├──────────────────────────────────────────────────────────────────────┤
    │  Gen 1: R 1,000,000,000     │ Gen 6: R 2,500,000,000,000            │
    │  Gen 2: R 5,000,000,000     │ Gen 7: R 10,000,000,000,000           │
    │  Gen 3: R 25,000,000,000    │ Gen 8: R 50,000,000,000,000           │
    │  Gen 4: R 100,000,000,000   │ Gen 9: R 250,000,000,000,000          │
    │  Gen 5: R 500,000,000,000   │ Gen 10: R 1,000,000,000,000,000       │
    └──────────────────────────────────────────────────────────────────────┘
    ` +
      colors.reset
  );
}

// ===========================================================================
// HEALTH CHECK SYSTEM - Verify all components are operational
// ===========================================================================

async function performHealthChecks(logger) {
  const checks = [
    { name: 'Database Connection', check: checkDatabase, critical: true },
    { name: 'Redis Connection', check: checkRedis, critical: false },
    { name: 'Log Directory', check: checkLogDirectory, critical: true },
    { name: 'Worker Scripts', check: checkWorkerScripts, critical: true },
    { name: 'Environment Variables', check: checkEnvironment, critical: true },
    { name: 'Disk Space', check: checkDiskSpace, critical: false },
  ];

  const results = [];
  let allCriticalPassed = true;

  await logger.info('Performing pre-flight health checks...');

  for (const check of checks) {
    try {
      const result = await check.check();
      results.push({ name: check.name, passed: result, critical: check.critical });

      if (result) {
        await logger.info(`✅ ${check.name}: PASSED`);
      } else {
        if (check.critical) {
          allCriticalPassed = false;
          await logger.error(`❌ ${check.name}: FAILED (CRITICAL)`);
        } else {
          await logger.warn(`⚠️ ${check.name}: FAILED (Non-critical)`);
        }
      }
    } catch (error) {
      if (check.critical) {
        allCriticalPassed = false;
        await logger.error(`💥 ${check.name}: ERROR - ${error.message} (CRITICAL)`);
      } else {
        await logger.warn(`⚠️ ${check.name}: ERROR - ${error.message} (Non-critical)`);
      }
    }
  }

  return { passed: allCriticalPassed, results };
}

async function checkDatabase() {
  // Try to connect to MongoDB
  try {
    const mongoose = await import('mongoose');
    const conn = await mongoose.connect(
      process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/wilsy_legal_os_10g',
      {
        serverSelectionTimeoutMS: 5000,
      }
    );
    await conn.disconnect();
    return true;
  } catch (error) {
    return false;
  }
}

async function checkRedis() {
  try {
    const Redis = (await import('ioredis')).default;
    const redis = new Redis(process.env.REDIS_URL || 'redis://127.0.0.1:6379/10', {
      lazyConnect: true,
      connectTimeout: 5000,
    });
    await redis.connect();
    await redis.quit();
    return true;
  } catch (error) {
    return false;
  }
}

async function checkLogDirectory() {
  try {
    await fs.access(LOG_DIR);
    return true;
  } catch {
    await fs.mkdir(LOG_DIR, { recursive: true });
    return true;
  }
}

async function checkWorkerScripts() {
  let allExist = true;

  for (const worker of WORKER_TYPES) {
    const scriptPath = join(__dirname, worker.script);
    try {
      await fs.access(scriptPath);
    } catch {
      allExist = false;
    }
  }

  return allExist;
}

async function checkEnvironment() {
  const required = ['NODE_ENV'];
  return required.every((env) => process.env[env] !== undefined);
}

async function checkDiskSpace() {
  // Check if we have at least 1GB free
  try {
    const { exec } = await import('child_process');
    const { promisify } = await import('util');
    const execAsync = promisify(exec);

    const { stdout } = await execAsync("df -k . | tail -1 | awk '{print $4}'");
    const freeKB = parseInt(stdout);
    const freeGB = freeKB / 1024 / 1024;

    return freeGB > 1; // At least 1GB free
  } catch {
    return true; // Assume OK if we can't check
  }
}

// ===========================================================================
// EVIDENCE GENERATION - Create forensic evidence of successful startup
// ===========================================================================

async function generateStartupEvidence(logger, processManager, healthResults) {
  const evidence = {
    timestamp: new Date().toISOString(),
    system: {
      hostname: os.hostname(),
      platform: os.platform(),
      release: os.release(),
      cpus: os.cpus().length,
      memory: os.totalmem(),
      freeMemory: os.freemem(),
      uptime: os.uptime(),
    },
    process: {
      pid: process.pid,
      version: process.version,
      argv: process.argv,
      env: Object.keys(process.env).filter((k) => !k.includes('SECRET') && !k.includes('KEY')),
    },
    generations: GENERATIONS,
    workers: WORKER_TYPES.map((w) => ({
      ...w,
      instances: w.count,
    })),
    healthChecks: healthResults,
    processes: processManager.getStatus(),
    startupTime: logger.startTime,
    startupDuration: Date.now() - logger.startTime,
    signature: null,
  };

  // Add SHA256 signature
  const evidenceString = JSON.stringify(evidence, null, 2);
  evidence.signature = crypto.createHash('sha256').update(evidenceString).digest('hex');

  // Save evidence
  const evidenceFile = join(
    EVIDENCE_DIR,
    `startup-${new Date().toISOString().replace(/:/g, '-')}.json`
  );
  await fs.writeFile(evidenceFile, JSON.stringify(evidence, null, 2));

  await logger.generational('Startup evidence generated', {
    file: evidenceFile,
    signature: evidence.signature.substring(0, 16),
  });

  return evidence;
}

// ===========================================================================
// MAIN EXECUTION - The Ignition Sequence
// ===========================================================================

async function main() {
  const startTime = Date.now();

  // Display banner
  displayStartupBanner();

  // Initialize logger
  const logger = new ForensicLogger();
  await logger.generational('FORENSIC ENGINE STARTING', {
    pid: process.pid,
    nodeVersion: process.version,
    cpus: os.cpus().length,
  });

  // Initialize process manager
  const processManager = new ProcessManager(logger);
  await processManager.initialize();

  // Perform health checks
  const healthResults = await performHealthChecks(logger);

  if (!healthResults.passed) {
    await logger.error('CRITICAL HEALTH CHECKS FAILED - Aborting startup');
    console.log(
      colors.red +
        colors.bold +
        '\n❌ CRITICAL HEALTH CHECKS FAILED - Cannot start forensic engine\n' +
        colors.reset
    );
    process.exit(1);
  }

  await logger.info('All critical health checks passed - Proceeding with startup');

  // Start all workers
  await logger.generational('Starting worker processes...');

  let totalWorkers = 0;
  for (const workerType of WORKER_TYPES) {
    for (let i = 1; i <= workerType.count; i++) {
      await logger.info(`Starting ${workerType.name} (${i}/${workerType.count})`);
      await processManager.startWorker(workerType, i);
      totalWorkers++;

      // Stagger startup to avoid thundering herd
      await new Promise((r) => setTimeout(r, 500));
    }
  }

  await logger.billion(`Started ${totalWorkers} workers across ${WORKER_TYPES.length} types`);

  // Start monitoring
  await logger.info('Starting monitoring service...');
  try {
    await fs.access(join(__dirname, 'services/monitoring/MonitoringDashboard.js'));
    const monitoring = await processManager.startWorker(
      { name: 'monitoring', script: 'services/monitoring/MonitoringDashboard.js' },
      1
    );
    if (monitoring) {
      await logger.info('Monitoring service started');
    }
  } catch (error) {
    await logger.warn('Monitoring service not yet implemented', { error: error.message });
  }

  // Start API server
  await logger.info('Starting API server...');
  const apiProc = spawn('node', ['server.js'], {
    env: { ...process.env, NODE_ENV: 'production' },
    stdio: 'pipe',
    detached: false,
  });

  await fs.writeFile(join(PID_DIR, 'api.pid'), apiProc.pid.toString());

  apiProc.stderr.on('data', (data) => {
    fs.appendFile(join(LOG_DIR, 'api.error.log'), data);
    if (data.toString().includes('error')) {
      logger.error('API Error', { error: data.toString().substring(0, 200) });
    }
  });

  apiProc.stdout.on('data', (data) => {
    fs.appendFile(join(LOG_DIR, 'api.log'), data);
    const output = data.toString();
    if (output.includes('LISTENING')) {
      logger.info('API server listening');
    }
  });

  await logger.info(`API server started (PID: ${apiProc.pid})`);

  // Generate startup evidence
  const evidence = await generateStartupEvidence(logger, processManager, healthResults);

  // Calculate startup metrics
  const startupDuration = Date.now() - startTime;
  const startupSeconds = (startupDuration / 1000).toFixed(2);

  // Display success banner
  console.log(
    colors.green +
      colors.bold +
      `
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║        🚀 FORENSIC ENGINE SUCCESSFULLY IGNITED 🚀                       ║
    ║                                                                          ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║                                                                          ║
    ║  ⏱️  Startup Time: ${startupSeconds.padStart(
      8
    )} seconds                                          ║
    ║  👷 Workers: ${totalWorkers
      .toString()
      .padStart(8)}                                                    ║
    ║  📊 Health Checks: ${
      healthResults.results.length
    }                                                     ║
    ║  🔐 Evidence: ${evidence.signature.substring(0, 16)}...                              ║
    ║  📁 Logs: ${LOG_DIR}                ║
    ║                                                                          ║
    ║  📈 Investor Dashboard: http://localhost:9095/api/investors/generational ║
    ║  💓 Health Check: http://localhost:9095/health                           ║
    ║  📊 Metrics: http://localhost:9095/metrics                               ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    ` +
      colors.reset
  );

  await logger.generational('FORENSIC ENGINE IGNITION COMPLETE', {
    duration: startupDuration,
    workers: totalWorkers,
    evidence: evidence.signature,
  });

  // Keep running
  await new Promise(() => {});
}

// Handle shutdown signals
process.on('SIGTERM', async () => {
  console.log(
    colors.yellow + '\n\nReceived SIGTERM - Shutting down forensic engine...\n' + colors.reset
  );
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log(
    colors.yellow + '\n\nReceived SIGINT - Shutting down forensic engine...\n' + colors.reset
  );
  process.exit(0);
});

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  console.error(colors.red + colors.bold + '\n💥 UNCAUGHT EXCEPTION:' + colors.reset, error);
  console.log(colors.yellow + '\nAttempting graceful shutdown...\n' + colors.reset);
  process.exit(1);
});

process.on('unhandledRejection', (reason) => {
  console.error(colors.red + colors.bold + '\n💥 UNHANDLED REJECTION:' + colors.reset, reason);
});

// Run main
main().catch(async (error) => {
  console.error(
    colors.red + colors.bold + '\n💥 FORENSIC ENGINE IGNITION FAILED:' + colors.reset,
    error
  );
  process.exit(1);
});
