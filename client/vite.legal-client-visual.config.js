/**
 * WILSY OS — LEGAL CLIENT COCKPIT VISUAL GATE
 * VERSION: v1.1.0-L8-7D9-LEGAL-CLIENT-WORKSPACE-VISUAL-GATE
 * AUTHORITY: Test-support only. Imports the real production LegalDashboard and
 *            real application CSS while replacing only the browser service
 *            module with deterministic sanitized D7-shaped visual evidence.
 * PRODUCTION IMPACT: NONE. D9 shared chrome Auth/Tenant context is mocked only for deterministic visual certification.
 * FAIL-CLOSED: Any SHERIFF/DEPUTY read or command invoked by LEGAL_CLIENT mode
 *              throws immediately so cross-role visual leakage cannot hide.
 */
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const VIRTUAL_ID = 'virtual:wilsy-legal-operations-visual-service';
const RESOLVED_ID = '\0' + VIRTUAL_ID;
const AUTH_CONTEXT_ID = 'virtual:wilsy-legal-client-auth-context';
const AUTH_CONTEXT_RESOLVED_ID = '\0' + AUTH_CONTEXT_ID;
const TENANT_CONTEXT_ID = 'virtual:wilsy-legal-client-tenant-context';
const TENANT_CONTEXT_RESOLVED_ID = '\0' + TENANT_CONTEXT_ID;

const visualServiceModule = String.raw`
export const LEGAL_OPERATIONS_CLIENT_VERSION =
  'v1.3.0-L8-7D7-CLIENT-MATTER-READ-CLIENT';

const denied = (name) => {
  throw new Error('L8_7V1_CROSS_ROLE_VISUAL_ACCESS_' + name);
};

export async function getLegalClientMatters() {
  return Object.freeze({
    schema: 'WILSY-LEGAL-CLIENT-MATTER-PROJECTION/V1',
    version: 'v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION',
    tenantId: 'tenant-visual-cert',
    visibility: 'LEGAL_CLIENT_EXPLICIT_MATTERS',
    matters: Object.freeze([
      Object.freeze({
        caseMatterId: 'matter-2026-001',
        matterReference: 'MABASO v ORION HOLDINGS',
        openedAt: '2026-09-18T08:15:00+02:00',
        state: 'OPEN',
      }),
      Object.freeze({
        caseMatterId: 'matter-2026-002',
        matterReference: 'NORTHSTAR PROPERTY TRANSFER',
        openedAt: '2026-09-12T10:30:00+02:00',
        state: 'OPEN',
      }),
      Object.freeze({
        caseMatterId: 'matter-2026-003',
        matterReference: 'KHUMALO ESTATE ADMINISTRATION',
        openedAt: '2026-08-29T09:00:00+02:00',
        state: 'CLOSED',
      }),
      Object.freeze({
        caseMatterId: 'matter-2026-004',
        matterReference: 'SABLE COMMERCIAL ADVISORY',
        openedAt: '2026-08-14T14:45:00+02:00',
        state: 'OPEN',
      }),
    ]),
  });
}

export async function getSheriffOperationalQueues() {
  return denied('SHERIFF_QUEUE_READ');
}

export async function getDeputyPersonalActiveWork() {
  return denied('DEPUTY_WORK_READ');
}

export async function getDeputyFieldCapabilities() {
  return denied('DEPUTY_CAPABILITY_READ');
}

export async function transitionDeputyFieldAttempt() {
  return denied('DEPUTY_TRANSITION_COMMAND');
}

export async function recordDeputyFieldOutcome() {
  return denied('DEPUTY_OUTCOME_COMMAND');
}
`;

const visualAuthContextModule = String.raw`
export const useAuth = () => ({
  user: {
    id: 'principal-visual-client',
    email: 'client@visual.wilsy.test',
    role: 'tenant_legal_client',
    tenantId: 'tenant-visual-cert',
  },
  tenant: {
    tenantId: 'tenant-visual-cert',
    displayName: 'Mabaso Legal Client Workspace',
    status: 'ACTIVE',
  },
});
`;

const visualTenantContextModule = String.raw`
export const useTenants = () => ({
  activeTenant: {
    tenantId: 'tenant-visual-cert',
    displayName: 'Mabaso Legal Client Workspace',
    status: 'ACTIVE',
  },
  tenants: [],
});
`;

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'wilsy-l8-7d9-legal-client-workspace-visual-service',
      enforce: 'pre',
      resolveId(source) {
        if (
          source.endsWith('/services/legalOperationsService.js')
          || source.endsWith('services/legalOperationsService.js')
        ) {
          return RESOLVED_ID;
        }
        if (
          source.endsWith('/contexts/authContext')
          || source.endsWith('/contexts/authContext.jsx')
          || source.endsWith('contexts/authContext')
          || source.endsWith('contexts/authContext.jsx')
        ) {
          return AUTH_CONTEXT_RESOLVED_ID;
        }
        if (
          source.endsWith('/contexts/tenantContext')
          || source.endsWith('/contexts/tenantContext.jsx')
          || source.endsWith('contexts/tenantContext')
          || source.endsWith('contexts/tenantContext.jsx')
        ) {
          return TENANT_CONTEXT_RESOLVED_ID;
        }
        return null;
      },
      load(id) {
        if (id === RESOLVED_ID) return visualServiceModule;
        if (id === AUTH_CONTEXT_RESOLVED_ID) return visualAuthContextModule;
        if (id === TENANT_CONTEXT_RESOLVED_ID) return visualTenantContextModule;
        return null;
      },
    },
  ],
  server: {
    host: '127.0.0.1',
    port: 4178,
    strictPort: true,
    open: false,
  },
});

/**
 * SOVEREIGN ARTIFACT SEAL
 * ARTIFACT: vite.legal-client-visual.config.js
 * VERSION: v1.1.0-L8-7D9-LEGAL-CLIENT-WORKSPACE-VISUAL-GATE
 * AUTHORITY BOUNDARY: visual test-support transport fixture only
 * PRODUCTION IMPACT: none
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
