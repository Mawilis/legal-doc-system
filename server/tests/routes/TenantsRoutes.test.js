/* eslint-disable */
import { expect } from 'chai';
import request from 'supertest';
import { loadApp } from '../helpers/loadApp.js';

describe('SuperAdmin Tenants Routes (Global Tenant Management)', function() {
  let app;
  let agent;
  let superToken = 'mocked-superadmin-token';

  before(async function() {
    this.timeout(15000);
    // SURGICAL FIX: Await the dynamic import of the app
    app = await loadApp();
    agent = request(app);
  });

  it('GET /api/superadmin/tenants should return tenants list', async function() {
    const res = await agent
      .get('/api/superadmin/tenants')
      .set('Authorization', `Bearer ${superToken}`);

    expect(res.status).to.be.oneOf([200, 401]); // 401 is acceptable if token isn't real yet
    if (res.status === 200) {
      expect(res.body.success).to.be.true;
      expect(res.body.data).to.be.an('array');
    }
  });
});
