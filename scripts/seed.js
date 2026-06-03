/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - ROOT SEED SCRIPT [V2.0.0-PRODUCTION-SECURITY]                                                                             ║
 * ║ [ENV-OWNED CREDENTIALS | EXPLICIT RESET GATE | USER MODEL COMPATIBILITY | NO SOURCE SECRETS]                                         ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.0.0-PRODUCTION-SECURITY | PRODUCTION READY | SAFE OPERATOR-CONTROLLED SEEDING                                             ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/scripts/seed.js                                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Required clean production source with no privacy or security credentials committed.                ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Replaced demo passwords with env-owned seed credentials and reset guardrails.                ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

require('dotenv').config();

const mongoose = require('mongoose');
const User = require('../server/models/userModel');

/**
 * @function requireSeedEnv
 * @description Reads a required seed environment variable and fails closed when it is missing.
 * @param {string} key - Environment variable key.
 * @returns {string} Environment value.
 * @collaboration Prevents source-level seed credentials while giving operators a deterministic startup failure.
 */
const requireSeedEnv = (key) => {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Missing required seed environment variable: ${key}`);
  }
  return value;
};

/**
 * @function buildSeedUsers
 * @description Builds user seed rows from env-owned operator credentials.
 * @returns {Array<Object>} Seed users.
 * @collaboration Keeps founder/admin bootstrap data configurable per deployment without source secrets.
 */
const buildSeedUsers = () => ([
  {
    name: process.env.SEED_ADMIN_NAME || 'Wilsy OS Administrator',
    email: requireSeedEnv('SEED_ADMIN_EMAIL'),
    password: requireSeedEnv('SEED_ADMIN_PASSWORD'),
    role: process.env.SEED_ADMIN_ROLE || 'admin'
  },
  {
    name: process.env.SEED_OPERATOR_NAME || 'Wilsy OS Operator',
    email: requireSeedEnv('SEED_OPERATOR_EMAIL'),
    password: requireSeedEnv('SEED_OPERATOR_PASSWORD'),
    role: process.env.SEED_OPERATOR_ROLE || 'user'
  }
]);

/**
 * @function connectSeedDatabase
 * @description Connects to the configured MongoDB seed target.
 * @returns {Promise<void>} Resolves when MongoDB is connected.
 * @collaboration Routes seed operations through env-managed infrastructure rather than hardcoded development databases.
 */
const connectSeedDatabase = async () => {
  await mongoose.connect(requireSeedEnv('MONGODB_URI'), {
    useNewUrlParser: true,
    useUnifiedTopology: true
  });
};

/**
 * @function assertSeedResetAllowed
 * @description Requires an explicit reset flag before deleting existing users.
 * @returns {void}
 * @collaboration Protects production tenants from accidental destructive seed runs.
 */
const assertSeedResetAllowed = () => {
  if (process.env.SEED_RESET_USERS !== 'true') {
    throw new Error('SEED_RESET_USERS=true is required before deleting and reseeding users.');
  }
};

/**
 * @function seedUsers
 * @description Seeds Wilsy OS users using env-owned credentials and explicit reset authorization.
 * @returns {Promise<void>} Resolves after seed completion.
 * @collaboration Gives operators a safe bootstrap path without leaking founder or tenant credentials into Git.
 */
const seedUsers = async () => {
  try {
    assertSeedResetAllowed();
    await connectSeedDatabase();
    await User.deleteMany({});
    await User.create(buildSeedUsers());
    console.log('Wilsy OS seed completed with env-owned credentials.');
    await mongoose.disconnect();
    process.exit(0);
  } catch (err) {
    console.error('Wilsy OS seed failed:', err.message);
    await mongoose.disconnect().catch(() => {});
    process.exit(1);
  }
};

seedUsers();
