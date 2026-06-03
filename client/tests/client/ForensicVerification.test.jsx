/* eslint-disable */
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '../test-utils';
import ForensicVerification from '../../src/pages/tenant/ForensicVerification';
import React from 'react';

describe('🔗 Forensic Verification Integrity Audit', () => {
  it('renders the hash input and authentication engine', () => {
    render(<ForensicVerification />);
    expect(screen.getByText(/Forensic Verification/i)).toBeDefined();
    expect(screen.getByPlaceholderText(/e.g. 5e884898/i)).toBeDefined();
    expect(screen.getByRole('button', { name: /Authenticate/i })).toBeDefined();
  });

  it('shows verifying state on button click', () => {
    render(<ForensicVerification />);
    const button = screen.getByRole('button', { name: /Authenticate/i });
    fireEvent.click(button);
    expect(screen.getByText(/Verifying.../i)).toBeDefined();
  });
});
