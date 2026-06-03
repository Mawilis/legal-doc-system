import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, beforeAll, vi } from 'vitest';
import App from '../../src/App';
import React from 'react';

beforeAll(() => {
  const mockContext = {
    fillRect: vi.fn(),
    clearRect: vi.fn(),
    beginPath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    stroke: vi.fn(),
    getImageData: vi.fn(() => ({
      data: new Uint8ClampedArray(1024).fill(255)
    })),
  };
  HTMLCanvasElement.prototype.getContext = vi.fn(() => mockContext);
  HTMLCanvasElement.prototype.toDataURL = vi.fn(() => 'data:image/png;base64,wilsy_auth_token');
});

describe('🏛️ Wilsy OS - Master Controller (App) Integrity', () => {
  it('[AUTHORITY] executes the full 3FA funnel to the Dashboard', async () => {
    const user = userEvent.setup();
    render(<App />);

    const gateBtn = await screen.findByTestId('initialize-gate');
    await user.click(gateBtn);

    const canvas = await screen.findByTestId('signature-canvas');
    fireEvent.mouseDown(canvas, { clientX: 10, clientY: 10 });
    fireEvent.mouseMove(canvas, { clientX: 100, clientY: 100 });
    fireEvent.mouseUp(canvas);

    await waitFor(() => {
      expect(screen.getByTestId('confirm-signature')).toHaveTextContent(/Anchor_Validated/i);
    }, { timeout: 4000 });

    const sealBtn = screen.getByTestId('seal-button');
    await user.click(sealBtn);

    const pulse = await screen.findByTestId('biometric-pulse', {}, { timeout: 6000 });
    await user.click(pulse);

    const passField = await screen.findByTestId('password-input');
    await user.type(passField, 'MASTER_KEY_2026');

    const submitBtn = screen.getByTestId('auth-submit');
    await user.click(submitBtn);

    // FIX: Match against the actual TestID found in the JSDOM dump
    await waitFor(() => {
      expect(screen.getByTestId('dashboard-header')).toBeInTheDocument();
      expect(screen.getByText(/QUANTUM CITADEL/i)).toBeInTheDocument();
    }, { timeout: 8000 });

  }, 20000);
});
