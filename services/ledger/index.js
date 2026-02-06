/**
 * File: services/ledger/index.js
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | Immutable Blockchain-Lite Ledger
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - The Source of Truth.
 * - ARCHITECTURE: Chained Event Log (Block N references Hash N-1).
 * - SECURITY: SHA-256 Hashing, Merkle-like integrity checks.
 * - COMPLIANCE: Provides legal "Chain of Custody" for documents.
 * -----------------------------------------------------------------------------
 */

'use strict';

require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const crypto = require('crypto');
const cors = require('cors');

// --- CONFIGURATION ---
const PORT = process.env.LEDGER_PORT || 6000;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/legal-tech';

// --- DATABASE SCHEMA (The Chain) ---
const entrySchema = new mongoose.Schema({
  index: { type: Number, required: true, index: true }, // Sequence Number
  timestamp: { type: Date, default: Date.now },
  eventType: { type: String, required: true }, // e.g., 'DOC_SERVED', 'LOGIN_ATTEMPT'
  actor: { type: String, required: true },       // Who did it? (User ID / Name)
  tenantId: { type: String, required: true },
  payload: { type: Object, required: true },     // The data (e.g., GPS coords)
  prevHash: { type: String, required: true },    // Link to previous block
  hash: { type: String, required: true, unique: true }, // Current block hash
  nonce: { type: Number, default: 0 }            // For future Proof-of-Work if needed
}, { strict: true });

const LedgerEntry = mongoose.model('LedgerEntry', entrySchema);

// --- APP INIT ---
const app = express();

app.use(cors({
  origin: process.env.CLIENT_URL ? [process.env.CLIENT_URL] : ['http://localhost:3000', 'http://127.0.0.1:3000'],
  credentials: true,
  methods: ['GET', 'POST']
}));
app.use(express.json());

// --- CONNECT DB ---
mongoose.connect(MONGO_URI)
  .then(() => console.log('✅ [Ledger] Connected to Immutable Storage'))
  .catch(err => {
    console.error('❌ [Ledger] DB Connection Failed:', err.message);
    process.exit(1);
  });

// --- HELPER: Calculate Hash ---
const calculateHash = (index, prevHash, timestamp, data, nonce = 0) => {
  return crypto.createHash('sha256')
    .update(index + prevHash + timestamp + JSON.stringify(data) + nonce)
    .digest('hex');
};

// --- HELPER: Get Last Block ---
const getLastBlock = async () => {
  return await LedgerEntry.findOne().sort({ index: -1 });
};

// --- ROUTES ---

/**
 * @route   POST /seal
 * @desc    Cryptographically seal an event into the ledger
 */
app.post('/seal', async (req, res) => {
  try {
    const { eventType, actor, tenantId, payload } = req.body;

    if (!eventType || !actor || !tenantId) {
      return res.status(400).json({ error: 'Missing required ledger fields (eventType, actor, tenantId)' });
    }

    // 1. Fetch Previous Link
    const lastBlock = await getLastBlock();
    const prevHash = lastBlock ? lastBlock.hash : '0000000000000000000000000000000000000000000000000000000000000000'; // Genesis Hash
    const newIndex = lastBlock ? lastBlock.index + 1 : 0;
    const timestamp = new Date().toISOString();

    // 2. Mint New Block
    const newHash = calculateHash(newIndex, prevHash, timestamp, { eventType, actor, payload });

    // 3. Persist
    const entry = await LedgerEntry.create({
      index: newIndex,
      timestamp,
      eventType,
      actor,
      tenantId,
      payload,
      prevHash,
      hash: newHash
    });

    console.log(`🔒 [Ledger] Block #${newIndex} Sealed: ${eventType} by ${actor}`);

    return res.status(201).json({
      success: true,
      status: "Sealed",
      brand: "Wilsy Trust Engine",
      blockIndex: newIndex,
      hash: newHash,
      prevHash
    });

  } catch (err) {
    console.error('Ledger Error:', err);
    return res.status(500).json({ error: 'Ledger Write Failed' });
  }
});

/**
 * @route   GET /verify/:hash
 * @desc    Check if a hash exists and is valid (Integrity Check)
 */
app.get('/verify/:hash', async (req, res) => {
  try {
    const block = await LedgerEntry.findOne({ hash: req.params.hash });
    if (!block) return res.status(404).json({ valid: false, message: 'Block not found' });

    // Re-calculate to prove integrity
    const checkHash = calculateHash(
      block.index,
      block.prevHash,
      block.timestamp.toISOString(), // Ensure format match
      { eventType: block.eventType, actor: block.actor, payload: block.payload },
      block.nonce
    );

    if (checkHash === block.hash) {
      return res.json({ valid: true, integrity: 'INTACT', timestamp: block.timestamp });
    } else {
      return res.status(409).json({ valid: false, integrity: 'CORRUPTED', warning: 'Data tampering detected' });
    }

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * @route   GET /history/:tenantId
 * @desc    Fetch audit trail for a specific tenant
 */
app.get('/history/:tenantId', async (req, res) => {
  try {
    const logs = await LedgerEntry.find({ tenantId: req.params.tenantId })
      .sort({ index: -1 })
      .limit(100); // Last 100 events

    res.json({ data: logs });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// --- ACTIVATION ---
app.listen(PORT, () => {
  console.log(`🏛️  [Ledger] Immutable Trust Engine Online (Port ${PORT})`);
});