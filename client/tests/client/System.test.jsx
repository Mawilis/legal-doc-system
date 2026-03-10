/* eslint-disable */
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import System from '../../../src/pages/superadmin/System';

jest.mock('../../../src/api/superadmin', () => ({
  fetchSystemSettings: jest.fn().mockResolvedValue({
    timezone: 'SAST',
    backupEnabled: true
  })
}));

test('renders system settings header', async () => {
  render(<System />);
  expect(await screen.findByText(/System Settings/i)).toBeInTheDocument();
});

test('renders system settings values', async () => {
  render(<System />);
  expect(await screen.findByText(/timezone/i)).toBeInTheDocument();
  expect(await screen.findByText(/SAST/i)).toBeInTheDocument();
});
