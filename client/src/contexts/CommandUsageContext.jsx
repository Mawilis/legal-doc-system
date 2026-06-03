/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - COMMAND USAGE TRACKER [V2.0.0-INSTITUTIONAL]                                                                                ║
 * ║ [FORENSIC TELEMETRY | PERSISTENT FREQUENCY SORTING | RESETTABLE SANCTUARY | LOCALSTORAGE + FALLBACK]                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.0.0-INSTITUTIONAL | PRODUCTION READY | INVESTOR-GRADE                                                                        ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | SOVEREIGN BEHAVIORAL ENGINE                                                       ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/contexts/CommandUsageContext.jsx                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated forensic telemetry and resettable usage sanctuary.                                   ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Added error logging, weighted sorting, and dual persistence.                                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'wilsy_command_usage';

const CommandUsageContext = createContext();

/**
 * @function useCommandUsage
 * @description Sovereign hook to access the behavioral engine.
 */
export const useCommandUsage = () => {
  const context = useContext(CommandUsageContext);
  if (!context) {
    throw new Error('useCommandUsage must be used within CommandUsageProvider');
  }
  return context;
};

/**
 * @function CommandUsageProvider
 * @description Orchestrates the persistence and ranking of institutional commands.
 */
export const CommandUsageProvider = ({ children }) => {
  const [usageMap, setUsageMap] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        // Hydrate from sovereign storage
        return new Map(Object.entries(JSON.parse(stored)));
      }
    } catch (err) {
      console.error('⚠️ [CommandUsage] HYDRATION FRACTURE:', err.message);
    }
    return new Map();
  });

  // 🔐 PERSISTENCE PROTOCOL: Synchronize with local storage
  useEffect(() => {
    try {
      const obj = Object.fromEntries(usageMap);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(obj));
    } catch (err) {
      console.error('⚠️ [CommandUsage] PERSISTENCE FRACTURE:', err.message);
    }
  }, [usageMap]);

  /**
   * @function recordCommand
   * @description Increments frequency count for a tactical command ID.
   */
  const recordCommand = useCallback((commandId) => {
    setUsageMap(prev => {
      const newMap = new Map(prev);
      const count = (newMap.get(commandId) || 0) + 1;
      newMap.set(commandId, count);

      // 📡 TELEMETRY HOOK: Ready for real-time dashboard broadcasting
      console.debug(`📡 [CommandUsage] Recorded command: ${commandId} (count=${count})`);

      return newMap;
    });
  }, []);

  /**
   * @function getFrequentCommands
   * @description Returns ranked commands based on frequency and optional weighting.
   * @param {number} limit - Number of top-tier results to return.
   * @param {function} weightFn - Optional logic for recency or custom prioritization.
   */
  const getFrequentCommands = useCallback((limit = 5, weightFn = null) => {
    let entries = Array.from(usageMap.entries());

    // Apply weighted sorting if protocol exists
    if (weightFn) {
      entries = entries.map(([id, count]) => [id, weightFn(id, count)]);
    }

    return entries
      .sort((a, b) => b[1] - a[1]) // Ranked by descending dominance
      .slice(0, limit)
      .map(([id]) => id);
  }, [usageMap]);

  /**
   * @function resetUsage
   * @description Forensically purges usage history to restore sanctuary baseline.
   */
  const resetUsage = useCallback(() => {
    setUsageMap(new Map());
    localStorage.removeItem(STORAGE_KEY);
    console.debug('🧹 [CommandUsage] Usage history purged.');
  }, []);

  return (
    <CommandUsageContext.Provider value={{ recordCommand, getFrequentCommands, resetUsage, usageMap }}>
      {children}
    </CommandUsageContext.Provider>
  );
};

export default CommandUsageProvider;
