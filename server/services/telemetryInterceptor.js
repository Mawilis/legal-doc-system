/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TELEMETRY BATCHING ENGINE [V72.0.0-PRODUCTION]                                                                             ║
 * ║ [BATCHED UPLINK | EXPONENTIAL BACKOFF | 429 SATURATION PROTECTION | FORENSIC QUEUE]                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 72.0.0-PRODUCTION | PRODUCTION READY | TRILLION DOLLAR SPEC                                                                  ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/telemetryInterceptor.js                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) – Mandated batched telemetry with exponential backoff to eliminate 429 storms.                 ║
 * ║ • AI Engineering (DeepSeek) – ENHANCED: Added queue persistence (optional), full JSDoc, forensic logging, and memory‑safe batch limit. ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import axios from 'axios';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ============================================================================
// 🔥 CONFIGURATION
// ============================================================================

/**
 * Maximum number of events to send in one batch.
 * @constant {number}
 */
const BATCH_SIZE = 10;

/**
 * Initial backoff delay (ms) when a 429 (Too Many Requests) is received.
 * @constant {number}
 */
const INITIAL_BACKOFF_MS = 1000;

/**
 * Maximum backoff delay (ms) – prevents infinite growth.
 * @constant {number}
 */
const MAX_BACKOFF_MS = 16000;

/**
 * Maximum number of events to keep in memory queue (prevents memory leak under extreme load).
 * @constant {number}
 */
const MAX_QUEUE_SIZE = 5000;

/**
 * Optional disk persistence directory for telemetry queue (enabled if directory exists).
 * @constant {string|null}
 */
const PERSISTENCE_DIR = process.env.TELEMETRY_QUEUE_DIR || null;

// ============================================================================
// 🔥 QUEUE STATE (in‑memory with optional disk fallback)
// ============================================================================

/** @type {Array<Object>} */
let telemetryQueue = [];

/** @type {boolean} */
let isSending = false;

/** @type {number} */
let currentBackoffMs = INITIAL_BACKOFF_MS;

/** @type {NodeJS.Timeout|null} */
let retryTimeout = null;

// ============================================================================
// 🔥 DISK PERSISTENCE (optional, for crash recovery)
// ============================================================================

/**
 * @constant {string} QUEUE_FILE - Path to persistent queue file.
 */
const QUEUE_FILE = PERSISTENCE_DIR ? path.join(PERSISTENCE_DIR, 'telemetry-queue.json') : null;

/**
 * Loads previously persisted queue from disk (if enabled).
 * @returns {void}
 */
function loadPersistedQueue() {
  if (!QUEUE_FILE || !fs.existsSync(QUEUE_FILE)) return;
  try {
    const data = fs.readFileSync(QUEUE_FILE, 'utf8');
    const parsed = JSON.parse(data);
    if (Array.isArray(parsed) && parsed.length > 0) {
      telemetryQueue.push(...parsed);
      console.log(`[TELEMETRY-INTERCEPTOR] Loaded ${parsed.length} events from persistent queue.`);
    }
  } catch (err) {
    console.error('[TELEMETRY-INTERCEPTOR] Failed to load persisted queue:', err.message);
  }
}

/**
 * Persists current queue to disk (if enabled).
 * @returns {void}
 */
function persistQueue() {
  if (!QUEUE_FILE) return;
  try {
    const dir = path.dirname(QUEUE_FILE);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(QUEUE_FILE, JSON.stringify(telemetryQueue.slice(0, MAX_QUEUE_SIZE)), 'utf8');
  } catch (err) {
    console.error('[TELEMETRY-INTERCEPTOR] Failed to persist queue:', err.message);
  }
}

// Load any pending events on startup
loadPersistedQueue();

// ============================================================================
// 🔥 HELPER: Generate forensic event ID (for deduplication on backend)
// ============================================================================

/**
 * Generates a deterministic forensic ID for a telemetry event.
 * @param {Object} event - The telemetry event.
 * @returns {string} SHA256 hash of event core fields.
 */
function generateEventId(event) {
  const core = {
    tenantId: event.tenantId,
    eventType: event.eventType,
    event: event.event,
    source: event.source,
    timestamp: event.metadata?.clientTimestamp || event.timestamp
  };
  const hash = crypto.createHash('sha256').update(JSON.stringify(core)).digest('hex');
  return hash.slice(0, 16);
}

// ============================================================================
// 🔥 BATCH SENDING WITH EXPONENTIAL BACKOFF
// ============================================================================

/**
 * Sends a batch of telemetry events to the backend.
 * Implements exponential backoff on 429 responses and retries failed batches.
 * @async
 * @returns {Promise<void>}
 *
 * @real-world
 *   Called automatically by `enqueueTelemetry`. Coalesces events to reduce network
 *   load and avoid rate‑limiting (429) errors that could cause data loss.
 *
 * @forensic
 *   - Failed batches are re‑queued (at the front) to preserve order.
 *   - Backoff doubles on each 429 up to 16 seconds, preventing saturation.
 *   - All sending attempts are logged to stderr for debugging.
 */
async function sendBatch() {
  if (isSending) return;
  if (telemetryQueue.length === 0) return;

  isSending = true;

  // Take up to BATCH_SIZE events from the front
  const batch = telemetryQueue.splice(0, BATCH_SIZE);
  persistQueue(); // update disk after removal

  try {
    const payload = {
      batch: batch.map(event => ({
        ...event,
        forensicId: generateEventId(event)
      })),
      timestamp: new Date().toISOString(),
      batchSize: batch.length,
      sender: 'telemetryInterceptor'
    };

    await axios.post('/api/telemetry/event', payload, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 10000
    });

    // Success – reset backoff
    currentBackoffMs = INITIAL_BACKOFF_MS;
    if (retryTimeout) clearTimeout(retryTimeout);
    retryTimeout = null;

    console.log(`[TELEMETRY-INTERCEPTOR] Sent batch of ${batch.length} events. Remaining queue: ${telemetryQueue.length}`);
  } catch (err) {
    // Re‑insert batch at the front (preserve order)
    telemetryQueue.unshift(...batch);
    persistQueue();

    const status = err.response?.status;
    if (status === 429) {
      console.warn(`[TELEMETRY-INTERCEPTOR] Rate limited (429). Backing off for ${currentBackoffMs}ms`);
      if (retryTimeout) clearTimeout(retryTimeout);
      retryTimeout = setTimeout(() => {
        retryTimeout = null;
        sendBatch().catch(console.error);
      }, currentBackoffMs);
      // Exponential backoff, but cap at MAX_BACKOFF_MS
      currentBackoffMs = Math.min(currentBackoffMs * 2, MAX_BACKOFF_MS);
    } else {
      console.error('[TELEMETRY-INTERCEPTOR] Failed to send batch:', err.message);
      // For non‑429 errors, retry after a fixed short delay (1 second)
      if (retryTimeout) clearTimeout(retryTimeout);
      retryTimeout = setTimeout(() => {
        retryTimeout = null;
        sendBatch().catch(console.error);
      }, 1000);
    }
  } finally {
    isSending = false;
    // If more events remain, trigger next batch (but avoid overlapping retry timers)
    if (telemetryQueue.length > 0 && !retryTimeout) {
      sendBatch().catch(console.error);
    }
  }
}

// ============================================================================
// 🔥 PUBLIC API
// ============================================================================

/**
 * Enqueues a telemetry event for batched sending.
 * If the queue exceeds MAX_QUEUE_SIZE, the oldest events are dropped (FIFO).
 *
 * @param {Object} event - The telemetry event (must be JSON‑serialisable).
 * @returns {void}
 *
 * @real-world
 *   Called by any service or middleware that needs to emit telemetry without
 *   blocking or risking 429 errors. Events are coalesced and sent in background.
 *
 * @forensic
 *   - Queue length is capped to prevent memory exhaustion.
 *   - Dropped events are logged with a warning.
 *   - Each event is assigned a forensic ID before sending.
 *
 * @example
 * enqueueTelemetry({
 *   tenantId: 'GLOBAL_ROOT',
 *   eventType: 'USER_ACTION',
 *   event: 'LOGIN',
 *   source: 'AuthController',
 *   metadata: { traceId: 'TRC-123', userId: 'usr_456' }
 * });
 */
export function enqueueTelemetry(event) {
  if (!event || typeof event !== 'object') {
    console.warn('[TELEMETRY-INTERCEPTOR] Invalid event ignored');
    return;
  }

  // Enforce maximum queue size (drop oldest)
  if (telemetryQueue.length >= MAX_QUEUE_SIZE) {
    const dropped = telemetryQueue.shift();
    console.warn(`[TELEMETRY-INTERCEPTOR] Queue full, dropped oldest event: ${dropped?.eventType || 'unknown'}`);
  }

  telemetryQueue.push(event);
  persistQueue();

  // Trigger batch sending (non‑blocking)
  sendBatch().catch(err => console.error('[TELEMETRY-INTERCEPTOR] sendBatch error:', err.message));
}

/**
 * Gracefully shuts down the telemetry interceptor, attempting to flush remaining events.
 * @returns {Promise<void>}
 *
 * @real-world
 *   Call this during server shutdown (e.g., in `process.on('SIGTERM')`) to ensure
 *   no telemetry is lost.
 */
export async function flushTelemetryQueue() {
  if (retryTimeout) clearTimeout(retryTimeout);
  retryTimeout = null;
  while (telemetryQueue.length > 0 && !isSending) {
    await sendBatch();
    // Small delay to avoid tight loop
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  if (QUEUE_FILE && fs.existsSync(QUEUE_FILE)) {
    try {
      fs.unlinkSync(QUEUE_FILE);
      console.log('[TELEMETRY-INTERCEPTOR] Persistent queue file cleaned.');
    } catch (err) {
      console.error('[TELEMETRY-INTERCEPTOR] Failed to delete queue file:', err.message);
    }
  }
}

// ============================================================================
// 🔥 GRACEFUL SHUTDOWN HOOKS (optional, if this file is imported early)
// ============================================================================

process.on('beforeExit', () => {
  if (telemetryQueue.length > 0) {
    console.log('[TELEMETRY-INTERCEPTOR] Flushing remaining events before exit...');
    flushTelemetryQueue().catch(console.error);
  }
});

export default {
  enqueueTelemetry,
  flushTelemetryQueue
};
