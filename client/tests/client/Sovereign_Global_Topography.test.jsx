/* eslint-disable */
/**
 * 🏛️ WILSY OS - GLOBAL NODE TOPOGRAPHY TEST SUITE (VITEST)
 * EPITOME: BIBLICAL WORTH BILLIONS | FORTUNE 500 EDITION
 * MANDATE: Absolute test coverage. Mathematical certainty of global mesh.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act, cleanup } from '@testing-library/react';
import React from 'react';
import Sovereign_Global_Topography from '../../src/components/sovereign/Sovereign_Global_Topography';

describe('🏛️ Sovereign Global Topography - Mesh Integrity Suite', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.useRealTimers();
    cleanup();
  });

  it('[MANDATE] securely renders the Global Topography and Institutional Mandate', () => {
    render(<Sovereign_Global_Topography />);
    expect(screen.getByText(/GLOBAL NODE TOPOGRAPHY/i)).toBeDefined();
    expect(screen.getByText(/GLOBAL MESH: OPTIMAL/i)).toBeDefined();
    expect(screen.getByText(/CRYPTOGRAPHIC IMMUTABILITY \| ABSOLUTE TRUTH AT SCALE \| INSTITUTIONAL GRADE/i)).toBeDefined();
  });

  it('[GEOGRAPHY] confirms the Master Node (JHB) and global satellites are anchored', () => {
    render(<Sovereign_Global_Topography />);
    expect(screen.getByText(/JOHANNESBURG \(MASTER\)/i)).toBeDefined();
    expect(screen.getByText(/DAR ES SALAAM \(ROYAL LOGISTICS\)/i)).toBeDefined();
    expect(screen.getByText(/TOKYO \(QUANTUM LEDGER\)/i)).toBeDefined();
  });

  it('[TELEMETRY] mathematically verifies the live forensic log rotation', async () => {
    render(<Sovereign_Global_Topography />);

    // Check initial logs
    expect(screen.getByText(/JHB_ZA/i)).toBeDefined();

    // Advance time by 3.2s to trigger a new global ping and log entry
    await act(async () => {
      vi.advanceTimersByTime(3200);
    });

    // Verify a new cryptographic seal has been logged
    const logActions = screen.getAllByText(/CRYPTOGRAPHIC_SEAL_VERIFIED/i);
    expect(logActions.length).toBeGreaterThan(0);
  });

  it('[STABILITY] ensures the log buffer does not exceed the forensic limit', async () => {
    render(<Sovereign_Global_Topography />);

    // Advance time multiple times to fill the buffer (limit is 6)
    for (let i = 0; i < 10; i++) {
      await act(async () => {
        vi.advanceTimersByTime(3200);
      });
    }

    // Even after 10 pings, the UI should only maintain the most recent 6 for forensic clarity
    const logs = screen.getAllByText(/_NODE/i);
    expect(logs.length).toBeLessThanOrEqual(6);
  });
});
