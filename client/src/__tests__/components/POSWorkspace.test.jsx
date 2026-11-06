import React from 'react';
import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import POSWorkspace from '../../components/pos/POSWorkspace.jsx';

vi.mock('../../services/api.js', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}));

describe('authenticated POS daily-use workspace', () => {
  it('presents commercial operations without claiming payment settlement', () => {
    render(<POSWorkspace />);
    expect(screen.getByRole('heading', { name: 'Point of Sale' })).toBeTruthy();
    for (const heading of ['Create a sale', 'Record tender intent', 'Record cash received', 'Create a return intent', 'Create a refund intent']) {
      expect(screen.getByRole('heading', { name: heading })).toBeTruthy();
    }
    expect(screen.getByText(/Kennel EOS retaining financial execution/i)).toBeTruthy();
    expect(screen.getByText(/Location input is never treated as access authority/i)).toBeTruthy();
  });

  it('requires a location selector before attempting a command', () => {
    render(<POSWorkspace />);
    fireEvent.click(screen.getByRole('button', { name: 'Create and record sale' }));
    expect(screen.getByRole('status').textContent).toContain('Enter a location ID');
  });
});
