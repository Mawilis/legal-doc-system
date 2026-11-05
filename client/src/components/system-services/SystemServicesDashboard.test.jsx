import React from 'react';
import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
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
    expect(screen.getAllByText('—')).toHaveLength(4);
    expect(screen.queryByText('0')).not.toBeInTheDocument();
  });


  it('renders only the incident queue and responder inbox capabilities supplied by EOS', () => {
    const onOpenAssignment = vi.fn();
    const onDecideAssignment = vi.fn();
    render(
      <SystemServicesDashboard
        workspace={{
          status: 'READY',
          authority: 'EOS_SYSTEM_SERVICES',
          principalId: 'system-principal-test',
          scope: 'SYSTEM',
          capabilities: ['system_services:queue:read', 'system_services:incident:escalate'],
          summary: {},
        }}
        incidents={[{
          incidentId: 'incident-1',
          category: 'SUSPECTED_COMPROMISE',
          status: 'REPORTED',
          observedAt: '2026-11-05T08:00:00+02:00',
        }]}
        assignments={[{
          assignmentId: 'assignment-1',
          incidentId: 'incident-1',
          status: 'PENDING_ACCEPTANCE',
          revision: 2,
        }]}
        onOpenAssignment={onOpenAssignment}
        onDecideAssignment={onDecideAssignment}
      />,
    );
    expect(screen.getByText('Security incident queue')).toBeInTheDocument();
    expect(screen.getByText('SUSPECTED_COMPROMISE')).toBeInTheDocument();
    expect(screen.getByText('My responder assignments')).toBeInTheDocument();
    expect(screen.getByText(/assignment-1/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Accept' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Decline' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'View incident' }));
    expect(onOpenAssignment).toHaveBeenCalledWith('assignment-1');
    fireEvent.click(screen.getByRole('button', { name: 'Accept' }));
    expect(onDecideAssignment).toHaveBeenCalledWith('assignment-1', 'accept');
    fireEvent.click(screen.getByRole('button', { name: 'Decline' }));
    expect(onDecideAssignment).toHaveBeenCalledWith('assignment-1', 'decline');
  });

  it('does not render responder controls without the exact escalation capability', () => {
    render(
      <SystemServicesDashboard
        workspace={{
          status: 'READY',
          authority: 'EOS_SYSTEM_SERVICES',
          principalId: 'system-principal-test',
          capabilities: ['system_services:queue:read'],
        }}
        assignments={[{
          assignmentId: 'assignment-1',
          incidentId: 'incident-1',
          status: 'PENDING_ACCEPTANCE',
          revision: 0,
        }]}
      />,
    );
    expect(screen.getByText('Security incident queue')).toBeInTheDocument();
    expect(screen.queryByText('My responder assignments')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Accept' })).not.toBeInTheDocument();
  });

});
