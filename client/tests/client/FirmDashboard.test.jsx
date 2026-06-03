/* eslint-disable */
import { describe, it, expect } from 'vitest';
import { render, screen } from '../test-utils';
import FirmDashboard from '../../src/pages/tenant/FirmDashboard';
import React from 'react';

describe('🏢 Firm Dashboard Integrity Test', () => {
  it('renders firm-specific stats and workspace header', () => {
    render(<FirmDashboard />);
    expect(screen.getByText(/Firm Workspace/i)).toBeDefined();
    expect(screen.getByText(/Active Vaults/i)).toBeDefined();
    expect(screen.getByText(/SECURE TRANSCODER/i)).toBeDefined();
  });

  it('verifies compliance rating visibility', () => {
    render(<FirmDashboard />);
    expect(screen.getByText(/100%/i)).toBeDefined();
  });
});
