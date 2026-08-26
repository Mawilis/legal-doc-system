/* eslint-disable */
import mongoose from 'mongoose';
import { expect } from 'chai';
import tenantController from '../../controllers/tenantController.js';
import Tenant from '../../models/Tenant.js';
import User from '../../models/User.js';

const mockResponse = () => {
  const res = { statusCode: 200, body: null };
  res.status = function (s) {
    this.statusCode = s;
    return this;
  };
  res.json = function (d) {
    this.body = d;
    return this;
  };
  return res;
};

describe('🏢 SOVEREIGN TENANT CONTROLLER', function () {
  before(async function () {
    this.timeout(10000);
    if (mongoose.connection.readyState === 0) {
      await mongoose.connect('mongodb://127.0.0.1:27017/wilsy_os_test_db');
    }
  });

  after(async function () {
    await mongoose.connection.db.dropDatabase();
    await mongoose.connection.close();
  });

  beforeEach(async function () {
    await Tenant.deleteMany({});
    await User.deleteMany({});
  });

  it('Should establish a firm, create an owner, and calculate initial MRR', async function () {
    const req = {
      body: { name: 'Genesis Law', ownerEmail: 'founder@wilsy.os', plan: 'professional' },
    };
    const res = mockResponse();
    await tenantController.createTenant(req, res);
    expect(res.statusCode).to.equal(201);
    expect(res.body.data.valuationMetrics.mrr).to.equal(2499);
  });

  it('Should upgrade plan and automatically trigger ARR recalculation', async function () {
    const tenant = await Tenant.create({
      name: 'Growth Law',
      slug: 'growth-law',
      subscription: 'basic',
      billing: { monthlyRevenue: 799 },
    });
    const req = { tenantId: tenant._id, body: { newPlan: 'enterprise' } };
    const res = mockResponse();
    await tenantController.upgradePlan(req, res);
    const updated = await Tenant.findById(tenant._id);
    expect(updated.billing.annualRecurringRevenue).to.equal(7999 * 12);
  });

  it('Should suspend the tenant and lock out all associated users', async function () {
    const tenant = await Tenant.create({ name: 'Rogue Law', slug: 'rogue-law' });
    // FIXED: Using 8+ character password
    await User.create({
      firstName: 'X',
      lastName: 'Y',
      email: 'x@y.com',
      password: 'SovereignPass2026!',
      tenantId: tenant._id,
      role: 'user_viewer',
    });
    const req = {
      params: { id: tenant._id },
      user: { _id: new mongoose.Types.ObjectId() },
      body: { reason: 'Violation' },
    };
    const res = mockResponse();
    await tenantController.suspendFirm(req, res);
    const users = await User.find({ tenantId: tenant._id });
    expect(users[0].isActive).to.be.false;
  });
});
