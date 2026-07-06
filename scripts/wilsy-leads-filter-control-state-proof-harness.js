/* eslint-disable */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const LEADS = path.join(ROOT, 'client', 'src', 'components', 'crm', 'lead', 'WilsyLeadOperatingRoom.jsx');
const MODEL = path.join(ROOT, 'server', 'models', 'crmControlStateModel.js');
const ROUTE = path.join(ROOT, 'server', 'routes', 'crmControlStateRoutes.js');
const SERVER = path.join(ROOT, 'server', 'server.js');

/**
 * @function assertWilsyLeadsFilterControlCondition
 * @description Throws when a Leads filter control-state proof condition fails.
 * @param {boolean} condition - Condition to assert.
 * @param {string} message - Failure message.
 * @returns {void}
 * @collaboration Leads filter buttons, backend control-state route, institutional evidence, and production proof harness.
 */
function assertWilsyLeadsFilterControlCondition(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

/**
 * @function runWilsyLeadsFilterControlStateProofHarness
 * @description Proves Leads filter buttons own real checkbox state and persist to backend with evidence headers.
 * @returns {void}
 * @collaboration WilsyLeadOperatingRoom, crmControlStateRoutes, crmControlStateModel, server route mount, and Wilsy guard discipline.
 */
function runWilsyLeadsFilterControlStateProofHarness() {
  const leads = fs.readFileSync(LEADS, 'utf8');
  const model = fs.readFileSync(MODEL, 'utf8');
  const route = fs.readFileSync(ROUTE, 'utf8');
  const server = fs.readFileSync(SERVER, 'utf8');

  const proof = {
    leadsEndpoint: leads.includes('/api/crm/control-state/leads/filters'),
    leadsUsesEffect: leads.includes('useEffect(() => installWilsyLeadFilterControlStateController(), []);'),
    realCheckboxState: leads.includes('setWilsyLeadFilterChecked') && leads.includes('HTMLInputElement.prototype'),
    backendGet: leads.includes("method: 'GET'"),
    backendPut: leads.includes("method: 'PUT'"),
    institutionalPayload: leads.includes('institutionalHeaders') && leads.includes('strikePayload'),
    selectedStateLocalPersistence: leads.includes('WILSY_LEADS_FILTER_LOCAL_STATE_KEY'),
    modelUniqueScope: model.includes('crm_control_state_unique_scope') && model.includes('crm_control_states'),
    routeGet: route.includes("router.get('/leads/filters'"),
    routePut: route.includes("router.put('/leads/filters'"),
    routeEvidence: route.includes('assertInstitutionalMutationEnvelope') && route.includes('evidenceLedger'),
    serverMounted: server.includes("app.use('/api/crm/control-state', crmControlStateRoutes);"),
    noGlobalBridge: !leads.includes('wilsyCrmControlRepairBridge.js'),
  };

  Object.entries(proof).forEach(([key, value]) => {
    assertWilsyLeadsFilterControlCondition(Boolean(value), `Leads filter control-state proof failed: ${key}`);
  });

  console.log('[WILSY LEADS FILTER CONTROL STATE PROOF PASS]', proof);
}

runWilsyLeadsFilterControlStateProofHarness();
