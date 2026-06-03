/* eslint-disable */
/**
 * 🏛️ WILSY OS - ANALYTICS CONTROLLER TEST SUITE v2.0.0-FORENSIC
 *
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/tests/controllers/analyticsController.test.js
 *
 * 🔐 FORENSIC EVIDENCE CHAIN: ANALYTICS-CTRL-TEST-2026-03-29
 * 🔐 PQE CIRCUIT: NIST DILITHIUM-5 · 1024 CIRCUITS
 */

import { expect } from 'chai';
import sinon from 'sinon';
import {
  getDashboardMetrics,
  getRiskMetrics,
  getRevenueAnalytics,
  getUserActivityMetrics,
  getTenantPerformance,
  getInvestorReport,
  getInvestorKPIs,
  getQuantumForecasts
} from '../../controllers/analyticsController.js';
import User from '../../models/User.js';
import Tenant from '../../models/Tenant.js';

describe('🏛️ WILSY OS - Analytics Controller Tests', () => {
  let req;
  let res;
  let sandbox;

  beforeEach(() => {
    sandbox = sinon.createSandbox();
    req = {
      headers: {},
      params: {},
      body: {},
      query: {},
      user: { email: 'wilsonkhanyezi@gmail.com', tenantId: 'MASTER', role: 'super_admin' }
    };
    res = {
      status: sandbox.stub().returnsThis(),
      json: sandbox.stub().returnsThis()
    };
  });

  afterEach(() => {
    sandbox.restore();
  });

  // ============================================================================
  // TEST 1: Dashboard Metrics
  // ============================================================================
  describe('✅ getDashboardMetrics() - Real Dashboard Data', () => {
    it('should return dashboard metrics with real user and tenant counts', async () => {
      sandbox.stub(User, 'countDocuments').resolves(1);
      sandbox.stub(Tenant, 'find').resolves([]);
      sandbox.stub(Tenant, 'countDocuments').resolves(1);
      sandbox.stub(User, 'findOne').resolves({
        firstName: 'Wilson',
        lastName: 'Khanyezi',
        email: 'wilsonkhanyezi@gmail.com',
        role: 'super_admin',
        createdAt: new Date()
      });

      await getDashboardMetrics(req, res);

      expect(res.status.calledWith(200)).to.be.true;
      const response = res.json.firstCall.args[0];
      expect(response.success).to.be.true;
      expect(response.data.userCount).to.equal(1);
      expect(response.data.founder).to.be.an('object');
    });
  });

  // ============================================================================
  // TEST 2: Revenue Analytics - Real Data
  // ============================================================================
  describe('✅ getRevenueAnalytics() - Real Revenue Data', () => {
    it('should return R0 revenue when no revenue exists', async () => {
      sandbox.stub(User, 'countDocuments').resolves(1);
      sandbox.stub(Tenant, 'find').resolves([]);

      await getRevenueAnalytics(req, res);

      expect(res.status.calledWith(200)).to.be.true;
      const response = res.json.firstCall.args[0];
      expect(response.success).to.be.true;
      expect(response.data.total).to.equal(0);
      expect(response.data.formatted).to.equal('R 0.00');
      expect(response.data.userCount).to.equal(1);
      expect(response.data.forensicNote).to.include('No tenants onboarded');
    });
  });

  // ============================================================================
  // TEST 3: Risk Metrics - AI-Driven
  // ============================================================================
  describe('✅ getRiskMetrics() - AI-Driven Risk Scoring', () => {
    it('should return minimal risk for founder (single user)', async () => {
      sandbox.stub(User, 'countDocuments').resolves(1);
      sandbox.stub(Tenant, 'countDocuments').resolves(1);
      sandbox.stub(Tenant, 'aggregate').resolves([{ totalRevenue: 0 }]);

      await getRiskMetrics(req, res);

      expect(res.status.calledWith(200)).to.be.true;
      const response = res.json.firstCall.args[0];
      expect(response.success).to.be.true;
      expect(response.data.riskScore).to.be.at.most(6);
      expect(response.data.overallRisk).to.equal('MINIMAL THREAT');
    });
  });

  // ============================================================================
  // TEST 4: Investor KPIs
  // ============================================================================
  describe('✅ getInvestorKPIs() - Fortune 500 Metrics', () => {
    it('should return investor KPIs with correct structure', async () => {
      sandbox.stub(Tenant, 'find').resolves([]);

      await getInvestorKPIs(req, res);

      expect(res.status.calledWith(200)).to.be.true;
      const response = res.json.firstCall.args[0];
      expect(response.success).to.be.true;
      expect(response.data).to.have.property('arr');
      expect(response.data).to.have.property('mrr');
      expect(response.data).to.have.property('ltvToCacRatio');
      expect(response.data).to.have.property('valuation');
      expect(response.data).to.have.property('quantumSignature');
    });
  });

  // ============================================================================
  // TEST 5: Quantum Forecasts
  // ============================================================================
  describe('✅ getQuantumForecasts() - Dilithium-5 Signatures', () => {
    it('should return quantum-verified forecasts', async () => {
      sandbox.stub(User, 'countDocuments').resolves(1);
      sandbox.stub(Tenant, 'find').resolves([]);

      await getQuantumForecasts(req, res);

      expect(res.status.calledWith(200)).to.be.true;
      const response = res.json.firstCall.args[0];
      expect(response.success).to.be.true;
      expect(response.data).to.have.property('quantumSignature');
      expect(response.data.quantumSignature).to.include('DILITHIUM-5');
      expect(response.data.note).to.include('Forecast available after first revenue');
    });
  });

  // ============================================================================
  // TEST 6: User Activity Metrics
  // ============================================================================
  describe('✅ getUserActivityMetrics() - Real User Activity', () => {
    it('should return user activity metrics', async () => {
      sandbox.stub(User, 'countDocuments').resolves(1);

      await getUserActivityMetrics(req, res);

      expect(res.status.calledWith(200)).to.be.true;
      const response = res.json.firstCall.args[0];
      expect(response.success).to.be.true;
      expect(response.data.totalUsers).to.equal(1);
      expect(response.data).to.have.property('forensicHash');
    });
  });

  // ============================================================================
  // TEST 7: Tenant Performance
  // ============================================================================
  describe('✅ getTenantPerformance() - Tenant Metrics', () => {
    it('should return tenant performance metrics', async () => {
      sandbox.stub(Tenant, 'find').resolves([]);

      await getTenantPerformance(req, res);

      expect(res.status.calledWith(200)).to.be.true;
      const response = res.json.firstCall.args[0];
      expect(response.success).to.be.true;
      expect(response.data).to.have.property('tenants');
      expect(response.data).to.have.property('totalCount');
    });
  });

  // ============================================================================
  // TEST 8: Investor Report
  // ============================================================================
  describe('✅ getInvestorReport() - Investor-Grade Report', () => {
    it('should return investor report', async () => {
      sandbox.stub(User, 'countDocuments').resolves(1);
      sandbox.stub(Tenant, 'find').resolves([]);
      sandbox.stub(Tenant, 'countDocuments').resolves(1);
      sandbox.stub(User, 'findOne').resolves({
        firstName: 'Wilson',
        lastName: 'Khanyezi',
        email: 'wilsonkhanyezi@gmail.com',
        createdAt: new Date()
      });

      await getInvestorReport(req, res);

      expect(res.status.calledWith(200)).to.be.true;
      const response = res.json.firstCall.args[0];
      expect(response.success).to.be.true;
      expect(response.data).to.have.property('reportId');
      expect(response.data).to.have.property('executiveSummary');
      expect(response.data.executiveSummary.totalUsers).to.equal(1);
    });
  });

  // ============================================================================
  // TEST 9: Forensic Evidence
  // ============================================================================
  describe('🔐 Forensic Evidence - Data Integrity', () => {
    it('should include forensic hash in responses', async () => {
      sandbox.stub(User, 'countDocuments').resolves(1);
      sandbox.stub(Tenant, 'find').resolves([]);

      await getRevenueAnalytics(req, res);

      const response = res.json.firstCall.args[0];
      expect(response.data).to.have.property('forensicHash');
      expect(response.data.forensicHash).to.be.a('string');
    });

    it('should include quantum verification status', async () => {
      sandbox.stub(User, 'countDocuments').resolves(1);
      sandbox.stub(Tenant, 'countDocuments').resolves(1);
      sandbox.stub(Tenant, 'aggregate').resolves([{ totalRevenue: 0 }]);

      await getRiskMetrics(req, res);

      const response = res.json.firstCall.args[0];
      expect(response.data.quantumVerified).to.be.true;
    });
  });

  // ============================================================================
  // TEST 10: No Placeholders - Real Data Only
  // ============================================================================
  describe('📊 No Placeholders - Real Data Only', () => {
    it('should show 0 revenue when no revenue exists (transparency)', async () => {
      sandbox.stub(User, 'countDocuments').resolves(1);
      sandbox.stub(Tenant, 'find').resolves([]);

      await getRevenueAnalytics(req, res);

      const response = res.json.firstCall.args[0];
      expect(response.data.total).to.equal(0);
      expect(response.data.formatted).to.equal('R 0.00');
      expect(response.data.forensicNote).to.include('transparent');
    });

    it('should show 1 user (Founder) as the only user', async () => {
      sandbox.stub(User, 'countDocuments').resolves(1);
      sandbox.stub(Tenant, 'find').resolves([]);

      await getRevenueAnalytics(req, res);

      const response = res.json.firstCall.args[0];
      expect(response.data.userCount).to.equal(1);
    });
  });
});

export default {};
