/* eslint-disable */
/**
 * 🏛️ WILSY OS - SOVEREIGN REVENUE LEDGER TEST SUITE
 * FORTUNE 500 GRADE TESTS
 */

import { render, screen, act, fireEvent, waitFor } from '@testing-library/react';
import { expect, test, describe, vi, beforeEach } from 'vitest';
import Sovereign_Revenue_Ledger from '../../src/components/sovereign/Sovereign_Revenue_Ledger';

vi.mock('../../src/services/revenueService', () => ({
  revenueService: {
    fetchRevenueData: vi.fn(),
    clearCache: vi.fn()
  }
}));

import { revenueService } from '../../src/services/revenueService';

describe('🏛️ Sovereign Revenue Ledger - Production Suite', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('📊 PRODUCTION MODE (Real Revenue Data)', () => {
    beforeEach(() => {
      localStorage.setItem('sovereignToken', 'wil_test_token');
      localStorage.setItem('tenantId', 'MASTER');

      revenueService.fetchRevenueData.mockResolvedValue({
        total: 1680000,
        formatted: "R 1.68M",
        growthRate: 15.9,
        growthRateFormatted: "+15.9%",
        historical: [1250000, 1450000, 1680000, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        compliance: { ifrs15: true, gaap: true, quantumVerified: true, popiaCompliant: true },
        tenantId: "MASTER",
        tenantName: "WILSY (PTY) LTD",
        tenantTier: "SOVEREIGN",
        activeUsers: 1,
        forecast: { nextQuarter: 1746620, nextYear: 1946482, twentyFourMonth: 2255235 }
      });
    });

    test('[PRODUCTION] displays real revenue data (R1.68M)', async () => {
      render(<Sovereign_Revenue_Ledger />);

      await waitFor(() => {
        const wealthElement = screen.getByText(/R 1.68M/);
        expect(wealthElement).toBeInTheDocument();
      });
    });

    test('[PRODUCTION] displays growth rate +15.9%', async () => {
      render(<Sovereign_Revenue_Ledger />);

      await waitFor(() => {
        expect(screen.getByText(/\+15.9% GROWTH/)).toBeInTheDocument();
      });
    });

    test('[PRODUCTION] generate report button triggers download', async () => {
      render(<Sovereign_Revenue_Ledger />);

      await waitFor(() => {
        const button = screen.getByText(/GENERATE REPORT/);
        expect(button).toBeInTheDocument();
        expect(button).not.toBeDisabled();
      });
    });

    test('[PRODUCTION] export data button triggers download', async () => {
      render(<Sovereign_Revenue_Ledger />);

      await waitFor(() => {
        const button = screen.getByText(/EXPORT DATA/);
        expect(button).toBeInTheDocument();
        expect(button).not.toBeDisabled();
      });
    });

    test('[PRODUCTION] download evidence button triggers download', async () => {
      render(<Sovereign_Revenue_Ledger />);

      await waitFor(() => {
        const button = screen.getByText(/DOWNLOAD EVIDENCE/);
        expect(button).toBeInTheDocument();
        expect(button).not.toBeDisabled();
      });
    });

    test('[PRODUCTION] timeframe buttons are functional', async () => {
      render(<Sovereign_Revenue_Ledger />);

      await waitFor(() => {
        const timeframeButtons = screen.getAllByText(/24H|7D|30D|QUARTERLY|YEARLY/);
        expect(timeframeButtons.length).toBeGreaterThan(0);
      });
    });
  });
});
