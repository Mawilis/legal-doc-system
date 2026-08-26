/* eslint-disable */
import mongoose from 'mongoose';
import { expect } from 'chai';
import userController from '../../controllers/userController.js';
import User from '../../models/User.js';
import Tenant from '../../models/Tenant.js';

const mockResponse = () => {
  const res = { statusCode: 200, body: null, cookieName: null };
  res.status = function (s) {
    this.statusCode = s;
    return this;
  };
  res.json = function (d) {
    this.body = d;
    return this;
  };
  res.cookie = function (n, v, o) {
    this.cookieName = n;
    return this;
  };
  return res;
};

describe('🔐 SOVEREIGN IDENTITY HANDSHAKE', function () {
  before(async function () {
    if (mongoose.connection.readyState === 0) {
      await mongoose.connect('mongodb://127.0.0.1:27017/wilsy_os_test_db');
    }
  });

  after(async function () {
    await mongoose.connection.db.dropDatabase();
    await mongoose.connection.close();
  });

  beforeEach(async () => {
    await User.deleteMany({});
    await Tenant.deleteMany({});
  });

  it('Should reject login with incorrect credentials', async function () {
    const req = { body: { email: 'w@k.law', password: 'wrong-password-long' } };
    const res = mockResponse();
    await userController.login(req, res);
    expect(res.statusCode).to.equal(401);
  });

  it('Should successfully login valid user', async function () {
    const tenant = await Tenant.create({ name: 'T', slug: 't' });
    // FIXED: Using 8+ character password
    const user = new User({
      firstName: 'W',
      lastName: 'K',
      email: 'w@k.law',
      password: 'SovereignPass2026!',
      tenantId: tenant._id,
      role: 'tenant_admin',
    });
    await user.save();
    const req = {
      body: { email: 'w@k.law', password: 'SovereignPass2026!' },
      get: () => 'Test',
      ip: '127.0.0.1',
    };
    const res = mockResponse();
    await userController.login(req, res);
    expect(res.statusCode).to.equal(200);
    expect(res.body.token).to.be.a('string');
    expect(res.cookieName).to.equal('wilsy_refresh');
  });
});
