/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - REACTIVE SLICE STORE FACTORY [V1.0.0-FG219]                                                                                ║
 * ║ [EPITOME: SUB-MILLISECOND ISOLATED SUBSCRIPTION STORE ENGINE | ZERO POLLING | NATIVE REACT 18/19 INTEGRATION]                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-FG219 | BILLION-DOLLAR ENTERPRISE SOFTWARE | BIBLICAL WORTH COMPLIANT                                                   ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/state/createSliceStore.js                                            ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ BIBLICAL WORTH BILLIONS:                                                                                                               ║
 * ║ "Through wisdom is an house builded; and by understanding it is established: And by knowledge shall the chambers be filled with    ║
 * ║ all precious and pleasant riches." — Proverbs 24:3-4                                                                                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Dictated zero polling, zero cross-reading, and isolated panel re-rendering invariants.              ║
 * ║ • AI Engineering (Gemini) - ARCHITECTED: Lightweight useSyncExternalStore factory engine for sub-millisecond updates.               ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

/**
 * Creates an isolated, pub-sub store slice adhering strictly to FG219 rules.
 * @param {string} sliceName - The unique identifier for this state slice.
 * @param {Object} initialState - Default state slice value.
 */
export const createSliceStore = (sliceName, initialState = {}) => {
  let state = initialState;
  let connectionState = 'DISCONNECTED';
  let lastUpdated = new Date().toISOString();
  const listeners = new Set();

  return {
    getSliceName: () => sliceName,
    
    getSnapshot: () => state,

    getMetaData: () => ({
      sliceName,
      connectionState,
      lastUpdated
    }),

    subscribe: (listener) => {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },

    setConnectionState: (status) => {
      connectionState = status;
      listeners.forEach((listener) => listener());
    },

    setInitialState: (data) => {
      if (data === undefined || data === null) return;
      state = data;
      lastUpdated = new Date().toISOString();
      connectionState = 'LIVE_STREAMING';
      listeners.forEach((listener) => listener());
    },

    mergeDelta: (deltaPayload) => {
      if (!deltaPayload || typeof deltaPayload !== 'object') return;
      if (Array.isArray(state)) {
        state = Array.isArray(deltaPayload) ? deltaPayload : [...state, deltaPayload];
      } else {
        state = { ...state, ...deltaPayload };
      }
      lastUpdated = new Date().toISOString();
      listeners.forEach((listener) => listener());
    }
  };
};
