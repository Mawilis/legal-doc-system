/**
 * TITLE: WILSY OS Controlled Dock Contract and Artifact Transport
 * VERSION: v1.0.0
 * AUTHORITY: WILSY OS Core Governance; Python EOS owns every command.
 * EPITOME: Validate inert components and bind exact-source work to canonical transport.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/intelligence/wilsyDockContract.js
 * COLLABORATION / OWNERSHIP: EOS wilsy.dock.v1, Projects, Intelligence Dock.
 * CERTIFICATION / UPDATE DATE: 2026-11-25
 * CHANGELOG: v1.0.0 adds closed catalog validation and deterministic PDF drafting.
 * COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC2 CC7.2.
 * SECURITY / PRIVACY POSTURE: Inert text only; no model routes, HTML or scripts.
 * TENANT BOUNDARY: Exact current principal and tenant required on every readback.
 * AUTHORITY BOUNDARY: Locators and drafts grant no permission or completion.
 * FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
 */
import { sha3_512 } from 'js-sha3';

const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const text = (value, limit, empty = false) => typeof value === 'string'
  && value.length <= limit && (empty || value.trim().length > 0);
const integer = value => Number.isSafeInteger(value) && value > 0;
const digest = value => /^[0-9a-f]{128}$/.test(value || '');
const ownKeys = (value, names) => object(value) && Object.keys(value).every(key => names.includes(key));
const strings = (value, max, length = 1000) => Array.isArray(value) && value.length <= max
  && value.every(item => text(item, length));
const failure = () => { throw new Error('WILSY_DOCK_COMPONENT_INVALID'); };
const sourceKeys = ['project_id', 'task_id', 'revision', 'fingerprint', 'participant_view'];
const validSource = source => ownKeys(source, sourceKeys)
  && /^prj-[0-9a-f]{48}$/.test(source.project_id || '')
  && /^ptk-[0-9a-f]{48}$/.test(source.task_id || '') && integer(source.revision)
  && digest(source.fingerprint) && typeof source.participant_view === 'boolean';
const equalSource = (a, b) => sourceKeys.every(key => a?.[key] === b?.[key]);
const operations = {
  DRAFT_PLAN: ['DRAFT_PLAN', null], OPEN_TASK: ['NAVIGATE_TASK', null],
  REVIEW_EVIDENCE: ['REVIEW_EVIDENCE', null], START_TASK: ['PROJECT_TASK_TRANSITION', 'IN_PROGRESS'],
  COMPLETE_TASK: ['PROJECT_TASK_TRANSITION', 'DONE'],
};

/**
 * @description Validate the closed catalog and exact live source, rejecting unknown fields.
 * @collaboration EOS router, renderer and tests. No persistence or IAM is created.
 * @institutional Historical or model text cannot become an executable action.
 * @returns The unchanged validated envelope; throws a stable contract error.
 */
export function assertDockEnvelope(value, { tenantId, principalId, locator } = {}) {
  if (!ownKeys(value, ['catalog', 'tenant_id', 'principal_id', 'observed_at', 'source',
    'components', 'model_invoked', 'financial_execution'])
    || value.catalog !== 'wilsy.dock.v1' || !text(value.tenant_id, 180) || !text(value.principal_id, 180)
    || (tenantId && value.tenant_id !== tenantId) || (principalId && value.principal_id !== principalId)
    || value.model_invoked !== false || value.financial_execution !== false
    || !Number.isFinite(Date.parse(value.observed_at)) || !validSource(value.source)
    || (locator && (locator.project_id !== value.source.project_id || locator.task_id !== value.source.task_id
      || Boolean(locator.participant_view) !== value.source.participant_view
      || (locator.task_revision !== undefined && locator.task_revision !== value.source.revision)))
    || !Array.isArray(value.components) || !value.components.length || value.components.length > 8
    || new TextEncoder().encode(JSON.stringify(value)).length > 65536) failure();
  const ids = new Set();
  const actionIds = new Set();
  for (const component of value.components) {
    if (!object(component) || !text(component.id, 100) || ids.has(component.id)) failure();
    ids.add(component.id);
    switch (component.type) {
      case 'TaskBrief':
        if (!ownKeys(component, ['type', 'id', 'source', 'title', 'purpose', 'status', 'owner', 'deadline',
          'dependencies', 'established', 'blockers', 'next_action', 'can_attach'])
          || !equalSource(component.source, value.source) || !text(component.title, 180)
          || !text(component.purpose, 5000, true)
          || !['TODO', 'IN_PROGRESS', 'BLOCKED', 'DONE', 'CANCELLED'].includes(component.status)
          || (component.owner !== null && !text(component.owner, 180))
          || (component.deadline !== null && !/^\d{4}-\d{2}-\d{2}$/.test(component.deadline || ''))
          || !strings(component.dependencies, 25, 52)
          || component.dependencies.some(id => !/^ptk-[a-f0-9]{48}$/.test(id))
          || !text(component.established, 500) || !strings(component.blockers, 25)
          || !text(component.next_action, 240) || typeof component.can_attach !== 'boolean') failure();
        break;
      case 'ActionList':
        if (!ownKeys(component, ['type', 'id', 'actions']) || !Array.isArray(component.actions)
          || component.actions.length > 4) failure();
        for (const [index, action] of component.actions.entries()) {
          if (!ownKeys(action, ['id', 'component_id', 'kind', 'source', 'outcome', 'priority',
            'availability', 'verified_revision', 'execution', 'correlation_id'])
            || !text(action.id, 100) || actionIds.has(action.id) || action.component_id !== component.id
            || !Object.hasOwn(operations, action.kind) || !equalSource(action.source, value.source)
            || action.verified_revision !== value.source.revision || !text(action.outcome, 240)
            || action.priority !== index || action.availability !== 'AVAILABLE' || !digest(action.correlation_id)
            || !ownKeys(action.execution, ['operation', 'target_status', 'requires_confirmation'])
            || action.execution.operation !== operations[action.kind][0]
            || action.execution.target_status !== operations[action.kind][1]
            || action.execution.requires_confirmation !== (action.execution.operation === 'PROJECT_TASK_TRANSITION')) failure();
          actionIds.add(action.id);
        }
        break;
      case 'Checklist':
        if (!ownKeys(component, ['type', 'id', 'items']) || !strings(component.items, 50)) failure();
        break;
      case 'ArtifactFrame':
        if (!ownKeys(component, ['type', 'id', 'source', 'title', 'state', 'provenance', 'content'])
          || !equalSource(component.source, value.source) || !text(component.title, 180)
          || !['DRAFT', 'EDITING', 'ATTACHING', 'UNVERIFIED', 'ATTACHED', 'DISCARDED'].includes(component.state)
          || !['DETERMINISTIC_DRAFT', 'GOVERNED_PROVIDER'].includes(component.provenance)
          || !text(component.content, 12000, true)) failure();
        break;
      case 'ApprovalCard':
        if (!ownKeys(component, ['type', 'id', 'approval_id', 'text'])
          || !/^par-[a-f0-9]{48}$/.test(component.approval_id || '') || !text(component.text, 1000)) failure();
        break;
      case 'StatusBanner':
        if (!ownKeys(component, ['type', 'id', 'state', 'text'])
          || !['PENDING', 'UNVERIFIED', 'VERIFIED', 'DENIED', 'UNAVAILABLE'].includes(component.state)
          || !text(component.text, 1000)) failure();
        break;
      case 'PlainText':
        if (!ownKeys(component, ['type', 'id', 'text']) || !text(component.text, 6000, true)) failure();
        break;
      default: failure();
    }
  }
  if (actionIds.size > 4) failure();
  return value;
}

/**
 * @description Draft from a validated source; no model, inferred facts or persisted success.
 * @collaboration ArtifactFrame edit/accept flow. No financial or task mutation.
 * @institutional Recommendations are explicitly separate from verified work state.
 */
export function draftDockPlan(envelope) {
  assertDockEnvelope(envelope);
  const brief = envelope.components.find(item => item.type === 'TaskBrief');
  if (!brief) failure();
  return {
    type: 'ArtifactFrame', id: 'task-plan', source: { ...envelope.source },
    title: `Alignment plan: ${brief.title}`.slice(0, 180), state: 'DRAFT', provenance: 'DETERMINISTIC_DRAFT',
    content: [
      brief.title, '', 'Deterministic task-plan draft. No AI model invoked.',
      `Source revision: ${brief.source.revision}`, `Observed: ${envelope.observed_at}`,
      '', 'Task purpose (source text):', brief.purpose || 'No purpose description supplied by Projects.',
      '', 'Established:', brief.established,
      ...(brief.deadline ? [`Recorded deadline: ${brief.deadline}`] : []),
      '', 'Recorded blockers:', ...(brief.blockers.length ? brief.blockers : ['No additional blocker was returned by this source read.']),
      `Recorded dependencies: ${brief.dependencies.length}. Review current dependency state in Projects.`,
      '', 'Proposed checklist (human review required):',
      '[ ] Confirm the intended outcome and acceptance evidence in the full task.',
      '[ ] Review current dependencies, required approvals and recorded evidence.',
      '[ ] Perform the authorized work and record supporting evidence.',
      '[ ] Verify the resulting EOS state independently.',
      '[ ] Request completion only when the canonical task authority permits it.',
      '', 'This draft does not prove work, approval, service, payment or settlement.',
    ].join('\n').slice(0, 12000),
  };
}

/**
 * @description Create a bounded, paginated PDF of the exact edited draft using local tooling.
 * @collaboration Existing Projects PDF quarantine upload; no external inference.
 * @institutional Bytes are immutable for one attachment attempt and hash readback.
 * @returns PDF Blob and SHA3-512 digest; no attachment or scan claim is made.
 */
export async function createDockPlanPdf(artifact) {
  if (!artifact || !['DETERMINISTIC_DRAFT', 'GOVERNED_PROVIDER'].includes(artifact.provenance) || !text(artifact.content, 12000)
    || !text(artifact.title, 180) || !validSource(artifact.source)) failure();
  const { jsPDF } = await import('jspdf');
  const document = new jsPDF({ unit: 'mm', format: 'a4', putOnlyUsedFonts: true });
  document.setProperties({ title: artifact.title, subject: artifact.provenance === 'GOVERNED_PROVIDER' ? 'Human-reviewed EOS-admitted model draft' : 'Human-reviewed deterministic task-plan draft' });
  document.setFont('helvetica', 'normal');
  document.setFontSize(10);
  // PDF standard fonts have a bounded glyph set. Normalize punctuation and
  // reject unsupported characters before upload; editable source stays intact.
  if (/[^\x09\x0a\x0d\x20-\x7e\xa0-\xff\u2010-\u2015\u2018\u2019\u201c\u201d]/.test(artifact.content)) {
    throw new Error('WILSY_DOCK_PDF_FONT_UNSUPPORTED');
  }
  const printable = artifact.content.replace(/[\u2010-\u2015]/g, '-').replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201c\u201d]/g, '"');
  const lines = document.splitTextToSize(printable, 174);
  let y = 20;
  for (const line of lines) {
    if (y > 274) { document.addPage(); y = 20; }
    document.text(line, 18, y); y += 5;
  }
  const count = document.getNumberOfPages();
  for (let page = 1; page <= count; page += 1) {
    document.setPage(page); document.setFontSize(8);
    document.text(`WILSY OS | Task revision ${artifact.source.revision} | Draft | ${page}/${count}`, 18, 287);
  }
  const bytes = document.output('arraybuffer');
  return { blob: new Blob([bytes], { type: 'application/pdf' }), digest: sha3_512(new Uint8Array(bytes)),
    filename: `alignment-plan-r${artifact.source.revision}.pdf`, size: bytes.byteLength };
}

/**
 * @description Resolve only canonical local navigation; no model route is accepted.
 * @collaboration Projects and My Work client routes; EOS reauthorizes on arrival.
 * @institutional A source locator confers no read, mutation or financial authority.
 */
export function dockTaskPath(source, evidence = false) {
  if (!validSource(source)) failure();
  const query = new URLSearchParams({ section: 'projects', project: source.project_id, task: source.task_id,
    ...(source.participant_view ? { view: 'assigned' } : {}), ...(evidence ? { task_action: 'attachments' } : {}) });
  return `/headquarters?${query}`;
}

// ARTIFACT: wilsyDockContract.js
// VERSION: v1.0.0
// AUTHORITY BOUNDARY: inert UI and draft bytes only; EOS owns commands and archive
// TENANT POSTURE: exact response scope, never a browser grant
// FAIL-CLOSED POSTURE: unknown types, tools, routes and stale bindings rejected
// FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
// END OF WILSY OS SOVEREIGN ARTIFACT



