/* eslint-disable */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '../test-utils';
import Users from '../../src/pages/superadmin/Users';

describe('👤 Users Component (Wilsy Vision 2050)', () => {
  it('renders the user management table with mock data', async () => {
    render(<Users />);

    // Using findBy to handle the async load of the Sovereign Engine
    const header = await screen.findByText(/User Management/i);
    expect(header).toBeDefined();

    const userEmail = screen.getByText(/admin@wilsy.co.za/i);
    expect(userEmail).toBeDefined();
  });
});
