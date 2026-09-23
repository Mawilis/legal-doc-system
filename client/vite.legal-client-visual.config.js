/**
 * WILSY OS — LEGAL CLIENT COCKPIT VISUAL GATE
 * VERSION: v1.0.0-L8-7V1-LEGAL-CLIENT-VISUAL-GATE
 * AUTHORITY: Test-support only. Imports the real production LegalDashboard and
 *            real application CSS while replacing only the browser service
 *            module with deterministic sanitized D7-shaped visual evidence.
 * PRODUCTION IMPACT: NONE.
 * FAIL-CLOSED: Any SHERIFF/DEPUTY read or command invoked by LEGAL_CLIENT mode
 *              throws immediately so cross-role visual leakage cannot hide.
 */
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const VIRTUAL_ID = 'virtual:wilsy-legal-operations-visual-service';
const RESOLVED_ID = '\0' + VIRTUAL_ID;

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

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'wilsy-l8-7v1-legal-client-visual-service',
      enforce: 'pre',
      resolveId(source) {
        if (
          source.endsWith('/services/legalOperationsService.js')
          || source.endsWith('services/legalOperationsService.js')
        ) {
          return RESOLVED_ID;
        }
        return null;
      },
      load(id) {
        return id === RESOLVED_ID ? visualServiceModule : null;
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
 * VERSION: v1.0.0-L8-7V1-LEGAL-CLIENT-VISUAL-GATE
 * AUTHORITY BOUNDARY: visual test-support transport fixture only
 * PRODUCTION IMPACT: none
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
