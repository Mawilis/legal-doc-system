/**
 * AuditService
 * ---------------------------------------------------------------------------
 * Production-ready, durable, client-side audit emitter for Wilsy OS.
 *
 * Purpose
 * - Best-effort, privacy-first telemetry for UI actions.
 * - Durable persistence (IndexedDB preferred, localStorage fallback).
 * - Batching, retry with exponential backoff + jitter, and graceful shutdown.
 *
 * Key APIs
 * - init(config)         : configure endpoint, headers, tenantId, and options.
 * - log(eventType, data) : fire-and-forget audit emitter; returns payload.
 * - flush()              : force-send queued events (useful in tests / before unload).
 * - shutdown()           : stop timers and flush remaining events.
 * - setHook(name, fn)    : attach test/telemetry hooks (onSend, onError, onPersist).
 *
 * Design Principles
 * - Non-blocking: never throw to UI; errors are logged and retried.
 * - Privacy-first: mask PII (emails) and attach non-PII fingerprint only.
 * - Durable: persist to IndexedDB (preferred) or localStorage fallback when offline.
 * - Observable: returns payload for tests and supports hooks for telemetry.
 *
 * Integration Notes
 * - Call init(...) early in app bootstrap (after auth token is available).
 * - Provide getAuthHeaders() if tokens rotate (function returning headers).
 * - Use AuditService.log(...) across UI components for critical actions.
 *
 * Collaboration
 * - @security: review masking rules and retention policy.
 * - @sre: wire server-side ingestion to append-only store and SIEM.
 * - @qa: add tests for offline persistence, retry, and masking.
 */

const DEFAULT_CONFIG = {
  endpoint: '/api/audits',
  batchSize: 10,
  batchIntervalMs: 3000,
  maxRetries: 5,
  retryBaseMs: 500,
  maxBatchBytes: 256 * 1024, // 256KB
  useIndexedDB: true,
  headers: { 'Content-Type': 'application/json' },
  tenantId: null,
  keepalive: true,
  enableConsoleFallback: true,
  env:
    typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.MODE
      ? import.meta.env.MODE
      : (typeof process !== 'undefined' && process.env && process.env.NODE_ENV) || 'development'
};

/* -------------------------
   Utilities
   ------------------------- */

/** safeString - ensure values are strings for payloads */
function safeString(v) {
  if (v === undefined || v === null) return '';
  if (typeof v === 'string') return v;
  try {
    return JSON.stringify(v);
  } catch {
    return String(v);
  }
}

/** generateCorrelationId - high-entropy id using Web Crypto when available */
function generateCorrelationId() {
  try {
    if (typeof crypto !== 'undefined' && typeof crypto.getRandomValues === 'function') {
      const arr = new Uint8Array(8);
      crypto.getRandomValues(arr);
      const hex = Array.from(arr).map((b) => b.toString(16).padStart(2, '0')).join('');
      return `req_${Date.now().toString(36)}_${hex}`;
    }
  } catch (e) {
    // fall through
  }
  return `req_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 10)}`;
}

/** maskEmail - minimal PII masking for emails used in actor field */
function maskEmail(email) {
  if (!email || typeof email !== 'string') return 'UNKNOWN_ACTOR';
  const parts = email.split('@');
  if (parts.length < 2) return 'INVALID_FORMAT';
  const [local, domain] = parts;
  const visible = Math.max(1, Math.min(3, local.length));
  const maskedLocal = local.substring(0, visible) + '*'.repeat(Math.max(4, local.length - visible));
  return `${maskedLocal}@${domain}`;
}

/** getFingerprint - non-PII device context for audit metadata */
function getFingerprint() {
  try {
    return {
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
      language: typeof navigator !== 'undefined' ? navigator.language : 'unknown',
      platform: typeof navigator !== 'undefined' ? navigator.platform : 'unknown',
      screen:
        typeof window !== 'undefined' && window.screen
          ? `${window.screen.width}x${window.screen.height}`
          : 'unknown',
      timezone: (() => {
        try {
          return Intl.DateTimeFormat().resolvedOptions().timeZone || 'unknown';
        } catch {
          return 'unknown';
        }
      })()
    };
  } catch (e) {
    return { userAgent: 'unknown', language: 'unknown', platform: 'unknown', screen: 'unknown', timezone: 'unknown' };
  }
}

/* -------------------------
   IndexedDB lightweight wrapper
   ------------------------- */

const IDB_DB_NAME = 'wilsy_audit_db';
const IDB_STORE_NAME = 'audit_queue';
let idbSupported = typeof indexedDB !== 'undefined';

function openIdb() {
  return new Promise((resolve, reject) => {
    if (!idbSupported) return reject(new Error('IndexedDB not supported'));
    const req = indexedDB.open(IDB_DB_NAME, 1);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(IDB_STORE_NAME)) {
        db.createObjectStore(IDB_STORE_NAME, { keyPath: 'id' });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error || new Error('Failed to open IndexedDB'));
  });
}

async function idbAdd(entry) {
  const db = await openIdb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(IDB_STORE_NAME, 'readwrite');
    const store = tx.objectStore(IDB_STORE_NAME);
    const r = store.put(entry);
    r.onsuccess = () => resolve(true);
    r.onerror = () => reject(r.error || new Error('idb put failed'));
  });
}

async function idbGetAll() {
  const db = await openIdb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(IDB_STORE_NAME, 'readonly');
    const store = tx.objectStore(IDB_STORE_NAME);
    const r = store.getAll();
    r.onsuccess = () => resolve(r.result || []);
    r.onerror = () => reject(r.error || new Error('idb getAll failed'));
  });
}

async function idbDelete(id) {
  const db = await openIdb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(IDB_STORE_NAME, 'readwrite');
    const store = tx.objectStore(IDB_STORE_NAME);
    const r = store.delete(id);
    r.onsuccess = () => resolve(true);
    r.onerror = () => reject(r.error || new Error('idb delete failed'));
  });
}

/* -------------------------
   LocalStorage fallback helpers
   ------------------------- */

function persistToLocalStorage(entry) {
  try {
    const key = 'wilsy_audit_queue';
    const raw = localStorage.getItem(key);
    const arr = raw ? JSON.parse(raw) : [];
    arr.push(entry);
    // cap to last 1000 entries
    localStorage.setItem(key, JSON.stringify(arr.slice(-1000)));
  } catch (e) {
    // ignore storage errors
  }
}

function drainLocalStorage() {
  try {
    const key = 'wilsy_audit_queue';
    const raw = localStorage.getItem(key);
    if (!raw) return [];
    const arr = JSON.parse(raw) || [];
    localStorage.removeItem(key);
    return arr;
  } catch (e) {
    return [];
  }
}

/* -------------------------
   AuditService core
   ------------------------- */

const AuditService = (function () {
  // Internal state
  let config = { ...DEFAULT_CONFIG };
  let queue = []; // in-memory queue
  let timer = null;
  let sending = false;
  let shutdownFlag = false;
  let hooks = { onSend: null, onError: null, onPersist: null };

  /**
   * init(userConfig)
   * - Configure endpoint, headers, tenantId, and options.
   * - getAuthHeaders can be a function returning headers (for dynamic tokens).
   */
  function init(userConfig = {}) {
    config = { ...DEFAULT_CONFIG, ...userConfig };
    if (config.useIndexedDB && typeof indexedDB === 'undefined') {
      idbSupported = false;
    }
    // Drain persisted localStorage entries into memory on init
    try {
      const persisted = drainLocalStorage();
      if (Array.isArray(persisted) && persisted.length > 0) {
        queue = queue.concat(persisted);
      }
    } catch {
      // ignore
    }
    startTimer();
    return config;
  }

  /**
   * setHook(name, fn)
   * - Attach telemetry/test hooks: 'onSend', 'onError', 'onPersist'
   */
  function setHook(name, fn) {
    if (typeof fn !== 'function') return;
    hooks[name] = fn;
  }

  /**
   * enqueue(entry)
   * - Add an audit entry to in-memory queue and persist durable copy.
   */
  async function enqueue(entry) {
    try {
      queue.push(entry);
      if (hooks.onPersist) hooks.onPersist(entry);
      // Persist durable copy
      if (config.useIndexedDB && idbSupported) {
        try {
          await idbAdd(entry);
        } catch (e) {
          // fallback to localStorage
          persistToLocalStorage(entry);
        }
      } else {
        persistToLocalStorage(entry);
      }
    } catch (e) {
      // swallow; do not block UI
      // eslint-disable-next-line no-console
      console.warn('[AuditService] enqueue failed', e);
    }
  }

  /**
   * buildPayload(eventType, details)
   * - Normalize and mask details, attach fingerprint and correlationId
   */
  function buildPayload(eventType, details = {}) {
    const correlationId = details.correlationId || generateCorrelationId();
    const actor = details.email ? maskEmail(details.email) : (details.actor || 'ANONYMOUS');
    const severity = (details.severity || (String(eventType || '').toUpperCase().includes('FAIL') ? 'WARN' : 'INFO')).toUpperCase();
    const payload = {
      id: `${correlationId}_${Math.random().toString(36).slice(2, 8)}`,
      timestamp: new Date().toISOString(),
      tenantId: details.tenantId || config.tenantId || 'PUBLIC_GATEWAY',
      correlationId,
      eventType: String(eventType || 'UNKNOWN').toUpperCase(),
      severity,
      actor,
      metadata: {
        ...(details.metadata || {}),
        fingerprint: getFingerprint()
      }
    };
    return payload;
  }

  /**
   * log(eventType, details)
   * - Public API: fire-and-forget audit emitter
   * - Returns the payload for tests or further processing
   */
  async function log(eventType, details = {}) {
    try {
      if (shutdownFlag) {
        // If service is shutting down, still attempt to persist locally
        const payload = buildPayload(eventType, details);
        await enqueue(payload);
        return payload;
      }

      const payload = buildPayload(eventType, details);
      await enqueue(payload);

      // If batch size reached, trigger immediate send
      if (queue.length >= config.batchSize) {
        flush().catch(() => { });
      }

      // Development visibility
      if (config.env === 'development' || config.enableConsoleFallback) {
        // eslint-disable-next-line no-console
        console.debug('[AuditService] queued', payload.eventType, payload.correlationId);
      }

      return payload;
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error('[AuditService] log error', e);
      if (hooks.onError) hooks.onError(e);
      return null;
    }
  }

  /** startTimer - periodically flush queue */
  function startTimer() {
    if (timer) clearInterval(timer);
    timer = setInterval(() => {
      if (queue.length > 0) flush().catch(() => { });
    }, config.batchIntervalMs);
  }

  /** stopTimer */
  function stopTimer() {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  }

  /**
   * flush()
   * - Force send queued events. Handles batching, retries, and durable deletion.
   */
  async function flush() {
    if (sending) return;
    sending = true;
    try {
      // Rehydrate persisted entries first (durable)
      let persisted = [];
      if (config.useIndexedDB && idbSupported) {
        try {
          persisted = await idbGetAll();
        } catch (e) {
          persisted = drainLocalStorage();
        }
      } else {
        persisted = drainLocalStorage();
      }

      // Merge persisted entries into queue (dedupe by id)
      const persistedMap = new Map((persisted || []).map((p) => [p.id, p]));
      queue = queue.filter((q) => !persistedMap.has(q.id)).concat(Array.from(persistedMap.values()));

      // Send in batches
      while (queue.length > 0) {
        const batch = queue.slice(0, config.batchSize);
        const batchPayload = { events: batch };
        const body = JSON.stringify(batchPayload);

        // If body too large, reduce batch size heuristically
        if (body.length > config.maxBatchBytes && batch.length > 1) {
          const half = Math.max(1, Math.floor(batch.length / 2));
          queue = queue.slice(half);
          continue;
        }

        // Attempt send with retries
        let attempt = 0;
        let success = false;
        let lastErr = null;
        while (attempt <= config.maxRetries && !success) {
          try {
            const headers = typeof config.getAuthHeaders === 'function' ? (await config.getAuthHeaders()) : config.headers;
            const fetchOptions = {
              method: 'POST',
              headers: { ...config.headers, ...(headers || {}) },
              body,
              keepalive: !!config.keepalive
            };
            const resp = await fetch(config.endpoint, fetchOptions);
            if (resp && (resp.status === 200 || resp.status === 201 || resp.status === 202)) {
              success = true;
              if (hooks.onSend) hooks.onSend(batch);
              // Remove sent entries from durable store
              for (const ev of batch) {
                try {
                  if (config.useIndexedDB && idbSupported) {
                    await idbDelete(ev.id);
                  }
                } catch {
                  // ignore idb delete errors
                }
              }
              // Remove from in-memory queue
              queue = queue.slice(batch.length);
              break;
            } else {
              lastErr = new Error(`Audit endpoint responded ${resp ? resp.status : 'no response'}`);
              attempt++;
              await sleepWithJitter(config.retryBaseMs * Math.pow(2, attempt));
            }
          } catch (err) {
            lastErr = err;
            attempt++;
            await sleepWithJitter(config.retryBaseMs * Math.pow(2, attempt));
          }
        } // end retry loop

        if (!success) {
          if (hooks.onError) hooks.onError(lastErr);
          // eslint-disable-next-line no-console
          console.warn('[AuditService] flush failed after retries', lastErr && lastErr.message ? lastErr.message : lastErr);
          // stop processing further batches to preserve queue for later retry
          break;
        }
      } // end while queue
    } finally {
      sending = false;
    }
  }

  /** sleepWithJitter */
  function sleepWithJitter(ms) {
    const jitter = Math.floor(Math.random() * Math.min(1000, ms));
    return new Promise((resolve) => setTimeout(resolve, ms + jitter));
  }

  /**
   * shutdown()
   * - Graceful shutdown: stop timer, flush, and mark shutdown flag
   */
  async function shutdown() {
    shutdownFlag = true;
    stopTimer();
    try {
      await flush();
    } catch {
      // ignore
    }
  }

  /** flushAllForTests - helper for tests to force send everything synchronously */
  async function flushAllForTests() {
    await flush();
  }

  // Expose public API
  return {
    init,
    log,
    flush,
    shutdown,
    setHook,
    flushAllForTests
  };
})();

export default AuditService;
