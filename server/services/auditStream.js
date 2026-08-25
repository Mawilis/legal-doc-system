/**
 * ====================================================================================
 * WILSY OS SOVEREIGN FILE
 * ====================================================================================
 * @version    v1.0.4-AUDIT-STREAM-FIXED
 * @authority  Wilsy OS Kennel EOS / Sovereignty Audit Command
 * @epitome    Hardened WebSocket interceptor and audit logging service.
 *             Uses `server.prependListener` to force authentication bypass *before*
 *             any other middleware can intercept the upgrade handshake.
 *             Exports `logAuditEvent` for programmatic audit logging.
 * ====================================================================================
 * @collaboration  Lead Architect @WilsyCore, Network Engineer @SecurityShield
 * @institutional  `prependListener` ensures Wilsy OS owns the upgrade event first.
 *                 Added `logAuditEvent` to support unit tests and enable
 *                 consistent audit logging across the system.
 * @compliance     POPIA §19, GDPR §32, SOC2 §CC7.2
 * ====================================================================================
 * @updated    2026-08-06
 * @history     v1.0.3 - Interceptor logic faulty due to `socket.destroy()`.
 *              v1.0.4 - Added `logAuditEvent` named export for test and system use.
 * ====================================================================================
 */

import { WebSocketServer } from 'ws';
import AuditLog from '../models/AuditLog.js';
import axios from 'axios';
import loggerRaw from '../utils/logger.js';

// @institutional  Handle both ES Module default and named imports for logger
const logger = loggerRaw.default || loggerRaw;

/**
 * @epitome  Initializes the institutional WebSocket audit stream.
 * @institutional  Uses `server.prependListener` to intercept `upgrade` events
 *                 at the highest priority. Logs the exact path to the console
 *                 for instant verification during testing.
 * @param {import('http').Server} server - The native HTTP server instance from `server.js`.
 * @returns {void}
 */
export default function startAuditStream(server) {
  // ============================================================================
  // WEB SOCKET SERVER INITIALIZATION
  // ============================================================================
  const wss = new WebSocketServer({ noServer: true });

  // ============================================================================
  // PREPEND LISTENER (Bypasses Express Auth with Priority)
  // ============================================================================
  server.prependListener('upgrade', (request, socket, head) => {
    const path = request.url || '';
    
    // @institutional  Exposed log to prove the interceptor is firing.
    console.log(`[AUDIT-STREAM-INTERCEPT] Detected upgrade request for path: ${path}`);

    // @institutional  Flexible path matching. Handles both exact matches
    //                 and potential trailing slashes/query params.
    if (path.startsWith('/api/audit/stream')) {
      // @institutional  If matched, hijack the socket and process the WebSocket.
      wss.handleUpgrade(request, socket, head, (ws) => {
        wss.emit('connection', ws, request);
      });
    } else {
      // @institutional  CRITICAL FIX: If we don't intercept, we MUST NOT destroy
      //                 the socket. We simply `return` so Node.js passes this
      //                 upgrade event to the next listener in the chain (usually
      //                 Express, if it has a WebSocket handler).
      return;
    }
  });

  // ============================================================================
  // CONNECTION HANDLER
  // ============================================================================
  wss.on('connection', async (ws, req) => {
    // 1. Extract Kennel EOS Tenant Context
    const tenantId = req.headers['x-tenant-id'] || req.headers['X-Tenant-ID'] || 'MASTER';
    logger.info(`[AUDIT-STREAM] WebSocket connection established for tenant ${tenantId}`);

    // 2. Send connection acknowledgment
    ws.send(JSON.stringify({
      status: 'connected',
      message: 'Audit stream live',
      tenantId,
      timestamp: new Date().toISOString()
    }));

    // 3. Push initial historical forensic events
    try {
      const recentEvents = await AuditLog.find()
        .sort({ timestamp: -1, createdAt: -1 })
        .limit(50)
        .lean()
        .exec();

      ws.send(JSON.stringify({
        type: 'init',
        events: recentEvents,
        count: recentEvents.length
      }));
      logger.debug(`[AUDIT-STREAM] Sent ${recentEvents.length} initial audit events`);
    } catch (err) {
      logger.error('[AUDIT-STREAM] Failed to fetch initial audit events:', err);
      ws.send(JSON.stringify({ type: 'error', message: 'Failed to load historical audit events' }));
    }

    // 4. Poll EOS Kennel Bridge for AI intelligence
    const kennelUrl = process.env.EOS_KENNEL_URL || 'http://127.0.0.1:9095';
    const intelligenceEndpoint = `${kennelUrl}/intelligence`;

    const interval = setInterval(async () => {
      try {
        const response = await axios.get(intelligenceEndpoint, {
          timeout: 3000,
          headers: {
            'X-Tenant-ID': tenantId,
            'Accept': 'application/json'
          }
        });
        const intelligence = response.data;
        if (intelligence && typeof intelligence === 'object') {
          ws.send(JSON.stringify({
            type: 'aiDecision',
            data: {
              agent: intelligence.agent || 'EOS Kennel',
              action: intelligence.action || 'decision',
              reason: intelligence.reason || '',
              reasoning: intelligence.reasoning || '',
              timestamp: intelligence.timestamp || new Date().toISOString(),
              ...intelligence
            }
          }));
          logger.debug('[AUDIT-STREAM] EOS intelligence pushed to client');
        }
      } catch (err) {
        logger.warn('[AUDIT-STREAM] EOS kennel fetch failed:', err.message);
      }
    }, 10000); // Poll every 10 seconds

    // 5. Cleanup on client disconnect
    ws.on('close', () => {
      logger.info(`[AUDIT-STREAM] WebSocket disconnected for tenant ${tenantId}`);
      clearInterval(interval);
    });

    // 6. Error-safe execution for socket errors
    ws.on('error', (err) => {
      logger.error('[AUDIT-STREAM] WebSocket error:', err);
    });
  });

  logger.info('[AUDIT-STREAM] WebSocket server started on path /api/audit/stream (prependListener active)');
}

// ================================================================================
// EXPORTED AUDIT LOGGING FUNCTION (for programmatic use)
// ================================================================================

/**
 * @epitome  Records an audit event to the database and logger.
 * @institutional  This function provides a consistent interface for logging
 *                 audit events from any part of the system. It ensures that
 *                 all events are stored in the AuditLog collection and are
 *                 accompanied by structured metadata for forensic analysis.
 * @param {Object} event - The audit event to log.
 * @param {string} event.action - The action performed (e.g., 'USER_LOGIN', 'INVOICE_CREATED').
 * @param {string} event.tenantId - The tenant identifier (defaults to 'MASTER').
 * @param {string} event.userId - The user identifier (optional).
 * @param {Object} event.metadata - Additional structured data (optional).
 * @param {string} event.timestamp - ISO timestamp (optional, defaults to now).
 * @returns {Promise<Object>} The saved audit log document.
 * @throws {Error} If the event cannot be saved, logs an error but does not throw.
 * @collaboration  Required for unit tests and to unify audit logging across services.
 * @compliance     POPIA §19 (data minimization), GDPR §32 (security), SOC2 §CC7.2 (audit trails).
 */
export async function logAuditEvent(event) {
  try {
    const auditEntry = {
      action: event.action || 'UNKNOWN_ACTION',
      tenantId: event.tenantId || 'MASTER',
      userId: event.userId || null,
      metadata: event.metadata || {},
      timestamp: event.timestamp || new Date().toISOString(),
      // Additional fields from Kennel EOS (can be extended)
      source: event.source || 'SYSTEM',
      severity: event.severity || 'INFO',
    };

    // Use the AuditLog model to save the entry
    const saved = await AuditLog.create(auditEntry);
    logger.debug(`[AUDIT] Logged event: ${auditEntry.action} for tenant ${auditEntry.tenantId}`);
    return saved.toObject ? saved.toObject() : saved;
  } catch (err) {
    logger.error('[AUDIT] Failed to log audit event:', err);
    // Do not rethrow; we want to avoid breaking the caller.
    return null;
  }
}

// ================================================================================
// VERIFICATION & HEALTH CHECK
// ================================================================================
/**
 * @institutional  Operational Seal.
 *
 * @collaboration  End-of-File Sign-off by Lead Architect @WilsyCore on 2026-08-06.
 * @version  v1.0.4-AUDIT-STREAM-FIXED  (Certified)
 */
