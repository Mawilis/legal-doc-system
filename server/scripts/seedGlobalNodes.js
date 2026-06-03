/* eslint-disable */
/**
 * WILSY OS - Global Sovereign Node Registry Seeder
 * Seeds the orchestrator map with jurisdiction-aware mesh anchors.
 */

import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import crypto from 'node:crypto';
import Node from '../models/nodeModel.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, '../../.env') });
dotenv.config({ path: path.resolve(__dirname, '../.env') });

const FOUNDER_OWNER = {
  systemOwner: 'Wilsy (Pty) Ltd',
  legalEntityName: 'Wilsy (Pty) Ltd',
  registrationNumber: '2024/617944/07',
  taxNumber: '9395759229',
  founder: 'Wilson Khanyezi',
  founderRole: 'Founder, CEO & Lead Architect',
  ownershipPercent: 100,
  commandAuthority: 'SOVEREIGN_SYSTEM_OWNER',
  legalAddress: 'Unit 29 Sumatra Estate, Cnr 8th Rd and 7th Rd, Noordwyk, Midrand, Gauteng, 1682',
  registrationDate: new Date('2024-10-02'),
  businessStartDate: new Date('2024-10-02'),
  corporateStatus: 'In Business',
  ownerVisible: true
};

const GLOBAL_NODE_MATRIX = [
  ['Wilsy (Pty) Ltd - Founder Root', 'ZAF-GP-MIDRAND', -25.9999, 28.1283, 'MASTER_NODE', 'ONLINE', 1.2, 100, 'Founder-owned sovereign system root and Africa command anchor', 'ZA', FOUNDER_OWNER]
];

export const seedGlobalNodes = async () => {
  const tenantId = 'WILSY_ROOT';
  const results = [];

  await Node.deleteMany({
    tenantId,
    isMasterAnchor: { $ne: true },
    $or: [
      { 'metadata.seededBy': 'WILSY_GLOBAL_NODE_SEED' },
      { entity: { $in: [
        'SADC LEGAL EDGE',
        'EAC JUSTICE NODE',
        'RWANDA COMPLIANCE NODE',
        'ECOWAS REVENUE NODE',
        'GHANA TRUST NODE',
        'UK COMMON LAW NODE',
        'EU PRIVACY NODE',
        'US ENTERPRISE NODE',
        'CANADA FIDUCIARY NODE',
        'BRAZIL LATAM NODE',
        'UAE CAPITAL NODE',
        'INDIA SCALE NODE',
        'SINGAPORE FINALITY NODE',
        'JAPAN PRECISION NODE',
        'AUSTRALIA APAC NODE'
      ] } }
    ]
  });

  for (const [entity, region, lat, lng, type, status, lastLatency, neuralStability, lane, jurisdiction, identity = {}] of GLOBAL_NODE_MATRIX) {
    const isMaster = type === 'MASTER_NODE';
    let node = isMaster
      ? await Node.findOne({ tenantId, isMasterAnchor: true, region })
      : await Node.findOne({ tenantId, entity, region });

    if (!node && isMaster) {
      node = await Node.findOne({ tenantId, entity: 'WILSY ROOT', region });
    }

    if (!node) {
      node = new Node({
        tenantId,
        entity,
        region,
        lat,
        lng,
        type,
        status,
        lastLatency,
        neuralStability,
        isMasterAnchor: type === 'MASTER_NODE',
        dilithiumSignature: `ML-DSA-5::${crypto.randomBytes(32).toString('hex').toUpperCase()}`,
        metadata: {}
      });
    }

    node.set({
      entity,
      region,
      lat,
      lng,
      type,
      status,
      lastLatency,
      neuralStability,
      isMasterAnchor: isMaster,
      metadata: {
        ...(node.metadata || {}),
        lane,
        jurisdiction,
        deploymentStage: status === 'ONLINE' ? 'ACTIVE_REGISTRY' : 'SYNCING_REGISTRY',
        seededBy: 'WILSY_GLOBAL_NODE_SEED',
        seededAt: new Date(),
        ...identity
      }
    });

    await node.save();
    results.push(node);
  }

  return { count: results.length, nodes: results };
};

const invokedDirectly = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);

if (invokedDirectly) {
  const uri = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/wilsy';
  mongoose.connect(uri)
    .then(seedGlobalNodes)
    .then(async ({ count }) => {
      console.log(JSON.stringify({ success: true, count }, null, 2));
      await mongoose.disconnect();
      process.exit(0);
    })
    .catch(async (error) => {
      console.error(error);
      if (mongoose.connection.readyState === 1) await mongoose.disconnect();
      process.exit(1);
    });
}
