/* eslint-disable */
/**
 * @file crmLeadProofLedgerPermissionService.js
 * @description Tenant-scoped permission spine for CRM Lead Proof Ledger access.
 * @collaboration Proof Ledger, Lead View registry, tenant access control, audit receipts, and operator evidence export.
 */

import crypto from 'crypto';
import mongoose from 'mongoose';

const PROOF_LEDGER_PERMISSION_VERSION = 'P60K5Q10FG104N1_PROOF_LEDGER_PERMISSION_SPINE';

const TENANT_WIDE_ROLES = new Set([
  'super_admin',
  'sovereign',
  'sovereign_root',
  'root',
  'founder',
  'owner',
  'tenant_owner',
  'tenant_admin',
  'admin',
  'administrator',
  'compliance',
  'compliance_officer',
  'auditor',
  'security_admin',
]);

const EXPORT_ROLES = new Set([
  'super_admin',
  'sovereign',
  'sovereign_root',
  'root',
  'founder',
  'owner',
  'tenant_owner',
  'tenant_admin',
  'admin',
  'administrator',
  'compliance',
  'compliance_officer',
  'auditor',
  'security_admin',
]);

const DELEGATE_ROLES = new Set([
  'super_admin',
  'sovereign',
  'sovereign_root',
  'root',
  'founder',
  'owner',
  'tenant_owner',
  'tenant_admin',
  'admin',
  'administrator',
  'security_admin',
]);

const TEAM_ROLES = new Set([
  'manager',
  'team_lead',
  'teamlead',
  'sales_manager',
  'crm_manager',
  'head_of_sales',
  'department_head',
]);

const USER_COLLECTION_CANDIDATES = [
  'users',
  'tenantusers',
  'tenant_users',
  'useraccounts',
  'user_accounts',
  'operators',
  'members',
  'teammembers',
  'team_members',
];

/**
 * @function normalizeProofLedgerText
 * @description Normalizes proof ledger text tokens.
 * @param {string} value Raw value.
 * @returns {string} Normalized token.
 * @collaboration Role parsing, tenant scoping, operator identity, and permission receipts.
 */
function normalizeProofLedgerText(value = '') {
  return String(value || '').trim();
}

/**
 * @function normalizeProofLedgerRole
 * @description Normalizes role names into a safe comparable token.
 * @param {string} role Raw role.
 * @returns {string} Normalized role.
 * @collaboration Role-based access control, tenant authority, and Proof Ledger policy decisions.
 */
function normalizeProofLedgerRole(role = '') {
  return normalizeProofLedgerText(role)
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
}

/**
 * @function createProofLedgerAccessReceiptId
 * @description Creates a compact receipt id for Proof Ledger access decisions.
 * @returns {string} Receipt id.
 * @collaboration Access receipts, tenant audit history, selected-user proof access, and evidence export.
 */
function createProofLedgerAccessReceiptId() {
  return `proof_ledger_access_${Date.now()}_${crypto.randomBytes(5).toString('hex')}`;
}

/**
 * @function resolveProofLedgerRequestContext
 * @description Resolves tenant, operator, role, target user, and institutional headers from a request.
 * @param {object} req Express request.
 * @returns {object} Request context.
 * @collaboration Tenant context, institutional headers, strike payload evidence, and permission policy.
 */
function resolveProofLedgerRequestContext(req = {}) {
  const body = req.body || {};
  const headers = req.headers || {};
  const institutionalHeaders = body.institutionalHeaders || {};
  const strikePayload = body.strikePayload || {};
  const tenantId = normalizeProofLedgerText(
    headers['x-tenant-id'] ||
      headers['x-wilsy-tenant-id'] ||
      institutionalHeaders.tenantId ||
      strikePayload.tenantId ||
      body.tenantId ||
      'MASTER'
  );
  const operatorUserId = normalizeProofLedgerText(
    headers['x-operator-user-id'] ||
      headers['x-operator-id'] ||
      headers['x-user-id'] ||
      institutionalHeaders.operatorUserId ||
      institutionalHeaders.operatorId ||
      strikePayload.operatorUserId ||
      strikePayload.operatorId ||
      body.operatorUserId ||
      body.userId ||
      'system'
  );
  const operatorEmail = normalizeProofLedgerText(
    headers['x-operator-email'] ||
      headers['x-user-email'] ||
      institutionalHeaders.operatorEmail ||
      strikePayload.operatorEmail ||
      body.operatorEmail ||
      ''
  );
  const operatorRole = normalizeProofLedgerRole(
    headers['x-operator-role'] ||
      headers['x-user-role'] ||
      headers['x-wilsy-role'] ||
      institutionalHeaders.operatorRole ||
      strikePayload.operatorRole ||
      body.operatorRole ||
      body.role ||
      'operator'
  );
  const targetUserId = normalizeProofLedgerText(
    body.targetUserId || body.selectedUserId || body.ownerUserId || operatorUserId
  );
  const reason = normalizeProofLedgerText(body.reason || body.accessReason || 'VIEW_PROOF_LEDGER');

  return {
    tenantId,
    operatorUserId,
    operatorEmail,
    operatorRole,
    targetUserId,
    reason,
    institutionalHeaders: {
      ...institutionalHeaders,
      tenantId,
      operatorUserId,
      operatorRole,
      route: req.originalUrl || req.url || '/api/crm/leads/views/proof-ledger/access',
      commandSurface:
        headers['x-command-surface'] || body.commandSurface || 'CRM_PROOF_LEDGER_ACCESS',
      generatedAt: institutionalHeaders.generatedAt || new Date().toISOString(),
    },
    strikePayload,
  };
}

/**
 * @function resolveProofLedgerCapabilities
 * @description Resolves Proof Ledger capabilities from a normalized role.
 * @param {string} role Normalized role.
 * @returns {object} Capability matrix.
 * @collaboration Tenant roles, audit controls, user selector visibility, export authority, and delegation authority.
 */
function resolveProofLedgerCapabilities(role = '') {
  const normalizedRole = normalizeProofLedgerRole(role);
  const tenantWide = TENANT_WIDE_ROLES.has(normalizedRole);
  const teamWide = tenantWide || TEAM_ROLES.has(normalizedRole);

  return {
    role: normalizedRole || 'operator',
    canViewOwnProofLedger: true,
    canViewTeamProofLedger: teamWide,
    canViewTenantProofLedger: tenantWide,
    canSelectProofLedgerUser: teamWide || tenantWide,
    canExportProofLedger: EXPORT_ROLES.has(normalizedRole),
    canDelegateProofLedgerAccess: DELEGATE_ROLES.has(normalizedRole),
  };
}

/**
 * @function getProofLedgerAccessModel
 * @description Returns a strict model for Proof Ledger access receipts.
 * @returns {object} Mongoose model.
 * @collaboration Access receipts, tenant audit trail, evidence replay, and admin review.
 */
function getProofLedgerAccessModel() {
  if (mongoose.models.CrmProofLedgerAccessReceipt) {
    return mongoose.models.CrmProofLedgerAccessReceipt;
  }

  const schema = new mongoose.Schema(
    {
      receiptId: { type: String, required: true, index: true, unique: true },
      tenantId: { type: String, required: true, index: true },
      operatorUserId: { type: String, required: true, index: true },
      operatorRole: { type: String, required: true, index: true },
      targetUserId: { type: String, required: true, index: true },
      scope: { type: String, required: true, index: true },
      decision: { type: String, required: true, index: true },
      reason: { type: String, default: 'VIEW_PROOF_LEDGER' },
      route: { type: String, default: '/api/crm/leads/views/proof-ledger/access' },
      commandSurface: { type: String, default: 'CRM_PROOF_LEDGER_ACCESS' },
      institutionalHeaders: { type: Object, default: {} },
      strikePayload: { type: Object, default: {} },
      generatedAt: { type: Date, default: Date.now, index: true },
    },
    {
      collection: 'crm_proof_ledger_access_receipts',
      minimize: false,
    }
  );

  return mongoose.model('CrmProofLedgerAccessReceipt', schema);
}

/**
 * @function resolveUserIdFromDocument
 * @description Resolves a stable user id from a user-like document.
 * @param {object} user User-like document.
 * @returns {string} User id.
 * @collaboration Tenant user selectors, cross-user Proof Ledger access, and subordinate checks.
 */
function resolveUserIdFromDocument(user = {}) {
  return normalizeProofLedgerText(
    user._id ||
      user.id ||
      user.userId ||
      user.operatorUserId ||
      user.operatorId ||
      user.ownerUserId ||
      user.email ||
      ''
  );
}

/**
 * @function sanitizeProofLedgerUser
 * @description Produces a minimal safe user selector record.
 * @param {object} user User-like document.
 * @returns {object} Sanitized user record.
 * @collaboration User selector, privacy minimization, tenant access, and Proof Ledger delegation.
 */
function sanitizeProofLedgerUser(user = {}) {
  const userId = resolveUserIdFromDocument(user);
  const role = normalizeProofLedgerRole(
    user.role || user.userRole || user.operatorRole || user.profile || ''
  );
  const name = normalizeProofLedgerText(
    user.name || user.fullName || user.displayName || user.firstName || user.email || userId
  );
  const email = normalizeProofLedgerText(user.email || user.operatorEmail || '');

  return {
    userId,
    name,
    email,
    role,
    managerId: normalizeProofLedgerText(
      user.managerId || user.reportsTo || user.supervisorId || user.teamLeadId || ''
    ),
    teamId: normalizeProofLedgerText(user.teamId || user.departmentId || user.groupId || ''),
    status: normalizeProofLedgerText(user.status || user.accountStatus || 'active'),
  };
}

/**
 * @function documentBelongsToTenant
 * @description Checks whether a user-like document belongs to the tenant.
 * @param {object} user User-like document.
 * @param {string} tenantId Tenant id.
 * @returns {boolean} True if tenant-scoped.
 * @collaboration Multi-tenant boundaries, user selector minimization, and no cross-tenant leakage.
 */
function documentBelongsToTenant(user = {}, tenantId = '') {
  const tenantFields = [
    user.tenantId,
    user.tenant,
    user.accountTenantId,
    user.organizationId,
    user.orgId,
    user.companyTenantId,
  ]
    .map((value) => normalizeProofLedgerText(value))
    .filter(Boolean);

  if (!tenantFields.length && tenantId === 'MASTER') {
    return true;
  }

  return tenantFields.includes(tenantId);
}

/**
 * @function queryTenantProofLedgerUsers
 * @description Resolves tenant users from available user-like collections without leaking cross-tenant data.
 * @param {object} context Request context.
 * @returns {Promise<Array<object>>} Sanitized tenant users.
 * @collaboration Tenant user selector, admin delegation, manager/team proof visibility, and minimal PII exposure.
 */
async function queryTenantProofLedgerUsers(context = {}) {
  if (mongoose.connection.readyState !== 1) {
    return [];
  }

  const tenantId = context.tenantId || 'MASTER';
  const collected = new Map();

  for (const collectionName of USER_COLLECTION_CANDIDATES) {
    try {
      const collection = mongoose.connection.collection(collectionName);
      const candidates = await collection
        .find({
          $or: [
            { tenantId },
            { tenant: tenantId },
            { accountTenantId: tenantId },
            { organizationId: tenantId },
            { orgId: tenantId },
            { companyTenantId: tenantId },
          ],
        })
        .limit(250)
        .toArray();

      for (const candidate of candidates) {
        if (!documentBelongsToTenant(candidate, tenantId)) continue;
        const sanitized = sanitizeProofLedgerUser(candidate);
        if (sanitized.userId) {
          collected.set(sanitized.userId, sanitized);
        }
      }
    } catch {
      // Collection may not exist. Keep resolver portable across tenants.
    }
  }

  if (!collected.has(context.operatorUserId)) {
    collected.set(context.operatorUserId, {
      userId: context.operatorUserId,
      name: context.operatorEmail || context.operatorUserId,
      email: context.operatorEmail || '',
      role: context.operatorRole || 'operator',
      managerId: '',
      teamId: '',
      status: 'active',
    });
  }

  return Array.from(collected.values()).sort((a, b) => a.name.localeCompare(b.name));
}

/**
 * @function resolveProofLedgerOperatorAuthority
 * @description Resolves operator role authority from tenant user records before accepting request fallback.
 * @param {object} context Proof Ledger request context.
 * @param {Array<object>} users Sanitized tenant users.
 * @returns {object} Verified authority packet.
 * @collaboration Tenant directory, role hardening, anti-spoofing policy, Proof Ledger export controls, and access receipts.
 */
function resolveProofLedgerOperatorAuthority(context = {}, users = []) {
  const operatorUserId = normalizeProofLedgerText(context.operatorUserId);
  const operatorEmail = normalizeProofLedgerText(context.operatorEmail).toLowerCase();
  const headerRole = normalizeProofLedgerRole(context.operatorRole || 'operator');

  const matchedUser =
    users.find((user) => {
      const userId = normalizeProofLedgerText(user.userId);
      const userEmail = normalizeProofLedgerText(user.email).toLowerCase();
      return Boolean(
        operatorUserId &&
        (userId === operatorUserId ||
          userEmail === operatorUserId.toLowerCase() ||
          (operatorEmail && userEmail === operatorEmail))
      );
    }) || null;

  const directoryRole = normalizeProofLedgerRole(matchedUser?.role || '');
  const productionMode = process.env.NODE_ENV === 'production';

  if (directoryRole) {
    return {
      role: directoryRole,
      authoritySource: 'TENANT_DIRECTORY',
      matchedUser: matchedUser
        ? {
            userId: matchedUser.userId,
            email: matchedUser.email,
            name: matchedUser.name,
            status: matchedUser.status,
          }
        : null,
      headerRole,
      productionFallbackUsed: false,
    };
  }

  if (!productionMode && headerRole) {
    return {
      role: headerRole,
      authoritySource: 'REQUEST_HEADER_DEV_FALLBACK',
      matchedUser: null,
      headerRole,
      productionFallbackUsed: true,
    };
  }

  return {
    role: 'operator',
    authoritySource: productionMode
      ? 'PRODUCTION_DIRECTORY_MISS_DENY_ELEVATION'
      : 'DIRECTORY_MISS_DEFAULT_OPERATOR',
    matchedUser: null,
    headerRole,
    productionFallbackUsed: false,
  };
}

// P60K5Q10FG104N2_AUTHORITY_SOURCE_HARDENING

/**
 * @function isProofLedgerSubordinate
 * @description Checks if target user reports to the operator using known manager fields.
 * @param {object} params Check params.
 * @returns {boolean} True if subordinate.
 * @collaboration Manager visibility, team proof access, hierarchy-safe user selection, and cross-user ledger controls.
 */
function isProofLedgerSubordinate(params = {}) {
  const operatorUserId = normalizeProofLedgerText(params.operatorUserId);
  const targetUser = params.targetUser || {};
  const managerFields = [
    targetUser.managerId,
    targetUser.reportsTo,
    targetUser.supervisorId,
    targetUser.teamLeadId,
  ]
    .map((value) => normalizeProofLedgerText(value))
    .filter(Boolean);

  return Boolean(operatorUserId && managerFields.includes(operatorUserId));
}

/**
 * @function resolveProofLedgerAccessDecision
 * @description Resolves whether operator can access target user's Proof Ledger.
 * @param {object} params Access params.
 * @returns {object} Access decision.
 * @collaboration Own ledger access, subordinate access, tenant-wide access, export authority, and access receipts.
 */
function resolveProofLedgerAccessDecision(params = {}) {
  const context = params.context || {};
  const capabilities = params.capabilities || {};
  const targetUser = params.targetUser || null;
  const targetUserId = normalizeProofLedgerText(
    params.targetUserId || context.targetUserId || context.operatorUserId
  );
  const operatorUserId = normalizeProofLedgerText(context.operatorUserId);
  const ownLedger = targetUserId === operatorUserId || !targetUserId;

  if (ownLedger && capabilities.canViewOwnProofLedger) {
    return { allowed: true, scope: 'OWN', reasonCode: 'OWN_LEDGER_ALLOWED' };
  }

  if (capabilities.canViewTenantProofLedger) {
    return { allowed: true, scope: 'TENANT', reasonCode: 'TENANT_LEDGER_ALLOWED' };
  }

  if (
    capabilities.canViewTeamProofLedger &&
    targetUser &&
    isProofLedgerSubordinate({ operatorUserId, targetUser })
  ) {
    return { allowed: true, scope: 'TEAM', reasonCode: 'TEAM_SUBORDINATE_LEDGER_ALLOWED' };
  }

  return { allowed: false, scope: 'DENIED', reasonCode: 'INSUFFICIENT_PROOF_LEDGER_AUTHORITY' };
}

/**
 * @function recordProofLedgerAccessReceipt
 * @description Persists a Proof Ledger access receipt when database is available.
 * @param {object} params Receipt params.
 * @returns {Promise<object>} Receipt packet.
 * @collaboration Audit persistence, access evidence, tenant review, and security accountability.
 */
async function recordProofLedgerAccessReceipt(params = {}) {
  const receipt = {
    receiptId: createProofLedgerAccessReceiptId(),
    tenantId: params.context.tenantId,
    operatorUserId: params.context.operatorUserId,
    operatorRole: params.context.operatorRole,
    targetUserId: params.targetUserId,
    scope: params.decision.scope,
    decision: params.decision.allowed ? 'ALLOW' : 'DENY',
    reason: params.context.reason,
    route: params.context.institutionalHeaders.route,
    commandSurface: params.context.institutionalHeaders.commandSurface,
    institutionalHeaders: params.context.institutionalHeaders,
    strikePayload: {
      ...params.context.strikePayload,
      proofLedgerAccess: {
        targetUserId: params.targetUserId,
        scope: params.decision.scope,
        reasonCode: params.decision.reasonCode,
      },
    },
    generatedAt: new Date(),
  };

  if (mongoose.connection.readyState === 1) {
    try {
      const AccessModel = getProofLedgerAccessModel();
      await AccessModel.create(receipt);
      return { ...receipt, persisted: true };
    } catch (error) {
      return { ...receipt, persisted: false, persistenceError: error.message };
    }
  }

  return { ...receipt, persisted: false, persistenceError: 'DATABASE_NOT_CONNECTED' };
}

/**
 * @function resolveProofLedgerAccessPolicy
 * @description Resolves Proof Ledger policy, selectable users, decision, and access receipt.
 * @param {object} req Express request.
 * @returns {Promise<object>} Policy packet.
 * @collaboration Backend-enforced permissions, tenant user selector, selected-user proof ledger, and audit receipts.
 */
async function resolveProofLedgerAccessPolicy(req = {}) {
  const context = resolveProofLedgerRequestContext(req);
  const users = await queryTenantProofLedgerUsers(context);
  const authority = resolveProofLedgerOperatorAuthority(context, users);
  context.operatorRole = authority.role;
  context.institutionalHeaders.operatorRole = authority.role;
  context.institutionalHeaders.authoritySource = authority.authoritySource;

  const capabilities = resolveProofLedgerCapabilities(authority.role);
  const usersById = new Map(users.map((user) => [user.userId, user]));
  const targetUserId = context.targetUserId || context.operatorUserId;
  const targetUser = usersById.get(targetUserId) || null;
  const decision = resolveProofLedgerAccessDecision({
    context,
    capabilities,
    targetUser,
    targetUserId,
  });
  const receipt = await recordProofLedgerAccessReceipt({
    context,
    capabilities,
    targetUserId,
    decision,
  });
  const selectableUsers = users
    .filter((user) => {
      if (capabilities.canViewTenantProofLedger) return true;
      if (user.userId === context.operatorUserId) return true;
      if (capabilities.canViewTeamProofLedger) {
        return isProofLedgerSubordinate({
          operatorUserId: context.operatorUserId,
          targetUser: user,
        });
      }
      return false;
    })
    .map((user) => ({
      userId: user.userId,
      name: user.name,
      email: user.email,
      role: user.role,
      status: user.status,
      accessScope:
        user.userId === context.operatorUserId
          ? 'OWN'
          : capabilities.canViewTenantProofLedger
            ? 'TENANT'
            : 'TEAM',
    }));

  return {
    ok: true,
    success: true,
    version: PROOF_LEDGER_PERMISSION_VERSION,
    tenantId: context.tenantId,
    operator: {
      userId: context.operatorUserId,
      email: context.operatorEmail,
      role: context.operatorRole,
      authoritySource: authority.authoritySource,
      headerRole: authority.headerRole,
      productionFallbackUsed: authority.productionFallbackUsed,
    },
    target: {
      userId: targetUserId,
      existsInTenantDirectory: Boolean(targetUser),
    },
    capabilities,
    decision,
    receipt,
    selectableUsers,
    exportPolicy: {
      enabled: Boolean(decision.allowed && capabilities.canExportProofLedger),
      reasonCode: decision.allowed
        ? capabilities.canExportProofLedger
          ? 'EXPORT_ALLOWED'
          : 'ROLE_CANNOT_EXPORT_PROOF_LEDGER'
        : decision.reasonCode,
      authoritySource: authority.authoritySource,
    },
    delegationPolicy: {
      enabled: Boolean(capabilities.canDelegateProofLedgerAccess),
      reasonCode: capabilities.canDelegateProofLedgerAccess
        ? 'DELEGATION_ALLOWED'
        : 'ROLE_CANNOT_DELEGATE_PROOF_LEDGER_ACCESS',
    },
  };
}

/**
 * @function handleProofLedgerAccessPolicy
 * @description Express handler for Proof Ledger policy resolution.
 * @param {object} req Express request.
 * @param {object} res Express response.
 * @returns {Promise<object>} JSON response.
 * @collaboration Backend routes, policy resolution, user selector hydration, and access receipts.
 */
async function handleProofLedgerAccessPolicy(req, res) {
  try {
    const policy = await resolveProofLedgerAccessPolicy(req);
    return res.status(200).json(policy);
  } catch (error) {
    return res.status(500).json({
      ok: false,
      success: false,
      error: 'PROOF_LEDGER_ACCESS_POLICY_FAILED',
      message: error.message,
    });
  }
}

export {
  PROOF_LEDGER_PERMISSION_VERSION,
  handleProofLedgerAccessPolicy,
  normalizeProofLedgerRole,
  queryTenantProofLedgerUsers,
  resolveProofLedgerAccessPolicy,
  resolveProofLedgerCapabilities,
  resolveProofLedgerOperatorAuthority,
  resolveProofLedgerRequestContext,
};
