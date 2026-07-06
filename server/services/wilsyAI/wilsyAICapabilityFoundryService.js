/* eslint-disable */
import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import mongoose from 'mongoose';
import {
  buildWilsyCapabilityManifest,
  buildWilsyCapabilityProofCases,
  buildWilsyPromotionGates,
  buildWilsyToolContract,
  inferWilsyCapabilityBlueprint,
  normalizeWilsyCapabilityId,
} from './wilsyAIToolRegistryService.js';

/**
 * @function coerceWilsyFoundryText
 * @description Safely coerces Foundry input into bounded text.
 * @param {unknown} value - Raw value.
 * @param {number} limit - Maximum length.
 * @returns {string} Bounded text.
 * @collaboration Capability Foundry, manifest generation, and quarantine safety.
 */
function coerceWilsyFoundryText(value = '', limit = 1400) {
  return String(value || '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, limit);
}

/**
 * @function buildWilsyFoundryCandidateId
 * @description Builds a stable candidate id from capability and source question.
 * @param {Object} params - Candidate parameters.
 * @param {string} params.capabilityId - Capability id.
 * @param {string} params.question - Source question.
 * @returns {string} Candidate id.
 * @collaboration Quarantine paths, database records, and reusable capability tracking.
 */
function buildWilsyFoundryCandidateId({
  capabilityId = 'custom_business_capability',
  question = '',
} = {}) {
  const hash = crypto
    .createHash('sha256')
    .update(`${capabilityId}:${coerceWilsyFoundryText(question, 1200)}`)
    .digest('hex')
    .slice(0, 12);

  return `${normalizeWilsyCapabilityId(capabilityId)}_${hash}`;
}

/**
 * @function getWilsyFoundryQuarantineRoot
 * @description Returns the Capability Foundry quarantine root.
 * @returns {string} Absolute quarantine root path.
 * @collaboration Quarantine staging, non-production code generation boundary, and review workflow.
 */
function getWilsyFoundryQuarantineRoot() {
  return path.resolve(process.cwd(), 'server/services/wilsyAI/foundry/quarantine');
}

/**
 * @function writeWilsyJsonFile
 * @description Writes a formatted JSON file into quarantine.
 * @param {string} filePath - Absolute file path.
 * @param {Object} payload - JSON payload.
 * @returns {Promise<void>} Completion promise.
 * @collaboration Capability quarantine, proof artifacts, and reviewable evidence files.
 */
async function writeWilsyJsonFile(filePath = '', payload = {}) {
  await fs.writeFile(filePath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
}

/**
 * @function persistWilsyFoundryCandidate
 * @description Persists a capability candidate to MongoDB when available.
 * @param {Object} candidate - Candidate object.
 * @returns {Promise<Object>} Persistence result.
 * @collaboration Capability backlog, tenant evidence, and reusable tool discovery.
 */
async function persistWilsyFoundryCandidate(candidate = {}) {
  const db = mongoose.connection?.db;

  if (!db) {
    return {
      status: 'PERSISTENCE_UNAVAILABLE',
      message: 'MongoDB is not connected; candidate was staged in quarantine only.',
    };
  }

  await db.collection('wilsy_capability_foundry_candidates').updateOne(
    { candidateId: candidate.candidateId },
    {
      $set: {
        ...candidate,
        updatedAt: new Date(),
      },
      $setOnInsert: {
        createdAt: new Date(),
      },
    },
    { upsert: true }
  );

  return {
    status: 'PERSISTED',
    message: 'Capability candidate persisted for review.',
  };
}

/**
 * @function stageWilsyCapabilityCandidate
 * @description Stages a missing capability candidate in quarantine with manifest, contract, and proof cases.
 * @param {Object} params - Candidate parameters.
 * @param {string} params.question - Tenant question.
 * @param {Object} params.intent - Operator intent.
 * @param {Object} params.tool - Failed or missing tool.
 * @param {string} params.tenantId - Tenant id.
 * @param {string} params.operatorId - Operator id.
 * @param {string} params.workspaceRoute - Workspace route.
 * @param {string} params.workspaceSurface - Workspace surface.
 * @returns {Promise<Object>} Candidate result.
 * @collaboration Self-extending tool registry, quarantine staging, evidence requirements, and admin approval workflow.
 */
export async function stageWilsyCapabilityCandidate({
  question = '',
  intent = {},
  tool = {},
  tenantId = 'MASTER',
  operatorId = 'WILSY_OPERATOR',
  workspaceRoute = '/crm/setup',
  workspaceSurface = 'Wilsy OS Workspace',
} = {}) {
  const blueprint = inferWilsyCapabilityBlueprint({ question, intent, tool });
  const manifest = buildWilsyCapabilityManifest({
    blueprint,
    question,
    tenantId,
    operatorId,
  });
  const contract = buildWilsyToolContract(manifest);
  const proofCases = buildWilsyCapabilityProofCases(manifest);
  const promotionGates = buildWilsyPromotionGates();
  const candidateId = buildWilsyFoundryCandidateId({
    capabilityId: manifest.capabilityId,
    question,
  });
  const quarantineRoot = getWilsyFoundryQuarantineRoot();
  const candidateDir = path.join(quarantineRoot, candidateId);
  const safeRelativePath = `server/services/wilsyAI/foundry/quarantine/${candidateId}`;

  await fs.mkdir(candidateDir, { recursive: true });

  const candidate = {
    contractVersion: 'P60K5Q10AR_CAPABILITY_FOUNDRY_CANDIDATE',
    candidateId,
    capabilityId: manifest.capabilityId,
    businessName: manifest.businessName,
    status: 'STAGED_FOR_REVIEW',
    generatedAt: new Date().toISOString(),
    tenantId,
    operatorId,
    workspaceRoute: coerceWilsyFoundryText(workspaceRoute, 240),
    workspaceSurface: coerceWilsyFoundryText(workspaceSurface, 1200),
    sourceQuestion: coerceWilsyFoundryText(question, 1200),
    mutationRisk: manifest.mutationRisk,
    approvalRequired: manifest.approvalRequired,
    evidenceRequired: manifest.evidenceRequired,
    quarantinePath: safeRelativePath,
    manifest,
    contract,
    proofCases,
    promotionGates,
    publication: {
      approved: false,
      published: false,
      autoPublish: false,
      reason: 'Human/admin approval required before promotion to live registry.',
    },
    institutionalHeaders: {
      tenantId,
      operatorId,
      generatedAt: new Date().toISOString(),
      route: workspaceRoute,
      commandSurface: 'WILSY_CAPABILITY_FOUNDRY',
      mutation: false,
      contractVersion: 'P60K5Q10AR_CAPABILITY_FOUNDRY',
    },
    strikePayload: {
      institutionalHeaders: {
        tenantId,
        operatorId,
        generatedAt: new Date().toISOString(),
        route: workspaceRoute,
        commandSurface: 'WILSY_CAPABILITY_FOUNDRY',
        mutation: false,
        contractVersion: 'P60K5Q10AR_CAPABILITY_FOUNDRY',
      },
      commandType: 'CAPABILITY_CANDIDATE_STAGED',
      mutation: false,
    },
  };

  await writeWilsyJsonFile(path.join(candidateDir, 'manifest.json'), manifest);
  await writeWilsyJsonFile(path.join(candidateDir, 'tool-contract.json'), contract);
  await writeWilsyJsonFile(path.join(candidateDir, 'proof-cases.json'), { proofCases });
  await writeWilsyJsonFile(path.join(candidateDir, 'promotion-gates.json'), { promotionGates });
  await writeWilsyJsonFile(path.join(candidateDir, 'candidate.json'), candidate);

  const persistence = await persistWilsyFoundryCandidate(candidate);

  return {
    ...candidate,
    persistence,
  };
}

/**
 * @function buildWilsyCapabilityFoundryToolRun
 * @description Builds a sourceTrace-compatible tool run for staged capability candidates.
 * @param {Object} candidate - Capability candidate.
 * @returns {Object} Tool run.
 * @collaboration Operator Kernel source trace, Capability Foundry visibility, and tenant-facing transparency.
 */
export function buildWilsyCapabilityFoundryToolRun(candidate = {}) {
  return {
    tool: 'capability_foundry',
    label: 'Capability Foundry',
    domain: candidate.manifest?.domain || 'foundry',
    status: candidate.status || 'STAGED_FOR_REVIEW',
    statusLabel: 'Capability staged for review',
    count: 1,
    collectionsChecked: ['Capability manifest', 'Tool contract', 'Proof cases', 'Promotion gates'],
    message: `${candidate.businessName || 'Capability'} was staged for review at ${candidate.quarantinePath || 'quarantine'}.`,
    candidateId: candidate.candidateId,
    capabilityId: candidate.capabilityId,
    approvalRequired: true,
  };
}

export default stageWilsyCapabilityCandidate;
