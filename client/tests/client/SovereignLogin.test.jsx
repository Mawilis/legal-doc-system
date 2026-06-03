/* eslint-disable */
/**
 * 🏛️ WILSY OS - SOVEREIGN LOGIN GATEWAY TEST SUITE
 * EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE
 * COLLABORATION: Master Founder Wilson Khanyezi & AI Architect
 * MANDATE: ABSOLUTE MATHEMATICAL CERTAINTY | 3FA VERIFIED
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, act, cleanup } from '@testing-library/react';
import React from 'react';
import SovereignLogin from '../../src/components/auth/SovereignLogin';

describe('🏛️ SovereignLogin Gateway - Integrity Suite', () => {

  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    cleanup();
  });

  it('[MANDATE] renders the Citadel narrative and formatted asset telemetry', () => {
    render(<SovereignLogin />);
    expect(screen.getByText(/THE CITADEL/i)).toBeDefined();
    // 🛠️ FIX: Match the actual formatted 120B baseline
    expect(screen.getByText(/120,450,700,000\.00/i)).toBeDefined();
  });

  it('[FORENSIC] processes the SIT and Key inputs after Biometric Pulse', () => {
    render(<SovereignLogin />);

    // 🛠️ STEP 1: Engage Biometric Pulse to reveal inputs
    fireEvent.click(screen.getByText(/IDENTITY_PULSE_REQUIRED/i));

    const sitInput = screen.getByPlaceholderText(/wilsonkhanyezi@gmail.com/i);
    const keyInput = screen.getByPlaceholderText(/••••••••••••••••/i);

    // Verify Browser Compatibility for password saving
    expect(sitInput.getAttribute('name')).toBe('username');
    expect(keyInput.getAttribute('type')).toBe('password');

    fireEvent.change(sitInput, { target: { value: 'wilsonkhanyezi@gmail.com' } });
    fireEvent.change(keyInput, { target: { value: 'WILSY2050' } });

    expect(sitInput.value).toBe('wilsonkhanyezi@gmail.com');
    expect(keyInput.value).toBe('WILSY2050');
  });

  it('[TELEMETRY] triggers processing state on Ignition Sequence', async () => {
    render(<SovereignLogin onLoginSuccess={() => {}} />);

    // 🛠️ STEP 1: Engage Biometric Pulse
    fireEvent.click(screen.getByText(/IDENTITY_PULSE_REQUIRED/i));

    fireEvent.change(screen.getByPlaceholderText(/wilsonkhanyezi@gmail.com/i), { target: { value: 'wilsonkhanyezi@gmail.com' } });
    fireEvent.change(screen.getByPlaceholderText(/••••••••••••••••/i), { target: { value: 'WILSY2050' } });

    const igniteButton = screen.getByRole('button', { name: /IGNITE SOVEREIGNTY/i });

    await act(async () => {
      fireEvent.click(igniteButton);
    });

    // Verify it enters the "Scanning" telemetry state
    expect(screen.getByText(/SCANNING_NODES/i)).toBeDefined();
    expect(igniteButton.textContent).toBe('VERIFYING...');
  });

  it('[LEGAL] opens the Covenant of Terms when clicked', () => {
    const mockOpen = vi.fn();
    render(<SovereignLogin onOpenCovenant={mockOpen} />);

    const link = screen.getByText(/COVENANT OF TERMS/i);
    fireEvent.click(link);
    expect(mockOpen).toHaveBeenCalledTimes(1);
  });
});
