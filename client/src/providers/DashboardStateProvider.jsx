/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DASHBOARD STATE PROVIDER [V1.0.0-FG219]                                                                                     ║
 * ║ [EPITOME: INITIAL SNAPSHOT HYDRATION & STREAMING GATEWAY DISTRIBUTOR]                                                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-FG219 | BILLION-DOLLAR ENTERPRISE SOFTWARE | BIBLICAL WORTH COMPLIANT                                                   ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/providers/DashboardStateProvider.jsx                                ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ EPITOME:                                                                                                                               ║
 * ║ Loads initial contract snapshot from GET /dashboard, opens the real-time Server-Sent Events stream, and routes deltas to isolated    ║
 * ║ stores without forcing re-renders across the component tree.                                                                           ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ BIBLICAL WORTH BILLIONS:                                                                                                               ║
 * ║ "Enlarge the place of thy tent, and let them stretch forth the curtains of thine habitations..." — Isaiah 54:2                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Established pure reactive stream-to-slice routing principles.                                        ║
 * ║ • AI Engineering (Gemini) - IMPLEMENTED: Automatic reconnect, stream parsing, and contract hydration suite.                          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { createContext, useEffect, useState } from 'react';
import { hydrateFullDashboard, dispatchStreamDelta } from '../state/dashboardStore.js';

export const DashboardStateContext = createContext({
  isHydrated: false,
  connectionStatus: 'DISCONNECTED',
  error: null
});

export const DashboardStateProvider = ({ children, apiBaseUrl = '' }) => {
  const [isHydrated, setIsHydrated] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('CONNECTING');
  const [error, setError] = useState(null);

  useEffect(() => {
    let eventSource = null;

    const initializeDashboardState = async () => {
      try {
        setConnectionStatus('HYDRATING');
        // 1. Initial Snapshot Load
        const response = await fetch(`${apiBaseUrl}/dashboard`);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to fetch Authoritative Dashboard Contract`);
        }
        const result = await response.json();
        
        if (result.success && result.data) {
          hydrateFullDashboard(result.data);
          setIsHydrated(true);
          setConnectionStatus('LIVE_STREAMING');
        } else {
          throw new Error('Invalid contract format returned from kernel.');
        }

        // 2. Open Real-time Streaming Delta Connection (SSE)
        const streamUrl = `${apiBaseUrl}/stream`;
        eventSource = new EventSource(streamUrl);

        eventSource.onopen = () => {
          setConnectionStatus('LIVE_STREAMING');
        };

        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type && data.payload) {
              dispatchStreamDelta(data.type, data.payload);
            }
          } catch (parseErr) {
            console.error('[WILSY-FG219] Stream Delta Parse Failure:', parseErr);
          }
        };

        eventSource.onerror = () => {
          setConnectionStatus('RECONNECTING');
        };

      } catch (err) {
        setError(err.message);
        setConnectionStatus('ERROR');
      }
    };

    initializeDashboardState();

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [apiBaseUrl]);

  return (
    <DashboardStateContext.Provider value={{ isHydrated, connectionStatus, error }}>
      {children}
    </DashboardStateContext.Provider>
  );
};

export default DashboardStateProvider;
