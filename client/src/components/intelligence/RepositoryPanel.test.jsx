/**
 * Epitome: Unit and Integration Test Suite for Repository Intelligence Panel.
 * Collaboration Comments: 
 *   - Architect: Wilsy OS Core Engineering (Wilson Khanyezi)
 *   - Tier: Billion-Dollar Production Grade (v8.0.0-Omega)
 *   - Standards: Vitest compliance, async state verification, fallback validation.
 *   - Biblical Worth Billions Reference: "And the Lord answered me: 'Write the vision; make it plain on tablets, so he may run who reads it.'" — Habakkuk 2:2
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import RepositoryPanel from './RepositoryPanel';

describe('RepositoryPanel Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders loading state initially and then loads repository census data successfully', async () => {
    const mockCensus = {
      pipeline_id: 'PIPE-FG231A-TEST',
      status: 'FG231A_PIPELINE_COMPLETED_AND_SEALED',
      total_engines_executed: 12,
      execution_duration_seconds: 0.001,
      merkle_root_hash: '0xtestmerklehash123456789',
      system_readiness_index: 100.0,
      completion_timestamp: '2026-07-27T09:02:36.274Z'
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCensus,
    });

    render(<RepositoryPanel />);

    // Verify loading state is shown initially
    expect(screen.getByTestId('repo-loading')).toBeDefined();

    // Wait for the data to render
    await waitFor(() => {
      expect(screen.getByTestId('repository-panel')).toBeDefined();
    });

    expect(screen.getByText('PIPE-FG231A-TEST')).toBeDefined();
    expect(screen.getByText('100.00 / 100.00')).toBeDefined();
  });

  it('gracefully falls back to sovereign baseline telemetry when API synchronization fails', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network offline'));

    render(<RepositoryPanel />);

    await waitFor(() => {
      expect(screen.getByTestId('repository-panel')).toBeDefined();
    });

    // Verify fallback pipeline ID is rendered
    expect(screen.getByText('PIPE-FG231A-20260727090236')).toBeDefined();
    expect(screen.getByText('0.00136s')).toBeDefined();
  });
});
