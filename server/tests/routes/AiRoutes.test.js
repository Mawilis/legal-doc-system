/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ 🧪 AI ROUTES TEST - WILSY OS 2050                                         ║
  ║ Validates AI analysis, redaction, batch, analytics & health endpoints     ║
  ║ Supreme Architect: Wilson Khanyezi - 10th Generation                      ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { expect } from 'chai';
import request from 'supertest';
import express from 'express';
import jwt from 'jsonwebtoken';
import aiRoutes from '../../routes/ai.routes.js';

describe('AI Routes - $500M Revenue Engine', function() {
  let app;
  let token;

  before(function() {
    process.env.JWT_SECRET = 'test-secret-key';
    token = jwt.sign({ id: 'user-id', role: 'partner', tenantId: 'tenant-id' }, process.env.JWT_SECRET, { expiresIn: '1h' });

    app = express();
    app.use(express.json());
    app.use('/api/v1/ai', aiRoutes);
  });

  const auth = () => ({ Authorization: `Bearer ${token}` });

  it('POST /analyze should return analysis result', async function() {
    const res = await request(app)
      .post('/api/v1/ai/analyze')
      .set(auth())
      .send({ documentId: '507f1f77bcf86cd799439011', analysisType: 'contract_summary', jurisdiction: 'RSA' })
      .expect(200);

    expect(res.body.success).to.be.true;
    expect(res.body.data).to.have.property('summary');
    expect(res.body.metadata).to.have.property('correlationId');
  });

  it('POST /redact should return redacted text', async function() {
    const res = await request(app)
      .post('/api/v1/ai/redact')
      .set(auth())
      .send({ text: 'John Doe, ID 8001015009087', piiTypes: ['RSA_ID'], redactionMethod: 'mask' })
      .expect(200);

    expect(res.body.success).to.be.true;
    expect(res.body.data).to.have.property('redactedText');
  });

  it('POST /batch-analyze should initiate batch job', async function() {
    const res = await request(app)
      .post('/api/v1/ai/batch-analyze')
      .set(auth())
      .send({ documents: ['507f1f77bcf86cd799439011'], analysisPipeline: ['clause_extraction'] })
      .expect(202);

    expect(res.body.success).to.be.true;
    expect(res.body.data).to.have.property('batchId');
  });

  it('GET /usage/analytics should return analytics', async function() {
    const res = await request(app)
      .get('/api/v1/ai/usage/analytics?period=month&currency=ZAR')
      .set(auth())
      .expect(200);

    expect(res.body.success).to.be.true;
    expect(res.body.metadata.reportingStandard).to.equal('IFRS');
  });

  it('GET /health should return AI health', async function() {
    const res = await request(app)
      .get('/api/v1/ai/health')
      .set(auth())
      .expect(200);

    expect(res.body.success).to.be.true;
    expect(res.body.metadata.service).to.equal('WilsyOS_AI_Engine');
  });

  it('GET /batch/:batchId/status should return batch status', async function() {
    const res = await request(app)
      .get('/api/v1/ai/batch/BATCH_test/status')
      .set(auth())
      .expect(200);

    expect(res.body.success).to.be.true;
    expect(res.body.data).to.have.property('status');
  });

  it('should return 401 without token', async function() {
    await request(app).get('/api/v1/ai/health').expect(401);
  });

  it('should handle invalid token', async function() {
    await request(app).get('/api/v1/ai/health').set('Authorization', 'Bearer invalid.token').expect(401);
  });
});
