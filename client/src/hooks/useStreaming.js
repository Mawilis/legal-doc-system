/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - USE STREAMING HOOK [V1.0.0-PRODUCTION-GRADE]                                                                               ║
 * ║ [EPITOME: ISOLATED CHANNEL-SPECIFIC STREAM SUBSCRIPTION REACT HOOK]                                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | FROZEN ABI COMPLIANT                                           ║
 * ║ ABSOLUTE PATH: client/src/hooks/useStreaming.js                                                                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Absolute mandate: No panel reaches into another panel's data slice.                                 ║
 * ║ • AI Engineering (Codex) - IMPLEMENTED: React hook maintaining channel subscription state with auto-reconnect fallback.              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import { useState, useEffect } from 'react';
import { createStreamConnection } from '../services/streamingService';

/**
 * @function useStreaming
 * @description Subscribes a React component to a streaming channel delta update feed.
 * @param {string} channel - Channel endpoint string.
 * @param {Object} initialSlice - Initial baseline state snapshot.
 * @returns {{ state: Object, isConnected: boolean, error: string|null }}
 */
export function useStreaming(channel, initialSlice = {}) {
  const [sliceState, setSliceState] = useState(initialSlice);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let activeSource = null;
    let reconnectTimer = null;

    const establishConnection = () => {
      try {
        activeSource = createStreamConnection(
          channel,
          (envelope) => {
            setIsConnected(true);
            setError(null);
            if (envelope && envelope.payload) {
              setSliceState((previousSlice) => ({
                ...previousSlice,
                ...envelope.payload
              }));
            }
          },
          (err) => {
            setIsConnected(false);
            setError('Stream disconnected. Retrying...');
            if (activeSource) {
              activeSource.close();
            }
            reconnectTimer = setTimeout(establishConnection, 3000);
          }
        );
      } catch (err) {
        setError(err.message);
        setIsConnected(false);
      }
    };

    establishConnection();

    return () => {
      if (activeSource) {
        activeSource.close();
      }
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
    };
  }, [channel]);

  return { state: sliceState, isConnected, error };
}
