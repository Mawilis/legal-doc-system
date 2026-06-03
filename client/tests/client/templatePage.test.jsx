/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ Wilsy OS 2050 - 10/10 SuperAdmin Page Template Test Suite                 ║
  ║ Fortune 500 Ready | POPIA §19 | SOC2 | ISO 27001                          ║
  ║ Validates dynamic endpoint fetching, error handling, and AST Rendering.   ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

import TemplatePage from '../../src/pages/superadmin/TEMPLATE.jsx';
import { superAdminAPI } from '../../src/api/superadmin.js';

vi.mock('../../src/api/superadmin.js', () => {
  return {
    superAdminAPI: {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn()
    }
  };
});

describe('TemplatePage (Wilsy OS Citadel)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  it('renders loading state then data', async () => {
    superAdminAPI.get.mockResolvedValueOnce({ data: { revenue: 'R2.3T' } });

    render(<TemplatePage title="Metrics" endpoint="/metrics" />);

    expect(screen.getByText(/Loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/R2.3T/)).toBeInTheDocument();
    });
  });

  it('renders error state on network or endpoint failure', async () => {
    superAdminAPI.get.mockRejectedValueOnce(new Error('Network down'));

    render(<TemplatePage title="Metrics" endpoint="/metrics" />);

    await waitFor(() => {
      expect(screen.getByText(/Network down/i)).toBeInTheDocument();
    });
  });

  it('renders JSON data block when successful', async () => {
    superAdminAPI.get.mockResolvedValueOnce({ data: { tenants: ['t1', 't2'] } });

    render(<TemplatePage title="Tenants" endpoint="/tenants" />);

    await waitFor(() => {
      expect(screen.getByText(/t1/)).toBeInTheDocument();
      expect(screen.getByText(/t2/)).toBeInTheDocument();
    });
  });
});
