/**
 * @file Dashboard.test.jsx
 * @module WilsyOS/Tests/Dashboard
 * @author Wilson Khanyezi (Founder & Architect)
 * @description Sovereign Integrity Suite for Wilsy OS Super Admin Dashboard.
 * @epitome "Except the Lord build the house, they labour in vain that build it..." (Psalm 127:1)
 * @collaboration-comments Production-ready test suite synchronized with current sovereign operator mock data and header text specifications.
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import Dashboard from '../../src/pages/superadmin/Dashboard';
import axios from 'axios';

vi.mock('axios');

describe('🏛️ Dashboard (Super Admin) - Sovereign Integrity Suite', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    axios.get.mockResolvedValue({
      data: {
        totalUsers: 10,
        activeTenants: 5,
        pendingAudits: 2,
        systemHealth: 100
      }
    });
  });

  it('renders welcome message with correct sovereign operator name', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Sovereign Operator:/i)).toBeInTheDocument();
      expect(screen.getByText(/Sovereign Master/i)).toBeInTheDocument();
    });
  });

  it('renders header with company & sovereign slogan', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/WILSY OS \/\/ SUPER ADMIN COMMAND/i)).toBeInTheDocument();
      expect(screen.getByText(/Wilsy \(Pty\) Ltd • Vision 2050 • Sovereign Legal Operating System/i)).toBeInTheDocument();
    });
  });

  it('renders stats grid metrics correctly', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Total Users')).toBeInTheDocument();
      expect(screen.getByText('Active Tenants')).toBeInTheDocument();
      expect(screen.getByText('Monthly Revenue')).toBeInTheDocument();
      expect(screen.getByText('Security Score')).toBeInTheDocument();
    });
  });
});
