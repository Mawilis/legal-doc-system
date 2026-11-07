import React from 'react';
import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import WilsyHeadquartersWorkspace from '../../components/workspaces/WilsyHeadquartersWorkspace.jsx';

vi.mock('../../components/workspaces/MyWorkWorkspace.jsx', () => ({
  default: () => <section><h2>My Work certified task centre</h2></section>,
}));
vi.mock('../../services/api.js', () => ({
  default: {
    get: vi.fn().mockResolvedValue({
      data: {
        items: [{
          employeeId: 'EMP-TEST-1',
          displayName: 'Test Directory Person',
          jobTitle: 'Engineer',
          department: 'Engineering',
          employmentStatus: 'ACTIVE',
          workEmail: 'test@example.invalid',
          workLocation: 'Remote',
        }],
        total: 1,
        limit: 50,
        offset: 0,
        hasMore: false,
      },
    }),
  },
}));

const renderHeadquarters = () => render(
  <MemoryRouter><WilsyHeadquartersWorkspace /></MemoryRouter>,
);

describe('WILSY Headquarters authenticated shell', () => {
  it('presents the company operating environment and daily task centre entry', () => {
    renderHeadquarters();
    expect(screen.getByRole('heading', { name: 'WILSY Headquarters' })).toBeTruthy();
    expect(screen.getByRole('button', { name: /My Work/ })).toBeTruthy();
    expect(screen.getByText(/does not invent headcount, revenue, customer totals/)).toBeTruthy();
  });

  it('mounts the existing My Work workspace rather than a duplicate task projection', () => {
    renderHeadquarters();
    fireEvent.click(screen.getByRole('button', { name: /My Work/ }));
    expect(screen.getByRole('heading', { name: 'My Work certified task centre' })).toBeTruthy();
  });

  it('keeps workforce records unavailable until the HR source is certified', () => {
    renderHeadquarters();
    fireEvent.click(screen.getByRole('button', { name: /Organisation & People/ }));
    expect(await screen.findByText('Authorised workforce directory')).toBeTruthy();
    expect(await screen.findByText('Test Directory Person')).toBeTruthy();
    expect(screen.getByText('test@example.invalid')).toBeTruthy();
  });

  it('separates supported business models from actual customer records', () => {
    renderHeadquarters();
    fireEvent.click(screen.getByRole('button', { name: /Products & Business Portfolio/ }));
    expect(screen.getByText('Importers & exporters')).toBeTruthy();
    expect(screen.getByText('Law firms')).toBeTruthy();
    expect(screen.getByText('Customer portfolio integration pending')).toBeTruthy();
    expect(screen.getByText(/does not imply that a listed business is already a customer/)).toBeTruthy();
  });

  it('does not represent unconnected department services as operational', () => {
    renderHeadquarters();
    fireEvent.click(screen.getByRole('button', { name: /Engineering/ }));
    expect(screen.getByText('Engineering source is not yet connected')).toBeTruthy();
    expect(screen.getByText('Source integration not yet certified')).toBeTruthy();
  });
});
