/* eslint-disable */
import { render, screen } from '@testing-library/react';
import { expect, test, describe } from 'vitest';
import React from 'react';
import SovereignNodeDashboard from '../../src/components/sovereign/SovereignNodeDashboard';

/**
 * 🏛️ SOVEREIGN MASTER COCKPIT - FORENSIC AUDIT
 * @description Validates the three-pane architecture and asset-based navigation labels.
 */
describe('🏛️ Sovereign Master Cockpit - Forensic Audit', () => {
  test('[MANDATE] verifies the Three-Pane Architecture and Institutional Identity', () => {
    render(<SovereignNodeDashboard />);

    /**
     * 1. VERIFY NAVIGATION RAIL (Sovereign Sidebar)
     * Matches the label in iconManifest.js for the AUDIT_VAULT key.
     */
    expect(screen.getByLabelText(/Forensic Vault/i)).toBeInTheDocument();

    /**
     * 2. VERIFY INTELLIGENCE VIEWPORT (Sovereign_Revenue_Ledger)
     * Validates the Title rendering within the viewport.
     */
    expect(screen.getByTestId('dashboard-title')).toHaveTextContent(/REVENUE LEDGER/i);

    /**
     * 3. VERIFY RISK SENTINEL (Visual HUD Status)
     * Validates that the Risk Sentinel module is rendering its technical baseline.
     */
    expect(screen.getByText(/RISK SENTINEL/i)).toBeInTheDocument();

    /**
     * 4. VERIFY IDENTITY (Operator & Founder Role)
     * Verifies the hardcoded Institutional Identity markers.
     */
    expect(screen.getByText(/OPERATOR:/i)).toBeInTheDocument();
    expect(screen.getByText(/FOUNDER/i)).toBeInTheDocument();
  });
});
