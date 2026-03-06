#!/usr/bin/env node
/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ TEST DATA GENERATOR - WILSY OS 2050                                      ║
  ║ Generates sample audit data for demonstration and testing               ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Import audit logger
const auditLoggerPath = path.join(__dirname, '../utils/auditLogger.js');
const { auditLogger } = await import(auditLoggerPath);

// Configuration
const TENANTS = ['tenant-001', 'tenant-002', 'tenant-003', 'tenant-004', 'tenant-005'];
const USERS = {
  'tenant-001': ['user-john', 'user-jane', 'user-bob'],
  'tenant-002': ['user-alice', 'user-charlie', 'user-diana'],
  'tenant-003': ['user-eve', 'user-frank', 'user-grace'],
  'tenant-004': ['user-henry', 'user-isabel', 'user-jack'],
  'tenant-005': ['user-kevin', 'user-laura', 'user-mike']
};
const DOCUMENTS = ['DOC-001', 'DOC-002', 'DOC-003', 'DOC-004', 'DOC-005', 'DOC-006', 'DOC-007', 'DOC-008', 'DOC-009', 'DOC-010'];
const JURISDICTIONS = ['ZA', 'EU', 'US', 'UK', 'SG', 'AU', 'BR', 'IN', 'JP', 'CN'];

console.log(`
╔═══════════════════════════════════════════════════════════════════════════╗
║ TEST DATA GENERATOR - WILSY OS 2050                                      ║
╚═══════════════════════════════════════════════════════════════════════════╝
`);

console.log('⚛️ Initializing Quantum Audit Logger...');
console.log(`• Tenants: ${TENANTS.length}`);
console.log(`• Users: ${Object.values(USERS).flat().length}`);
console.log(`• Jurisdictions: ${JURISDICTIONS.length}`);

// Generate quantum events
console.log('\n📝 Generating quantum audit events...');

// Generate data access events (POPIA §19)
for (let i = 0; i < 50; i++) {
  const tenant = TENANTS[Math.floor(Math.random() * TENANTS.length)];
  const user = USERS[tenant][Math.floor(Math.random() * USERS[tenant].length)];
  const document = DOCUMENTS[Math.floor(Math.random() * DOCUMENTS.length)];
  const jurisdiction = JURISDICTIONS[Math.floor(Math.random() * JURISDICTIONS.length)];
  
  auditLogger.dataAccess(tenant, user, document, 'READ', {
    ipAddress: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    jurisdiction,
    retentionPolicy: 'COMPANIES_ACT_7_YEARS'
  });
}

// Generate cross-border transfers (POPIA §72)
for (let i = 0; i < 20; i++) {
  const tenant = TENANTS[Math.floor(Math.random() * TENANTS.length)];
  const source = JURISDICTIONS[Math.floor(Math.random() * JURISDICTIONS.length)];
  const target = JURISDICTIONS[Math.floor(Math.random() * JURISDICTIONS.length)];
  
  auditLogger.crossBorderTransfer(tenant, source, target, ['personal_data', 'financial_data'], {
    dataVolume: Math.floor(Math.random() * 1000) + 100,
    legalBasis: 'standard_contractual_clauses',
    transferDate: new Date().toISOString()
  });
}

// Generate consent events (POPIA §11)
for (let i = 0; i < 30; i++) {
  const tenant = TENANTS[Math.floor(Math.random() * TENANTS.length)];
  const user = USERS[tenant][Math.floor(Math.random() * USERS[tenant].length)];
  const consentType = ['marketing', 'data_processing', 'third_party_sharing', 'cookies'][Math.floor(Math.random() * 4)];
  const status = Math.random() > 0.2 ? 'given' : 'withdrawn';
  
  auditLogger.consent(tenant, user, consentType, status, {
    consentVersion: 'v2.1',
    timestamp: new Date().toISOString(),
    ipAddress: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`
  });
}

// Generate security events
for (let i = 0; i < 15; i++) {
  const tenant = TENANTS[Math.floor(Math.random() * TENANTS.length)];
  const severity = ['info', 'warning', 'critical'][Math.floor(Math.random() * 3)];
  
  auditLogger.security(`Security event ${i+1} detected`, {
    tenantId: tenant,
    severity,
    eventType: ['login_attempt', 'password_change', 'mfa_setup', 'api_key_rotation'][Math.floor(Math.random() * 4)],
    sourceIp: `45.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
    success: Math.random() > 0.1
  });
}

// Generate forensic events
for (let i = 0; i < 10; i++) {
  const tenant = TENANTS[Math.floor(Math.random() * TENANTS.length)];
  const user = USERS[tenant][Math.floor(Math.random() * USERS[tenant].length)];
  
  auditLogger.forensic(`Forensic evidence collection ${i+1}`, {
    tenantId: tenant,
    userId: user,
    caseNumber: `CASE-2026-${String(i+1).padStart(3, '0')}`,
    evidenceType: 'audit_log',
    collectionMethod: 'quantum_verified',
    chainOfCustody: true
  });
}

// Generate quantum-verified events (highest level)
for (let i = 0; i < 25; i++) {
  const tenant = TENANTS[Math.floor(Math.random() * TENANTS.length)];
  const user = USERS[tenant][Math.floor(Math.random() * USERS[tenant].length)];
  
  auditLogger.quantum(`Quantum transaction ${i+1} verified`, {
    tenantId: tenant,
    userId: user,
    transactionId: `TX-${crypto.randomBytes(8).toString('hex').toUpperCase()}`,
    entanglementScore: 0.9997,
    quantumAlgorithm: 'DILITHIUM-3-SHAKE256',
    postQuantumReady: true
  });
}

// Generate compliance events
for (let i = 0; i < 20; i++) {
  const tenant = TENANTS[Math.floor(Math.random() * TENANTS.length)];
  const framework = ['POPIA', 'GDPR', 'FICA', 'ECT'][Math.floor(Math.random() * 4)];
  
  auditLogger.compliance(`Compliance check for ${framework}`, {
    tenantId: tenant,
    framework,
    checkType: 'automated',
    result: Math.random() > 0.05 ? 'passed' : 'failed',
    nextReviewDate: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString()
  });
}

// Generate legal hold events
for (let i = 0; i < 5; i++) {
  const tenant = TENANTS[Math.floor(Math.random() * TENANTS.length)];
  const documentIds = DOCUMENTS.slice(0, Math.floor(Math.random() * 5) + 1);
  
  auditLogger.placeLegalHold(
    tenant,
    documentIds,
    `Active litigation case LIT-2026-${String(i+1).padStart(3, '0')}`,
    `COURT-ORD-${crypto.randomBytes(4).toString('hex').toUpperCase()}`
  );
}

console.log('✅ Test data generation complete!');
console.log('\n📊 Generated events:');
console.log('  • Data Access Events: 50');
console.log('  • Cross-Border Transfers: 20');
console.log('  • Consent Events: 30');
console.log('  • Security Events: 15');
console.log('  • Forensic Events: 10');
console.log('  • Quantum-Verified Events: 25');
console.log('  • Compliance Events: 20');
console.log('  • Legal Hold Events: 5');
console.log(`  • TOTAL: 175 audit entries`);

console.log('\n⚛️ Quantum signatures applied to all events');
console.log('🔒 Forensic chain of custody maintained');
console.log('📋 Court-admissible evidence ready');

// Save forensic data
const forensicDir = path.join(__dirname, '../data/forensic');
await fs.mkdir(forensicDir, { recursive: true }).catch(() => {});

const forensicData = {
  generatedAt: new Date().toISOString(),
  tenantCount: TENANTS.length,
  eventCount: 175,
  quantumEnabled: true,
  retentionPolicy: 'QUANTUM_100_YEARS',
  dataResidency: 'ZA'
};

await fs.writeFile(
  path.join(forensicDir, `forensic-${Date.now()}.json`),
  JSON.stringify(forensicData, null, 2)
);

console.log('\n📁 Forensic data saved to: /Users/wilsonkhanyezi/legal-doc-system/server/data/forensic/');
console.log('\n🚀 WILSY OS 2050 test environment ready!');
