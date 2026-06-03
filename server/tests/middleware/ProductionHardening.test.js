/* eslint-disable */
/**
 * 🧪 ProductionHardening Forensic Audit
 * @description Verifying the active defense layers of the Citadel Shield.
 */
import { expect } from 'chai';
import express from 'express';
import request from 'supertest';
import { integrityShield } from '../../middleware/ProductionHardening.middleware.js';

describe('🛡️ ProductionHardening Forensic Audit', () => {
  let app;

  before(() => {
    app = express();
    app.use(express.json());
    app.get('/test-shield', integrityShield, (req, res) => res.status(200).json({ success: true }));
  });

  it('blocks a request that lacks the X-Sovereign-Key header', async () => {
    const res = await request(app).get('/test-shield');
    expect(res.status).to.equal(403);
    expect(res.body.error).to.equal('INTEGRITY_VIOLATION');
  });

  it('allows a request that carries the correct Sovereign Key', async () => {
    const res = await request(app)
      .get('/test-shield')
      .set('x-sovereign-key', 'MASTER_FOUNDER_KEY_2050');

    expect(res.status).to.equal(200);
    expect(res.body.success).to.be.true;
  });
});
