/* eslint-disable */
import { expect } from 'chai';
import request from 'supertest';
import { app } from '../../app.js'; // Pointing to the fresh Cache-Breaker file

describe('⚛️ Full-Stack Bridge Audit', () => {
  it('verifies the Citadel rejects unsigned requests', async () => {
    const res = await request(app).get('/api/v2/sovereign/citadel/health');
    expect(res.status).to.equal(403);
  });

  it('verifies Citadel accepts authorized SIT handshakes', async () => {
    const res = await request(app)
      .get('/api/v2/sovereign/citadel/health')
      .set('x-sovereign-key', 'MASTER_FOUNDER_KEY_2050');
    expect(res.status).to.equal(200);
  });
});
