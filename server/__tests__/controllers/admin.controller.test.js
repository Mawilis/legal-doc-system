/* eslint-disable */
import mongoose from 'mongoose';
import { expect } from 'chai';
import adminController from '../../controllers/adminController.js';
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

describe('🏛️ SOVEREIGN ADMIN CONTROLLER', function () {
  before(async function () {
    if (mongoose.connection.readyState === 0) {
      await mongoose.connect('mongodb://127.0.0.1:27017/wilsy_os_test_db');
    }
  });

  after(async function () {
    await mongoose.connection.db.dropDatabase();
    await mongoose.connection.close();
  });

  it('Should aggregate global financial metrics correctly', async function () {
    // 1. Seed two firms with MRR
    await Tenant.create([
      { name: 'Firm A', slug: 'firm-a', billing: { monthlyRevenue: 1000 } },
      { name: 'Firm B', slug: 'firm-b', billing: { monthlyRevenue: 2000 } },
    ]);

    const req = { user: { id: new mongoose.Types.ObjectId() } };
    const res = mockResponse();

    await adminController.getDashboardStats(req, res);

    expect(res.statusCode).to.equal(200);
    // Total MRR should be 3000
    expect(res.body.data.financials.globalMRR).to.equal(3000);
    // Total Valuation should be (3000 * 12) * 15 = 540,000
    expect(res.body.data.financials.currentSystemValuation).to.equal(540000);
  });
});
