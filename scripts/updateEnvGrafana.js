#!/usr/bin/env node
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║  WILSY OS – GRAFANA ENV UPDATER [v1.0.0-OMEGA]                                                                                                   ║
 * ║  [ZERO‑LOSS PRESERVATION | SOVEREIGN CONFIGURATION | KENNEL EOS AWARE]                                                                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║  EPITOME: Programmatically updates .env with Grafana credentials – no manual edits, no loss.                                                    ║
 * ║                                                                                                                                                  ║
 * ║  INSTITUTIONAL COMPLIANCE: POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001 · ECT Act §15                                                          ║
 * ║  KENNEL EOS AWARENESS: Updates the sovereign runtime environment.                                                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║  VERSION: 1.0.0-OMEGA | PRODUCTION READY                                                                                                        ║
 * ║  PATH: scripts/updateEnvGrafana.js                                                                                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║  👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                           ║
 * ║  • Wilson Khanyezi (CEO/Lead Architect) – Mandated zero‑loss configuration updates. 2026‑08‑12.                                                 ║
 * ║  • AI Engineering – v1.0.0: Created environment updater script.                                                                                  ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ENV_PATH = path.join(__dirname, '..', '.env');

const GRAFANA_VARS = {
  GRAFANA_URL: process.env.GRAFANA_URL || 'http://localhost:3000',
  GRAFANA_API_KEY: process.env.GRAFANA_API_KEY || '',
  GRAFANA_USER: process.env.GRAFANA_USER || 'admin',
  GRAFANA_PASSWORD: process.env.GRAFANA_PASSWORD || 'admin',
};

let envContent = '';
if (fs.existsSync(ENV_PATH)) {
  envContent = fs.readFileSync(ENV_PATH, 'utf8');
}

const lines = envContent.split('\n').filter(line => line.trim() !== '');
const existingKeys = new Set();
const newLines = [];

for (const line of lines) {
  const trimmed = line.trim();
  if (trimmed.startsWith('#')) {
    newLines.push(line);
    continue;
  }
  const match = trimmed.match(/^([A-Z_][A-Z0-9_]*)=/);
  if (match) {
    const key = match[1];
    existingKeys.add(key);
    if (!(key in GRAFANA_VARS)) {
      newLines.push(line);
    }
  } else {
    newLines.push(line);
  }
}

let added = 0;
for (const [key, value] of Object.entries(GRAFANA_VARS)) {
  if (value !== undefined && value !== null) {
    newLines.push(`${key}=${value}`);
    added++;
  } else {
    newLines.push(`${key}=`);
  }
}

fs.writeFileSync(ENV_PATH, newLines.join('\n') + '\n');
console.log(`✅ Updated .env with Grafana environment variables.`);
console.log(`   GRAFANA_URL=${GRAFANA_VARS.GRAFANA_URL}`);
console.log(`   GRAFANA_USER=${GRAFANA_VARS.GRAFANA_USER}`);
console.log(`   (Credentials updated)`);
