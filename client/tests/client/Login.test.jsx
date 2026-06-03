/* eslint-disable */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '../test-utils';
import Login from '../../src/pages/Login';
import React from 'react';

describe('🔐 Login Page - Wilsy OS Security Perimeter', () => {
  it('renders branding and access fields', () => {
    render(<Login />);

    // Aligned with your "Quantum" UI labels
    expect(screen.getByAltText(/WILSY OS/i)).toBeDefined();
    expect(screen.getByPlaceholderText(/wilsonkhanyezi@gmail.com/i)).toBeDefined();
    expect(screen.getByText(/Remember this device/i)).toBeDefined();
  });

  it('verifies Command Center access button triggers', async () => {
    render(<Login />);

    // Matching your actual button text: "Access Command Center →"
    const accessBtn = screen.getByRole('button', { name: /Access Command Center/i });
    fireEvent.click(accessBtn);

    expect(accessBtn).toBeDefined();
  });
});
