/* eslint-disable */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import InvestorKPIs from '../../../src/components/analytics/InvestorKPIs';

// Mock fetch
global.fetch = vi.fn();

describe('InvestorKPIs Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('sovereignToken', 'mock-token');
  });

  it('should show loading state initially', () => {
    render(<InvestorKPIs />);
    expect(screen.getByText(/LOADING INVESTOR METRICS/i)).toBeDefined();
  });

  it('should display KPIs after loading', async () => {
    const mockKPIs = {
      success: true,
      data: {
        arrFormatted: 'R 1.25M',
        mrrFormatted: 'R 104K',
        ltvToCacRatio: '3.5',
        valuationFormatted: 'R 18.75M',
        churnRate: '2.1',
        churnPrediction: 'LOW RISK',
        runwayMonths: 24,
        grossMargin: 85,
        netRevenueRetention: 98.5,
        quantumSignature: 'DILITHIUM-5:ABC123...'
      }
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockKPIs
    });

    render(<InvestorKPIs />);

    await waitFor(() => {
      expect(screen.getByText(/ARR/i)).toBeDefined();
    });
  });
});
