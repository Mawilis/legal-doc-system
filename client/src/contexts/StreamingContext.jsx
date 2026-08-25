/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - STREAMING CONTEXT PROVIDER [V1.0.0-PRODUCTION-GRADE]                                                                       ║
 * ║ [EPITOME: GLOBAL STREAM TRANSPORT LIFECYCLE AND HYDRATION ORCHESTRATOR]                                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | FROZEN ABI COMPLIANT                                           ║
 * ║ ABSOLUTE PATH: client/src/contexts/StreamingContext.jsx                                                                               ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Enforced snapshot GET /dashboard initialization followed by perpetual stream updates.                ║
 * ║ • AI Engineering (Codex) - IMPLEMENTED: React context provider wrapping visual shell with connectivity telemetry.                      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { createStreamConnection } from '../services/streamingService';

const StreamingContext = createContext(null);

/**
 * @function StreamingProvider
 * @description Provider managing global dashboard connection state.
 */
export function StreamingProvider({ children }) {
  const [streamStatus, setStreamStatus] = useState('INITIALIZING');
  const [lastPulse, setLastPulse] = useState(null);

  useEffect(() => {
    let mainSource = null;

    const connectGlobalDashboard = () => {
      mainSource = createStreamConnection(
        '/stream/dashboard',
        (envelope) => {
          setStreamStatus('LIVE_STREAMING');
          setLastPulse(new Date().toISOString());
        },
        () => {
          setStreamStatus('RECONNECTING');
        }
      );
    };

    connectGlobalDashboard();

    return () => {
      if (mainSource) {
        mainSource.close();
      }
    };
  }, []);

  return (
    <StreamingContext.Provider value={{ streamStatus, lastPulse }}>
      {children}
    </StreamingContext.Provider>
  );
}

/**
 * @function useStreamingContext
 * @description Custom hook to consume global stream connection status.
 */
export function useStreamingContext() {
  const context = useContext(StreamingContext);
  if (!context) {
    throw new Error('[STREAM-CONTEXT-ERROR] useStreamingContext must be used within a StreamingProvider');
  }
  return context;
}
