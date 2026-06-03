/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ 🧪 ROLES CONSTANTS TEST - WILSY OS 2050                                   ║
  ║ Validates role hierarchy, permissions, and forensic profiles              ║
  ║ Supreme Architect: Wilson Khanyezi - 10th Generation                      ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import * as chai from 'chai';
const { expect } = chai;

import {
  ROLES,
  isRoleHigher,
  hasPermission,
  getRoleProfile
} from '../../constants/roles.js'; // Fixed path - go up two levels from tests/constants/ to server/, then into constants/

describe('Roles Constants (Supreme Command Center)', function() {
  it('should define all core roles', function() {
    expect(ROLES.SUPER_ADMIN).to.equal('super_admin');
    expect(ROLES.TENANT_OWNER).to.equal('tenant_owner');
    expect(ROLES.USER_VIEWER).to.equal('user_viewer');
  });

  it('should correctly compare hierarchy', function() {
    expect(isRoleHigher(ROLES.SUPER_ADMIN, ROLES.TENANT_OWNER)).to.be.true;
    expect(isRoleHigher(ROLES.USER_VIEWER, ROLES.TENANT_ADMIN)).to.be.false;
  });

  it('should validate permissions', function() {
    expect(hasPermission(ROLES.TENANT_ADMIN, 'user:create')).to.be.true;
    expect(hasPermission(ROLES.USER_VIEWER, 'user:create')).to.be.false;
  });

  it('should return a forensic role profile', function() {
    const profile = getRoleProfile(ROLES.TENANT_OWNER);
    expect(profile).to.have.keys(['role','hierarchy','permissions','complianceTags']);
    expect(profile.complianceTags).to.include('ISO27001');
  });
});
