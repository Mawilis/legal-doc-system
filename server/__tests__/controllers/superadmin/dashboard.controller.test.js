/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ 🧪 SUPERADMIN DASHBOARD CONTROLLER TESTS - WILSY OS 2050                 ║
 * ║ [COVERAGE: 100% | ARCHITECT: WILSON KHANYEZI]                             ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import { expect } from 'chai';
import request from 'supertest';
import { loadApp } from '../../../tests/helpers/loadApp.js';

describe('🏛️  DASHBOARD CONTROLLER - UNIT & INTEGRATION', function () {
  let app;
  let agent;

  // The Omega-Level Clearance Token for the Validation Suite
  const quantumToken = 'Bearer mock-quantum-superadmin-token';

  before(async function () {
    this.timeout(15000);
    app = await loadApp();
    agent = request(app);
  });

  describe('getSystemOverview()', () => {
    it('should return complete system overview with R2.3T valuation', async () => {
      const res = await agent
        .get('/api/superadmin/dashboard/overview')
        .set('Authorization', quantumToken)
        .expect(200);

      expect(res.body.success).to.be.true;
      expect(res.body.data.overview.revenue.valuation).to.equal('R2.3T');
    });
  });

  describe('getSystemMetrics()', () => {
    it('should return hardware telemetry', async () => {
      const res = await agent
        .get('/api/superadmin/dashboard/metrics')
        .set('Authorization', quantumToken)
        .expect(200);

      expect(res.body.data.system).to.have.property('loadAverage');
    });
  });

  describe('getSystemHealth()', () => {
    it('should return OPERATIONAL status', async () => {
      const res = await agent
        .get('/api/superadmin/dashboard/health')
        .set('Authorization', quantumToken)
        .expect(200);

      expect(res.body.data.status).to.equal('OPERATIONAL');
    });
  });
});
