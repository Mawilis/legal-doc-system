/**
 * WILSY OS — PRODUCTION LEGAL OPERATIONS VISUAL GATE
 * VERSION: v1.0.3-L8-7D14-LEGAL-OPERATIONS-VISUAL-GATE-ALIAS-PARITY
 * AUTHORITY: Test-support only; imports the real production LegalDashboard and CSS.
 * EPITOME: Deterministic LEGAL_PARTNER visual evidence for the complete D14
 *          workspace while denying client/sheriff/deputy cross-role access.
 * CHANGELOG: 2026-09-24 v1.0.3 mirrors the production Vite @ → src alias so\n *            transitive production imports resolve inside the deterministic visual gate.\n *            2026-09-24 v1.0.2 rebinds the visual virtual adapter to the
 *            hardened D14 summary-validation version; synthetic state counters
 *            remain exact with their displayed rows.
 *            2026-09-24 v1.0.1 aligns synthetic document/attempt/execution
 *            lifecycle states so every displayed execution has a terminal
 *            source attempt and every active attempt has an allocated document.
 * PRODUCTION IMPACT: NONE.
 * FAIL-CLOSED: Unintended role transport throws immediately.
 */
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';\nimport path from 'path';

const SERVICE_ID = 'virtual:wilsy-legal-operations-visual-service';
const SERVICE_RESOLVED = '\0' + SERVICE_ID;
const AUTH_ID = 'virtual:wilsy-legal-operations-auth-context';
const AUTH_RESOLVED = '\0' + AUTH_ID;
const TENANT_ID = 'virtual:wilsy-legal-operations-tenant-context';
const TENANT_RESOLVED = '\0' + TENANT_ID;

const serviceModule = String.raw`
export const LEGAL_OPERATIONS_CLIENT_VERSION =
  'v1.5.1-L8-7D14-WORKSPACE-SUMMARY-VALIDATION';

const evidence = (character) => character.repeat(128);
const denied = (name) => {
  throw new Error('D14_CROSS_ROLE_VISUAL_ACCESS_' + name);
};

export async function getLegalPracticeWorkspace() {
  return Object.freeze({
    schema: 'WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V1',
    version: 'v1.7.0-L8-7D11-LEGAL-PRACTICE-WORKSPACE-API',
    tenantId: 'tenant-wilsy-legal',
    visibility: 'LEGAL_PRACTICE_WORKSPACE',
    summary: Object.freeze({
      instructions_total: 6,
      instructions_registered: 2,
      instructions_accepted: 3,
      instructions_closed: 1,
      instructions_cancelled: 0,
      documents_total: 6,
      documents_registered: 1,
      documents_received: 1,
      documents_allocated: 3,
      documents_returned: 1,
      attempts_total: 3,
      attempts_allocated: 0,
      attempts_attempted: 1,
      attempts_completed: 1,
      attempts_not_completed: 1,
      attempts_cancelled: 0,
      executions_total: 2,
      executions_completed: 1,
      executions_not_completed: 1,
      returns_total: 1,
    }),
    instructions: Object.freeze([
      Object.freeze({ instruction_id:'instruction-2026-001',case_matter_id:'matter-2026-001',document_id:'document-2026-001',registered_at:'2026-09-23T08:10:00+02:00',state:'ACCEPTED',evidence_identity:evidence('a') }),
      Object.freeze({ instruction_id:'instruction-2026-002',case_matter_id:'matter-2026-002',document_id:'document-2026-002',registered_at:'2026-09-23T08:40:00+02:00',state:'REGISTERED',evidence_identity:evidence('b') }),
      Object.freeze({ instruction_id:'instruction-2026-003',case_matter_id:'matter-2026-003',document_id:'document-2026-003',registered_at:'2026-09-23T09:15:00+02:00',state:'ACCEPTED',evidence_identity:evidence('c') }),
      Object.freeze({ instruction_id:'instruction-2026-004',case_matter_id:'matter-2026-004',document_id:'document-2026-004',registered_at:'2026-09-23T10:05:00+02:00',state:'REGISTERED',evidence_identity:evidence('d') }),
      Object.freeze({ instruction_id:'instruction-2026-005',case_matter_id:'matter-2026-005',document_id:'document-2026-005',registered_at:'2026-09-23T11:20:00+02:00',state:'ACCEPTED',evidence_identity:evidence('e') }),
      Object.freeze({ instruction_id:'instruction-2026-006',case_matter_id:'matter-2026-006',document_id:'document-2026-006',registered_at:'2026-09-22T14:30:00+02:00',state:'CLOSED',evidence_identity:evidence('f') }),
    ]),
    documents: Object.freeze([
      Object.freeze({ document_id:'document-2026-001',case_matter_id:'matter-2026-001',document_type:'SUMMONS',registered_at:'2026-09-23T08:11:00+02:00',state:'ALLOCATED_TO_DEPUTY',evidence_identity:evidence('1') }),
      Object.freeze({ document_id:'document-2026-002',case_matter_id:'matter-2026-002',document_type:'NOTICE OF MOTION',registered_at:'2026-09-23T08:41:00+02:00',state:'REGISTERED',evidence_identity:evidence('2') }),
      Object.freeze({ document_id:'document-2026-003',case_matter_id:'matter-2026-003',document_type:'WARRANT',registered_at:'2026-09-23T09:16:00+02:00',state:'ALLOCATED_TO_DEPUTY',evidence_identity:evidence('3') }),
      Object.freeze({ document_id:'document-2026-004',case_matter_id:'matter-2026-004',document_type:'SUBPOENA',registered_at:'2026-09-23T10:06:00+02:00',state:'RECEIVED',evidence_identity:evidence('4') }),
      Object.freeze({ document_id:'document-2026-005',case_matter_id:'matter-2026-005',document_type:'COURT ORDER',registered_at:'2026-09-23T11:21:00+02:00',state:'ALLOCATED_TO_DEPUTY',evidence_identity:evidence('5') }),
      Object.freeze({ document_id:'document-2026-006',case_matter_id:'matter-2026-006',document_type:'SUMMONS',registered_at:'2026-09-22T14:31:00+02:00',state:'RETURNED_TO_CLIENT',evidence_identity:evidence('6') }),
    ]),
    attempts: Object.freeze([
      Object.freeze({ attempt_id:'attempt-2026-001',instruction_id:'instruction-2026-001',document_id:'document-2026-001',deputy_id:'deputy-jhb-014',allocated_at:'2026-09-23T09:00:00+02:00',state:'NOT_COMPLETED',evidence_identity:evidence('7') }),
      Object.freeze({ attempt_id:'attempt-2026-002',instruction_id:'instruction-2026-003',document_id:'document-2026-003',deputy_id:'deputy-pta-008',allocated_at:'2026-09-23T10:30:00+02:00',state:'ATTEMPTED',evidence_identity:evidence('8') }),
      Object.freeze({ attempt_id:'attempt-2026-003',instruction_id:'instruction-2026-006',document_id:'document-2026-006',deputy_id:'deputy-jhb-021',allocated_at:'2026-09-22T15:00:00+02:00',state:'COMPLETED',evidence_identity:evidence('9') }),
    ]),
    executions: Object.freeze([
      Object.freeze({ service_execution_id:'execution-2026-001',attempt_id:'attempt-2026-001',instruction_id:'instruction-2026-001',document_id:'document-2026-001',outcome:'NOT_COMPLETED',executed_at:'2026-09-23T12:10:00+02:00',evidence_identity:evidence('a') }),
      Object.freeze({ service_execution_id:'execution-2026-002',attempt_id:'attempt-2026-003',instruction_id:'instruction-2026-006',document_id:'document-2026-006',outcome:'COMPLETED',executed_at:'2026-09-22T16:45:00+02:00',evidence_identity:evidence('b') }),
    ]),
    returns: Object.freeze([
      Object.freeze({ return_id:'return-2026-001',instruction_id:'instruction-2026-006',document_id:'document-2026-006',attempt_id:'attempt-2026-003',service_execution_id:'execution-2026-002',service_outcome:'COMPLETED',generated_at:'2026-09-22T17:15:00+02:00',state:'GENERATED',evidence_identity:evidence('c') }),
    ]),
  });
}

export async function getLegalFinanceEvidence(kind, identity) {
  return Object.freeze({
    tenantId: 'tenant-wilsy-legal',
    entityType: kind === 'INVOICE' ? 'ClientInvoice' : kind === 'TARIFF_ASSESSMENT' ? 'TariffAssessment' : 'ProcessServiceBillingEligibility',
    entityIdentity: identity,
    visibility: 'FINANCE_VISIBLE',
    data: Object.freeze({ identity, status: 'CERTIFIED_EVIDENCE', currency: 'ZAR' }),
  });
}

export async function registerLegalIntake(value) {
  return Object.freeze({ disposition:'CREATED',tenantId:'tenant-wilsy-legal',caseMatter:Object.freeze({case_matter_id:value.caseMatterId}),instruction:Object.freeze({instruction_id:value.instructionId}),document:Object.freeze({document_id:value.documentId}),custodyEvent:Object.freeze({custody_event_id:value.registrationCustodyEventId}) });
}

export async function generateLegalReturnOfService(value) {
  return Object.freeze({ tenantId:'tenant-wilsy-legal',returnId:value.returnId,serviceExecutionId:value.executionId,serviceOutcome:'COMPLETED',state:'GENERATED' });
}

export async function getSheriffOperationalQueues() { return denied('SHERIFF_QUEUE_READ'); }
export async function getDeputyPersonalActiveWork() { return denied('DEPUTY_WORK_READ'); }
export async function getDeputyFieldCapabilities() { return denied('DEPUTY_CAPABILITY_READ'); }
export async function getLegalClientMatters() { return denied('CLIENT_MATTER_READ'); }
export async function transitionDeputyFieldAttempt() { return denied('DEPUTY_TRANSITION'); }
export async function recordDeputyFieldOutcome() { return denied('DEPUTY_OUTCOME'); }
`;

const authModule = String.raw`
export const useAuth = () => ({
  user: {
    id: 'principal-visual-partner',
    email: 'partner@wilsy.legal',
    role: 'tenant_legal_partner',
    tenantId: 'tenant-wilsy-legal',
  },
  tenant: {
    tenantId: 'tenant-wilsy-legal',
    displayName: 'WILSY Legal Practice',
    status: 'ACTIVE',
  },
});
`;

const tenantModule = String.raw`
export const useTenants = () => ({
  activeTenant: {
    tenantId: 'tenant-wilsy-legal',
    displayName: 'WILSY Legal Practice',
    status: 'ACTIVE',
  },
  tenants: [],
});
`;

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'wilsy-d14-legal-operations-visual-gate',
      enforce: 'pre',
      resolveId(source) {
        if (source.endsWith('/services/legalOperationsService.js') || source.endsWith('services/legalOperationsService.js')) return SERVICE_RESOLVED;
        if (source.endsWith('/contexts/authContext') || source.endsWith('/contexts/authContext.jsx') || source.endsWith('contexts/authContext') || source.endsWith('contexts/authContext.jsx')) return AUTH_RESOLVED;
        if (source.endsWith('/contexts/tenantContext') || source.endsWith('/contexts/tenantContext.jsx') || source.endsWith('contexts/tenantContext') || source.endsWith('contexts/tenantContext.jsx')) return TENANT_RESOLVED;
        return null;
      },
      load(id) {
        if (id === SERVICE_RESOLVED) return serviceModule;
        if (id === AUTH_RESOLVED) return authModule;
        if (id === TENANT_RESOLVED) return tenantModule;
        return null;
      },
    },
  ],
  resolve: {\n    alias: {\n      '@': path.resolve(__dirname, './src'),\n    },\n  },\n  server: {
    host: '127.0.0.1',
    port: 4178,
    strictPort: true,
    open: false,
  },
});

/**
 * SOVEREIGN ARTIFACT SEAL
 * ARTIFACT: vite.legal-operations-visual.config.js
 * VERSION: v1.0.3-L8-7D14-LEGAL-OPERATIONS-VISUAL-GATE-ALIAS-PARITY
 * AUTHORITY BOUNDARY: deterministic visual test support only
 * PRODUCTION IMPACT: none
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
