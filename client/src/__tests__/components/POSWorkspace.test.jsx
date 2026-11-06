import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import POSWorkspace from '../../components/pos/POSWorkspace.jsx';
import api from '../../services/api.js';

vi.mock('../../services/api.js', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}));

describe('authenticated POS daily-use workspace', () => {
  beforeEach(() => {
    api.get.mockResolvedValue({ data: { locations: [{ location_id: 'store-01', assignment_id: 'assignment-01', revision: 0, status: 'ACTIVE' }] } });
    api.post.mockResolvedValue({ data: {} });
  });
  it('presents commercial operations without claiming payment settlement', () => {
    render(<POSWorkspace />);
    expect(screen.getByRole('heading', { name: 'Point of Sale' })).toBeTruthy();
    for (const heading of ['Create a sale', 'Record tender intent', 'Record cash received', 'Create a return intent', 'Create a refund intent']) {
      expect(screen.getByRole('heading', { name: heading })).toBeTruthy();
    }
    expect(screen.getByText(/Kennel EOS retaining financial execution/i)).toBeTruthy();
    expect(screen.getByText(/Options come from the authenticated EOS assignment registry/i)).toBeTruthy();
  });

  it('requires a location selector before attempting a command', () => {
    render(<POSWorkspace />);
    fireEvent.click(screen.getByRole('button', { name: 'Create and record sale' }));
    expect(screen.getByRole('status').textContent).toContain('Choose an active location');
  });
});


describe('assigned location admission', () => {
  beforeEach(() => {
    api.get.mockResolvedValue({ data: { locations: [{ location_id: 'store-01', assignment_id: 'assignment-01', revision: 2, status: 'ACTIVE' }] } });
  });
  it('loads only the server-projected assigned location choices', async () => {
    render(<POSWorkspace />);
    expect(await screen.findByRole('option', { name: 'store-01' })).toBeTruthy();
    expect(api.get).toHaveBeenCalledWith('/pos/locations');
  });
});
