import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Sovereign_Asset_Nexus from '../../src/components/sovereign/Sovereign_Asset_Nexus';

describe('🏛️ Sovereign Asset Nexus - Integrity Suite', () => {
  it('[MANDATE] renders global topography nodes correctly', () => {
    render(<Sovereign_Asset_Nexus />);
    expect(screen.getByText(/South Africa \(HQ\)/i)).toBeInTheDocument();
    expect(screen.getByText(/40% MANDATE/i)).toBeInTheDocument();
  });

  it('[FOREX] converts ZAR baseline to USD valuation', () => {
    render(<Sovereign_Asset_Nexus />);
    const valueDisplay = screen.getByTestId('nexus-converted-value');
    // Baseline R 120.45B * 0.053 (USD Rate) = $ 6,383,887,100.00
    expect(valueDisplay.textContent).toMatch(/\$ 6,383,887,100\.00/);
  });

  it('[SECURITY] toggles system security status via kill switch', () => {
    render(<Sovereign_Asset_Nexus />);
    const killBtn = screen.getByRole('button', { name: /SYSTEM_SECURE/i });

    // Trigger Kill Switch
    fireEvent.click(killBtn);
    expect(killBtn.textContent).toMatch(/TERMINATE_SESSIONS/i);
  });

  it('[TELEMETRY] updates wealth projection based on multiplier input', () => {
    render(<Sovereign_Asset_Nexus />);
    const slider = screen.getByLabelText(/multiplier-slider/i);
    const valueDisplay = screen.getByTestId('nexus-converted-value');

    // Move multiplier to 2.0x
    fireEvent.change(slider, { target: { value: '2.0' } });

    // Expect value to double: $ 6,383,887,100.00 * 2 = $ 12,767,774,200.00
    expect(valueDisplay.textContent).toMatch(/\$ 12,767,774,200\.00/);
  });
});
