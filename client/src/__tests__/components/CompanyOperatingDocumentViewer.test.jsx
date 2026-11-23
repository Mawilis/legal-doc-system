/**
 * TITLE: WILSY OS Company Document Viewer Contract Certificate
 * VERSION: v1.12.0-FOUNDER-STRATEGY-COMMAND-CERT
 * AUTHORITY: Isolated client contract evidence; Python EOS owns publication.
 * EPITOME: Exercise the real adapter/viewer across privacy, session turnover,
 * history, command/readback, honest empty state and keyboard close boundaries.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/__tests__/components/CompanyOperatingDocumentViewer.test.jsx
 * COLLABORATION / OWNERSHIP: Viewer, current auth scope and source client adapter.
 * CERTIFICATION / UPDATE DATE: 2026-11-20
 * CHANGELOG: v1.12.0-FOUNDER-STRATEGY-COMMAND-CERT
 *            verifies exact readback, mission denial and authenticated
 *            Founder strategy draft/submit/ratification transport paths.
 * CHANGELOG: v1.11.1-M03-UNVERIFIED-LINK-READBACK-CERT
 *            distinguishes the pre-project verification link state from an
 *            EOS 409 received after explicit source readback. No synthetic
 *            publication/link status is asserted before its request.
 * CHANGELOG: v1.11.0-M03-AUTHORITY-PUBLICATION-GATE-CERT
 *            verifies read-only Strategy publication and independent publisher
 *            gates from live admitted source actions without granting IAM or
 *            issuing a synthetic publication/link write.
 * CHANGELOG: v1.10.0-M02-LIVE-PROJECT-SNAPSHOT-CERT verifies
 *            18 distinct EOS records, live lifecycle transitions after
 *            refresh, predecessor and calendar due-date counts; incomplete
 *            coverage never produces manufactured execution totals.
 * CHANGELOG: v1.9.1-EXACT-PROJECTS-503-TRANSPORT-CERT verifies
 *            timed-out no-response Projects read distinguishes network from
 *            EOS denial while keeping the project source unavailable;
 *            current Strategy relationship description is source-owned.
 * CHANGELOG: v1.9.0-STRATEGY-PUBLICATION-LIFECYCLE-CTA-CERT verifies
 *            exact source-authorized review and draft submission action
 *            exposure, no unauthorized publish, and no auto document writes.
 * CHANGELOG: v1.8.2-EXACT-UNPUBLISHED-STRATEGY-FIXTURE corrects
 *            the synthetic no-publication response classification to
 *            STRATEGY, retaining strict source validation and independent
 *            review handoff without changing production response checks.
 * CHANGELOG: v1.8.1-PUBLISHED-STRATEGY-DEPENDENCY-CERT certifies
 *            exact EOS 409 publication-required UI recovery, explicit
 *            separately authorized review path, and no link mutation from
 *            approved but unpublished source content.
 * CHANGELOG: v1.8.0-STRATEGY-LINK-READBACK-BROWSER-CERT certifies
 *            distinct source-owned link readback and one independently
 *            confirmed link command after all 18 implementation records
 *            exist; linking never certifies a strategy progress percentage.
 * CHANGELOG: v1.7.0-PARTIAL-STRATEGY-PLAN-RECOVERY-CERT validates
 *            accurate planned vs persisted source counts, disables further
 *            creation after full admission and preserves one-write-per-item
 *            replay safety when the UI refreshes.
 * CHANGELOG: v1.6.2-EXACT-PROJECT-ACTION-QUERIES aligns three action
 *            selector assertions to the canonical, full EOS project name.
 *            Test setup and source-owned IAM and command guards stay intact.
 * CHANGELOG: v1.6.1-EXACT-FOUNDATION-NAME-FIXTURE uses the source-owned
 *            canonical existing WILSY OS foundation project name for the
 *            plan admission test. The production exact-project gate is kept;
 *            unrelated projects remain ineligible for plan creation.
 * CHANGELOG: v1.6.0-PLAN-PERSISTENCE-READBACK-CERT verifies that eighteen
 *            planned milestones/tasks remain separate from EOS state until
 *            explicit owner-authorized idempotent creation. Each result
 *            requires exact-tenant durable readback; repeats skip existing.
 * CHANGELOG: v1.5.1-EXPLICIT-PROJECT-NAVIGATION-FIXTURE provides the
 *            actual Headquarters navigation callback when testing the
 *            conditional Open project control, without changing production
 *            authorization or inventing any project route.
 * CHANGELOG: v1.5.0-STRATEGY-EXECUTION-LAYOUT-CERT verifies
 *            project identity/status/action grouping and collapsed creation;
 *            authenticated task reads remain the only source of execution.
 * CHANGELOG: v1.4.1-STRATEGY-TRANSIENT-503-RECOVERY-CERT verifies
 *            a persistent Projects HTTP 503 never fabricates Strategy
 *            project task readback and presents an authorized navigation
 *            route into the existing Projects workspace.
 * CHANGELOG: v1.4.0-STRATEGY-PROJECT-EXECUTION-CERT checks authenticated
 *            exact-project source readback and rejection of malformed task
 *            pages without inferring strategy completion or granting access.
 * CHANGELOG: v1.3.0-APPROVED-SOURCE-PENDING-PUBLICATION-CERT certifies the
 *            existing approved-source preparation workflow while retaining
 *            publication, permission, scope, replay and independent readback gates.
 * CHANGELOG: v1.2.0-INTERACTIVE-DOCUMENT-STUDIO-CERT verifies
 *            EOS-authorized draft entry, multi-section reorder/remove,
 *            unpublished private preview and denied-command exclusion.
 * CHANGELOG: v1.2.0-INTERACTIVE-DOCUMENT-STUDIO-CERT covers classified source/auth failures,
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
const reduceDraftToOneSection = () => {
  const titles = screen.getAllByLabelText('Section title');
  expect(titles.length).toBeGreaterThan(1);
  expect(screen.getByLabelText('Document version')).toHaveValue('1.1.0');
  for (let remaining = titles.length; remaining > 1; remaining -= 1) {
    fireEvent.click(screen.getByRole('button', { name: 'Remove section ' + remaining }));
  }
};
const fillDraft = async () => {
  fireEvent.click(await screen.findByRole('button', { name: 'Prepare approved v1.1.0' }));
  reduceDraftToOneSection();
  fireEvent.change(screen.getByLabelText('Document title'), { target: { value: 'Synthetic proposal' } });
  fireEvent.change(screen.getByLabelText('Document version'), { target: { value: '1.0.0' } });
  fireEvent.change(screen.getByLabelText('Section title'), { target: { value: 'Synthetic purpose' } });
  fireEvent.change(screen.getByLabelText('Proposed content'), { target: { value: 'Synthetic source content only.' } });
};
beforeEach(() => { vi.clearAllMocks(); api.get.mockResolvedValue({ data: view() }); });

describe('governed company document experience', () => {
  it('survives Strict Mode and shows honest unpublished state without policy', async () => {
    render(wrap());
    expect(await screen.findByText('NOT YET PUBLISHED', { exact: true })).toBeVisible();
    expect(screen.queryByText('Synthetic source content only.')).not.toBeInTheDocument();
    expect(document.querySelector('[data-document-state="FOUNDER_APPROVED_EOS_PENDING"]')).toBeVisible();
    expect(screen.getByText(/not an EOS-published revision/)).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Prepare approved v1.1.0' })).not.toBeInTheDocument();
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
    expect(await screen.findByText('NOT YET PUBLISHED', { exact: true })).toBeVisible();
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
    expect(screen.queryByText('NOT YET PUBLISHED', { exact: true })).not.toBeInTheDocument();
    expect(screen.queryByText('Current company session required')).not.toBeInTheDocument();
    expect(screen.queryByText('CONFIDENTIAL-DO-NOT-RENDER')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Prepare approved v1.1.0' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Approve and publish' })).not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
    api.get.mockResolvedValue({ data: view() });
    fireEvent.click(screen.getByRole('button', { name: 'Retry source read' }));
    expect(await screen.findByText('NOT YET PUBLISHED', { exact: true })).toBeVisible();
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
    expect(screen.queryByRole('button', { name: 'Prepare approved v1.1.0' })).not.toBeInTheDocument();
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
    expect(await screen.findByText('NOT YET PUBLISHED', { exact: true })).toBeVisible();
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
    expect(await screen.findByText('NOT YET PUBLISHED', { exact: true })).toBeVisible();
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
    await screen.findByText('NOT YET PUBLISHED', { exact: true });
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
  it('brings source-admitted company document actions forward and edits an unpublished multi-section proposal', async () => {
    api.get.mockResolvedValue({ data: view(null, ['READ_HISTORY', 'CREATE_DRAFT', 'REVIEW_DRAFTS']) });
    render(wrap());
    await screen.findByText('NOT YET PUBLISHED', { exact: true });
    const deck = screen.getByRole('navigation', { name: 'Company document actions' });
    expect(deck).toBeVisible();
    expect(deck).toHaveTextContent('Founder-approved source · EOS publication pending');
    fireEvent.click(screen.getByRole('button', { name: 'Prepare approved v1.1.0' }));
    reduceDraftToOneSection();
    const editor = screen.getByRole('form', { name: 'Company private draft editor' });
    expect(editor).toBeVisible();
    fireEvent.change(screen.getByLabelText('Document title'), { target: { value: 'Proposed mission' } });
    fireEvent.change(screen.getByLabelText('Document version'), { target: { value: '1.0.0' } });
    fireEvent.change(screen.getByLabelText('Section title'), { target: { value: 'Purpose' } });
    fireEvent.change(screen.getByLabelText('Proposed content'), { target: { value: 'Serve customers with verified outcomes.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Add section' }));
    expect(screen.getByText('2 sections', { exact: false })).toBeVisible();
    const titles = screen.getAllByLabelText('Section title');
    const bodies = screen.getAllByLabelText('Proposed content');
    fireEvent.change(titles[1], { target: { value: 'Principles' } });
    fireEvent.change(bodies[1], { target: { value: 'Accountability and clarity.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Move section 2 up' }));
    expect(screen.getAllByLabelText('Section title')[0]).toHaveValue('Principles');
    fireEvent.click(screen.getByRole('button', { name: 'Preview draft' }));
    expect(screen.getByRole('region', { name: 'Unpublished draft preview' })).toHaveTextContent('Proposed mission');
    expect(screen.getByText('UNPUBLISHED PREVIEW · NOT COMPANY POLICY')).toBeVisible();
    expect(api.post).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Edit document' }));
    fireEvent.click(screen.getByRole('button', { name: 'Remove section 2' }));
    expect(screen.getAllByLabelText('Section title')).toHaveLength(1);
    expect(screen.getByRole('button', { name: 'Save private draft to EOS' })).toBeEnabled();
  });
  it('keeps author and publisher commands absent when EOS admits only reading', async () => {
    render(wrap());
    await screen.findByText('NOT YET PUBLISHED', { exact: true });
    expect(screen.getByText(/Your current EOS permission allows reading this Founder-approved source/)).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Prepare approved v1.1.0' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Save private draft to EOS' })).not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });
  it('uses stable commands, blocks duplicate clicks and claims success only after independent readback', async () => {
    api.get.mockResolvedValue({ data: view(null, ['READ_HISTORY', 'CREATE_DRAFT', 'REVIEW_DRAFTS']) });
    render(wrap()); await fillDraft();
    const ack = deferred(); api.post.mockImplementation(() => ack.promise);
    fireEvent.click(screen.getByRole('button', { name: 'Save private draft to EOS' }));
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
    fireEvent.click(screen.getByRole('button', { name: 'Save private draft to EOS' }));
    expect(await screen.findByRole('heading', { name: 'Command recorded; current readback unverified' })).toBeVisible();
    expect(screen.queryByText(/EOS confirmed the command/)).not.toBeInTheDocument();
  });
  it('closes with Escape and restores the invoking control focus', async () => {
    const onClose = vi.fn(); const trigger = document.createElement('button'); document.body.append(trigger); trigger.focus();
    const mounted = render(wrap({ onClose })); await screen.findByText('NOT YET PUBLISHED', { exact: true });
    expect(screen.getByRole('button', { name: 'Close company document' })).toHaveFocus();
    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Escape' }); expect(onClose).toHaveBeenCalledTimes(1);
    mounted.unmount(); expect(trigger).toHaveFocus(); trigger.remove();
  });
});

describe('Strategy source-owned project execution readback', () => {
  const projectId = 'prj-' + 'a'.repeat(48);
  const taskId = 'ptk-' + 'b'.repeat(48);
  const project = { project_id: projectId, tenant_id: scope.tenantId,
    name: 'WILSY OS — Unified Operating Platform Foundation', status: 'ACTIVE', revision: 2 };
  const projectList = () => ({ schema: 'WILSY-PROJECT-LIST/V1',
    tenant_id: scope.tenantId, principal_id: scope.principalId,
    limit: 100, offset: 0, has_more: false, next_offset: null, items: [project] });
  const taskList = () => ({ schema: 'WILSY-PROJECT-TASK-LIST/V1',
    tenant_id: scope.tenantId, principal_id: scope.principalId, project_id: projectId,
    offset: 0, limit: 50, has_more: false, next_offset: null,
    items: [{ tenant_id: scope.tenantId, project_id: projectId, task_id: taskId,
      kind: 'MILESTONE', title: 'Complete operating taxonomy',
      status: 'TODO', due_date: null }] });
  it('M02 updates 18-record lifecycle and predecessor counts only after source refresh', async () => {
    const milestones = [
      'Operating taxonomy and strategy alignment',
      'Governed work graph and multi-source accountability',
      'Role-aware work execution and approval decisions',
      'Ranked Founder operating workspace',
      'Audited workflow automation and Intelligence Dock parity',
      'Production readiness and strategy outcome certification',
    ];
    const tasks = [
      'Inventory canonical My Work sources, capacities and IAM',
      'Define Operating, Platform Build and Unclassified work',
      'Implement audited source-owned work classification',
      'Derive source-authorized work identities and accountability',
      'Integrate independent project approvals in My Work',
      'Deliver Founder Operating, Platform and Waiting filters',
      'Certify role capacity packs and tenant isolation',
      'Implement explainable ranking and source diversity',
      'Wire source-owned task and decision commands',
      'Build governed event-driven workflow automation',
      'Align Intelligence Dock with the authorized work graph',
      'Certify production readiness and rollback',
    ];
    const createItem = (kind, index, title) => ({
      tenant_id: scope.tenantId, project_id: projectId,
      task_id: 'ptk-' + (index + 1).toString(16).padStart(48, '0'),
      kind, title: 'MW-' + (kind === 'MILESTONE' ? 'M' : 'T')
        + String(kind === 'MILESTONE' ? index + 1 : index - 5).padStart(2, '0') + ' — ' + title,
      status: 'TODO', due_date: null, depends_on: [],
    });
    let items = [...milestones.map((title, i) => createItem('MILESTONE', i, title)),
      ...tasks.map((title, i) => createItem('TASK', i + 6, title))];
    items[6].depends_on = [items[0].task_id];
    items[7].status = 'IN_PROGRESS';
    items[8].status = 'BLOCKED';
    items[9].due_date = '2020-01-01';
    const page = () => ({
      schema: 'WILSY-PROJECT-TASK-LIST/V1',
      tenant_id: scope.tenantId, principal_id: scope.principalId,
      project_id: projectId, offset: 0, limit: 50,
      has_more: false, next_offset: null, items: items.map(item => ({ ...item })),
    });
    api.get.mockImplementation(url => {
      if (url === '/projects') return Promise.resolve({ data: projectList() });
      if (url === '/projects/' + projectId + '/tasks')
        return Promise.resolve({ data: page() });
      if (url === '/company-operating-documents/STRATEGY/project-links')
        return Promise.reject({ response: { status: 409, data: { detail: {
          error: 'STRATEGY_LINK_PUBLISHED_SOURCE_REQUIRED',
        } } } });
      if (url === '/company-operating-documents/STRATEGY')
        return Promise.resolve({ data: { ...view(null), classification: 'STRATEGY' } });
      return Promise.reject(new Error('UNEXPECTED_ROUTE'));
    });
    render(wrap({ classification: 'STRATEGY' }));
    fireEvent.click(await screen.findByRole('button', {
      name: /Verify execution for WILSY OS — Unified Operating Platform Foundation/,
    }));
    const readback = await screen.findByRole('region', { name: 'M02 live execution readback' });
    const currentReadback = () => screen.getByRole('region', { name: 'M02 live execution readback' });
    const values = () => Array.from(currentReadback().querySelectorAll('dl > div')).map(el => el.textContent);
    expect(values()).toEqual(['To do16', 'In progress1', 'Done0', 'Blocked1', 'Cancelled0']);
    expect(readback.textContent).toContain('1 programme records waiting on 1 unfinished predecessor relationships');
    expect(readback.textContent).toContain('1 unfinished records with calendar due dates');
    expect(readback.textContent).toMatch(/Successful Projects read observed:/);
    items[0] = { ...items[0], status: 'DONE' };
    items[7] = { ...items[7], status: 'DONE' };
    fireEvent.click(screen.getByRole('button', { name: 'Refresh execution' }));
    await waitFor(() => expect(values()).toEqual([
      'To do15', 'In progress0', 'Done2', 'Blocked1', 'Cancelled0',
    ]));
    expect(currentReadback().textContent).toContain('0 programme records waiting on 0 unfinished predecessor relationships');
    expect(api.post).not.toHaveBeenCalled();
    // A missing or ambiguous plan record must suppress M02 entirely.
    items = items.slice(1);
    fireEvent.click(screen.getByRole('button', { name: 'Refresh execution' }));
    expect(await screen.findByText(/M02 execution summary unavailable: full/)).toBeVisible();
    expect(screen.queryByRole('region', { name: 'M02 live execution readback' })).not.toBeInTheDocument();
  });

  it('M03 validates exact Founder self-ratification and rejects copied approval for other classes', async () => {
    const reference = 'WILSY-INSTITUTIONAL-FOUNDER-SELF-RATIFICATION-20261123';
    const ratified = { ...record('STRATEGY'), approved_by_principal_id: scope.principalId,
      approval_reference: reference };
    const accepted = { ...view(ratified), classification: 'STRATEGY' };
    expect(assertCompanyDocumentView(accepted, 'STRATEGY', scope)).toBe(accepted);
    expect(() => assertCompanyDocumentView({
      ...view({ ...ratified, classification: 'MISSION', document_id: 'wilsy-company-mission' }),
      classification: 'MISSION',
    }, 'MISSION', scope)).toThrow('COMPANY_DOCUMENT_RESPONSE_INVALID');
    expect(() => assertCompanyDocumentView({
      ...accepted, document: { ...ratified, approval_reference: 'SYNTHETIC-SPOOF' },
    }, 'STRATEGY', scope)).toThrow('COMPANY_DOCUMENT_RESPONSE_INVALID');
    api.post.mockResolvedValue(receipt(ratified));
    await commandCompanyDocument('STRATEGY', scope, 'FOUNDER_RATIFY',
      { expected_revision: 2, effective_from: asOf }, 'ratify-test-key',
      { token: auth.token });
    expect(api.post.mock.calls[0][0]).toBe('/company-operating-documents/STRATEGY/founder-ratify');
    expect(api.post.mock.calls[0][2].headers['Idempotency-Key']).toBe('ratify-test-key');
    await expect(commandCompanyDocument('MISSION', scope, 'FOUNDER_RATIFY', {}, 'mission-denied',
      { token: auth.token })).rejects.toThrow('COMPANY_DOCUMENT_FOUNDER_STRATEGY_ONLY');
    expect(api.post).toHaveBeenCalledTimes(1);
  });

  it('M03 offers Founder draft creation only after explicit EOS-admitted source action', async () => {
    api.get.mockImplementation(url => {
      if (url === '/company-operating-documents/STRATEGY')
        return Promise.resolve({ data: { ...view(null, [
          'READ_HISTORY', 'REVIEW_DRAFTS', 'FOUNDER_CREATE_DRAFT',
        ]), classification: 'STRATEGY' } });
      if (url === '/projects') return Promise.resolve({ data: projectList() });
      return Promise.reject(new Error('UNEXPECTED_ROUTE'));
    });
    render(wrap({ classification: 'STRATEGY' }));
    expect(await screen.findByText(/Verified Founder can prepare Strategy through durable source authority/)).toBeVisible();
    fireEvent.click(screen.getByRole('button', { name: 'Prepare approved v1.1.0' }));
    expect(screen.getByRole('form', { name: 'Company private draft editor' })).toBeVisible();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('M03 presents unpublished read-only source authority without writing publisher or pillar links', async () => {
    api.get.mockImplementation(url => {
      if (url === '/company-operating-documents/STRATEGY')
        return Promise.resolve({ data: { ...view(null), classification: 'STRATEGY' } });
      if (url === '/company-operating-documents/STRATEGY/project-links')
        return Promise.reject({ response: { status: 409, data: {
          detail: { error: 'STRATEGY_LINK_PUBLISHED_SOURCE_REQUIRED' },
        } } });
      if (url === '/projects') return Promise.resolve({ data: projectList() });
      return Promise.reject(new Error('UNEXPECTED_ROUTE'));
    });
    render(wrap({ classification: 'STRATEGY' }));
    const gates = await screen.findByRole('region', { name: 'M03 Strategy governance gates' });
    expect(gates).toHaveTextContent('Current source offers read-only actions; author admission not established');
    expect(gates).toHaveTextContent('No publication action admitted in this source view');
    expect(gates).toHaveTextContent('Not verified as published and effective');
    // Before the Foundation execution read, EOS project-link readback is not
    // initiated; an unpublished 409 cannot be asserted without its request.
    expect(gates).toHaveTextContent('Current link readback not verified');
    expect(api.get.mock.calls.some(([url]) =>
      url === '/company-operating-documents/STRATEGY/project-links')).toBe(false);
    expect(screen.queryByRole('button', { name: 'Link verified Foundation project to Pillar 1' })).not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('shows independently verified project tasks, not invented Strategy progress', async () => {
    api.get.mockImplementation(url => {
      if (url === '/projects') return Promise.resolve({ data: projectList() });
      if (url === '/projects/' + projectId + '/tasks')
        return Promise.resolve({ data: taskList() });
      if (url === '/company-operating-documents/STRATEGY')
        return Promise.resolve({ data: view(record('STRATEGY')) });
      return Promise.reject(new Error('UNEXPECTED_ROUTE'));
    });
    const onOpenProject = vi.fn();
    render(wrap({ classification: 'STRATEGY', onOpenProject }));
    const verifyButton = await screen.findByRole('button', { name: /Verify execution for WILSY OS — Unified Operating Platform Foundation/ });
    expect(screen.getByRole('button', { name: /Open project delivery for WILSY OS — Unified Operating Platform Foundation/ })).toBeVisible();
    expect(onOpenProject).not.toHaveBeenCalled();
    expect(screen.getByText('Revision 2')).toBeVisible();
    const newProjectForm = document.querySelector('form[aria-label="Create governed EOS project"]');
    expect(newProjectForm?.closest('details')?.open).toBe(false);
    expect(api.post).not.toHaveBeenCalled();
    fireEvent.click(verifyButton);
    expect(await screen.findByRole('heading', { name: 'Source-verified project execution' })).toBeVisible();
    expect(screen.getByText(/Complete operating taxonomy/)).toBeVisible();
    expect(screen.getByText(/No strategic pillar linkage or Strategy completion percentage is inferred/)).toBeVisible();
    const call = api.get.mock.calls.find(([url]) => url === '/projects/' + projectId + '/tasks');
    expect(call[1].headers).toEqual({ 'X-Tenant-ID': scope.tenantId,
      Authorization: 'Bearer synthetic-only' });
  });
  it('exposes source-owned Strategy draft lifecycle without inventing a publisher', async () => {
    const draft = record('STRATEGY', 'DRAFT', 1);
    api.get.mockImplementation((url, config) => {
      if (url === '/projects') return Promise.resolve({ data: projectList() });
      if (url === '/company-operating-documents/STRATEGY') {
        return Promise.resolve({ data: config?.params?.review === true
          ? view(draft, ['READ_HISTORY', 'REVIEW_DRAFTS', 'SUBMIT'], true)
          : { ...view(null, ['READ_HISTORY', 'REVIEW_DRAFTS'], false),
              classification: 'STRATEGY' } });
      }
      return Promise.reject(new Error('UNEXPECTED_ROUTE'));
    });
    render(wrap({ classification: 'STRATEGY' }));
    expect(await screen.findByText(/Official publication not yet established/)).toBeVisible();
    expect(screen.getByRole('button', { name: 'Review authorized publication state' })).toBeEnabled();
    expect(screen.queryByRole('button', { name: 'Open independent approval form' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Review authorized publication state' }));
    expect(await screen.findByText(/Stage 1 of 3 · Author draft/)).toBeVisible();
    expect(screen.getByRole('button', { name: 'Submit Strategy for independent approval' })).toBeEnabled();
    expect(screen.queryByRole('button', { name: 'Open independent approval form' })).not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });
  it('explains exact unpublished Strategy source and offers authorized review without linking', async () => {
    api.get.mockImplementation((url, config) => {
      if (url === '/projects') return Promise.resolve({ data: projectList() });
      if (url === '/projects/' + projectId + '/tasks')
        return Promise.resolve({ data: taskList() });
      if (url === '/company-operating-documents/STRATEGY/project-links')
        return Promise.reject({ response: { status: 409, data: { detail: {
          error: 'STRATEGY_LINK_PUBLISHED_SOURCE_REQUIRED',
        } } } });
      if (url === '/company-operating-documents/STRATEGY')
        return Promise.resolve({ data: {
          ...view(null, ['READ_HISTORY', 'REVIEW_DRAFTS'], config?.params?.review === true),
          classification: 'STRATEGY',
        } });
      return Promise.reject(new Error('UNEXPECTED_ROUTE'));
    });
    render(wrap({ classification: 'STRATEGY' }));
    fireEvent.click(await screen.findByRole('button', {
      name: /Verify execution for WILSY OS — Unified Operating Platform Foundation/,
    }));
    expect(await screen.findByText(/No currently effective EOS-published Strategy exists/)).toBeVisible();
    expect(screen.getByText(/An authorized author must prepare and submit the Strategy/)).toBeVisible();
    expect(screen.queryByRole('button', {
      name: 'Link verified Foundation project to Pillar 1',
    })).not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', {
      name: 'Review private Strategy publication workflow',
    }));
    await waitFor(() => expect(api.get.mock.calls.some(([url, config]) =>
      url === '/company-operating-documents/STRATEGY' && config?.params?.review === true)).toBe(true));
    expect(api.post).not.toHaveBeenCalled();
  });
  it('creates eighteen missing programme items only through explicit audited EOS commands and skips them on replay', async () => {
    const existing = taskList().items;
    const created = [];
    let linked = false;
    const strategyPublication = { ...record('STRATEGY'),
      sections: [{ section_id: 'pillar-one', title: 'One OS', body: 'Synthetic operating strategy.' }] };
    const linkUrl = '/company-operating-documents/STRATEGY/project-links';
    const taskUrl = '/projects/' + projectId + '/tasks';
    api.get.mockImplementation((url, config) => {
      if (url === '/projects') return Promise.resolve({ data: projectList() });
      if (url === taskUrl) {
        const limit = config?.params?.limit ?? 50;
        const rows = [...existing, ...created];
        return Promise.resolve({ data: { ...taskList(), limit, items: rows } });
      }
      if (url === linkUrl) return Promise.resolve({ data: {
        schema: 'WILSY-STRATEGY-PROJECT-LINK-LIST/V1',
        tenant_id: scope.tenantId, principal_id: scope.principalId, classification: 'STRATEGY',
        strategy_revision: strategyPublication.revision, source_verified: true,
        strategy_progress: null, items: linked ? [{ pillar_id: 'pillar-one', project_id: projectId,
          project_name: project.name, project_status: 'active', source_project_revision: project.revision,
          source_strategy_revision: strategyPublication.revision, state: 'VERIFIED_CURRENT' }] : [],
      } });
      if (url === '/company-operating-documents/STRATEGY')
        return Promise.resolve({ data: view(strategyPublication) });
      return Promise.reject(new Error('UNEXPECTED_ROUTE'));
    });
    api.post.mockImplementation((url, body, config) => {
      if (url === linkUrl) {
        expect(created).toHaveLength(18);
        expect(body).toEqual({ pillar_id: 'pillar-one', project_id: projectId,
          expected_strategy_revision: strategyPublication.revision,
          expected_project_revision: project.revision });
        expect(config.headers['Idempotency-Key']).toContain('strategy-pillar-one-foundation-v1');
        linked = true;
        return Promise.resolve({ data: {
          schema: 'WILSY-STRATEGY-PROJECT-LINK-RESULT/V1',
          tenant_id: scope.tenantId, principal_id: scope.principalId, classification: 'STRATEGY',
          pillar_id: 'pillar-one', project_id: projectId, strategy_revision: strategyPublication.revision,
          project_revision: project.revision, relationship_state: 'RECORDED_NOT_OUTCOME_CERTIFIED',
          strategy_progress: null,
        } });
      }
      if (url !== taskUrl || !config?.headers?.['Idempotency-Key'])
        return Promise.reject(new Error('INVALID_OR_UNAUTHORIZED_SOURCE_COMMAND'));
      const index = created.length + 1;
      const task = { ...existing[0], task_id: 'ptk-' + index.toString(16).padStart(48, '0'),
        kind: body.kind, title: body.title, status: 'TODO',
        description: body.description, due_date: null };
      created.push(task);
      return Promise.resolve({ data: { schema: 'WILSY-PROJECT-TASK-RESULT/V1',
        tenant_id: scope.tenantId, principal_id: scope.principalId,
        project_id: projectId, task } });
    });
    render(wrap({ classification: 'STRATEGY' }));
    fireEvent.click(await screen.findByRole('button', { name: /Verify execution for WILSY OS — Unified Operating Platform Foundation/ }));
    expect(await screen.findByRole('heading', { name: 'My Work implementation programme' })).toBeVisible();
    expect(screen.getByText(/0 of 18 planned records persisted in EOS/)).toBeVisible();
    expect(screen.getByText('MW-M01 — Operating taxonomy and strategy alignment')).toBeVisible();
    expect(screen.getByText('MW-T12 — Certify production readiness and rollback')).toBeVisible();
    expect(api.post).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: 'Create missing in EOS' }));
    expect(await screen.findByText(/18 created and independently verified; 0 previously present/, {}, { timeout: 9000 })).toBeVisible();
    expect(api.post).toHaveBeenCalledTimes(18);
    expect(created).toHaveLength(18);
    expect(api.post.mock.calls.every(([, body, config]) =>
      body.assignee_principal_id === null && body.due_date === null
      && config.headers['X-Tenant-ID'] === scope.tenantId
      && config.headers['Idempotency-Key'].startsWith('strategy-foundation-v1-'))).toBe(true);
    await waitFor(() => expect(screen.getAllByText('Persisted in EOS')).toHaveLength(18));

    expect(screen.getByText(/18 of 18 planned records persisted in EOS/)).toBeVisible();
    expect(screen.getByRole('button', { name: 'All 18 verified in EOS' })).toBeDisabled();
    expect(api.post).toHaveBeenCalledTimes(18);
    const linkButton = await screen.findByRole('button', {
      name: 'Link verified Foundation project to Pillar 1',
    });
    expect(linkButton).toBeEnabled();
    fireEvent.click(linkButton);
    expect(await screen.findByText(/Linked in EOS · current Strategy and project snapshots verified/)).toBeVisible();
    expect(api.post).toHaveBeenCalledTimes(19);
    expect(linked).toBe(true);
    expect(screen.getByText(/No outcome score certified/)).toBeVisible();
  });
  it('rejects mismatched task tenant and hides unverified delivery', async () => {
    const foreign = taskList();
    foreign.items[0].tenant_id = 'FOREIGN';
    api.get.mockImplementation(url => {
      if (url === '/projects') return Promise.resolve({ data: projectList() });
      if (url === '/projects/' + projectId + '/tasks')
        return Promise.resolve({ data: foreign });
      if (url === '/company-operating-documents/STRATEGY')
        return Promise.resolve({ data: view(record('STRATEGY')) });
      return Promise.reject(new Error('UNEXPECTED_ROUTE'));
    });
    render(wrap({ classification: 'STRATEGY' }));
    fireEvent.click(await screen.findByRole('button', { name: /Verify execution/ }));
    expect(await screen.findByText(/No Strategy progress was inferred/)).toBeVisible();
    expect(screen.queryByRole('heading', { name: 'Source-verified project execution' })).not.toBeInTheDocument();
  });
});

describe('Strategy Projects read recovery', () => {
  it('identifies a timed-out project list without claiming an empty current registry', async () => {
    const onOpenProjects = vi.fn();
    api.get.mockImplementation(url => {
      if (url === '/projects')
        return Promise.reject({ code: 'ECONNABORTED', message: 'synthetic-only timeout' });
      if (url === '/company-operating-documents/STRATEGY')
        return Promise.resolve({ data: view(record('STRATEGY')) });
      return Promise.reject(new Error('UNEXPECTED_ROUTE'));
    });
    render(wrap({ classification: 'STRATEGY', onOpenProjects }));
    expect(await screen.findByText(/Project list request timed out before an EOS response/)).toBeVisible();
    expect(screen.queryByRole('heading', { name: 'Source-verified project execution' })).not.toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });

  it('keeps a persistent 503 unavailable and navigates to existing Projects without creating a record', async () => {
    const onOpenProjects = vi.fn();
    api.get.mockImplementation(url => {
      if (url === '/projects') return Promise.reject({ response: { status: 503, data: {
        detail: 'PROJECT_DATABASE_UNAVAILABLE',
      } } });
      if (url === '/company-operating-documents/STRATEGY')
        return Promise.resolve({ data: view(record('STRATEGY')) });
      return Promise.reject(new Error('UNEXPECTED_ROUTE'));
    });
    render(wrap({ classification: 'STRATEGY', onOpenProjects }));
    expect(await screen.findByRole('button', { name: 'Open existing Projects workspace' }, { timeout: 5000 })).toBeVisible();
    expect(screen.getByText(/HTTP 503/)).toBeVisible();
    expect(screen.queryByRole('heading', { name: 'Source-verified project execution' })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Open existing Projects workspace' }));
    expect(onOpenProjects).toHaveBeenCalledTimes(1);
    expect(api.post).not.toHaveBeenCalled();
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
// VERSION: v1.12.0-FOUNDER-STRATEGY-COMMAND-CERT
// AUTHORITY BOUNDARY: Client regression only; source IAM and publication stay EOS-owned.
// TENANT POSTURE: Exact scope and late-session negative gates.
// FAIL-CLOSED POSTURE: Unverified commands never receive a success assertion.
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
// END OF WILSY OS SOVEREIGN ARTIFACT
