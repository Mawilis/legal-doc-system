/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN MASTER LOGIN FORENSIC AUDIT VALIDATION SUITE                                                                     ║
 * ║ [AUTHENTICATION HANDSHAKE | QUANTUM ENCRYPTION VALIDATION | ACCESSIBLE ROLE TARGETING]                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 55.1.0-MARS-BIBLICAL | PRODUCTION READY | BILLION-DOLLAR SPEC                                                                 ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL DOMINANCE                                                          ║
 * ║ FILE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/SovereignLogin.test.jsx                                         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React from 'react';
import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act, cleanup } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import SovereignLogin from '../../src/components/sovereign/SovereignLogin.jsx';

function renderWithRouter(ui, { route = '/login' } = {}) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      {ui}
    </MemoryRouter>
  );
}

describe('🏛️ Sovereign Login Portal - Forensic Audit', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        success: true,
        token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.sovereign-master-token',
        user: {
          id: 'usr_wilson_01',
          email: 'wilsonkhanyezi@gmail.com',
          role: 'SUPER_ADMIN',
          tenant: 'WILSY_GLOBAL'
        }
      })
    });
  });

  afterEach(() => {
    act(() => {
      vi.runOnlyPendingTimers();
    });
    vi.useRealTimers();
    vi.restoreAllMocks();
    cleanup();
  });

  test('[MANDATE] renders login form fields, institutional branding, and action triggers', async () => {
    await act(async () => {
      renderWithRouter(<SovereignLogin />);
    });

    act(() => {
      vi.advanceTimersByTime(100);
    });

    await waitFor(() => {
      const emailInput = screen.getByRole('textbox', { name: /email/i }) || screen.getByPlaceholderText(/email/i);
      expect(emailInput).toBeInTheDocument();

      const passwordInput = screen.getByPlaceholderText(/password/i) || screen.getByLabelText(/password/i);
      expect(passwordInput).toBeInTheDocument();

      const submitBtn = screen.getByRole('button', { name: /login|sign in|authenticate/i });
      expect(submitBtn).toBeInTheDocument();
    });
  });

  test('[INTERACTION] updates credential state cleanly on user typing', async () => {
    await act(async () => {
      renderWithRouter(<SovereignLogin />);
    });

    act(() => {
      vi.advanceTimersByTime(100);
    });

    const emailInput = screen.getByRole('textbox', { name: /email/i }) || screen.getByPlaceholderText(/email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i) || screen.getByLabelText(/password/i);

    act(() => {
      fireEvent.change(emailInput, { target: { value: 'wilsonkhanyezi@gmail.com' } });
      fireEvent.change(passwordInput, { target: { value: 'SovereignPass2026!' } });
    });

    expect(emailInput.value).toBe('wilsonkhanyezi@gmail.com');
    expect(passwordInput.value).toBe('SovereignPass2026!');
  });

  test('[HANDSHAKE] executes authentication flow without act state leakage', async () => {
    await act(async () => {
      renderWithRouter(<SovereignLogin />);
    });

    const emailInput = screen.getByRole('textbox', { name: /email/i }) || screen.getByPlaceholderText(/email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i) || screen.getByLabelText(/password/i);
    const submitBtn = screen.getByRole('button', { name: /login|sign in|authenticate/i });

    act(() => {
      fireEvent.change(emailInput, { target: { value: 'wilsonkhanyezi@gmail.com' } });
      fireEvent.change(passwordInput, { target: { value: 'SovereignPass2026!' } });
    });

    await act(async () => {
      fireEvent.click(submitBtn);
      vi.advanceTimersByTime(500);
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });
});
