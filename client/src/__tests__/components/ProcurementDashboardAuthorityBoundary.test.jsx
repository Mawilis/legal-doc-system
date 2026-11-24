/**
 * TITLE: WILSY OS procurement source-boundary client certificate
 * VERSION: v1.0.0-NO-UNVERIFIED-PROCUREMENT-AUTHORITY
 * AUTHORITY: Client regression evidence only; Python EOS owns business authority.
 * EPITOME: Ensures the Procurement surface states its source is unavailable and
 *          cannot present invented operational figures or commands.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/ProcurementDashboardAuthorityBoundary.test.jsx
 * COLLABORATION / OWNERSHIP: Vitest and Testing Library; no database or service is contacted.
 * CERTIFICATION / UPDATE DATE: 2026-11-15
 * CHANGELOG: v1.0.0-NO-UNVERIFIED-PROCUREMENT-AUTHORITY certifies the unavailable
 *            tenant-scoped source state and absence of procurement commands.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Uses no tenant fixture, credential, record, or network transport.
 * TENANT BOUNDARY: No tenant identity is read, selected, or inferred.
 * AUTHORITY BOUNDARY: Presentation-only regression test; no business authority.
 * FINANCIAL AUTHORITY BOUNDARY: No purchase, approval, payment, or settlement occurs.
 */
import React from 'react';
import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import ProcurementDashboard from '../../components/procurement/ProcurementDashboard.jsx';

describe('ProcurementDashboard authority boundary', () => {
  it('shows unavailable tenant-scoped sources without invented metrics or commands', () => {
    render(<ProcurementDashboard/>);

    expect(screen.getByRole('main')).toHaveAttribute('data-procurement-state', 'SOURCE_UNAVAILABLE');
    expect(screen.getByRole('heading', { name: 'Tenant-scoped procurement source unavailable' })).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveTextContent('No operational data or commands are available');

    const capabilities = screen.getByRole('list', { name: 'Unavailable procurement capabilities' });
    expect(within(capabilities).getAllByText(/source unavailable/)).toHaveLength(4);

    expect(screen.queryByRole('button')).not.toBeInTheDocument();
    expect(screen.queryByRole('link')).not.toBeInTheDocument();
    expect(screen.queryByText(/TOTAL VENDORS|OPEN POs|INVENTORY VALUE|125,000/)).not.toBeInTheDocument();
  });
});

/*
 * ARTIFACT: WILSY OS procurement source-boundary client certificate
 * VERSION: v1.0.0-NO-UNVERIFIED-PROCUREMENT-AUTHORITY
 * AUTHORITY BOUNDARY: Test evidence only; Python EOS owns business authority.
 * TENANT POSTURE: No tenant data or identity is accessed.
 * FAIL-CLOSED POSTURE: Unavailable sources remain unavailable, not empty or zero.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no execution occurs here.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
