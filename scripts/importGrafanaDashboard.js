#!/usr/bin/env node
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║  WILSY OS – GRAFANA DASHBOARD IMPORTER [v1.0.0-OMEGA]                                                                                           ║
 * ║  [DEPLOYMENT SCRIPT | AUTOMATED | SOVEREIGN TELEMETRY]                                                                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║  EPITOME: Automatically imports the Verification Sync dashboard into Grafana via API.                                                           ║
 * ║                                                                                                                                                  ║
 * ║  INSTITUTIONAL COMPLIANCE: POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001 · ECT Act §15                                                          ║
 * ║  KENNEL EOS AWARENESS: Dashboard is tenant‑agnostic; metrics are labelled.                                                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║  VERSION: 1.0.0-OMEGA | PRODUCTION READY                                                                                                        ║
 * ║  PATH: scripts/importGrafanaDashboard.js                                                                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║  👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                           ║
 * ║  • Wilson Khanyezi (CEO/Lead Architect) – Mandated automated deployment of monitoring dashboards. 2026‑08‑12.                                   ║
 * ║  • AI Engineering – v1.0.0: Created import script for Grafana API.                                                                              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

dotenv.config();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DASHBOARD_PATH = path.join(__dirname, '..', 'infrastructure', 'grafana', 'dashboards', 'verification-sync.json');

const GRAFANA_URL = process.env.GRAFANA_URL || 'http://localhost:3000';
const GRAFANA_API_KEY = process.env.GRAFANA_API_KEY;
const GRAFANA_USER = process.env.GRAFANA_USER;
const GRAFANA_PASSWORD = process.env.GRAFANA_PASSWORD;

if (!GRAFANA_API_KEY && (!GRAFANA_USER || !GRAFANA_PASSWORD)) {
  console.error('❌ Missing credentials. Set GRAFANA_API_KEY or GRAFANA_USER/GRAFANA_PASSWORD in .env');
  process.exit(1);
}

try {
  const dashboardJson = JSON.parse(fs.readFileSync(DASHBOARD_PATH, 'utf8'));
  const payload = {
    dashboard: dashboardJson.dashboard,
    overwrite: true,
  };

  const headers = {
    'Content-Type': 'application/json',
  };

  if (GRAFANA_API_KEY) {
    headers['Authorization'] = `Bearer ${GRAFANA_API_KEY}`;
  } else {
    const basic = Buffer.from(`${GRAFANA_USER}:${GRAFANA_PASSWORD}`).toString('base64');
    headers['Authorization'] = `Basic ${basic}`;
  }

  const response = await fetch(`${GRAFANA_URL}/api/dashboards/db`, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`❌ Import failed (${response.status}): ${errorText}`);
    process.exit(1);
  }

  const result = await response.json();
  console.log(`✅ Dashboard imported successfully. UID: ${result.uid}, URL: ${GRAFANA_URL}${result.url}`);
} catch (err) {
  console.error('❌ Import error:', err.message);
  process.exit(1);
}
