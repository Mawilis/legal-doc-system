/**
 * WILSY OS — INTERNAL RECOVERY DELIVERY BRIDGE DIRECT CERTIFICATE
 * VERSION: v1.0.0-R10E5-INTERNAL-RECOVERY-DELIVERY-BRIDGE-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies the internal HMAC-authenticated Node recovery delivery
 *          ingress without SMTP, external network, or recovery authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/tests/routes/passwordRecoveryDelivery.test.js
 * COLLABORATION / OWNERSHIP: Test-only evidence for passwordRecoveryDelivery;
 *                            injected transport owns no real provider connection.
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG: v1.0.0-R10E5-INTERNAL-RECOVERY-DELIVERY-BRIDGE-CERT — Adds exact body-shape,
 *            SHA3-512 HMAC, timing freshness, transport delegation, generic
 *            failure, and sensitive-response suppression coverage.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
 * SECURITY / PRIVACY POSTURE: Synthetic recovery bearer only; no real secrets.
 * TENANT BOUNDARY: No tenant input is admitted by the internal route.
 * AUTHORITY BOUNDARY: Internal transport authentication evidence only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import crypto from 'node:crypto';
import { expect } from 'chai';
import express from 'express';
import request from 'supertest';

import {
  RECOVERY_DELIVERY_SIGNATURE_HEADER,
  RECOVERY_DELIVERY_TIMESTAMP_HEADER,
  createPasswordRecoveryDeliveryRouter,
  recoveryDeliverySigningPayload,
} from '../../routes/passwordRecoveryDelivery.js';

const NOW_MS = 1790096400000;
const SECRET = 'synthetic-r10e5-recovery-delivery-secret-0123456789';
const BODY = Object.freeze({
  recipient_email: 'person@example.com',
  recovery_token: 'synthetic-recovery-token-0123456789-ABCDE',
  expires_at: '2026-09-22T18:30:00.000Z',
});

function signature(timestamp, body = BODY, secret = SECRET) {
  return crypto
    .createHmac('sha3-512', secret)
    .update(recoveryDeliverySigningPayload(timestamp, body), 'utf8')
    .digest('hex');
}

function harness({ secret = SECRET, transportFailure = false } = {}) {
  const calls = [];
  const transport = {
    deliver: async (payload) => {
      calls.push({ ...payload });
      if (transportFailure) throw new Error('synthetic provider details');
      return { status: 'DELIVERED' };
    },
  };
  const app = express();
  app.use(express.json());
  app.use(
    '/internal/auth',
    createPasswordRecoveryDeliveryRouter({
      transport,
      clock: () => NOW_MS,
      environment: { WILSY_RECOVERY_DELIVERY_SECRET: secret },
    }),
  );
  return { app, calls };
}

describe('internal password recovery delivery bridge', () => {
  it('accepts one fresh exact HMAC request and delegates once', async () => {
    const { app, calls } = harness();
    const timestamp = String(Math.floor(NOW_MS / 1000));
    const response = await request(app)
      .post('/internal/auth/password-recovery-delivery')
      .set(RECOVERY_DELIVERY_TIMESTAMP_HEADER, timestamp)
      .set(RECOVERY_DELIVERY_SIGNATURE_HEADER, signature(timestamp))
      .send(BODY);

    expect(response.status).to.equal(204);
    expect(response.text).to.equal('');
    expect(calls).to.deep.equal([{
      recipientEmail: BODY.recipient_email,
      recoveryToken: BODY.recovery_token,
      expiresAt: BODY.expires_at,
    }]);
  });

  it('rejects stale and malformed signatures without transport execution', async () => {
    const { app, calls } = harness();
    const stale = String(Math.floor((NOW_MS - 61000) / 1000));
    const staleResponse = await request(app)
      .post('/internal/auth/password-recovery-delivery')
      .set(RECOVERY_DELIVERY_TIMESTAMP_HEADER, stale)
      .set(RECOVERY_DELIVERY_SIGNATURE_HEADER, signature(stale))
      .send(BODY);
    expect(staleResponse.status).to.equal(401);

    const current = String(Math.floor(NOW_MS / 1000));
    const badResponse = await request(app)
      .post('/internal/auth/password-recovery-delivery')
      .set(RECOVERY_DELIVERY_TIMESTAMP_HEADER, current)
      .set(RECOVERY_DELIVERY_SIGNATURE_HEADER, '0'.repeat(128))
      .send(BODY);
    expect(badResponse.status).to.equal(401);
    expect(calls).to.deep.equal([]);
  });

  it('rejects extra or malformed body authority fields before transport', async () => {
    const { app, calls } = harness();
    const timestamp = String(Math.floor(NOW_MS / 1000));
    const extra = { ...BODY, tenant_id: 'forbidden-caller-authority' };
    const response = await request(app)
      .post('/internal/auth/password-recovery-delivery')
      .set(RECOVERY_DELIVERY_TIMESTAMP_HEADER, timestamp)
      .set(RECOVERY_DELIVERY_SIGNATURE_HEADER, signature(timestamp, extra))
      .send(extra);
    expect(response.status).to.equal(400);
    expect(response.body).to.deep.equal({ status: 'RECOVERY_DELIVERY_REQUEST_INVALID' });
    expect(calls).to.deep.equal([]);
  });

  it('fails closed when the internal shared secret is unavailable', async () => {
    const { app, calls } = harness({ secret: '' });
    const timestamp = String(Math.floor(NOW_MS / 1000));
    const response = await request(app)
      .post('/internal/auth/password-recovery-delivery')
      .set(RECOVERY_DELIVERY_TIMESTAMP_HEADER, timestamp)
      .set(RECOVERY_DELIVERY_SIGNATURE_HEADER, signature(timestamp))
      .send(BODY);
    expect(response.status).to.equal(503);
    expect(response.body).to.deep.equal({ status: 'RECOVERY_DELIVERY_UNAVAILABLE' });
    expect(calls).to.deep.equal([]);
  });

  it('maps transport failure generically without recipient or token leakage', async () => {
    const { app, calls } = harness({ transportFailure: true });
    const timestamp = String(Math.floor(NOW_MS / 1000));
    const response = await request(app)
      .post('/internal/auth/password-recovery-delivery')
      .set(RECOVERY_DELIVERY_TIMESTAMP_HEADER, timestamp)
      .set(RECOVERY_DELIVERY_SIGNATURE_HEADER, signature(timestamp))
      .send(BODY);
    expect(response.status).to.equal(503);
    expect(response.body).to.deep.equal({ status: 'RECOVERY_DELIVERY_FAILED' });
    expect(JSON.stringify(response.body)).not.to.contain(BODY.recipient_email);
    expect(JSON.stringify(response.body)).not.to.contain(BODY.recovery_token);
    expect(calls).to.have.lengthOf(1);
  });

  it('binds the signature to each exact delivery field', async () => {
    const { app, calls } = harness();
    const timestamp = String(Math.floor(NOW_MS / 1000));
    const changed = { ...BODY, recipient_email: 'other@example.com' };
    const response = await request(app)
      .post('/internal/auth/password-recovery-delivery')
      .set(RECOVERY_DELIVERY_TIMESTAMP_HEADER, timestamp)
      .set(RECOVERY_DELIVERY_SIGNATURE_HEADER, signature(timestamp, BODY))
      .send(changed);
    expect(response.status).to.equal(401);
    expect(calls).to.deep.equal([]);
  });
});

/**
 * ARTIFACT: server/tests/routes/passwordRecoveryDelivery.test.js
 * VERSION: v1.0.0-R10E5-INTERNAL-RECOVERY-DELIVERY-BRIDGE-CERT
 * AUTHORITY BOUNDARY: deterministic internal HMAC bridge evidence only
 * TENANT POSTURE: no tenant field accepted or projected
 * FAIL-CLOSED POSTURE: invalid shape, missing secret, stale/bad HMAC, and transport failure reject
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
