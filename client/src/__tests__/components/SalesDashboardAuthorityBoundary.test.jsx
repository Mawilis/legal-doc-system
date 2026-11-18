/**
 * TITLE: WILSY OS Sales Dashboard Authority Boundary Tests
 * VERSION: v1.0.0-EOS-SALES-SOURCE-REQUIRED
 * AUTHORITY: Client regression tests only; Python EOS owns Sales authority.
 * EPITOME: Prove the unsupported Sales route cannot present zero-data as live
 *          or send browser requests without an EOS source contract.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/SalesDashboardAuthorityBoundary.test.jsx
 * COLLABORATION / OWNERSHIP: Vitest and React Testing Library exercise SalesDashboard.
 * CERTIFICATION / UPDATE DATE: 2026-11-15
 * CHANGELOG: v1.0.0-EOS-SALES-SOURCE-REQUIRED verifies explicit unavailable
 *            posture, absence of invented metrics/actions, and no network call.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic rendering only; no identity or tenant fixture.
 * TENANT BOUNDARY: No tenant data or credentials are used.
 * AUTHORITY BOUNDARY: Tests prove the UI creates no business authority.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive execution authority.
 */
import React from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import SalesDashboard from '../../components/sales/SalesDashboard.jsx';

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe('SalesDashboard EOS authority boundary', () => {
  it('shows an explicit source-unavailable state without fake zero metrics or actions', () => {
    vi.stubGlobal('fetch', vi.fn());

    render(<SalesDashboard />);

    expect(screen.getByRole('main')).toHaveAttribute('data-sales-source-state', 'SOURCE_UNAVAILABLE');
    expect(screen.getByRole('heading', { name: 'Sales pipeline is unavailable' })).toBeInTheDocument();
    expect(screen.getByText('SALES_PIPELINE_SOURCE_UNAVAILABLE')).toBeInTheDocument();
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
    expect(screen.queryByText(/pipeline\s*0|quotes\s*0|orders\s*0|commissions\s*0|forecasts\s*0/i)).not.toBeInTheDocument();
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });
});

/*
 * ARTIFACT: SalesDashboardAuthorityBoundary.test.jsx
 * VERSION: v1.0.0-EOS-SALES-SOURCE-REQUIRED
 * AUTHORITY BOUNDARY: Presentation regression proof only; no Sales authority.
 * TENANT POSTURE: No tenant or user record is created or read.
 * FAIL-CLOSED POSTURE: Missing source remains visibly unavailable.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
