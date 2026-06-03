/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - TENANT ADMINISTRATION SENTINEL - OMEGA SINGULARITY                                                                          ║
 * ║ [TENANT ISOLATION | USER GOVERNANCE | COMPLIANCE TAGGING | PQE-256]                                                                    ║
 * ║ VERSION: 15.0.0-SINGULARITY                                                                                                            ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/tenantAdminController.js                                     ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import User from '../models/User.js';
import Tenant from '../models/Tenant.js';
import TenantInvitation from '../models/TenantInvitation.js';
import SovereignAudit from '../models/SovereignAudit.js';
import auditLogger from '../utils/auditLogger.js';
import cryptoUtils from '../utils/cryptoUtils.js';
import { sendInvitationEmail, sendWelcomeEmail } from '../services/emailService.js';
import { getCurrentTenant, getCurrentUser, getCurrentRequestId } from '../middleware/tenantContext.js';
import { hasPermission } from '../constants/roles.js';
import crypto from 'crypto';

/**
 * Utility: Standard error response with requestId for forensic tracking
 */
function errorResponse(res, error, message, req) {
  console.error(`🚨 [Citadel Error] ${message}:`, error);
  return res.status(500).json({
    success: false,
    message,
    requestId: getCurrentRequestId(),
    timestamp: new Date().toISOString()
  });
}

/* ---------------------------------------------------------------------------
   DASHBOARD & STATISTICS
   --------------------------------------------------------------------------- */

/**
 * @desc    Get tenant dashboard stats and recent forensic activity
 * @route   GET /api/tenant-admin/dashboard
 */
export const getDashboard = async (req, res) => {
  const tenantId = getCurrentTenant();
  try {
    const [totalUsers, activeUsers, recentActivity] = await Promise.all([
      User.countDocuments({ tenantId }),
      User.countDocuments({ tenantId, isActive: true }),
      SovereignAudit.find({ tenantId })
        .sort('-createdAt')
        .limit(10)
        .populate('performedBy', 'name email')
    ]);

    res.json({
      success: true,
      data: {
        stats: {
          totalUsers,
          activeUsers,
          pendingInvitations: await TenantInvitation.countDocuments({ tenantId, status: 'pending' }),
          activePercentage: totalUsers ? Math.round((activeUsers / totalUsers) * 100) : 0
        },
        recentActivity
      }
    });
  } catch (error) {
    return errorResponse(res, error, 'Get tenant dashboard error', req);
  }
};

/* ---------------------------------------------------------------------------
   USER MANAGEMENT
   --------------------------------------------------------------------------- */

/**
 * @desc    Get all users in tenant with advanced filtering
 * @route   GET /api/tenant-admin/users
 */
export const getUsers = async (req, res) => {
  const tenantId = getCurrentTenant();
  try {
    const {
      page = 1, limit = 20, search, role, status,
      sortBy = 'createdAt', sortOrder = 'desc'
    } = req.query;

    const query = { tenantId };
    if (search) {
      query.$or = [
        { name: { $regex: search, $options: 'i' } },
        { email: { $regex: search, $options: 'i' } }
      ];
    }
    if (role) query.role = role;
    if (status) query.isActive = status === 'active';

    const total = await User.countDocuments(query);
    const users = await User.find(query)
      .select('-password -refreshToken -mfaSecret')
      .sort({ [sortBy]: sortOrder === 'desc' ? -1 : 1 })
      .limit(parseInt(limit))
      .skip((parseInt(page) - 1) * parseInt(limit));

    res.json({
      success: true,
      data: {
        users,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / parseInt(limit))
        }
      }
    });
  } catch (error) {
    return errorResponse(res, error, 'Get tenant users error', req);
  }
};

/**
 * @desc    Create new user or send secure invitation
 * @route   POST /api/tenant-admin/users
 */
export const createUser = async (req, res) => {
  const tenantId = getCurrentTenant();
  const performerId = getCurrentUser();
  const { email, name, role, sendInvite = true } = req.body;

  try {
    const currentUserRole = performerId?.role; // adjust based on context
    if (!hasPermission(currentUserRole, 'user:create')) {
      return res.status(403).json({ success: false, message: 'Insufficient permissions' });
    }

    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ success: false, message: 'User already exists in the system' });
    }

    if (sendInvite) {
      const invitation = await TenantInvitation.create({
        tenantId,
        email,
        role,
        invitedBy: performerId._id,
        metadata: { ipAddress: req.ip, userAgent: req.get('User-Agent') }
      });
      await sendInvitationEmail(email, invitation.token, tenantId);

      await auditLogger.log({
        action: 'USER_INVITED',
        category: 'ACCESS',
        tenantId,
        performedBy: performerId._id,
        metadata: { invitedEmail: email, role, ip: req.ip },
        severity: 'audit',
        status: 'success',
        complianceTags: ['POPIA', 'SOC2']
      });

      return res.status(201).json({ success: true, message: 'Secure invitation dispatched' });
    }

    const tempPassword = crypto.randomBytes(12).toString('base64');
    const user = await User.create({
      email, name, role, tenantId,
      password: tempPassword,
      mustChangePassword: true,
      createdBy: performerId._id
    });

    await sendWelcomeEmail(email, name, tempPassword, tenantId);

    await auditLogger.log({
      action: 'USER_CREATED',
      category: 'ACCESS',
      tenantId,
      performedBy: performerId._id,
      targetUser: user._id,
      metadata: { ip: req.ip },
      severity: 'audit',
      status: 'success',
      complianceTags: ['POPIA', 'ISO27001']
    });

    res.status(201).json({ success: true, message: 'User created successfully' });
  } catch (error) {
    return errorResponse(res, error, 'Create tenant user error', req);
  }
};

/**
 * @desc    Update user permissions and status with audit trail
 * @route   PUT /api/tenant-admin/users/:userId
 */
export const updateUser = async (req, res) => {
  const tenantId = getCurrentTenant();
  const performerId = getCurrentUser();
  const { userId } = req.params;
  const { name, role, isActive } = req.body;

  try {
    const user = await User.findOne({ _id: userId, tenantId });
    if (!user) return res.status(404).json({ success: false, message: 'User not found in this tenant' });

    const currentUserRole = performerId?.role;
    if (role && role !== user.role && !hasPermission(currentUserRole, 'user:assign_roles')) {
      return res.status(403).json({ success: false, message: 'Insufficient permissions for role assignment' });
    }

    const changes = { before: {}, after: {} };
    if (name && name !== user.name) {
      changes.before.name = user.name;
      changes.after.name = name;
      user.name = name;
    }
    if (role && role !== user.role) {
      changes.before.role = user.role;
      changes.after.role = role;
      user.role = role;
    }
    if (isActive !== undefined && isActive !== user.isActive) {
      changes.before.isActive = user.isActive;
      changes.after.isActive = isActive;
      user.isActive = isActive;
    }

    await user.save();

    if (Object.keys(changes.before).length > 0) {
      await auditLogger.log({
        action: 'USER_UPDATED',
        category: 'ACCESS',
        tenantId,
        performedBy: performerId._id,
        targetUser: user._id,
        changes,
        metadata: { ip: req.ip },
        severity: 'audit',
        status: 'success',
        complianceTags: ['POPIA', 'SOC2']
      });
    }

    res.json({ success: true, message: 'User profile updated' });
  } catch (error) {
    return errorResponse(res, error, 'Update tenant user error', req);
  }
};

/**
 * @desc    Delete user with "Right to be Forgotten" forensic logging
 * @route   DELETE /api/tenant-admin/users/:userId
 */
export const deleteUser = async (req, res) => {
  const tenantId = getCurrentTenant();
  const performerId = getCurrentUser();
  const { userId } = req.params;

  try {
    if (userId === performerId._id.toString()) {
      return res.status(400).json({ success: false, message: 'Account suicide prevention: Cannot delete own profile' });
    }

    const user = await User.findOne({ _id: userId, tenantId });
    if (!user) return res.status(404).json({ success: false, message: 'User not found' });

    await auditLogger.log({
      action: 'USER_DELETED',
      category: 'ACCESS',
      tenantId,
      performedBy: performerId._id,
      metadata: {
        ip: req.ip,
        deletedEmail: user.email
      },
      severity: 'critical',
      status: 'success',
      complianceTags: ['POPIA', 'GDPR', 'RTBF']
    });

    await user.deleteOne();
    res.json({ success: true, message: 'User purged from system' });
  } catch (error) {
    return errorResponse(res, error, 'Delete tenant user error', req);
  }
};

/* ---------------------------------------------------------------------------
   TENANT CONFIGURATION
   --------------------------------------------------------------------------- */

/**
 * @desc    Update Tenant-wide configuration and compliance settings
 * @route   PUT /api/tenant-admin/settings
 */
export const updateSettings = async (req, res) => {
  const tenantId = getCurrentTenant();
  const performerId = getCurrentUser();
  const { settings, legalName, contactInfo } = req.body;

  try {
    const tenant = await Tenant.findById(tenantId);
    if (!tenant) return res.status(404).json({ success: false, message: 'Tenant not found' });

    const changes = {
      before: { settings: tenant.settings, legalName: tenant.legalName },
      after: { settings, legalName }
    };

    if (settings) tenant.settings = { ...tenant.settings, ...settings };
    if (legalName) tenant.legalName = legalName;
    if (contactInfo) tenant.contactInfo = { ...tenant.contactInfo, ...contactInfo };

    await tenant.save();

    await auditLogger.log({
      action: 'TENANT_SETTINGS_UPDATED',
      category: 'CONFIG',
      tenantId,
      performedBy: performerId._id,
      changes,
      metadata: { ip: req.ip },
      severity: 'warn',
      status: 'success',
      complianceTags: ['ISO27001', 'SOC2']
    });

    res.json({ success: true, message: 'Tenant settings synchronized' });
  } catch (error) {
    return errorResponse(res, error, 'Update settings error', req);
  }
};

// Default export
export default {
  getDashboard,
  getUsers,
  createUser,
  updateUser,
  deleteUser,
  updateSettings,
};
