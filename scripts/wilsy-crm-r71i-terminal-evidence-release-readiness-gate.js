/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R71I-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-RELEASE-READINESS-AUTHORITY',
  'WILSY_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_READINESS_VERSION',
  'buildLeadSearchRegulatorInvestorTerminalEvidenceReleaseReadiness',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_READINESS_READY',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_READINESS',
  'releaseGates',
  'goLiveChecklist',
  'releaseReadinessScore',
  'deploymentPosture',
  'releaseNotes',
  'protectedBoundaries',
  'TERMINAL_EVIDENCE_API_SURFACE_RELEASE',
  'releaseDecision',
  'GO',
  'uiMutationRequired',
  'authMutationRequired',
  'securityMutationRequired',
  'filesystemExportRequired',
  'sourceApiSurfaceRegistrySummary',
  'productizationSurface',
  'terminalStop',
  'noR70F',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R71I_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_READINESS_ROUTE_CONTRACT',
  '/search/regulator-evidence/terminal-release-readiness/latest',
  '/api/crm/command/search/regulator-evidence/terminal-release-readiness/latest',
  '/api/crm/command/search/regulator-evidence/terminal-api-surface-registry/latest',
  '/api/crm/command/search/regulator-evidence/terminal-cockpit-contract/latest',
  'R71I_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_RELEASE_READINESS_ROUTE',
  'productizationSurface',
  'terminalStop',
  'noR70F',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R71I terminal evidence release readiness gate.
 * @collaboration CRM regulator evidence gates, API surface registry, release readiness API.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R71I terminal evidence release readiness contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R71I gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior or recursive expansion appears.
 * @collaboration JSON-only terminal evidence release readiness posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R71I gate blocked ${label}`);
  }
};

/**
 * @function runR71ITerminalEvidenceReleaseReadinessGate
 * @description Validates R71I terminal regulator/investor evidence release readiness service and route contracts.
 * @collaboration CRM command routes, lead search engine service, R71H API surface registry.
 */
const runR71ITerminalEvidenceReleaseReadinessGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');
  assertBlocked(service, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in service');
  assertBlocked(route, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in route');

  console.log('PASS: WILSY CRM TERMINAL REGULATOR INVESTOR EVIDENCE RELEASE READINESS GATE');
  console.log(' - R71I release readiness authority present');
  console.log(' - R71H API surface registry and R71G cockpit contract source routes anchored');
  console.log(' - release gates/checklist/deployment posture present');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - filesystem export and recursive expansion blocked');
};

runR71ITerminalEvidenceReleaseReadinessGate();
