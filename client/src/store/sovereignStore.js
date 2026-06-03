import { create } from 'zustand';

/**
 * 🏛️ WILSY OS - SOVEREIGN STORE v3.7.0
 * MANDATE: UNIFIED STATE MANAGEMENT | TELEMETRY ORCHESTRATION
 */
export const useSovereignStore = create((set) => ({
  activeModule: 'REVENUE_LEDGER',
  telemetry: { status: 'OPTIMAL', sync: '101/10', latency: '42ms' },
  isProcessing: false,

  setActiveModule: (module) => set({ activeModule: module }),
  setProcessing: (bool) => set({ isProcessing: bool }),
  updateTelemetry: (data) => set((state) => ({
    telemetry: { ...state.telemetry, ...data }
  })),

  // CRITICAL FOR TEST STABILITY
  resetStore: () => set({
    activeModule: 'REVENUE_LEDGER',
    isProcessing: false,
    telemetry: { status: 'OPTIMAL', sync: '101/10', latency: '42ms' }
  }),
}));
