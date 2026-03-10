/* eslint-disable */
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Audit from '../../../src/pages/superadmin/Audit';

jest.mock('../../../src/api/superadmin', () => ({
  fetchAuditLogs: jest.fn().mockResolvedValue([
    { action: 'Login', user: 'admin@wilsy.co.za', timestamp: '2026-03-10 08:00:00', status: 'Success' }
  ])
}));

test('renders audit trail header', async () => {
  render(<Audit />);
  expect(await screen.findByText(/Audit Trail/i)).toBeInTheDocument();
});

test('renders audit logs table', async () => {
  render(<Audit />);
  expect(await screen.findByText(/Login/i)).toBeInTheDocument();
  expect(await screen.findByText(/admin@wilsy.co.za/i)).toBeInTheDocument();
});
