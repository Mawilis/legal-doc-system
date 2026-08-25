/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ 🏛️ WILSY OS – BACKFILL TRACE & NONCE SCRIPT [v2.0.0-SOVEREIGN-MIGRATION]                                                             ║
 * ║ AUTHORITY: WILSY OS CORE INFRASTRUCTURE | TERMINAL WORKFLOW COMPLIANT                                                                  ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME: Backfills traceId and signNonce for all existing Invoices and Statements by connecting to the same DB as the main app.       ║
 * ║           Uses simple document‑by‑document updates to avoid aggregation pipeline issues.                                              ║
 * ║ COMPLIANCE: POPIA §19 · GDPR §32 · SOC2 §CC7.2                                                                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.0.0-SOVEREIGN-MIGRATION | PRODUCTION READY                                                                                  ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/scripts/backfillTraceAndNonce.js                                         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import mongoose from 'mongoose';
import crypto from 'node:crypto';
import logger from '../utils/logger.js';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment from server/.env
dotenv.config({ path: path.resolve(__dirname, '../.env') });

// ─── Connection URI from environment ──────────────────────────────────────
const MONGO_URI = process.env.MONGODB_URI || process.env.MONGO_URI;
if (!MONGO_URI) {
  console.error('❌ MONGODB_URI not set in environment. Please set it in server/.env');
  console.error('   Example: MONGODB_URI=mongodb://username:password@localhost:27017/wilsy');
  process.exit(1);
}

// ─── Helper functions (same as pre‑save) ────────────────────────────────
function generateTraceId(tenantId, numberField = null) {
  const tenantPrefix = String(tenantId || 'MASTER').slice(0, 8).toUpperCase();
  const entropy = crypto.randomBytes(16).toString('hex').toUpperCase();
  const base = numberField ? numberField.slice(-8) : entropy.slice(0, 8);
  return `WILSY-TRACE-${tenantPrefix}-${base}-${entropy.slice(0, 8)}`;
}

function generateSignNonce() {
  return crypto.randomBytes(32).toString('hex');
}

// ─── Main backfill ──────────────────────────────────────────────────────
async function backfillTraceAndNonce() {
  try {
    console.log('🔍 Connecting to MongoDB...');
    await mongoose.connect(MONGO_URI);
    console.log('✅ Connected to MongoDB.');

    // Dynamically import models after connection
    const Invoice = (await import('../models/Invoice.js')).default;
    const Statement = (await import('../models/Statement.js')).default;

    // ── Backfill Invoices ──────────────────────────────────────────────
    console.log('📄 Processing Invoices...');
    const invoices = await Invoice.find({
      $or: [
        { traceId: { $exists: false } },
        { traceId: null },
        { traceId: '' },
        { signNonce: { $exists: false } },
        { signNonce: null },
      ],
    });

    let invoiceCount = 0;
    for (const inv of invoices) {
      let modified = false;
      if (!inv.traceId) {
        inv.traceId = generateTraceId(inv.tenantId, inv.invoiceNumber);
        modified = true;
      }
      if (!inv.signNonce) {
        inv.signNonce = generateSignNonce();
        modified = true;
      }
      if (modified) {
        await inv.save({ validateBeforeSave: false }); // skip validation to avoid pre‑save overhead
        invoiceCount++;
        if (invoiceCount % 10 === 0) console.log(`  ... ${invoiceCount} invoices updated`);
      }
    }
    console.log(`✅ Invoices updated: ${invoiceCount} documents modified.`);

    // ── Backfill Statements ──────────────────────────────────────────────
    console.log('📄 Processing Statements...');
    const statements = await Statement.find({
      $or: [
        { traceId: { $exists: false } },
        { traceId: null },
        { traceId: '' },
        { signNonce: { $exists: false } },
        { signNonce: null },
      ],
    });

    let statementCount = 0;
    for (const stmt of statements) {
      let modified = false;
      if (!stmt.traceId) {
        stmt.traceId = generateTraceId(stmt.tenantId, stmt.statementNumber);
        modified = true;
      }
      if (!stmt.signNonce) {
        stmt.signNonce = generateSignNonce();
        modified = true;
      }
      if (modified) {
        await stmt.save({ validateBeforeSave: false });
        statementCount++;
        if (statementCount % 10 === 0) console.log(`  ... ${statementCount} statements updated`);
      }
    }
    console.log(`✅ Statements updated: ${statementCount} documents modified.`);

    console.log('🎉 Backfill completed successfully.');
  } catch (err) {
    console.error('❌ Backfill failed:', err);
    process.exit(1);
  } finally {
    await mongoose.disconnect();
    console.log('🔌 Disconnected from MongoDB.');
  }
}

backfillTraceAndNonce();

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏛️ INSTITUTIONAL CERTIFICATION SEAL — backfillTraceAndNonce.js v2.0.0-SOVEREIGN-MIGRATION
 * ═══════════════════════════════════════════════════════════════════════════════
 */
