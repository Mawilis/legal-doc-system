/**
 * TITLE: WILSY OS Company Document Viewer Contract Certificate
 * VERSION: v1.1.0-DOCUMENT-SESSION-FAILURE-CERT
 * AUTHORITY: Isolated client contract evidence; Python EOS owns publication.
 * EPITOME: Exercise the real adapter/viewer across privacy, session turnover,
 * history, command/readback, honest empty state and keyboard close boundaries.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/CompanyOperatingDocumentViewer.test.jsx
 * COLLABORATION / OWNERSHIP: Viewer, current auth scope and source client adapter.
 * CERTIFICATION / UPDATE DATE: 2026-11-13
 * CHANGELOG: v1.1.0-DOCUMENT-SESSION-FAILURE-CERT covers classified source/auth failures,
 * explicit recovery, stale capacity/tenant/session reads and unauthorized controls.
 * CHANGELOG: v1.0.0-COMPANY-DOCUMENT-VIEWER-CERT establishes focused regression gates.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Synthetic publication and credentials only.
 * TENANT BOUNDARY: Exact fixtures; previous session results must never render.
 * AUTHORITY BOUNDARY: Mocks never certify live IAM/Mongo; separate browser gate does.
 * FINANCIAL AUTHORITY BOUNDARY: No execution authority.
 */
import React, { StrictMode } from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import AuthContext from '../../contexts/authContext.jsx';
import api from '../../services/api.js';
import CompanyOperatingDocumentViewer from '../../components/workspaces/CompanyOperatingDocumentViewer.jsx';
import { assertCompanyDocumentView, commandCompanyDocument, readCompanyDocumentHistory } from '../../services/companyOperatingDocumentsClient.js';

vi.mock('../../services/api.js', () => ({ default: { get: vi.fn(), post: vi.fn() } }));
const scope = { tenantId: 'WILSYTENANT-4CD2FZ4O', principalId: 'synthetic-author' };
const auth = { isAuthenticated: true, authStage: 'AUTHENTICATED', token: 'synthetic-only', sessionGeneration: 1,
  user: { id: scope.principalId, tenantId: scope.tenantId, businessRole: 'tenant_owner', workspaceId: 'WILSY_HEADQUARTERS' } };
const asOf = '2026-11-13T00:00:00.000+00:00';
const record = (classification = 'MISSION', state = 'PUBLISHED', revision = 3) => ({
  schema: 'WILSY-COMPANY-OPERATING-DOCUMENT/V1', tenant_id: scope.tenantId,
  document_id: 'wilsy-company-' + classification.toLowerCase(), classification,
  title: 'Synthetic approved ' + classification.toLowerCase(), document_version: '1.0.0', revision, state,
  sections: [{ section_id: 'purpose', title: 'Synthetic purpose', body: 'Synthetic source content only.' }],
  author_principal_id: scope.principalId, recorded_at: asOf, previous_fingerprint: revision > 1 ? 'a'.repeat(128) : null,
  approved_by_principal_id: state === 'PUBLISHED' ? 'synthetic-publisher' : null,
  approval_reference: state === 'PUBLISHED' ? 'SYNTHETIC-APPROVAL' : null,
  effective_from: state === 'PUBLISHED' ? asOf : null, fingerprint: 'b'.repeat(128),
});
const view = (document = null, actions = ['READ_HISTORY'], review = false) => ({
  schema: 'WILSY-COMPANY-OPERATING-DOCUMENT-VIEW/V1', tenant_id: scope.tenantId, principal_id: scope.principalId,
  classification: document?.classification || 'MISSION', view: review ? 'review' : 'published',
  state: document?.state || 'NOT_YET_PUBLISHED', document, current_revision: document?.revision || 0,
  available_actions: actions, as_of: asOf, relationships: { state: 'NOT_GOVERNED' },
  authority: { publication_owned_by: 'PYTHON_EOS', financial_execution: false },
});
const receipt = document => ({ data: { schema: 'WILSY-COMPANY-OPERATING-DOCUMENT-COMMAND-RESULT/V1',
  tenant_id: scope.tenantId, principal_id: scope.principalId, classification: document.classification, document } });
const wrap = (props = {}, identity = auth) => <StrictMode><AuthContext.Provider value={identity}><CompanyOperatingDocumentViewer classification="MISSION" onClose={() => {}} onOpenWork={() => {}} {...props}/></AuthContext.Provider></StrictMode>;
const deferred = () => { let resolve; const promise = new Promise(done => { resolve = done; }); return { promise, resolve }; };
const fillDraft = async () => {
  fireEvent.click(await screen.findByRole('button', { name: 'Prepare draft' }));
  fireEvent.change(screen.getByLabelText('Document title'), { target: { value: 'Synthetic proposal' } });
  fireEvent.change(screen.getByLabelText('Document version'), { target: { value: '1.0.0' } });
  fireEvent.change(screen.getByLabelText('Section title'), { target: { value: 'Synthetic purpose' } });
  fireEvent.change(screen.getByLabelText('Proposed content'), { target: { value: 'Synthetic source content only.' } });
};
beforeEach(() => { vi.clearAllMocks(); api.get.mockResolvedValue({ data: view() }); });

describe('governed company document experience', () => {
  it('survives Strict Mode and shows honest unpublished state without policy', async () => {
    render(wrap());
    expect(await screen.findByRole('heading', { name: 'Not yet published' })).toBeVisible();
    expect(screen.queryByText('Synthetic source content only.')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Prepare draft' })).not.toBeInTheDocument();
    expect(api.get.mock.calls.at(-1)[0]).toBe('/company-operating-documents/MISSION');
    expect(api.get.mock.calls.at(-1)[1].headers).toEqual({ 'X-Tenant-ID': scope.tenantId, Authorization: 'Bearer synthetic-only' });
  });
  it('renders only source-approved content with authority and accessible contents', async () => {
    api.get.mockResolvedValue({ data: view(record()) }); render(wrap());
    expect(await screen.findByRole('heading', { name: 'Synthetic approved mission' })).toBeVisible();
    expect(screen.getByRole('button', { name: 'Synthetic purpose' })).toBeVisible();
    expect(screen.getByText('synthetic-publisher')).toBeVisible();
    expect(screen.getByText('SYNTHETIC-APPROVAL')).toBeVisible();
    expect(screen.getByText('Synthetic source content only.')).toBeVisible();
  });
  it('shows denied source and permits an explicit retry without fabricated content', async () => {
    api.get.mockRejectedValue({ response: { status: 403 } }); render(wrap());
    expect(await screen.findByRole('heading', { name: 'Access denied' })).toBeVisible();
    api.get.mockResolvedValue({ data: view() }); fireEvent.click(screen.getByRole('button', { name: 'Retry source read' }));
    expect(await screen.findByRole('heading', { name: 'Not yet published' })).toBeVisible();
  });
  it.each([
    [401, { detail: { error: 'COMPANY_DOCUMENT_AUTHENTICATED_SCOPE_REQUIRED' } }, 'Sign-in verification required', 'AUTHENTICATION_REQUIRED'],
    [403, { error: { code: 'FORBIDDEN_OPERATION' } }, 'Access denied', 'ACCESS_DENIED'],
    [503, { detail: { error: 'COMPANY_DOCUMENT_SOURCE_UNAVAILABLE', message: 'CONFIDENTIAL-DO-NOT-RENDER' } }, 'Document source unavailable', 'UNAVAILABLE'],
    [404, { detail: 'Not Found' }, 'Document source unavailable', 'UNAVAILABLE'],
    [404, { detail: { error: 'COMPANY_DOCUMENT_NOT_FOUND' } }, 'Revision unavailable', 'REVISION_UNAVAILABLE'],
    [null, null, 'Document source unavailable', 'UNAVAILABLE'],
  ])('classifies HTTP %s without substituting an unpublished or stale-authority state', async (status, data, title, kind) => {
    api.get.mockRejectedValue(status ? { response: { status, data } } : new Error('Network Error'));
    render(wrap());
    expect(await screen.findByRole('heading', { name: title })).toBeVisible();
    expect(screen.getByRole('alert')).toHaveAttribute('data-document-state', kind);
    expect(screen.getByRole('heading', { name: 'Next step' })).toBeVisible();
    expect(screen.queryByRole('heading', { name: 'Not yet published' })).not.toBeInTheDocument();
    expect(screen.queryByText('Current company session required')).not.toBeInTheDocument();
    expect(screen.queryByText('CONFIDENTIAL-DO-NOT-RENDER')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Prepare draft' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Approve and publish' })).not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
    api.get.mockResolvedValue({ data: view() });
    fireEvent.click(screen.getByRole('button', { name: 'Retry source read' }));
    expect(await screen.findByRole('heading', { name: 'Not yet published' })).toBeVisible();
    expect(api.get.mock.calls.at(-1)[1].params).toEqual({ review: false });
  });
  it('classifies a malformed source response without treating the session as missing', async () => {
    api.get.mockResolvedValue({ data: { success: true } }); render(wrap());
    expect(await screen.findByRole('heading', { name: 'Document response could not be verified' })).toBeVisible();
    expect(screen.getByText('COMPANY_DOCUMENT_RESPONSE_INVALID')).toBeVisible();
    expect(screen.queryByText('Company session verification required')).not.toBeInTheDocument();
  });
  it('requires canonical authentication locally without issuing a request', async () => {
    render(wrap({}, { ...auth, token: null }));
    expect(await screen.findByRole('heading', { name: 'Sign-in verification required' })).toBeVisible();
    expect(screen.getByText('Not sent · current session required')).toBeVisible();
    expect(api.get).not.toHaveBeenCalled();
  });
  it('removes earlier content and command hints after a denied history read', async () => {
    api.get.mockResolvedValue({ data: view(record(), ['READ_HISTORY', 'CREATE_DRAFT']) }); render(wrap());
    await screen.findByText('Synthetic source content only.');
    api.get.mockRejectedValue({ response: { status: 403 } });
    fireEvent.click(screen.getByRole('button', { name: 'Revision history' }));
    expect(await screen.findByRole('heading', { name: 'Access denied' })).toBeVisible();
    expect(screen.queryByText('Synthetic source content only.')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Prepare draft' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Synthetic purpose' })).not.toBeInTheDocument();
    expect(screen.getByText('Document access denied by EOS')).toBeVisible();
  });
  it.each(['tenant', 'capacity', 'generation'])('invalidates the previous %s scope before accepting a later response', async field => {
    const late = deferred(); api.get.mockImplementation(() => late.promise);
    const mounted = render(wrap());
    const next = { ...auth, user: { ...auth.user } };
    if (field === 'tenant') next.user.tenantId = 'synthetic-foreign-tenant';
    if (field === 'capacity') { next.user.businessRole = 'tenant_admin'; next.user.businessRoleRevision = 2; }
    if (field === 'generation') next.sessionGeneration += 1;
    api.get.mockResolvedValue({ data: { ...view(), tenant_id: next.user.tenantId } });
    mounted.rerender(wrap({}, next));
    expect(await screen.findByRole('heading', { name: 'Not yet published' })).toBeVisible();
    await act(async () => late.resolve({ data: view(record()) }));
    expect(screen.queryByText('Synthetic source content only.')).not.toBeInTheDocument();
    expect(api.get.mock.calls.at(-1)[1].headers['X-Tenant-ID']).toBe(next.user.tenantId);
    expect(api.get.mock.calls[0][1].signal.aborted).toBe(true);
  });
  it('discards a late response after credential and principal turnover', async () => {
    const late = deferred(); api.get.mockImplementation(() => late.promise);
    const mounted = render(wrap());
    const changed = { ...auth, token: 'synthetic-next', sessionGeneration: 2, user: { ...auth.user, id: 'next-principal' } };
    api.get.mockResolvedValue({ data: { ...view(), principal_id: 'next-principal' } }); mounted.rerender(wrap({}, changed));
    expect(await screen.findByRole('heading', { name: 'Not yet published' })).toBeVisible();
    await act(async () => late.resolve({ data: view(record()) }));
    expect(screen.queryByText('Synthetic source content only.')).not.toBeInTheDocument();
    expect(api.get.mock.calls.at(-1)[1].headers.Authorization).toBe('Bearer synthetic-next');
  });
  it('does not retain content when the document classification changes', async () => {
    api.get.mockResolvedValue({ data: view(record()) }); const mounted = render(wrap());
    await screen.findByText('Synthetic source content only.');
    api.get.mockResolvedValue({ data: { ...view(), classification: 'STRATEGY' } }); mounted.rerender(wrap({ classification: 'STRATEGY' }));
    expect(screen.queryByText('Synthetic source content only.')).not.toBeInTheDocument();
    expect(await screen.findByRole('heading', { name: 'Our Strategy' })).toBeVisible();
    await screen.findByRole('heading', { name: 'Not yet published' });
  });
  it('reads source history then re-reads the selected permitted revision', async () => {
    const published = record(); const { sections, ...metadata } = published;
    api.get.mockImplementation((path, options) => Promise.resolve({ data: path.endsWith('/revisions') ? {
      schema: 'WILSY-COMPANY-OPERATING-DOCUMENT-HISTORY/V1', tenant_id: scope.tenantId, principal_id: scope.principalId,
      classification: 'MISSION', view: 'published', as_of: asOf, items: [metadata],
    } : view(published) })); render(wrap()); await screen.findByText('Synthetic source content only.');
    fireEvent.click(screen.getByRole('button', { name: 'Revision history' }));
    fireEvent.click(await screen.findByRole('button', { name: /Version 1.0.0 · revision 3/ }));
    await screen.findByText('Historical revision 3');
    expect(api.get.mock.calls.at(-1)[1].params.revision).toBe(3);
  });
  it('refreshes the current document after viewing permitted history', async () => {
    const published = record(); const { sections, ...metadata } = published;
    api.get.mockImplementation(path => Promise.resolve({ data: path.endsWith('/revisions') ? {
      schema: 'WILSY-COMPANY-OPERATING-DOCUMENT-HISTORY/V1', tenant_id: scope.tenantId,
      principal_id: scope.principalId, classification: 'MISSION', view: 'published', as_of: asOf, items: [metadata],
    } : view(published) }));
    render(wrap()); await screen.findByText('Synthetic source content only.');
    fireEvent.click(screen.getByRole('button', { name: 'Revision history' }));
    await screen.findByRole('button', { name: /Version 1.0.0 · revision 3/ });
    fireEvent.click(screen.getByRole('button', { name: 'Refresh source' }));
    expect(await screen.findByText('Synthetic source content only.')).toBeVisible();
    expect(screen.queryByText('No permitted revisions are available.')).not.toBeInTheDocument();
  });
  it('uses stable commands, blocks duplicate clicks and claims success only after independent readback', async () => {
    api.get.mockResolvedValue({ data: view(null, ['READ_HISTORY', 'CREATE_DRAFT', 'REVIEW_DRAFTS']) });
    render(wrap()); await fillDraft();
    const ack = deferred(); api.post.mockImplementation(() => ack.promise);
    fireEvent.click(screen.getByRole('button', { name: 'Save private draft' }));
    expect(screen.queryByText(/EOS confirmed the command/)).not.toBeInTheDocument();
    expect(api.post).toHaveBeenCalledTimes(1);
    const saved = record('MISSION', 'DRAFT', 1); api.get.mockResolvedValue({ data: view(saved, ['READ_HISTORY', 'SUBMIT'], true) });
    await act(async () => ack.resolve(receipt(saved)));
    expect(await screen.findByText(/EOS confirmed the command and its durable document readback/)).toBeVisible();
    expect(api.post.mock.calls[0][0]).toBe('/company-operating-documents/MISSION/drafts');
    expect(api.post.mock.calls[0][2].headers['Idempotency-Key']).toMatch(/^[a-f0-9-]{36}$/);
    expect(api.get.mock.calls.at(-1)[1].params.review).toBe(true);
  });
  it('does not fabricate success when acknowledgment lacks matching durable readback', async () => {
    api.get.mockResolvedValue({ data: view(null, ['CREATE_DRAFT']) }); render(wrap()); await fillDraft();
    api.post.mockResolvedValue(receipt(record('MISSION', 'DRAFT', 1)));
    api.get.mockResolvedValue({ data: view(null, [], true) });
    fireEvent.click(screen.getByRole('button', { name: 'Save private draft' }));
    expect(await screen.findByRole('heading', { name: 'Command recorded; current readback unverified' })).toBeVisible();
    expect(screen.queryByText(/EOS confirmed the command/)).not.toBeInTheDocument();
  });
  it('closes with Escape and restores the invoking control focus', async () => {
    const onClose = vi.fn(); const trigger = document.createElement('button'); document.body.append(trigger); trigger.focus();
    const mounted = render(wrap({ onClose })); await screen.findByRole('heading', { name: 'Not yet published' });
    expect(screen.getByRole('button', { name: 'Close company document' })).toHaveFocus();
    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Escape' }); expect(onClose).toHaveBeenCalledTimes(1);
    mounted.unmount(); expect(trigger).toHaveFocus(); trigger.remove();
  });
});

describe('source contract rejection', () => {
  it.each([
    value => ({ ...value, tenant_id: 'foreign' }),
    value => ({ ...value, principal_id: 'previous' }),
    value => view(record('MISSION', 'DRAFT', 1)),
    value => view({ ...record(), effective_from: '2030-01-01T00:00:00Z' }),
  ])('rejects mismatched scope, private drafts and future effective publications', mutate => {
    expect(() => assertCompanyDocumentView(mutate(view(record())), 'MISSION', scope)).toThrow('COMPANY_DOCUMENT_RESPONSE_INVALID');
  });
  it('rejects a command receipt from a previous principal', async () => {
    const response = receipt(record()); response.data.principal_id = 'foreign-principal'; api.post.mockResolvedValue(response);
    await expect(commandCompanyDocument('MISSION', scope, 'SUBMIT', { expected_revision: 1 }, 'synthetic-key', { token: 'synthetic' })).rejects.toThrow('COMPANY_DOCUMENT_RESPONSE_INVALID');
  });
  it('rejects content concealed inside supposedly public history metadata', async () => {
    api.get.mockResolvedValue({ data: { schema: 'WILSY-COMPANY-OPERATING-DOCUMENT-HISTORY/V1', tenant_id: scope.tenantId,
      principal_id: scope.principalId, classification: 'MISSION', view: 'published', as_of: asOf, items: [record()] } });
    await expect(readCompanyDocumentHistory('MISSION', scope, { token: 'synthetic' })).rejects.toThrow('COMPANY_DOCUMENT_RESPONSE_INVALID');
  });
});

// ARTIFACT: CompanyOperatingDocumentViewer.test.jsx
// VERSION: v1.1.0-DOCUMENT-SESSION-FAILURE-CERT
// AUTHORITY BOUNDARY: Client regression only; source IAM and publication stay EOS-owned.
// TENANT POSTURE: Exact scope and late-session negative gates.
// FAIL-CLOSED POSTURE: Unverified commands never receive a success assertion.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
