/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - STREAMING SERVICE CLIENT [V1.0.0-PRODUCTION-GRADE]                                                                        ║
 * ║ [EPITOME: CLIENT-SIDE SSE TRANSPORT LAYER CONNECTION MANAGER]                                                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | FROZEN ABI COMPLIANT                                           ║
 * ║ ABSOLUTE PATH: client/src/services/streamingService.js                                                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated zero polling across all console UI components.                                              ║
 * ║ • AI Engineering (Codex) - IMPLEMENTED: Server-Sent Events (SSE) stream manager with robust parsing and error callbacks.              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

/**
 * @function createStreamConnection
 * @description Opens an EventSource SSE connection to a channel endpoint.
 * @param {string} channelUri - Streaming channel endpoint (e.g., '/stream/runtime').
 * @param {Function} onDeltaReceived - Callback triggered when state delta arrives.
 * @param {Function} onError - Callback triggered on stream connection fault.
 * @returns {EventSource} Active EventSource connection object.
 */
export function createStreamConnection(channelUri, onDeltaReceived, onError) {
  if (!channelUri) {
    throw new Error('[STREAM-SERVICE-ERROR] Channel URI is required to create stream connection.');
  }

  const eventSource = new EventSource(channelUri);

  eventSource.onmessage = (event) => {
    try {
      if (!event.data) return;
      const parsedEnvelope = JSON.parse(event.data);
      if (onDeltaReceived) {
        onDeltaReceived(parsedEnvelope);
      }
    } catch (err) {
      console.warn(`[WILSY-STREAM-PARSE-WARN] Failed parsing payload on channel ${channelUri}:`, err);
    }
  };

  eventSource.onerror = (error) => {
    if (onError) {
      onError(error);
    }
  };

  return eventSource;
}
