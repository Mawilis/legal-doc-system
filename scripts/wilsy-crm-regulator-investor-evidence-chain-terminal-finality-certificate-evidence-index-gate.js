/* eslint-disable */
const fs = require('fs');
const path = require('path');

const SERVICE = path.resolve('server/services/wilsyCrmLeadSearchEngineService.js');
const ROUTE = path.resolve('server/routes/crmCommandRoutes.js');

const requiredServiceContracts = [
  'R69F-REGULATOR-INVESTOR-EVIDENCE-CHAIN-TERMINAL-FINALITY-CERTIFICATE-EVIDENCE-INDEX-AUTHORITY',
  'WILSY_CRM_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_VERSION',
  'buildLeadSearchRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndex',
  'computeRegulatorInvestorEvidenceChainTerminalFinalityCertificateEvidenceIndexHash',
  'REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEXED',
  'FINALITY_CERTIFICATE_EVIDENCE_INDEXED',
  'terminalFinalityCertificateEvidenceIndex',
  'evidenceIndexHash',
  'evidenceRoutes',
  'expectedSourceStatusesVerified',
  'evidenceRoutesVerified',
  'certificateHashVerified',
  'receiptHashVerified',
  'terminalSealHashVerified',
  'finalityDispositionVerified',
  'regulatorReady',
  'investorReady',
  'JSON_RESPONSE_ONLY',
  'noFilesystemWrite',
];

const requiredRouteContracts = [
  'WILSY_R69F_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_ROUTE_CONTRACT',
  '/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/latest',
  '/api/crm/command/search/regulator-evidence/dossier-chain/evidence-bundle/terminal-seal/verification-receipt/finality-certificate/evidence-index/latest',
  'R69F_SAFE_REGULATOR_INVESTOR_EVIDENCE_CHAIN_TERMINAL_FINALITY_CERTIFICATE_EVIDENCE_INDEX_ROUTE',
];

/**
 * @function readSourceFile
 * @description Reads a source file for R69F terminal finality certificate evidence index gate validation.
 * @collaboration CRM regulator evidence gates, backend route contracts, terminal evidence index controls.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertIncludes
 * @description Fails the R69F gate when a required contract is missing.
 * @collaboration CRM regulator evidence gates, documentation guard, secret guard.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R69F gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails the R69F gate when forbidden filesystem export behavior appears.
 * @collaboration CRM regulator evidence gates, JSON-only proof controls, filesystem safety checks.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R69F gate blocked ${label}`);
  }
};

/**
 * @function runR69FTerminalFinalityCertificateEvidenceIndexGate
 * @description Validates R69F terminal regulator and investor finality certificate evidence index contracts.
 * @collaboration CRM command routes, lead search engine service, regulator/investor proof chain.
 */
const runR69FTerminalFinalityCertificateEvidenceIndexGate = () => {
  const service = readSourceFile(SERVICE);
  const route = readSourceFile(ROUTE);

  requiredServiceContracts.forEach((contract) => {
    assertIncludes(service, contract, 'service contract');
  });

  requiredRouteContracts.forEach((contract) => {
    assertIncludes(route, contract, 'route contract');
  });

  assertBlocked(service, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in service');
  assertBlocked(route, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem export in route');

  console.log('PASS: WILSY CRM REGULATOR INVESTOR EVIDENCE CHAIN TERMINAL FINALITY CERTIFICATE EVIDENCE INDEX GATE');
  console.log(' - R69F terminal finality certificate evidence index authority contract present');
  console.log(' - R69E finality certificate verifier source route anchored');
  console.log(' - evidence index hash contract present');
  console.log(' - JSON response only evidence index contract present');
  console.log(' - filesystem export behavior blocked');
};

runR69FTerminalFinalityCertificateEvidenceIndexGate();
