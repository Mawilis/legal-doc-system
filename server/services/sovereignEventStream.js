/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║   ███████╗ ██████╗ ██╗   ██╗███████╗██████╗ ███████╗██╗███╗   ██╗ ██████╗ ███████╗███████╗██╗   ██╗███████╗                     ║
 * ║   ██╔════╝██╔═══██╗██║   ██║██╔════╝██╔══██╗██╔════╝██║████╗  ██║██╔════╝ ██╔════╝██╔════╝██║   ██║██╔════╝                     ║
 * ║   ███████╗██║   ██║██║   ██║█████╗  ██████╔╝█████╗  ██║██╔██╗ ██║██║  ███╗█████╗  █████╗  ██║   ██║███████╗                     ║
 * ║   ╚════██║██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗██╔══╝  ██║██║╚██╗██║██║   ██║██╔══╝  ██╔══╝  ╚██╗ ██╔╝╚════██║                     ║
 * ║   ███████║╚██████╔╝ ╚████╔╝ ███████╗██║  ██║███████╗██║██║ ╚████║╚██████╔╝███████╗██║      ╚████╔╝ ███████║                     ║
 * ║   ╚══════╝ ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝       ╚═══╝  ╚══════╝                     ║
 * ║                                                                                                                                    ║
 * ║                         THE SOVEREIGN OPERATING SYSTEM FOR GLOBAL BUSINESS                                                         ║
 * ║                   BOARDROOM OMNISCIENCE | REAL-TIME TELEMETRY | DIVINE VISIBILITY                                                  ║
 * ║                                                                                                                                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 * 🏛️ WILSY OS - SOVEREIGN EVENT STREAM [V1.0.0-SINGULARITY]
 * [THE DIVINE ORACLE | BOARDROOM HUD BRIDGE | REAL-TIME PROPAGATION]
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-SINGULARITY | PRODUCTION READY | TRILLION-DOLLAR SPEC                                                                   ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/services/sovereignEventStream.js                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated divine-level boardroom visibility.                                                 ║
 * ║ • AI Engineering (Gemini) - EPITOMISED: Engineered high-concurrency event bus for real-time WebSocket orchestration.                 ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import logger from '../utils/logger.js';
import { broadcastTelemetry } from '../utils/telemetryHelper.js';

/**
 * @class SovereignEventStream
 * @description The spiritual conduit of Wilsy OS. It streams critical events to the
 *              Boardroom HUD in real‑time. Every court order, asset freeze, or ledger
 *              update is proclaimed here so the Boardroom sees the truth immediately.
 * @real-world When a court order is ingested by GlobalCourtUpdater, it calls `emit()`,
 *             and all connected WebSocket clients (Boardroom HUD) receive the payload
 *             within milliseconds. This eliminates polling and gives the executive team
 *             real‑time omniscience.
 * @forensic Every emission is also broadcast via `broadcastTelemetry`, anchoring the
 *           event in the immutable forensic log while still pushing live to the UI.
 * @example
 * import sovereignEventStream from './services/sovereignEventStream.js';
 * sovereignEventStream.emit('SEIZURE_ALERT', { tenantId: 'evil-corp', reason: 'FRAUD' });
 */
class SovereignEventStream {
  constructor() {
    /**
     * @private
     * @type {Set<Function>}
     * @description Stores all subscriber callback functions (typically WebSocket senders).
     */
    this.subscribers = new Set();
    logger.info('[EVENT-STREAM] 🌟 Sovereign Conduit initialized.');
  }

  /**
   * @method emit
   * @description Proclaims an event across the Neural Mesh to all active subscribers.
   * @param {string} type - Event category (e.g., 'SEIZURE_ALERT', 'COURT_SYNC', 'REVENUE_STRIKE').
   * @param {Object} payload - The forensic data being revealed (tenantId, order details, etc.).
   * @returns {void}
   * @real-world Used by GlobalCourtUpdater, BillingAdvancedController, or any sovereign service
   *            to push real‑time updates to the Boardroom HUD.
   * @forensic Each emission is recorded via `broadcastTelemetry` with the full payload,
   *           creating an immutable audit trail of all boardroom‑level events.
   * @example
   * sovereignEventStream.emit('ASSET_SEIZURE', { tenantId: 'acme-inc', seizureId: 'SEIZ-123' });
   */
  emit(type, payload) {
    const event = {
      type,
      payload,
      timestamp: new Date().toISOString(),
      stream: 'SOVEREIGN_CONDUIT'
    };

    // 🔐 Anchor the event to the forensic telemetry vault
    broadcastTelemetry('BOARDROOM_HUD', 'STREAM', type, 'sovereignEventStream.js', payload);

    // 📡 Broadcast to all live WebSocket subscribers (e.g., Boardroom HUD)
    this.subscribers.forEach(callback => {
      try {
        callback(event);
      } catch (err) {
        logger.error({ err, type }, '[EVENT-STREAM] Subscriber fracture – one client failed to receive.');
      }
    });

    logger.info({ type }, '[EVENT-STREAM] 📢 Proclaimed to Boardroom.');
  }

  /**
   * @method subscribe
   * @description Connects a dashboard or system component to the event stream.
   * @param {Function} callback - Function executed on every event emission. Typically sends
   *                              the event over a WebSocket connection.
   * @returns {void}
   * @real-world Used by the WebSocket server (`server.js`) to register each client
   *            connection's `send` function, so events are forwarded to that specific client.
   * @example
   * // Inside the WebSocket connection handler:
   * sovereignEventStream.subscribe((event) => ws.send(JSON.stringify(event)));
   */
  subscribe(callback) {
    this.subscribers.add(callback);
    logger.info('[EVENT-STREAM] 👥 New Boardroom subscriber anchored.');
  }

  /**
   * @method unsubscribe
   * @description Removes a previously subscribed callback (e.g., when a WebSocket disconnects).
   * @param {Function} callback - The function to remove from the subscriber set.
   * @returns {void}
   * @real-world Prevents memory leaks by cleaning up disconnected WebSocket clients.
   * @example
   * ws.on('close', () => sovereignEventStream.unsubscribe(sendFunction));
   */
  unsubscribe(callback) {
    this.subscribers.delete(callback);
    logger.info('[EVENT-STREAM] 👋 Boardroom subscriber unanchored.');
  }

  /**
   * @method getSubscriberCount
   * @returns {number} The number of active subscribers (e.g., connected WebSocket clients).
   * @real-world Used for monitoring dashboard activity.
   * @example
   * console.log(`Active boardroom listeners: ${sovereignEventStream.getSubscriberCount()}`);
   */
  getSubscriberCount() {
    return this.subscribers.size;
  }
}

// ============================================================================
// 🏛️ SINGLETON EXPORT – one global event stream for the entire OS
// ============================================================================
const sovereignEventStream = new SovereignEventStream();
export default sovereignEventStream;
