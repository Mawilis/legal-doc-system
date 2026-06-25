/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R71B-CRM-TERMINAL-REGULATOR-INVESTOR-EVIDENCE-MANIFEST-AUTHORITY',
  'WILSY_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_MANIFEST_VERSION',
  'buildLeadSearchRegulatorInvestorTerminalEvidenceManifest',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_MANIFEST_READY',
  'CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_MANIFEST',
  'routeRegistry',
  'hashRegistry',
  'authorityRegistry',
  'inspectionSections',
  'competitivePosture',
  'productizationSurface',
  'terminalStop',
  'noR70F',
  'sourceTerminalEvidenceSummary',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R71B_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_MANIFEST_ROUTE_CONTRACT',
  '/search/regulator-evidence/terminal-manifest/latest',
  '/api/crm/command/search/regulator-evidence/terminal-manifest/latest',
  '/api/crm/command/search/regulator-evidence/terminal-summary/latest',
  'R71B_SAFE_CRM_TERMINAL_REGULATOR_INVESTOR_EVIDENCE_MANIFEST_ROUTE',
  'productizationSurface',
  'terminalStop',
  'noR70F',
];

/**
 * @function readSourceFile
 * @description Reads source files for the short-name R71B terminal evidence manifest gate.
 * @collaboration CRM regulator evidence gates, terminal summary API, buyer-readable manifest API.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails when a required R71B terminal evidence manifest contract is missing.
 * @collaboration Documentation guard, secret guard, CRM regulator evidence gates.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R71B gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden filesystem export behavior or recursive expansion appears.
 * @collaboration JSON-only terminal evidence manifest posture, regulator/investor evidence guardrails.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R71B gate blocked ${label}`);
  }
};

/**
 * @function runR71BTerminalEvidenceManifestGate
 * @description Validates R71B terminal regulator/investor evidence manifest service and route contracts.
 * @collaboration CRM command routes, lead search engine service, R71A terminal summary.
 */
const runR71BTerminalEvidenceManifestGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => assertIncludes(service, contract, 'service contract'));
  requiredRouteContracts.forEach((contract) => assertIncludes(route, contract, 'route contract'));

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');
  assertBlocked(service, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in service');
  assertBlocked(route, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive R70F expansion in route');

  console.log('PASS: WILSY CRM TERMINAL REGULATOR INVESTOR EVIDENCE MANIFEST GATE');
  console.log(' - R71B manifest authority contract present');
  console.log(' - R71A terminal summary source route anchored');
  console.log(' - route/hash/authority/inspection manifest posture present');
  console.log(' - terminalStop and noR70F posture present');
  console.log(' - filesystem export and recursive expansion blocked');
};

runR71BTerminalEvidenceManifestGate();
