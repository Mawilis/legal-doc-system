/**
 * ============================================================================
 * WILSY OS - CRM ENTERPRISE ENGINE VALIDATION SUITE (FG231B)
 * ============================================================================
 *
 * @file         crmEnterpriseEngine.test.js
 * @directory    server/src/enterprise/crm/
 * @system       Wilsy OS - Subsystem Testing & Verification Layer (FG231B)
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      2.0.0-GEN2
 * @epitome      Automated unit test suite verifying lead scoring algorithms,
 *               POPIA redaction safety, state transitions, and audit hashing
 *               for the FG231B CRM Enterprise Engine using native ES Modules.
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT LOG
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 2.0.0   | Standardized ESM test suite for FG231B.
 * ============================================================================
 */

import test from 'node:test';
import assert from 'node:assert/strict';
import { CrmEnterpriseEngine, LEAD_STATES } from './crmEnterpriseEngine.js';

test('CRM Enterprise Engine - Initial State & Health Diagnostics', async (t) => {
  await t.test('should instantiate with correct engine identifier', () => {
    const engine = new CrmEnterpriseEngine();
    assert.equal(engine.engineId, 'ENGINE_CRM_v2.0.0');
    assert.equal(engine.maxLeadScore, 100);
  });

  await t.test('should pass self-contained health check diagnostics', () => {
    const engine = new CrmEnterpriseEngine();
    const health = engine.healthCheck();

    assert.equal(health.status, 'OPERATIONAL');
    assert.equal(health.certified, true);
    assert.equal(typeof health.testScoreCalculated, 'number');
    assert.equal(health.sampleHash.length, 64);
  });
});

test('CRM Enterprise Engine - POPIA / GDPR Data Redaction Safety', async (t) => {
  await t.test('should redact South African ID numbers, emails, and phone numbers', () => {
    const engine = new CrmEnterpriseEngine();
    const rawLead = {
      name: 'John Doe',
      nationalId: '9001015009087',
      email: 'john.doe@enterprise.co.za',
      phone: '+27821234567'
    };

    const redacted = engine.redactSensitiveData(rawLead);

    assert.equal(redacted.nationalId, '******[REDACTED_POPIA]******');
    assert.ok(redacted.email.startsWith('jo***@'));
    assert.ok(redacted.phone.includes('****'));
    assert.equal(redacted.name, 'John Doe');
  });
});

test('CRM Enterprise Engine - Algorithmic Lead Scoring Vector', async (t) => {
  await t.test('should calculate maximum score (100) for enterprise decision maker', () => {
    const engine = new CrmEnterpriseEngine();
    const score = engine.calculateLeadScore({
      budget: 1500000,
      interactions: 10,
      decisionMaker: true,
      urgencyDays: 7
    });

    assert.equal(score, 100);
  });

  await t.test('should calculate partial score for mid-tier leads', () => {
    const engine = new CrmEnterpriseEngine();
    const score = engine.calculateLeadScore({
      budget: 100000,
      interactions: 2,
      decisionMaker: false,
      urgencyDays: 45
    });

    assert.equal(score, 30);
  });
});

test('CRM Enterprise Engine - Pipeline State Transition & Audit Hashing', async (t) => {
  await t.test('should execute valid state transition and yield SHA-256 audit hash', () => {
    const engine = new CrmEnterpriseEngine();
    const transition = engine.transitionLeadState(
      LEAD_STATES.QUALIFIED,
      LEAD_STATES.PROPOSAL_SENT,
      { tenantId: 'TENANT_ZA_001', operatorId: 'OPERATOR_WILSON' }
    );

    assert.equal(transition.success, true);
    assert.equal(transition.previousState, 'QUALIFIED');
    assert.equal(transition.newState, 'PROPOSAL_SENT');
    assert.equal(transition.auditHash.length, 64);
  });

  await t.test('should reject invalid state transitions gracefully', () => {
    const engine = new CrmEnterpriseEngine();
    const transition = engine.transitionLeadState('INVALID_STATE', 'CLOSED_WON');

    assert.equal(transition.success, false);
    assert.ok(transition.error.includes('Invalid origin state'));
  });
});
