/* eslint-disable */
/**
 * 🧪 SovereignAPI v2 Forensic Audit
 * @description Verifying the unified routing of the Wilsy OS Citadel.
 */
import { expect } from 'chai';
import express from 'express';
import request from 'supertest';
import SovereignAPI_v2 from '../../routes/v2/SovereignAPI_v2.js';

describe('🏛️ SovereignAPI v2 Master Audit', () => {
  let app;

  before(() => {
    app = express();
    app.use(express.json());
    app.use('/api/v2/sovereign', SovereignAPI_v2);
  });

  it('successfully routes to the Citadel Health endpoint with signed data', async () => {
    const res = await request(app).get('/api/v2/sovereign/citadel/health');
    expect(res.status).to.equal(200);
    expect(res.body.healthData.status).to.equal('SOVEREIGN_ACTIVE');
    expect(res.body.vitalitySignature).to.have.lengthOf(128);
  });

  it('successfully routes to the Global Sync Map with node telemetry', async () => {
    const res = await request(app).get('/api/v2/sovereign/citadel/sync-map');
    expect(res.status).to.equal(200);
    expect(res.body.metrics.globalIntegrityScore).to.equal(1.0);
  });
});
