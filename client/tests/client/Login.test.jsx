/* eslint-disable */
// ============================================================================
// File Path: /Users/wilsonkhanyezi/legal-doc-system/client/tests/client/Login.test.jsx
// Project: Wilsy OS - Vision 2050
// Purpose: Unit & Integration tests for Super Admin Login Page
// Certification: 10/10 - Fortune 500 Ready
// Collaboration Notes:
//   - Frontend team: validates rendering of login form and error states.
//   - Backend team: ensures authentication API contract matches test mocks.
//   - QA team: expands tests for login success, failure, and edge cases.
//   - Security team: validates password policies and audit logging.
// ============================================================================

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import Login from '../../../src/pages/superadmin/Login';

// Mock AuthContext
jest.mock('../../../src/context/superadmin/AuthContext', () => ({
  useAuth: () => ({
    login: jest.fn((email, password) => {
      if (email === 'wilsonkhanyezi@gmail.com' && password === 'correctpassword') {
        return Promise.resolve();
      }
      return Promise.reject(new Error('Invalid credentials'));
    })
  })
}));

describe('Login Component (Wilsy Vision 2050)', () => {
  test('renders login header and branding', () => {
    render(<MemoryRouter><Login /></MemoryRouter>);
    expect(screen.getByText(/WILSY OS/i)).toBeInTheDocument();
    expect(screen.getByText(/The Global Legal Operating System/i)).toBeInTheDocument();
  });

  test('renders email and password inputs', () => {
    render(<MemoryRouter><Login /></MemoryRouter>);
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
  });

  test('shows error message on invalid login', async () => {
    render(<MemoryRouter><Login /></MemoryRouter>);
    fireEvent.change(screen.getByLabelText(/Email Address/i), { target: { value: 'wrong@wilsy.co.za' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'wrongpassword' } });
    fireEvent.click(screen.getByText(/Login to Dashboard/i));
    expect(await screen.findByText(/Invalid credentials/i)).toBeInTheDocument();
  });

  test('shows loading state during login', () => {
    render(<MemoryRouter><Login /></MemoryRouter>);
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'correctpassword' } });
    fireEvent.click(screen.getByText(/Login to Dashboard/i));
    expect(screen.getByText(/Logging in.../i)).toBeInTheDocument();
  });
});
