/* eslint-disable */
import 'dotenv/config';
import { createRequire } from 'node:module';

// R18AD32_SERVER_MONGOOSE_SINGLETON
const requireFromWilsyServer = createRequire(new URL('../server/services/accountEvidenceCommandService.js', import.meta.url));
const mongoose = requireFromWilsyServer('mongoose');
import {
  createAccountComplianceEvidenceReceipt,
  generateAccountRegulatorBundle,
  getAccountComplianceEvidenceSnapshot
} from '../server/services/accountEvidenceCommandService.js';

/**
 * @function readCliOption
 * @description Reads a named command-line option.
 * @param {string[]} args - CLI arguments.
 * @param {string} name - Option name without dashes.
 * @param {string} fallback - Fallback value.
 * @returns {string} Option value.
 * @collaboration Keeps evidence generation explicit and operator-controlled.
 */
function readCliOption(args = [], name = '', fallback = '') {
  const prefix = `--${name}=`;
  const match = args.find((arg) => String(arg).startsWith(prefix));

  if (!match) {
    return fallback;
  }

  return String(match).slice(prefix.length).trim() || fallback;
}

/**
 * @function resolveMongoUri
 * @description Resolves the MongoDB connection URI from environment configuration.
 * @returns {string} MongoDB URI.
 * @collaboration Refuses to generate receipts without an explicit database connection.
 */
function resolveMongoUri() {
  const uri = process.env.MONGODB_URI || process.env.MONGO_URI || process.env.DATABASE_URL;

  if (!uri) {
    throw new Error('Missing MongoDB connection URI. Set MONGODB_URI, MONGO_URI or DATABASE_URL before generating evidence.');
  }

  return uri;
}

/**
 * @function runAccountComplianceEvidenceGenerator
 * @description Creates one real Account Compliance evidence receipt and writes a regulator bundle.
 * @returns {Promise<void>} Resolves when generation completes.
 * @collaboration Moves Wilsy Compliance from evidence-pending to evidence-backed using explicit backend receipts.
 */
async function runAccountComplianceEvidenceGenerator() {
  const args = process.argv.slice(2);
  const tenantId = readCliOption(args, 'tenant', 'wilsy-sovereign-root');
  const actor = readCliOption(args, 'actor', 'wilsy-system');
  const reason = readCliOption(args, 'reason', 'manual-production-evidence-generation');
  const mongoUri = resolveMongoUri();

  await mongoose.connect(mongoUri, {
    serverSelectionTimeoutMS: 10000
  });

  const before = await getAccountComplianceEvidenceSnapshot({ tenantId });
  const receipt = await createAccountComplianceEvidenceReceipt({ tenantId, actor, reason });
  const after = await getAccountComplianceEvidenceSnapshot({ tenantId });
  const bundle = await generateAccountRegulatorBundle({ tenantId });

  console.log(JSON.stringify({ ok: true, before, receipt, after, bundle }, null, 2));

  await mongoose.disconnect();
}

runAccountComplianceEvidenceGenerator().catch(async (error) => {
  console.error(JSON.stringify({ ok: false, error: error.message }, null, 2));

  try {
    await mongoose.disconnect();
  } catch {
    // noop
  }

  process.exit(1);
});
