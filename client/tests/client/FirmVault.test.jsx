/* eslint-disable */
import { describe, it, expect } from 'vitest';
import { render, screen } from '../test-utils';
import FirmVault from '../../src/pages/tenant/FirmVault';
import React from 'react';

describe('🔒 Firm Vault Forensic Audit', () => {
  it('renders vault registry and multiple asset verifications', () => {
    render(<FirmVault />);

    expect(screen.getByText(/Legal Vaults/i)).toBeDefined();
    expect(screen.getByText(/High-Court_Filings_2026/i)).toBeDefined();

    // Using getAllByText because multiple vaults are verified
    const verifications = screen.getAllByText(/SHA-256_VERIFIED/i);
    expect(verifications.length).toBeGreaterThan(0);
  });

  it('verifies the immutability storage label', () => {
    render(<FirmVault />);
    expect(screen.getByText(/Storage Architecture: Immutable/i)).toBeDefined();
  });
});
