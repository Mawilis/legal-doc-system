/* eslint-disable */
/**
 * WILSY OS — CRM / CONTRACT LEDGER SOURCE CONNECTOR
 * VERSION: 2.0.0-LIVE-EVIDENCE-SPINE
 *
 * Story:
 * CRM is not a contact list. In Wilsy OS, CRM is the legal identity spine:
 * counterparty identity, governing agreement, deal posture, and authority to bind.
 *
 * This connector links:
 * - Zoho CRM live records when OAuth/API credentials exist.
 * - Existing Wilsy CrmRecord model when MongoDB is live.
 * - Optional file ledger when configured.
 *
 * Truth policy:
 * It never fabricates VERIFIED.
 * VERIFIED requires auditable source identity and retrieval metadata.
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import mongoose from 'mongoose';
import { fileURLToPath, pathToFileURL } from 'url';
import dotenv from 'dotenv';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SERVER_ROOT = path.resolve(__dirname, '../..');
const REPO_ROOT = path.resolve(SERVER_ROOT, '..');

const TRUTH_POLICY = 'NO_FAKE_VERIFIED';
const CONNECTOR_LABEL = 'CRM / Contract Ledger';
const LOCAL_MODEL_PATH = path.resolve(SERVER_ROOT, 'models/CrmRecord.js');
const DEFAULT_LEDGER_PATH = 'server/data/source-registry/crm-contract-ledger.MASTER.json';

const ZOHO_MODULES = Object.freeze({
  leads: 'Leads',
  contacts: 'Contacts',
  accounts: 'Accounts',
  deals: 'Deals',
  tasks: 'Tasks',
  meetings: 'Events',
});

const ZOHO_FIELDS = Object.freeze({
  Leads: [
    'id',
    'Lead_Name',
    'First_Name',
    'Last_Name',
    'Company',
    'Email',
    'Phone',
    'Lead_Source',
    'Owner',
    'Created_Time',
    'Modified_Time',
  ],
  Contacts: [
    'id',
    'Full_Name',
    'First_Name',
    'Last_Name',
    'Account_Name',
    'Email',
    'Phone',
    'Title',
    'Owner',
    'Created_Time',
    'Modified_Time',
  ],
  Accounts: [
    'id',
    'Account_Name',
    'Account_Number',
    'Website',
    'Phone',
    'Industry',
    'Owner',
    'Created_Time',
    'Modified_Time',
  ],
  Deals: [
    'id',
    'Deal_Name',
    'Account_Name',
    'Contact_Name',
    'Stage',
    'Amount',
    'Closing_Date',
    'Owner',
    'Created_Time',
    'Modified_Time',
  ],
});

/**
 * @function sha3
 * @description Creates a SHA3-512 evidence fingerprint.
 * @param {*} value - Value to hash.
 * @returns {string} SHA3-512 hex digest.
 * @collaboration Gives CRM evidence responses a stable audit fingerprint without exposing secrets.
 */
function sha3(value) {
  return crypto
    .createHash('sha3-512')
    .update(String(value || ''))
    .digest('hex');
}

/**
 * @function safeString
 * @description Converts unknown values into trimmed strings.
 * @param {*} value - Candidate value.
 * @returns {string} Safe string.
 * @collaboration Prevents connector matching from failing on null CRM values.
 */
function safeString(value) {
  return String(value ?? '').trim();
}

/**
 * @function isMongooseConnected
 * @description Checks whether MongoDB is ready before querying the local CRM model.
 * @returns {boolean} Whether Mongoose has an active connection.
 * @collaboration Prevents local CRM fallback from causing runtime connector errors during boot.
 */
function isMongooseConnected() {
  return mongoose?.connection?.readyState === 1;
}

/**
 * @function normalizeInput
 * @description Normalizes Source Registry artifact input for CRM evidence lookup.
 * @param {object} input - Source Registry or artifact payload.
 * @returns {object} Normalized lookup context.
 * @collaboration Allows verify routes, dashboard actions and connector smoke tests to share one CRM contract.
 */
function normalizeInput(input = {}) {
  const artifact = input.artifact || input.document || input.record || input || {};

  return {
    tenantId: input.tenantId || artifact.tenantId || 'MASTER',
    artifactId:
      artifact.id ||
      artifact.artifactId ||
      artifact.templateId ||
      artifact.type ||
      input.artifactId ||
      input.id ||
      '',
    artifactType: artifact.type || input.type || '',
    title: artifact.title || input.title || '',
    agreementId:
      artifact.agreementId ||
      artifact.contractId ||
      artifact.dealId ||
      input.agreementId ||
      input.contractId ||
      input.dealId ||
      '',
    counterpartyLegalName:
      artifact.counterpartyLegalName ||
      artifact.counterpartyName ||
      artifact.company ||
      artifact.accountName ||
      input.counterpartyLegalName ||
      input.counterpartyName ||
      '',
    email: artifact.email || input.email || '',
    raw: artifact,
  };
}

/**
 * @function sourceEnvelope
 * @description Wraps source evidence metadata in one consistent object.
 * @param {string} sourceSystem - Source system name.
 * @param {string} sourceRecordId - Source record id.
 * @param {object} record - Source record.
 * @param {string} retrievedAt - Retrieval timestamp.
 * @returns {object} Source envelope.
 * @collaboration Makes every CRM connector result explain where the evidence came from.
 */
function sourceEnvelope(
  sourceSystem,
  sourceRecordId,
  record,
  retrievedAt = new Date().toISOString()
) {
  return {
    sourceSystem,
    sourceRecordId: safeString(sourceRecordId),
    retrievedAt,
    record,
    evidenceHash: sha3(JSON.stringify({ sourceSystem, sourceRecordId, retrievedAt, record })),
  };
}

/**
 * @function resultBase
 * @description Builds common CRM connector result metadata.
 * @param {string} method - Connector method.
 * @param {object} context - Lookup context.
 * @returns {object} Common result fields.
 * @collaboration Keeps Source Registry repair cards consistent across CRM methods.
 */
function resultBase(method, context = {}) {
  return {
    connector: CONNECTOR_LABEL,
    method,
    tenantId: context.tenantId || 'MASTER',
    artifactId: context.artifactId || '',
    artifactType: context.artifactType || '',
    title: context.title || '',
    agreementId: context.agreementId || '',
    counterpartyLegalName: context.counterpartyLegalName || '',
    truthPolicy: TRUTH_POLICY,
    generatedAt: new Date().toISOString(),
  };
}

/**
 * @function missingResult
 * @description Returns a controlled MISSING state instead of a runtime connector error.
 * @param {string} method - Connector method.
 * @param {object} context - Lookup context.
 * @param {string} message - Missing evidence message.
 * @param {object} extra - Additional metadata.
 * @returns {object} Missing evidence result.
 * @collaboration Moves the repair board from broken integration to executable evidence work.
 */
function missingResult(method, context = {}, message = 'Live CRM evidence required.', extra = {}) {
  return {
    ...resultBase(method, context),
    success: false,
    status: 'MISSING',
    evidenceStatus: 'MISSING',
    message,
    story:
      'CRM is the Wilsy OS legal identity spine: counterparty, agreement, and authority must be proven before VERIFIED status.',
    requiredEvidence: [
      'Counterparty legal identity',
      'CRM or account source record id',
      'Contract or deal record id',
      'Authorized signatory or authority evidence',
      'Retrieval timestamp',
    ],
    operatorAction:
      'Connect Zoho CRM OAuth, existing Wilsy CrmRecord data, or a real contract-ledger evidence file. Do not promote this record to VERIFIED without auditable source identity.',
    ...extra,
  };
}

/**
 * @function verifiedResult
 * @description Returns VERIFIED only when a source record has identity and retrieval metadata.
 * @param {string} method - Connector method.
 * @param {object} context - Lookup context.
 * @param {object} source - Source envelope.
 * @param {object} evidence - Evidence projection.
 * @returns {object} Verified evidence result.
 * @collaboration Enforces no-fake-verified while allowing real CRM evidence to clear repair signals.
 */
function verifiedResult(method, context = {}, source = {}, evidence = {}) {
  if (!source.sourceSystem || !source.sourceRecordId || !source.retrievedAt) {
    return missingResult(
      method,
      context,
      'Source record exists but is not auditable enough for VERIFIED.',
      { evidence }
    );
  }

  return {
    ...resultBase(method, context),
    success: true,
    status: 'VERIFIED',
    evidenceStatus: 'VERIFIED',
    message: 'Live CRM evidence resolved.',
    sourceSystem: source.sourceSystem,
    sourceRecordId: source.sourceRecordId,
    retrievedAt: source.retrievedAt,
    evidence,
    evidenceHash: source.evidenceHash,
    truthPolicy: TRUTH_POLICY,
  };
}

/**
 * @function resolveLedgerPath
 * @description Resolves optional local CRM evidence ledger path.
 * @returns {string} Absolute ledger path.
 * @collaboration Keeps file-backed evidence as a fallback, not the primary story.
 */
function resolveLedgerPath() {
  const configured = process.env.WILSY_CRM_EVIDENCE_FILE || DEFAULT_LEDGER_PATH;
  return path.isAbsolute(configured) ? configured : path.resolve(REPO_ROOT, configured);
}

/**
 * @function readFileLedger
 * @description Reads optional local CRM evidence ledger.
 * @returns {{ledger:object|null,error:string|null,ledgerPath:string}} Ledger read result.
 * @collaboration Allows controlled evidence fallback without pretending a file is a live CRM.
 */
function readFileLedger() {
  const ledgerPath = resolveLedgerPath();

  if (!fs.existsSync(ledgerPath)) {
    return { ledger: null, error: 'CRM evidence file is not configured or not found.', ledgerPath };
  }

  try {
    return { ledger: JSON.parse(fs.readFileSync(ledgerPath, 'utf8')), error: null, ledgerPath };
  } catch (error) {
    return {
      ledger: null,
      error: `CRM evidence file is invalid JSON: ${error.message}`,
      ledgerPath,
    };
  }
}

/**
 * @function getZohoAccessToken
 * @description Returns a Zoho access token from env or refresh-token flow.
 * @returns {Promise<string>} Access token or empty string.
 * @collaboration Enables live Zoho evidence without storing secrets in source code.
 */
async function getZohoAccessToken() {
  if (process.env.ZOHO_CRM_ACCESS_TOKEN) {
    return process.env.ZOHO_CRM_ACCESS_TOKEN;
  }

  const refreshToken = process.env.ZOHO_CRM_REFRESH_TOKEN;
  const clientId = process.env.ZOHO_CRM_CLIENT_ID;
  const clientSecret = process.env.ZOHO_CRM_CLIENT_SECRET;
  const accountsDomain = process.env.ZOHO_ACCOUNTS_DOMAIN || 'https://accounts.zoho.com';

  if (!refreshToken || !clientId || !clientSecret) {
    return '';
  }

  const body = new URLSearchParams({
    refresh_token: refreshToken,
    client_id: clientId,
    client_secret: clientSecret,
    grant_type: 'refresh_token',
  });

  const response = await fetch(`${accountsDomain.replace(/\/$/, '')}/oauth/v2/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });

  if (!response.ok) {
    return '';
  }

  const payload = await response.json();
  return payload?.access_token || '';
}

/**
 * @function fetchZohoModuleRecords
 * @description Fetches a small live record sample from a Zoho CRM module.
 * @param {string} moduleName - Zoho module API name.
 * @returns {Promise<Array<object>>} Live Zoho records.
 * @collaboration Lets Wilsy OS use Zoho as source evidence while telling a richer Source Registry story.
 */
async function fetchZohoModuleRecords(moduleName) {
  const token = await getZohoAccessToken();

  if (!token) return [];

  const apiDomain = process.env.ZOHO_CRM_API_DOMAIN || 'https://www.zohoapis.com';
  const fields = ZOHO_FIELDS[moduleName] || ['id'];

  const url = new URL(`${apiDomain.replace(/\/$/, '')}/crm/v8/${moduleName}`);
  url.searchParams.set('fields', fields.join(','));
  url.searchParams.set('page', '1');
  url.searchParams.set('per_page', '50');

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      Authorization: `Zoho-oauthtoken ${token}`,
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    return [];
  }

  const payload = await response.json();
  return Array.isArray(payload?.data) ? payload.data : [];
}

/**
 * @function importCrmRecordModel
 * @description Imports the existing Wilsy CRM model when available.
 * @returns {Promise<object|null>} Mongoose model or null.
 * @collaboration Links Source Registry evidence to existing Wilsy CRM infrastructure before creating anything new.
 */
async function importCrmRecordModel() {
  if (!fs.existsSync(LOCAL_MODEL_PATH)) {
    return null;
  }

  try {
    const namespace = await import(
      `${pathToFileURL(LOCAL_MODEL_PATH).href}?crmConnector=${Date.now()}`
    );
    return (
      namespace.default ||
      namespace.CrmRecord ||
      namespace.crmRecord ||
      mongoose.models.CrmRecord ||
      null
    );
  } catch {
    return mongoose.models.CrmRecord || null;
  }
}

/**
 * @function schemaHas
 * @description Checks whether a Mongoose model exposes a schema path.
 * @param {object} model - Mongoose model.
 * @param {string} field - Field name.
 * @returns {boolean} Whether field exists.
 * @collaboration Prevents local CRM queries from relying on unknown schema fields.
 */
function schemaHas(model, field) {
  return Boolean(model?.schema?.paths?.[field]);
}

/**
 * @function firstSchemaField
 * @description Returns the first model schema field available from candidate names.
 * @param {object} model - Mongoose model.
 * @param {Array<string>} candidates - Candidate field names.
 * @returns {string} Matching field or empty string.
 * @collaboration Makes CRM connector compatible with existing model naming instead of forcing new schema.
 */
function firstSchemaField(model, candidates = []) {
  return candidates.find((field) => schemaHas(model, field)) || '';
}

/**
 * @function queryLocalCrmRecords
 * @description Queries existing Wilsy CRM records when MongoDB is connected.
 * @param {Array<string>} moduleNames - Candidate modules.
 * @param {object} context - Lookup context.
 * @returns {Promise<Array<object>>} Local CRM records.
 * @collaboration Uses current Wilsy CRM infrastructure as a source before creating any new evidence file.
 */
async function queryLocalCrmRecords(moduleNames = [], context = {}) {
  if (!isMongooseConnected()) return [];

  const model = await importCrmRecordModel();
  if (!model?.find) return [];

  const tenantField = firstSchemaField(model, ['tenantId', 'tenant', 'orgId', 'organizationId']);
  const moduleField = firstSchemaField(model, [
    'module',
    'moduleName',
    'recordType',
    'entityType',
    'type',
  ]);
  const nameField = firstSchemaField(model, [
    'name',
    'legalName',
    'displayName',
    'company',
    'accountName',
    'title',
  ]);
  const emailField = firstSchemaField(model, ['email', 'Email']);
  const agreementField = firstSchemaField(model, ['agreementId', 'contractId', 'dealId']);

  const and = [];

  if (tenantField && context.tenantId) {
    and.push({ [tenantField]: context.tenantId });
  }

  if (moduleField && moduleNames.length) {
    and.push({ [moduleField]: { $in: moduleNames } });
  }

  const or = [];

  if (nameField && context.counterpartyLegalName) {
    or.push({
      [nameField]: new RegExp(
        context.counterpartyLegalName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'),
        'i'
      ),
    });
  }

  if (emailField && context.email) {
    or.push({ [emailField]: context.email });
  }

  if (agreementField && context.agreementId) {
    or.push({ [agreementField]: context.agreementId });
  }

  if (or.length) {
    and.push({ $or: or });
  }

  const query = and.length ? { $and: and } : {};
  return model.find(query).limit(25).lean();
}

/**
 * @function flattenRecord
 * @description Flattens CRM records that may store fields inside data/payload/raw.
 * @param {object} record - CRM record.
 * @returns {object} Flattened record.
 * @collaboration Handles Zoho, local CRM model and file-ledger records through one evidence projection.
 */
function flattenRecord(record = {}) {
  const payload = record.data || record.payload || record.raw || record.fields || {};
  return { ...record, ...payload };
}

/**
 * @function pickLegalName
 * @description Extracts legal or display name from a CRM record.
 * @param {object} record - CRM record.
 * @returns {string} Legal/display name.
 * @collaboration Normalizes Zoho Leads, Contacts and Accounts into one legal identity field.
 */
function pickLegalName(record = {}) {
  const flat = flattenRecord(record);

  return safeString(
    flat.legalName ||
      flat.Account_Name ||
      flat.Company ||
      flat.Full_Name ||
      flat.Lead_Name ||
      [flat.First_Name, flat.Last_Name].filter(Boolean).join(' ') ||
      flat.name ||
      flat.title
  );
}

/**
 * @function pickSourceRecordId
 * @description Extracts the strongest source record id from a CRM record.
 * @param {object} record - CRM record.
 * @returns {string} Source record id.
 * @collaboration Guarantees evidence identity is explicit before VERIFIED can happen.
 */
function pickSourceRecordId(record = {}) {
  const flat = flattenRecord(record);
  return safeString(
    flat.sourceRecordId || flat.zohoId || flat.crmId || flat.externalId || flat.id || record._id
  );
}

/**
 * @function localSourceEnvelope
 * @description Builds source metadata for existing Wilsy CRM records.
 * @param {object} record - Local CRM record.
 * @returns {object} Evidence source envelope.
 * @collaboration Treats local CRM records as auditable only when they expose identity and timestamps.
 */
function localSourceEnvelope(record = {}) {
  const flat = flattenRecord(record);
  return sourceEnvelope(
    flat.sourceSystem || flat.provider || 'WILSY_CRM_RECORD',
    pickSourceRecordId(record),
    flat,
    flat.retrievedAt || flat.updatedAt || flat.createdAt || ''
  );
}

/**
 * @function zohoSourceEnvelope
 * @description Builds source metadata for live Zoho records.
 * @param {string} moduleName - Zoho module.
 * @param {object} record - Zoho record.
 * @returns {object} Evidence source envelope.
 * @collaboration Treats Zoho as live evidence only when an API record id is present.
 */
function zohoSourceEnvelope(moduleName, record = {}) {
  return sourceEnvelope(
    `ZOHO_CRM_${moduleName.toUpperCase()}`,
    record.id,
    record,
    new Date().toISOString()
  );
}

/**
 * @function readLedgerRecords
 * @description Reads records from optional local file ledger.
 * @param {string} bucket - Ledger bucket name.
 * @returns {Array<object>} Ledger records.
 * @collaboration Keeps manual evidence fallback isolated from live CRM logic.
 */
function readLedgerRecords(bucket) {
  const { ledger } = readFileLedger();
  return Array.isArray(ledger?.[bucket]) ? ledger[bucket] : [];
}

/**
 * @function selectBestRecord
 * @description Selects the best CRM evidence record from candidates.
 * @param {Array<object>} records - Candidate records.
 * @param {object} context - Lookup context.
 * @returns {object|null} Selected record.
 * @collaboration Prioritizes exact counterparty/agreement matches while still allowing controlled missing results.
 */
function selectBestRecord(records = [], context = {}) {
  if (!records.length) return null;

  const wantedName = safeString(context.counterpartyLegalName).toLowerCase();
  const wantedAgreement = safeString(context.agreementId).toLowerCase();
  const wantedEmail = safeString(context.email).toLowerCase();

  const exact = records.find((record) => {
    const flat = flattenRecord(record);
    const legalName = pickLegalName(flat).toLowerCase();
    const agreement = safeString(
      flat.agreementId || flat.contractId || flat.dealId || flat.id
    ).toLowerCase();
    const email = safeString(flat.Email || flat.email).toLowerCase();

    return (
      (wantedName && legalName === wantedName) ||
      (wantedAgreement && agreement === wantedAgreement) ||
      (wantedEmail && email === wantedEmail)
    );
  });

  return exact || records[0];
}

/**
 * @function gatherIdentityCandidates
 * @description Gathers CRM records that may prove tenant/counterparty identity.
 * @param {object} context - Lookup context.
 * @returns {Promise<Array<object>>} Candidate identity records.
 * @collaboration Combines Zoho, Wilsy CRM model and file ledger into one identity evidence stream.
 */
async function gatherIdentityCandidates(context = {}) {
  const local = await queryLocalCrmRecords(
    ['Lead', 'Leads', 'Contact', 'Contacts', 'Account', 'Accounts'],
    context
  );
  const zohoAccounts = await fetchZohoModuleRecords(ZOHO_MODULES.accounts);
  const zohoContacts = await fetchZohoModuleRecords(ZOHO_MODULES.contacts);
  const zohoLeads = await fetchZohoModuleRecords(ZOHO_MODULES.leads);
  const ledger = readLedgerRecords('tenantProfiles');

  return [
    ...local.map((record) => ({ record, source: localSourceEnvelope(record) })),
    ...zohoAccounts.map((record) => ({ record, source: zohoSourceEnvelope('Accounts', record) })),
    ...zohoContacts.map((record) => ({ record, source: zohoSourceEnvelope('Contacts', record) })),
    ...zohoLeads.map((record) => ({ record, source: zohoSourceEnvelope('Leads', record) })),
    ...ledger.map((record) => ({
      record,
      source: sourceEnvelope(
        record.sourceSystem || 'CRM_FILE_LEDGER',
        record.sourceRecordId || record.id,
        record,
        record.retrievedAt || ''
      ),
    })),
  ];
}

/**
 * @function gatherContractCandidates
 * @description Gathers CRM records that may prove a governing agreement or deal.
 * @param {object} context - Lookup context.
 * @returns {Promise<Array<object>>} Candidate contract/deal records.
 * @collaboration Converts Deals and local CRM contract records into Source Registry contract evidence.
 */
async function gatherContractCandidates(context = {}) {
  const local = await queryLocalCrmRecords(
    ['Deal', 'Deals', 'Contract', 'Contracts', 'Agreement', 'Agreements'],
    context
  );
  const zohoDeals = await fetchZohoModuleRecords(ZOHO_MODULES.deals);
  const ledger = readLedgerRecords('contracts');

  return [
    ...local.map((record) => ({ record, source: localSourceEnvelope(record) })),
    ...zohoDeals.map((record) => ({ record, source: zohoSourceEnvelope('Deals', record) })),
    ...ledger.map((record) => ({
      record,
      source: sourceEnvelope(
        record.sourceSystem || 'CRM_FILE_LEDGER',
        record.sourceRecordId || record.id || record.agreementId,
        record,
        record.retrievedAt || ''
      ),
    })),
  ];
}

/**
 * @function gatherAuthorityCandidates
 * @description Gathers CRM records that may prove authority to bind.
 * @param {object} context - Lookup context.
 * @returns {Promise<Array<object>>} Candidate authority records.
 * @collaboration Keeps signatory authority separate from mere CRM existence.
 */
async function gatherAuthorityCandidates(context = {}) {
  const local = await queryLocalCrmRecords(
    ['Authority', 'AuthorityRecord', 'Contact', 'Contacts', 'Deal', 'Deals'],
    context
  );
  const zohoContacts = await fetchZohoModuleRecords(ZOHO_MODULES.contacts);
  const ledger = readLedgerRecords('authorityRecords');

  return [
    ...local.map((record) => ({ record, source: localSourceEnvelope(record) })),
    ...zohoContacts.map((record) => ({ record, source: zohoSourceEnvelope('Contacts', record) })),
    ...ledger.map((record) => ({
      record,
      source: sourceEnvelope(
        record.sourceSystem || 'CRM_FILE_LEDGER',
        record.sourceRecordId || record.id,
        record,
        record.retrievedAt || ''
      ),
    })),
  ];
}

/**
 * @function hasIdentityEvidence
 * @description Checks whether a CRM record can prove identity.
 * @param {object} record - Candidate record.
 * @returns {boolean} Whether the identity evidence is adequate.
 * @collaboration Allows live Zoho/CRM identity records to clear identity repair signals.
 */
function hasIdentityEvidence(record = {}) {
  return Boolean(pickLegalName(record) && pickSourceRecordId(record));
}

/**
 * @function hasContractEvidence
 * @description Checks whether a CRM record can prove a contract/deal ledger entry.
 * @param {object} record - Candidate record.
 * @returns {boolean} Whether contract evidence is adequate.
 * @collaboration Requires an agreement/deal id before clearing contract-ledger repair signals.
 */
function hasContractEvidence(record = {}) {
  const flat = flattenRecord(record);
  return Boolean(
    (flat.agreementId || flat.contractId || flat.dealId || flat.id) && pickSourceRecordId(record)
  );
}

/**
 * @function hasAuthorityEvidence
 * @description Checks whether a CRM record can prove authority to bind.
 * @param {object} record - Candidate record.
 * @returns {boolean} Whether authority evidence is adequate.
 * @collaboration Prevents default CRM contacts from becoming fake authority records.
 */
function hasAuthorityEvidence(record = {}) {
  const flat = flattenRecord(record);

  return Boolean(
    (flat.authorizedSignatoryName ||
      flat.authorityEvidenceType ||
      flat.Authority_Evidence_Type ||
      flat.Signatory_Authority ||
      flat.Title) &&
    pickSourceRecordId(record)
  );
}

/**
 * @function getTenantProfile
 * @description Retrieves live tenant/counterparty identity evidence from Zoho, Wilsy CRM model, or file ledger.
 * @param {object} input - Artifact or verification input.
 * @returns {Promise<object>} Evidence result.
 * @collaboration Turns CRM identity into Source Registry evidence instead of generic CRM dashboard data.
 */
export async function getTenantProfile(input = {}) {
  const context = normalizeInput(input);
  const candidates = await gatherIdentityCandidates(context);
  const selected = selectBestRecord(
    candidates.map((item) => item.record),
    context
  );

  if (!selected || !hasIdentityEvidence(selected)) {
    return missingResult(
      'getTenantProfile',
      context,
      'No auditable CRM tenant/counterparty identity record resolved.'
    );
  }

  const sourceCandidate = candidates.find((item) => item.record === selected) || {};
  const source = sourceCandidate.source || localSourceEnvelope(selected);

  return verifiedResult('getTenantProfile', context, source, {
    legalName: pickLegalName(selected),
    sourceRecordId: source.sourceRecordId,
    sourceSystem: source.sourceSystem,
  });
}

/**
 * @function getContractLedger
 * @description Retrieves live governing agreement/deal evidence from Zoho, Wilsy CRM model, or file ledger.
 * @param {object} input - Artifact or verification input.
 * @returns {Promise<object>} Evidence result.
 * @collaboration Converts Deals and contract records into legal evidence for artifact verification.
 */
export async function getContractLedger(input = {}) {
  const context = normalizeInput(input);
  const candidates = await gatherContractCandidates(context);
  const selected = selectBestRecord(
    candidates.map((item) => item.record),
    context
  );

  if (!selected || !hasContractEvidence(selected)) {
    return missingResult(
      'getContractLedger',
      context,
      'No auditable CRM deal/contract ledger record resolved.'
    );
  }

  const flat = flattenRecord(selected);
  const sourceCandidate = candidates.find((item) => item.record === selected) || {};
  const source = sourceCandidate.source || localSourceEnvelope(selected);

  return verifiedResult('getContractLedger', context, source, {
    agreementId: flat.agreementId || flat.contractId || flat.dealId || flat.id,
    dealName: flat.Deal_Name || flat.name || flat.title || '',
    stage: flat.Stage || flat.stage || '',
    amount: flat.Amount || flat.amount || '',
    counterpartyLegalName: pickLegalName(flat),
    sourceRecordId: source.sourceRecordId,
    sourceSystem: source.sourceSystem,
  });
}

/**
 * @function getCounterpartyAuthority
 * @description Retrieves auditable authority-to-bind evidence.
 * @param {object} input - Artifact or verification input.
 * @returns {Promise<object>} Evidence result.
 * @collaboration Separates real authority proof from ordinary CRM contact existence.
 */
export async function getCounterpartyAuthority(input = {}) {
  const context = normalizeInput(input);
  const candidates = await gatherAuthorityCandidates(context);
  const selected = selectBestRecord(
    candidates.map((item) => item.record),
    context
  );

  if (!selected || !hasAuthorityEvidence(selected)) {
    return missingResult(
      'getCounterpartyAuthority',
      context,
      'No auditable counterparty authority-to-bind evidence resolved.'
    );
  }

  const flat = flattenRecord(selected);
  const sourceCandidate = candidates.find((item) => item.record === selected) || {};
  const source = sourceCandidate.source || localSourceEnvelope(selected);

  return verifiedResult('getCounterpartyAuthority', context, source, {
    counterpartyLegalName: pickLegalName(flat),
    authorizedSignatoryName: flat.authorizedSignatoryName || flat.Full_Name || flat.name || '',
    authorityEvidenceType:
      flat.authorityEvidenceType ||
      flat.Authority_Evidence_Type ||
      flat.Signatory_Authority ||
      flat.Title ||
      '',
    sourceRecordId: source.sourceRecordId,
    sourceSystem: source.sourceSystem,
  });
}

export default {
  getTenantProfile,
  getContractLedger,
  getCounterpartyAuthority,
};
