import React from 'react';
import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import SystemServicesDashboard, { hasSystemServicesCapability } from './SystemServicesDashboard.jsx';

describe('SystemServicesDashboard EOS authority boundary', () => {
  it('fails closed when the EOS workspace projection is absent', () => {
    render(<SystemServicesDashboard />);
    expect(screen.getByText('EOS workspace projection unavailable.')).toBeInTheDocument();
    expect(screen.queryByText('Support cases')).not.toBeInTheDocument();
  });

  it('does not infer capabilities from a role label', () => {
    expect(hasSystemServicesCapability({ role: 'founder' }, 'system_services:queue:read')).toBe(false);
  });

  it('renders only exact capabilities supplied by a ready EOS projection', () => {
    render(
      <SystemServicesDashboard
        workspace={{
          status: 'READY',
          authority: 'EOS_SYSTEM_SERVICES',
          principalId: 'principal-test',
          scope: 'SYSTEM',
          capabilities: ['system_services:queue:read'],
          summary: { openCases: 3 },
          cases: [{ caseId: 'case-1', reference: 'SYS-001', category: 'ACCOUNT_ACCESS', status: 'TRIAGED' }],
        }}
      />,
    );
    expect(screen.getByText('EOS authority verified')).toBeInTheDocument();
    expect(screen.getByText('Support cases')).toBeInTheDocument();
    expect(screen.getByText('SYS-001')).toBeInTheDocument();
    expect(screen.queryByText('Account security')).not.toBeInTheDocument();
  });

  it('does not convert missing metrics into zero', () => {
    render(
      <SystemServicesDashboard
        workspace={{
          status: 'READY',
          authority: 'EOS_SYSTEM_SERVICES',
          principalId: 'principal-test',
          capabilities: ['system_services:queue:read'],
          summary: {},
        }}
      />,
    );
    expect(screen.getByText('—')).toBeInTheDocument();
    expect(screen.queryByText('0')).not.toBeInTheDocument();
  });
});
