import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Audit_Vault_Security from '../../src/components/sovereign/Audit_Vault_Security';

/**
 * 🏛️ WILSY OS - AUDIT VAULT INTEGRITY SUITE
 * MANDATE: VERIFY 101/10 FOREX PRECISION | SOVEREIGN LOG INTEGRITY
 */
describe('🏛️ Audit Vault & Security - Integrity Suite', () => {

  it('[MANDATE] renders the Vault with Post-Quantum Security status', () => {
    render(<Audit_Vault_Security />);
    expect(screen.getByText(/VAULT_STATUS:/i)).toBeInTheDocument();
    expect(screen.getByText(/LOCKED \[PQE-256\]/i)).toBeInTheDocument();
  });

  it('[FOREX] executes real-world ZAR to USD conversion correctly', () => {
    render(<Audit_Vault_Security />);

    // Baseline check: R 120,450,700,000.00
    // Rate: 0.0531
    // Expected: $ 6,395,932,170.00
    const resultValue = screen.getByText(/\$ 6,395,932,170\.00/);
    expect(resultValue).toBeInTheDocument();
  });

  it('[FOREX] updates valuation dynamically when target currency shifts to EUR', () => {
    render(<Audit_Vault_Security />);
    const selector = screen.getByRole('combobox');

    // Shift to EUR Corridor
    fireEvent.change(selector, { target: { value: 'EUR' } });

    // Baseline R 120,450,700,000.00 * 0.0487 (EUR Rate) = € 5,865,949,090.00
    expect(screen.getByText(/€ 5,865,949,090\.00/)).toBeInTheDocument();
  });

  it('[FOREX] manual input updates global arbitrage result', () => {
    render(<Audit_Vault_Security />);
    const input = screen.getByLabelText(/BASE_ASSET_VALUE \(ZAR\)/i);

    // Manual Audit of R 1,000,000.00
    fireEvent.change(input, { target: { value: '1000000' } });

    // 1M * 0.0531 (USD) = $ 53,100.00
    expect(screen.getByText(/\$ 53,100\.00/)).toBeInTheDocument();
  });

  it('[AUDIT] verifies the presence of forensic access logs', () => {
    render(<Audit_Vault_Security />);
    expect(screen.getByText(/W. KHANYEZI/i)).toBeInTheDocument();
    expect(screen.getByText(/SOVEREIGN_ACCESS_GRANTED/i)).toBeInTheDocument();
    expect(screen.getByText(/\[VERIFIED\]/i)).toBeInTheDocument();
  });

});
