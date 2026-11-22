/**
 * TITLE: WILSY OS Project Participant Command UI Certificate
 * VERSION: v1.3.0-FAULT-ISOLATED-PROJECT-PEOPLE-CERT
 * AUTHORITY: Synthetic client contract tests; EOS alone owns IAM and grants.
 * EPITOME: Verify source choices, explicit role grant/revoke, fresh state
 *          readback and denial of invented members or session-scoped outcomes.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/ProjectParticipantsPanel.test.jsx
 * COLLABORATION / OWNERSHIP: ProjectParticipantsPanel; vi mocks api.js only.
 * CERTIFICATION / UPDATE DATE: 2026-11-18
 * CHANGELOG: v1.3.0-FAULT-ISOLATED-PROJECT-PEOPLE-CERT verifies current participant listing remains readable after independent eligible-directory 403, distinguishes actual HTTP 403 from network loss, and prevents any grant or revocation without both verified current EOS sources.
 * CHANGELOG: v1.2.0-ACTIVE-PARTICIPATION-LABEL-CERT scopes contributor label checks to the active participant list rather than the adjacent role picker.
 * CHANGELOG: v1.1.0-HUMAN-ONLY-PARTICIPANT-CERT ensures audit-only
 *          revision numbers never appear in active participant labels.
 * CHANGELOG: v1.0.0-SOURCE-VERIFIED-PARTICIPANT-LIFECYCLE-CERT adds an actual
 *          source list -> grant -> readback -> revoke -> readback UI loop.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; WCAG 2.2 AA.
 * SECURITY / PRIVACY POSTURE: Synthetic opaque members and tenant.
 * TENANT BOUNDARY: All API replies explicitly identify one tenant/project.
 * AUTHORITY BOUNDARY: No real authentication, IAM or employment is tested.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import React from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }));
vi.mock('../../services/api.js', () => ({ default: api }));
import ProjectParticipantsPanel from '../../components/workspaces/ProjectParticipantsPanel.jsx';

const tenantId = 'projects-test-tenant';
const principalId = 'tenant-owner';
const projectId = 'prj-' + 'f'.repeat(48);
const target = 'eligible-person';
const record = {
  schema: 'wilsy.project.participant.v1', tenant_id: tenantId,
  project_id: projectId, principal_id: target,
  role: 'CONTRIBUTOR', state: 'ACTIVE', revision: 1,
  granted_by_principal_id: principalId, updated_by_principal_id: principalId,
  created_at: '2026-11-18T06:00:00+00:00',
  updated_at: '2026-11-18T06:00:00+00:00',
  fingerprint: 'a'.repeat(128),
};

beforeEach(() => {
  vi.clearAllMocks();
  let seed = 0;
  vi.stubGlobal('crypto', { randomUUID: () => 'cert-key-' + (++seed) });
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it('grants and revokes only verified selectable tenant participants', async () => {
  let active = [];
  api.get.mockImplementation(async path => {
    if (path === '/projects/' + projectId + '/participants?limit=50&offset=0') return {
      data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1',
        tenant_id: tenantId, principal_id: principalId, project_id: projectId,
        limit: 50, offset: 0, items: active,
        has_more: false, next_offset: null,
      },
    };
    if (path === '/projects/' + projectId + '/participant-options?limit=50&offset=0') return {
      data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-OPTIONS/V1',
        tenant_id: tenantId, principal_id: principalId, project_id: projectId,
        limit: 50, offset: 0, items: [{ principal_id: target }],
        has_more: false, next_offset: null,
      },
    };
    throw new Error('Unexpected source read: ' + path);
  });
  api.post.mockImplementation(async (path, body, options) => {
    expect(options.headers['X-Tenant-ID']).toBe(tenantId);
    expect(options.headers['Idempotency-Key']).toBeTruthy();
    if (path === '/projects/' + projectId + '/participants') {
      expect(body).toEqual({ principal_id: target, role: 'CONTRIBUTOR' });
      active = [record];
      return { data: {
        schema: 'WILSY-PROJECT-PARTICIPANT-RESULT/V1',
        tenant_id: tenantId, principal_id: principalId, project_id: projectId,
        participant: record,
      } };
    }
    expect(path).toBe('/projects/' + projectId + '/participants/' + target + '/revoke');
    expect(body).toEqual({ expected_revision: 1 });
    const revoked = { ...record, state: 'REVOKED', revision: 2, fingerprint: 'b'.repeat(128) };
    active = [];
    return { data: {
      schema: 'WILSY-PROJECT-PARTICIPANT-RESULT/V1',
      tenant_id: tenantId, principal_id: principalId, project_id: projectId,
      participant: revoked,
    } };
  });
  render(<ProjectParticipantsPanel tenantId={tenantId} principalId={principalId}
    projectId={projectId} tenantHeaders={{ 'X-Tenant-ID': tenantId }}/>);
  const select = await screen.findByRole('combobox', { name: 'Eligible participant' });
  expect(screen.getByRole('button', { name: 'Add participant' })).toBeDisabled();
  fireEvent.change(select, { target: { value: target } });
  fireEvent.click(screen.getByRole('button', { name: 'Add participant' }));
  await waitFor(() => expect(screen.getByRole('button', { name: 'Revoke participation' })).toBeVisible());
  expect(screen.getAllByText('Contributor').some(node => node.closest('li'))).toBe(true);
  fireEvent.click(screen.getByRole('button', { name: 'Revoke participation' }));
  await waitFor(() => expect(screen.queryByRole('button', { name: 'Revoke participation' })).not.toBeInTheDocument());
  expect(api.post).toHaveBeenCalledTimes(2);
});

it('does not expose unverified candidate options or a grant button', async () => {
  api.get.mockImplementation(async path => ({
    data: path.includes('participant-options')
      ? {
        schema: 'WILSY-PROJECT-PARTICIPANT-OPTIONS/V1',
        tenant_id: 'foreign-tenant', principal_id: principalId,
        project_id: projectId, limit: 50, offset: 0, items: [{ principal_id: target }],
        has_more: false, next_offset: null,
      } : {
        schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1',
        tenant_id: tenantId, principal_id: principalId, project_id: projectId,
        limit: 50, offset: 0, items: [], has_more: false, next_offset: null,
      },
  }));
  render(<ProjectParticipantsPanel tenantId={tenantId} principalId={principalId}
    projectId={projectId} tenantHeaders={{ 'X-Tenant-ID': tenantId }}/>);
  expect(await screen.findByRole('alert')).toHaveTextContent('response scope or schema invalid');
  expect(screen.queryByRole('button', { name: 'Add participant' })).not.toBeInTheDocument();
  expect(api.post).not.toHaveBeenCalled();
});


it('preserves existing participant view but blocks commands if eligible member directory returns HTTP 403', async () => {
  api.get.mockImplementation(async path => {
    if (path.includes('/participant-options?')) {
      const denied = new Error('Forbidden');
      denied.response = { status: 403, data: { detail: 'PROJECT_PARTICIPANT_DIRECTORY_DENIED' } };
      throw denied;
    }
    return { data: {
      schema: 'WILSY-PROJECT-PARTICIPANT-LIST/V1',
      tenant_id: tenantId, principal_id: principalId, project_id: projectId,
      limit: 50, offset: 0, items: [record], has_more: false, next_offset: null,
    } };
  });
  render(<ProjectParticipantsPanel tenantId={tenantId} principalId={principalId}
    projectId={projectId} tenantHeaders={{ 'X-Tenant-ID': tenantId }}/>);
  const alert = await screen.findByRole('alert');
  expect(alert).toHaveTextContent('Eligible tenant member directory: permission denied by EOS (HTTP 403)');
  expect(screen.getByText('Verified project participant')).toBeVisible();
  expect(screen.getByText('Contributor')).toBeVisible();
  expect(screen.getByRole('button', { name: 'Revoke participation' })).toBeDisabled();
  expect(screen.queryByRole('button', { name: 'Add participant' })).not.toBeInTheDocument();
  expect(api.post).not.toHaveBeenCalled();
});

it('does not treat denied participant-list authority as an empty project roster', async () => {
  api.get.mockImplementation(async path => {
    if (path.includes('/participants?')) {
      const denied = new Error('Forbidden');
      denied.response = { status: 403 };
      throw denied;
    }
    return { data: {
      schema: 'WILSY-PROJECT-PARTICIPANT-OPTIONS/V1',
      tenant_id: tenantId, principal_id: principalId, project_id: projectId,
      limit: 50, offset: 0, items: [{ principal_id: target }],
      has_more: false, next_offset: null,
    } };
  });
  render(<ProjectParticipantsPanel tenantId={tenantId} principalId={principalId}
    projectId={projectId} tenantHeaders={{ 'X-Tenant-ID': tenantId }}/>);
  expect(await screen.findByRole('alert')).toHaveTextContent(
    'Project participants: permission denied by EOS (HTTP 403)',
  );
  expect(screen.queryByText('No verified active participants on this page.')).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Add participant' })).not.toBeInTheDocument();
  expect(api.post).not.toHaveBeenCalled();
});

// ARTIFACT: ProjectParticipantsPanel.test.jsx
// VERSION: v1.3.0-FAULT-ISOLATED-PROJECT-PEOPLE-CERT
// AUTHORITY BOUNDARY: mocked EOS client only, no real assignments
// TENANT POSTURE: foreign tenant options discarded
// FAIL-CLOSED POSTURE: no grant without valid source choice and exact readback
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT
