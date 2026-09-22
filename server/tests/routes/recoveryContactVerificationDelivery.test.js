/**
 * WILSY OS — INTERNAL RECOVERY CONTACT VERIFICATION DELIVERY CERTIFICATE
 * VERSION: v1.0.0-R10E16-INTERNAL-RECOVERY-CONTACT-VERIFICATION-DELIVERY-CERT
 * AUTHORITY: Wilsy OS Core Governance
 * EPITOME: Certifies dedicated HMAC-authenticated verification-delivery ingress
 *          without SMTP, external network, or recovery-contact authority.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/server/tests/routes/recoveryContactVerificationDelivery.test.js
 * CERTIFICATION / UPDATE DATE: 2026-09-22
 * CHANGELOG:
 *   v1.0.0-R10E16-INTERNAL-RECOVERY-CONTACT-VERIFICATION-DELIVERY-CERT — Certifies
 *   exact body shape, dedicated secret, SHA3-512 HMAC, freshness, transport
 *   delegation, generic failures, and sensitive-response suppression.
 * AUTHORITY BOUNDARY: Internal transport authentication evidence only.
 * FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
 */

import crypto from 'node:crypto';
import { expect } from 'chai';
import express from 'express';
import request from 'supertest';

import {
  RECOVERY_CONTACT_VERIFICATION_SIGNATURE_HEADER,
  RECOVERY_CONTACT_VERIFICATION_TIMESTAMP_HEADER,
  createRecoveryContactVerificationDeliveryRouter,
  recoveryContactVerificationSigningPayload,
} from '../../routes/recoveryContactVerificationDelivery.js';

const NOW_MS = 1790100000000;
const SECRET = 'synthetic-r10e16-contact-verification-secret-0123456789';
const BODY = Object.freeze({
  recipient_email: 'person@example.com',
  verification_token: 'synthetic-verification-token-0123456789-ABCDE',
  expires_at: '2026-09-22T20:15:00.000Z',
});

function signature(timestamp, body = BODY, secret = SECRET) {
  return crypto
    .createHmac('sha3-512', secret)
    .update(recoveryContactVerificationSigningPayload(timestamp, body), 'utf8')
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
    createRecoveryContactVerificationDeliveryRouter({
      transport,
      clock: () => NOW_MS,
      environment: {
        WILSY_RECOVERY_CONTACT_VERIFICATION_DELIVERY_SECRET: secret,
      },
    }),
  );
  return { app, calls };
}

describe('internal recovery contact verification delivery bridge', () => {
  it('accepts one fresh exact HMAC request and delegates once', async () => {
    const { app, calls } = harness();
    const timestamp = String(Math.floor(NOW_MS / 1000));
    const response = await request(app)
      .post('/internal/auth/recovery-contact-verification-delivery')
      .set(RECOVERY_CONTACT_VERIFICATION_TIMESTAMP_HEADER, timestamp)
      .set(RECOVERY_CONTACT_VERIFICATION_SIGNATURE_HEADER, signature(timestamp))
      .send(BODY);

    expect(response.status).to.equal(204);
    expect(response.text).to.equal('');
    expect(calls).to.deep.equal([{
      recipientEmail: BODY.recipient_email,
      verificationToken: BODY.verification_token,
      expiresAt: BODY.expires_at,
    }]);
  });

  it('rejects stale or malformed signatures without transport execution', async () => {
    const { app, calls } = harness();
    const stale = String(Math.floor((NOW_MS - 61000) / 1000));
    const staleResponse = await request(app)
      .post('/internal/auth/recovery-contact-verification-delivery')
      .set(RECOVERY_CONTACT_VERIFICATION_TIMESTAMP_HEADER, stale)
      .set(RECOVERY_CONTACT_VERIFICATION_SIGNATURE_HEADER, signature(stale))
      .send(BODY);
    expect(staleResponse.status).to.equal(401);

    const current = String(Math.floor(NOW_MS / 1000));
    const badResponse = await request(app)
      .post('/internal/auth/recovery-contact-verification-delivery')
      .set(RECOVERY_CONTACT_VERIFICATION_TIMESTAMP_HEADER, current)
      .set(RECOVERY_CONTACT_VERIFICATION_SIGNATURE_HEADER, '0'.repeat(128))
      .send(BODY);
    expect(badResponse.status).to.equal(401);
    expect(calls).to.deep.equal([]);
  });

  it('rejects extra tenant/principal authority fields before transport', async () => {
    const { app, calls } = harness();
    const timestamp = String(Math.floor(NOW_MS / 1000));
    const extra = { ...BODY, tenant_id: 'forbidden', principal_id: 'forbidden' };
    const response = await request(app)
      .post('/internal/auth/recovery-contact-verification-delivery')
      .set(RECOVERY_CONTACT_VERIFICATION_TIMESTAMP_HEADER, timestamp)
      .set(RECOVERY_CONTACT_VERIFICATION_SIGNATURE_HEADER, signature(timestamp, extra))
      .send(extra);
    expect(response.status).to.equal(400);
    expect(response.body).to.deep.equal({
      status: 'RECOVERY_CONTACT_VERIFICATION_DELIVERY_REQUEST_INVALID',
    });
    expect(calls).to.deep.equal([]);
  });

  it('fails closed when the dedicated shared secret is unavailable', async () => {
    const { app, calls } = harness({ secret: '' });
    const timestamp = String(Math.floor(NOW_MS / 1000));
    const response = await request(app)
      .post('/internal/auth/recovery-contact-verification-delivery')
      .set(RECOVERY_CONTACT_VERIFICATION_TIMESTAMP_HEADER, timestamp)
      .set(RECOVERY_CONTACT_VERIFICATION_SIGNATURE_HEADER, signature(timestamp))
      .send(BODY);
    expect(response.status).to.equal(503);
    expect(response.body).to.deep.equal({
      status: 'RECOVERY_CONTACT_VERIFICATION_DELIVERY_UNAVAILABLE',
    });
    expect(calls).to.deep.equal([]);
  });

  it('maps provider failure generically without recipient or token leakage', async () => {
    const { app, calls } = harness({ transportFailure: true });
    const timestamp = String(Math.floor(NOW_MS / 1000));
    const response = await request(app)
      .post('/internal/auth/recovery-contact-verification-delivery')
      .set(RECOVERY_CONTACT_VERIFICATION_TIMESTAMP_HEADER, timestamp)
      .set(RECOVERY_CONTACT_VERIFICATION_SIGNATURE_HEADER, signature(timestamp))
      .send(BODY);
    expect(response.status).to.equal(503);
    expect(response.body).to.deep.equal({
      status: 'RECOVERY_CONTACT_VERIFICATION_DELIVERY_FAILED',
    });
    expect(JSON.stringify(response.body)).not.to.contain(BODY.recipient_email);
    expect(JSON.stringify(response.body)).not.to.contain(BODY.verification_token);
    expect(calls).to.have.lengthOf(1);
  });

  it('binds the signature to every exact delivery field', async () => {
    const { app, calls } = harness();
    const timestamp = String(Math.floor(NOW_MS / 1000));
    const changed = { ...BODY, recipient_email: 'other@example.com' };
    const response = await request(app)
      .post('/internal/auth/recovery-contact-verification-delivery')
      .set(RECOVERY_CONTACT_VERIFICATION_TIMESTAMP_HEADER, timestamp)
      .set(RECOVERY_CONTACT_VERIFICATION_SIGNATURE_HEADER, signature(timestamp, BODY))
      .send(changed);
    expect(response.status).to.equal(401);
    expect(calls).to.deep.equal([]);
  });
});

/**
 * ARTIFACT: server/tests/routes/recoveryContactVerificationDelivery.test.js
 * VERSION: v1.0.0-R10E16-INTERNAL-RECOVERY-CONTACT-VERIFICATION-DELIVERY-CERT
 * AUTHORITY BOUNDARY: deterministic dedicated HMAC bridge evidence only
 * TENANT POSTURE: no tenant/principal field accepted or projected
 * FAIL-CLOSED POSTURE: invalid shape, missing secret, stale/bad HMAC, and transport failure reject
 * FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
