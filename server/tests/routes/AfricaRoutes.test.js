/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ 🧪 AFRICA ROUTES TEST - WILSY OS 2050                                     ║
  ║ Validates Africa expansion API endpoint                                   ║
  ║ Supreme Architect: Wilson Khanyezi - 10th Generation                      ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { expect } from 'chai';
import request from 'supertest';
import express from 'express';
import africaRoutes from '../../routes/africaRoutes.js';

describe('Africa Routes (Expansion API)', function() {
  let app;

  before(function() {
    app = express();
    app.use('/api/africa', africaRoutes);
  });

  it('GET /api/africa should return API status', async function() {
    const res = await request(app)
      .get('/api/africa')
      .expect(200);

    expect(res.body.success).to.be.true;
    expect(res.body.status).to.equal('active');
    expect(res.body.message).to.equal('Africa expansion API');
    expect(res.body.version).to.equal('1.0.0');
    expect(res.body.region).to.equal('Africa');
    expect(res.body).to.have.property('timestamp');
  });

  it('GET /api/africa should include ISO timestamp', async function() {
    const res = await request(app)
      .get('/api/africa')
      .expect(200);

    const timestamp = new Date(res.body.timestamp);
    expect(timestamp.toISOString()).to.equal(res.body.timestamp);
  });
});
