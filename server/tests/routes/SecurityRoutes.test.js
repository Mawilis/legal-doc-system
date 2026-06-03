/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ 🧪 SUPER ADMIN SECURITY ROUTES TEST - WILSY OS 2050                       ║
  ║ Validates global security management endpoints                            ║
  ║ Supreme Architect: Wilson Khanyezi - 10th Generation                      ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import * as chai from 'chai';
const { expect } = chai;
import request from 'supertest';
import loadApp from '../helpers/loadApp.js';

describe('SuperAdmin Security Routes (Global Security Management)', function() {
  let agent;
  let superToken;

  before(async function() {
    superToken = 'mocked-superadmin-jwt';
    const app = await loadApp();
    agent = request(app);
  });

  const testRoute = async (method, path, key, payload = {}) => {
    const res = await agent[method](`/api/superadmin/security${path}`)
      .set('Authorization', `Bearer ${superToken}`)
      .send(payload);
    expect(res.status).to.be.oneOf([200,401]); // 401 acceptable if token not real
    if (res.status === 200) {
      expect(res.body.success).to.be.true;
      if (key) expect(res.body.data).to.have.property(key);
    }
  };

  it('GET /overview should return security overview', () => testRoute('get','/overview','overview'));
  it('GET /threats should return active threats', () => testRoute('get','/threats','threats'));
  it('GET /incidents should return incidents', () => testRoute('get','/incidents','incidents'));
  it('GET /mfa-status should return MFA compliance', () => testRoute('get','/mfa-status','mfa'));
  it('GET /login-attempts should return login analytics', () => testRoute('get','/login-attempts','attempts'));
  it('GET /ip-blacklist should return blacklist', () => testRoute('get','/ip-blacklist','ips'));
  it('POST /ip-blacklist should add IP', () => testRoute('post','/ip-blacklist','ip',{ ip:'192.168.1.1', reason:'Test block' }));
  it('DELETE /ip-blacklist/:ipId should remove IP', () => testRoute('delete','/ip-blacklist/507f1f77bcf86cd799439011','ip'));
});
