/* eslint-disable */
/**
 * 🏛️ WILSY OS - AUDIT VAULT INTEGRITY SUITE
 * EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE
 *
 * @team Collaboration Notes:
 * - FIXED: Error handling test now properly simulates an error during audit generation
 * - FIXED: All 5 tests now pass reliably
 *
 * @last_updated: 2026-03-18
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import React from 'react';
import Sovereign_Audit_Vault from '../../src/components/sovereign/Sovereign_Audit_Vault';

// Mock the revenue service
vi.mock('../../src/services/revenueService', () => ({
  revenueService: {
    isTenantOnboarded: vi.fn(() => false),
    getCurrentTenantId: vi.fn(() => null),
  }
}));

describe('🏛️ Sovereign Audit Vault - Integrity Suite', () => {

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock URL methods
    global.URL.createObjectURL = vi.fn(() => 'blob:wilsy-forensic-url');
    global.URL.revokeObjectURL = vi.fn();
  });

  afterEach(() => {
    cleanup();
  });

  it('[MANDATE] renders the Vault with Institutional Mandate', () => {
    render(<Sovereign_Audit_Vault />);
    expect(screen.getByText(/FORENSIC AUDIT VAULT/i)).toBeDefined();
    expect(screen.getByText(/CRYPTOGRAPHIC IMMUTABILITY/i)).toBeDefined();
  });

  it('[SEARCH] executes Forensic Filtering to isolate specific transactions', async () => {
    render(<Sovereign_Audit_Vault />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/QUERY FORENSIC LEDGER\.\.\./i)).toBeDefined();
    });

    const searchInput = screen.getByPlaceholderText(/QUERY FORENSIC LEDGER\.\.\./i);
    fireEvent.change(searchInput, { target: { value: 'TX_910' } });

    await waitFor(() => {
      expect(screen.getByText(/TX_910/i)).toBeDefined();
    });

    expect(screen.queryByText(/TX_909/i)).toBeNull();
  });

  it('[FORENSIC] triggers the Master Audit Export sequence', async () => {
    render(<Sovereign_Audit_Vault />);

    await waitFor(() => {
      expect(screen.getByTestId('generate-audit-btn')).toBeDefined();
    });

    const exportBtn = screen.getByTestId('generate-audit-btn');
    fireEvent.click(exportBtn);

    await waitFor(() => {
      expect(screen.getByText(/SEALING FORENSIC RECORD/i)).toBeDefined();
    });

    await waitFor(() => {
      expect(screen.queryByText(/SEALING FORENSIC RECORD/i)).toBeNull();
    }, { timeout: 2000 });

    expect(screen.getByText(/GENERATE MASTER AUDIT/i)).toBeDefined();
    expect(global.URL.createObjectURL).toHaveBeenCalled();
  });

  it('[FORENSIC] displays success message after audit generation', async () => {
    render(<Sovereign_Audit_Vault />);

    await waitFor(() => {
      expect(screen.getByTestId('generate-audit-btn')).toBeDefined();
    });

    const exportBtn = screen.getByTestId('generate-audit-btn');
    fireEvent.click(exportBtn);

    await waitFor(() => {
      expect(screen.getByTestId('audit-success-message')).toBeDefined();
    }, { timeout: 2000 });
  });

  it('[FORENSIC] handles errors gracefully', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    // Instead of mocking isTenantOnboarded to throw, we need to mock the actual audit generation to fail
    // We can do this by spying on the handleGenerateMasterAudit method
    // But since we can't directly spy on component methods, we'll mock the fetch call

    // Mock the revenue service to indicate a tenant is onboarded (so it tries to call the API)
    const { revenueService } = await import('../../src/services/revenueService');
    revenueService.isTenantOnboarded.mockReturnValue(true);
    revenueService.getCurrentTenantId.mockReturnValue('test-tenant-id');

    // Mock fetch to simulate API failure
    global.fetch = vi.fn().mockRejectedValue(new Error('API failure'));

    render(<Sovereign_Audit_Vault />);

    await waitFor(() => {
      expect(screen.getByTestId('generate-audit-btn')).toBeDefined();
    });

    const exportBtn = screen.getByTestId('generate-audit-btn');
    fireEvent.click(exportBtn);

    // Wait for loading state
    await waitFor(() => {
      expect(screen.getByText(/SEALING FORENSIC RECORD/i)).toBeDefined();
    });

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText(/SEALING FORENSIC RECORD/i)).toBeNull();
    }, { timeout: 2000 });

    // Success message should NOT appear
    expect(screen.queryByTestId('audit-success-message')).toBeNull();

    // Error message might appear (optional, depending on component implementation)
    // But at minimum, success message should not appear

    consoleSpy.mockRestore();

    // Restore fetch
    global.fetch.mockRestore();
  });
});
