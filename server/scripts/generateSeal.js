#!/usr/bin/env node
/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * WILSY OS — Sovereign Seal Generator (Forensic Helper)
 * ═══════════════════════════════════════════════════════════════════════════════
 * File:           server/scripts/generateSeal.js
 * Version:        v1.1.0‑EXECUTE‑FLAG
 * Authority:      Wilsy OS Core Governance
 * Epitome:        Generates cryptographic headers and optionally executes the
 *                 curl command. No manual copying – set env vars and run.
 *
 * Usage:
 *   node generateSeal.js --file=payload.json --execute
 *   TENANT_ID=acme ENDPOINT=/api/subscriptions node generateSeal.js --file=payload.json --execute
 *
 * Options:
 *   --file=FILE     Read JSON payload from file.
 *   --payload='{}'  Provide JSON payload directly.
 *   --execute       Execute the curl command immediately.
 *   --help, -h      Show help.
 *
 * Compliance: POPIA §19, GDPR §32
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import fs from 'node:fs';
import crypto from 'node:crypto';
import { execSync } from 'node:child_process';
import pkg from 'js-sha3';

const { sha3_512 } = pkg;

// ─── Deterministic sorting ──────────────────────────────────────────────────
function sortKeys(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(sortKeys);
  return Object.keys(obj)
    .sort()
    .reduce((acc, key) => {
      acc[key] = sortKeys(obj[key]);
      return acc;
    }, {});
}

function generateTraceAnchor() {
  return `TRC-${Date.now()}-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;
}

function generateNonce() {
  return `NONCE-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;
}

function getSyncedTimestamp() {
  return new Date().toISOString();
}

function parseArgs() {
  const args = process.argv.slice(2);
  let payload = null;
  let fromFile = null;
  let execute = false;

  for (const arg of args) {
    if (arg.startsWith('--payload=')) {
      try {
        const json = arg.substring('--payload='.length);
        payload = JSON.parse(json);
      } catch (e) {
        console.error(`❌ Invalid JSON in --payload: ${e.message}`);
        process.exit(1);
      }
    } else if (arg.startsWith('--file=')) {
      fromFile = arg.substring('--file='.length);
    } else if (arg === '--execute') {
      execute = true;
    } else if (arg === '--help' || arg === '-h') {
      console.log(`
Usage:
  node generateSeal.js --file=payload.json [--execute]
  TENANT_ID=acme ENDPOINT=/api/subscriptions node generateSeal.js --file=payload.json --execute

Options:
  --file=FILE     Read JSON payload from file.
  --payload='{}'  Provide JSON payload directly.
  --execute       Execute the curl command immediately.
  --help, -h      Show this help.

Environment variables:
  METHOD         HTTP method (default: POST)
  API_URL        Base URL (default: http://localhost:4000)
  ENDPOINT       API endpoint (default: /api/subscriptions)
  TENANT_ID      Tenant ID (required for the x-tenant-id header)
  TOKEN          JWT token (optional, for Authorization header)
`);
      process.exit(0);
    }
  }

  if (!payload && !fromFile && !process.stdin.isTTY) {
    let stdinData = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', chunk => { stdinData += chunk; });
    process.stdin.on('end', () => {
      if (stdinData.trim()) {
        try {
          payload = JSON.parse(stdinData);
          generateAndOutput(payload, execute);
        } catch (e) {
          console.error(`❌ Invalid JSON from stdin: ${e.message}`);
          process.exit(1);
        }
      } else {
        console.error('❌ No payload provided. Use --payload, --file, or pipe JSON.');
        process.exit(1);
      }
    });
    return;
  }

  if (fromFile) {
    try {
      const fileContent = fs.readFileSync(fromFile, 'utf8');
      payload = JSON.parse(fileContent);
    } catch (e) {
      console.error(`❌ Failed to read file: ${e.message}`);
      process.exit(1);
    }
  }

  if (!payload) {
    console.error('❌ No payload provided. Use --payload, --file, or pipe JSON.');
    process.exit(1);
  }

  generateAndOutput(payload, execute);
}

function generateAndOutput(payload, execute) {
  const traceId = generateTraceAnchor();
  const timestamp = getSyncedTimestamp();
  const nonce = generateNonce();

  const sortedPayload = sortKeys(payload || {});
  const payloadStr = JSON.stringify(sortedPayload);

  const message = `${traceId}|${timestamp}|${payloadStr}|${nonce}`;
  const seal = sha3_512(message).toLowerCase();

  const method = process.env.METHOD || 'POST';
  const url = process.env.API_URL || 'http://localhost:4000';
  const endpoint = process.env.ENDPOINT || '/api/subscriptions';
  const tenantId = process.env.TENANT_ID || 'your-tenant-id';
  const token = process.env.TOKEN;
  const authHeader = token ? ` -H "Authorization: Bearer ${token}"` : '';

  const curlCmd = `curl -X ${method} "${url}${endpoint}" \\
  -H "Content-Type: application/json" \\
  -H "x-tenant-id: ${tenantId}" \\
  -H "x-trace-id: ${traceId}" \\
  -H "x-forensic-timestamp: ${timestamp}" \\
  -H "x-cryptographic-nonce: ${nonce}" \\
  -H "x-request-seal: ${seal}"${authHeader} \\
  -d '${payloadStr}'`;

  console.log('\n✅ Sovereign Seal Generated\n');
  console.log(`x-trace-id: ${traceId}`);
  console.log(`x-forensic-timestamp: ${timestamp}`);
  console.log(`x-cryptographic-nonce: ${nonce}`);
  console.log(`x-request-seal: ${seal}`);
  console.log('\n─── curl command ───');

  if (execute) {
    console.log('🚀 Executing curl...\n');
    try {
      const output = execSync(curlCmd, { encoding: 'utf8' });
      console.log('✅ Response:');
      console.log(output);
    } catch (err) {
      console.error('❌ curl execution failed:');
      console.error(err.stderr || err.message);
      process.exit(1);
    }
  } else {
    console.log(curlCmd);
    console.log('\n💡 To execute automatically, add --execute flag.');
  }
}

if (process.stdin.isTTY) {
  parseArgs();
}
