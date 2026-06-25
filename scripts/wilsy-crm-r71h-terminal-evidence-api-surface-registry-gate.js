/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R71H-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-API-SURFACE-REGISTRY-AUTHORITY',
  'WILSY_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_API_SURFACE_REGISTRY_VERSION',
  'buildLeadSearchRegulatorInvestorTerminalEvidenceApiSurfaceRegistry',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_API_SURFACE_REGISTRY_READY',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_API_SURFACE_REGISTRY',
  'apiSurfaceRegistry',
  'clientContracts',
  'responseSchemaRegistry',
  'integrationChecklist',
  'terminal_summary',
  'terminal_manifest',
  'terminal_packet',
  'terminal_inspection_desk',
  'terminal_diligence_room',
  'terminal_command_index',
  'terminal_cockpit_contract',
  'crm_cockpit',
  'ai_command_layer',
  'regulator_portal',
  'investor_room',
  'audit_assurance',
  'sourceCockpitContractSummary',
  'productizationSurface',
  'terminalStop',
  'noR70F',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R71H_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_API_SURFACE_REGISTRY_ROUTE_CONTRACT',
  '/search/regulator-evidence/terminal-api-surface-registry/latest',
  '/api/crm/command/search/regulator-evidence/terminal-api-surface-registry/latest',
  '/api/crm/command/search/regulator-evidence/terminal-cockpit-contract/latest',
  '/api/crm/command/search/regulator-evidence/terminal-command-index/latest',
  'R71H_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_API_SURFACE_REGISTRY_ROUTE',
  'productizationSurface',
  'terminalStop',
  'noR70F',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R71H terminal evidence API surface registry gate.
 * @collaboration CRM regulator evidence gates, cockpit contract API, API surface registry.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R71H terminal evidence API surface registry contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R71H gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior or recursive expansion appears.
 * @collaboration JSON-only terminal evidence API surface registry posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R71H gate blocked ${label}`);
  }
};

/**
 * @function runR71HTerminalEvidenceApiSurfaceRegistryGate
 * @description Validates R71H terminal regulator/investor evidence API surface registry service and route contracts.
 * @collaboration CRM command routes, lead search engine service, R71G cockpit contract.
 */
const runR71HTerminalEvidenceApiSurfaceRegistryGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');
  assertBlocked(service, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in service');
  assertBlocked(route, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in route');

  console.log('PASS: WILSY CRM TERMINAL REGULATOR INVESTOR EVIDENCE API SURFACE REGISTRY GATE');
  console.log(' - R71H API surface registry authority present');
  console.log(' - R71G cockpit contract and R71F command index source routes anchored');
  console.log(' - surface/client/schema/integration registry posture present');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - filesystem export and recursive expansion blocked');
};

runR71HTerminalEvidenceApiSurfaceRegistryGate();
