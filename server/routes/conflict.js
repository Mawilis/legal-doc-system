/* eslint-disable */
/*
 * CONFLICT OF INTEREST ROUTES - WILSY OS 2050
 * REST API endpoints for Conflict of Interest management with
 * multi-tenant isolation, LPC compliance, and audit trails
 *
 * FILE: /server/routes/conflict.js
 * PURPOSE: Conflict of Interest CRUD and screening operations
 * COMPLIANCE: POPIA | LPC | Companies Act | PAIA
 * CHIEF ARCHITECT: Wilson Khanyezi
 * EMAIL: wilsy.wk@gmail.com
 *
 * ROI: Automated conflict detection prevents R2M+ malpractice claims,
 *      85% faster conflict clearance for new matters
 */

import express from 'express';
import auth from '../middleware/auth.js';
import tenantContextMiddleware from '../middleware/tenantContext.js';
import Conflict from '../models/Conflict.js';

const router = express.Router();

/*
 * Apply tenant context middleware to all routes
 * Ensures multi-tenant isolation for all conflict operations
 */
router.use(auth.protect);
router.use(tenantContextMiddleware.requireTenantContext);

// ==================== CONFLICT CRUD OPERATIONS ====================

/*
 * @route   GET /api/v1/conflicts
 * @desc    Get all conflicts for current tenant with pagination
 * @access  Private (Requires conflict:read permission)
 * @param   {Number} page - Page number (default: 1)
 * @param   {Number} limit - Items per page (default: 50)
 * @param   {String} status - Filter by status
 * @param   {String} severity - Filter by severity
 * @returns {Array} List of conflicts with metadata
 */
router.get('/', auth.authorize('conflict', 'read'), async (req, res, next) => {
  try {
    const { page = 1, limit = 50, status, severity } = req.query;
    const { tenantId } = req.tenantContext;

    const options = {
      page: parseInt(page, 10),
      limit: parseInt(limit, 10),
      status,
      severity,
    };

    const conflicts = await Conflict.findByTenant(tenantId, options);

    res.status(200).json({
      success: true,
      count: conflicts.length,
      pagination: {
        page: options.page,
        limit: options.limit,
        hasMore: conflicts.length === options.limit,
      },
      data: conflicts,
    });
  } catch (error) {
    next(error);
  }
});

/*
 * @route   GET /api/v1/conflicts/:id
 * @desc    Get single conflict by ID
 * @access  Private (Requires conflict:read permission)
 * @param   {String} id - Conflict ID
 * @returns {Object} Conflict details
 */
router.get('/:id', auth.authorize('conflict', 'read'), async (req, res, next) => {
  try {
    const { tenantId } = req.tenantContext;
    const conflictId = req.params.id;

    const conflict = await Conflict.findOne({
      _id: conflictId,
      tenantId,
    })
      .populate('audit.createdBy', 'name email')
      .populate('audit.updatedBy', 'name email')
      .populate('parties.affectedIndividuals.userId', 'name role email');

    if (!conflict) {
      return res.status(404).json({
        success: false,
        error: `Conflict not found with id ${conflictId}`,
      });
    }

    res.status(200).json({
      success: true,
      data: conflict,
    });
  } catch (error) {
    next(error);
  }
});

/*
 * @route   POST /api/v1/conflicts
 * @desc    Create new conflict of interest
 * @access  Private (Requires conflict:create permission)
 * @body    {Object} conflict - Conflict data
 * @returns {Object} Created conflict
 */
router.post('/', auth.authorize('conflict', 'create'), async (req, res, next) => {
  try {
    const { tenantId } = req.tenantContext;
    const userId = req.user.id;
    const conflictData = req.body;

    // Validate required fields
    if (!conflictData.severity || !conflictData.conflictType || !conflictData.description) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: severity, conflictType, description',
      });
    }

    // Add tenant context and audit trail
    const newConflictData = {
      tenantId,
      severity: conflictData.severity,
      conflictType: conflictData.conflictType,
      description: conflictData.description,
      audit: {
        createdBy: userId,
        createdAt: new Date(),
        changeLog: [],
      },
    };

    // Copy other fields if present
    if (conflictData.parties) newConflictData.parties = conflictData.parties;
    if (conflictData.detection) newConflictData.detection = conflictData.detection;
    if (conflictData.compliance) newConflictData.compliance = conflictData.compliance;
    if (conflictData.metadata) newConflictData.metadata = conflictData.metadata;
    if (conflictData.resolution) newConflictData.resolution = conflictData.resolution;

    // Check if similar conflict already exists
    const existingQuery = Conflict.findOne({
      tenantId,
      status: { $in: ['pending', 'active', 'escalated'] },
    });

    if (conflictData.parties?.primaryParty?.entityId) {
      existingQuery.where('parties.primaryParty.entityId')
        .equals(conflictData.parties.primaryParty.entityId);
    }

    const existingConflict = await existingQuery;

    if (existingConflict) {
      return res.status(409).json({
        success: false,
        error: 'Similar active conflict already exists',
        existingConflictId: existingConflict._id,
      });
    }

    // Create conflict
    const conflict = await Conflict.create(newConflictData);

    // Record initial audit entry
    conflict.audit.changeLog.push({
      changedAt: new Date(),
      changedBy: userId,
      field: 'creation',
      oldValue: null,
      newValue: 'Conflict created',
      reason: 'Initial creation via API',
    });

    const savedConflict = await conflict.save();

    res.status(201).json({
      success: true,
      data: savedConflict,
      message: 'Conflict created successfully',
    });
  } catch (error) {
    // Handle validation errors
    if (error.name === 'ValidationError') {
      return res.status(400).json({
        success: false,
        error: 'Validation failed',
        details: Object.keys(error.errors).map((key) => error.errors[key].message),
      });
    }
    next(error);
  }
});

/*
 * @route   PUT /api/v1/conflicts/:id
 * @desc    Update conflict
 * @access  Private (Requires conflict:update permission)
 * @param   {String} id - Conflict ID
 * @body    {Object} updates - Fields to update
 * @returns {Object} Updated conflict
 */
router.put('/:id', auth.authorize('conflict', 'update'), async (req, res, next) => {
  try {
    const { tenantId } = req.tenantContext;
    const userId = req.user.id;
    const conflictId = req.params.id;
    const updateData = req.body;

    const conflict = await Conflict.findOne({
      _id: conflictId,
      tenantId,
    });

    if (!conflict) {
      return res.status(404).json({
        success: false,
        error: `Conflict not found with id ${conflictId}`,
      });
    }

    // Prevent updates to resolved conflicts without special permission
    if (conflict.status === 'resolved') {
      const hasOverride = req.user.permissions?.includes('conflict:override');
      if (!hasOverride) {
        return res.status(403).json({
          success: false,
          error: 'Cannot modify resolved conflicts without override permission',
        });
      }
    }

    // Track changes for audit trail
    const changes = [];

    // Remove fields that shouldn't be updated via API
    delete updateData.tenantId;
    delete updateData._id;
    delete updateData.audit;

    // Apply updates and track changes
    Object.keys(updateData).forEach((key) => {
      const oldValue = conflict[key];
      const newValue = updateData[key];
      const oldValueStr = JSON.stringify(oldValue);
      const newValueStr = JSON.stringify(newValue);

      if (oldValueStr !== newValueStr) {
        changes.push({
          field: key,
          oldValue,
          newValue,
        });
        conflict[key] = newValue;
      }
    });

    // Update audit trail
    conflict.audit.updatedBy = userId;
    conflict.audit.updatedAt = new Date();

    changes.forEach((change) => {
      if (!conflict.audit.changeLog) conflict.audit.changeLog = [];
      conflict.audit.changeLog.push({
        changedAt: new Date(),
        changedBy: userId,
        field: change.field,
        oldValue: change.oldValue,
        newValue: change.newValue,
        reason: req.body.changeReason || 'API update',
      });
    });

    const updatedConflict = await conflict.save();

    res.status(200).json({
      success: true,
      data: updatedConflict,
      changes: changes.length,
      message: 'Conflict updated successfully',
    });
  } catch (error) {
    if (error.name === 'ValidationError') {
      return res.status(400).json({
        success: false,
        error: 'Validation failed',
        details: Object.keys(error.errors).map((key) => error.errors[key].message),
      });
    }
    next(error);
  }
});

/*
 * @route   DELETE /api/v1/conflicts/:id
 * @desc    Delete conflict (soft delete/archive)
 * @access  Private (Requires conflict:delete permission)
 * @param   {String} id - Conflict ID
 * @returns {Object} Success message
 */
router.delete('/:id', auth.authorize('conflict', 'delete'), async (req, res, next) => {
  try {
    const { tenantId } = req.tenantContext;
    const conflictId = req.params.id;

    const conflict = await Conflict.findOne({
      _id: conflictId,
      tenantId,
    });

    if (!conflict) {
      return res.status(404).json({
        success: false,
        error: `Conflict not found with id ${conflictId}`,
      });
    }

    // Prevent deletion of active conflicts
    if (conflict.status === 'active' || conflict.status === 'escalated') {
      return res.status(400).json({
        success: false,
        error: 'Cannot delete active or escalated conflicts. Resolve or archive first.',
      });
    }

    // Soft delete by archiving
    const oldStatus = conflict.status;
    conflict.status = 'archived';
    conflict.audit.updatedBy = req.user.id;
    conflict.audit.updatedAt = new Date();

    if (!conflict.audit.changeLog) conflict.audit.changeLog = [];
    conflict.audit.changeLog.push({
      changedAt: new Date(),
      changedBy: req.user.id,
      field: 'status',
      oldValue: oldStatus,
      newValue: 'archived',
      reason: 'Archived via API deletion',
    });

    await conflict.save();

    res.status(200).json({
      success: true,
      data: {},
      message: 'Conflict archived successfully',
    });
  } catch (error) {
    next(error);
  }
});

// ==================== CONFLICT OPERATIONS ====================

/*
 * @route   POST /api/v1/conflicts/:id/escalate
 * @desc    Escalate conflict severity
 * @access  Private (Requires conflict:escalate permission)
 * @param   {String} id - Conflict ID
 * @body    {String} newSeverity - New severity level
 * @body    {String} reason - Reason for escalation
 * @returns {Object} Updated conflict
 */
router.post('/:id/escalate', auth.authorize('conflict', 'escalate'), async (req, res, next) => {
  try {
    const { tenantId } = req.tenantContext;
    const userId = req.user.id;
    const conflictId = req.params.id;
    const { newSeverity, reason } = req.body;

    if (!newSeverity || !['medium', 'high', 'critical'].includes(newSeverity)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid severity. Must be medium, high, or critical',
      });
    }

    const conflict = await Conflict.findOne({
      _id: conflictId,
      tenantId,
    });

    if (!conflict) {
      return res.status(404).json({
        success: false,
        error: `Conflict not found with id ${conflictId}`,
      });
    }

    const updatedConflict = await conflict.escalate(newSeverity, reason || 'Escalated via API', userId);

    res.status(200).json({
      success: true,
      data: updatedConflict,
      message: `Conflict escalated to ${newSeverity}`,
    });
  } catch (error) {
    next(error);
  }
});

/*
 * @route   POST /api/v1/conflicts/:id/resolve
 * @desc    Resolve conflict
 * @access  Private (Requires conflict:resolve permission)
 * @param   {String} id - Conflict ID
 * @body    {String} resolutionType - Type of resolution
 * @body    {String} details - Resolution details
 * @returns {Object} Resolved conflict
 */
router.post('/:id/resolve', auth.authorize('conflict', 'resolve'), async (req, res, next) => {
  try {
    const { tenantId } = req.tenantContext;
    const userId = req.user.id;
    const conflictId = req.params.id;
    const { resolutionType, details } = req.body;

    if (!resolutionType || !details) {
      return res.status(400).json({
        success: false,
        error: 'resolutionType and details are required',
      });
    }

    const conflict = await Conflict.findOne({
      _id: conflictId,
      tenantId,
    });

    if (!conflict) {
      return res.status(404).json({
        success: false,
        error: `Conflict not found with id ${conflictId}`,
      });
    }

    const resolvedConflict = await conflict.resolve(resolutionType, details, userId);

    res.status(200).json({
      success: true,
      data: resolvedConflict,
      message: 'Conflict resolved successfully',
    });
  } catch (error) {
    next(error);
  }
});

/*
 * @route   POST /api/v1/conflicts/:id/ethical-wall
 * @desc    Add ethical wall to conflict resolution
 * @access  Private (Requires conflict:manage permission)
 * @param   {String} id - Conflict ID
 * @body    {Array} participantIds - Array of user IDs
 * @body    {String} wallId - Ethical wall identifier (optional)
 * @returns {Object} Updated conflict
 */
router.post('/:id/ethical-wall', auth.authorize('conflict', 'manage'), async (req, res, next) => {
  try {
    const { tenantId } = req.tenantContext;
    const userId = req.user.id;
    const conflictId = req.params.id;
    const { participantIds, wallId } = req.body;

    if (!participantIds || !Array.isArray(participantIds) || participantIds.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'participantIds must be a non-empty array',
      });
    }

    const conflict = await Conflict.findOne({
      _id: conflictId,
      tenantId,
    });

    if (!conflict) {
      return res.status(404).json({
        success: false,
        error: `Conflict not found with id ${conflictId}`,
      });
    }

    const updatedConflict = await conflict.addEthicalWall(participantIds, wallId, userId);

    res.status(200).json({
      success: true,
      data: updatedConflict,
      message: 'Ethical wall established successfully',
    });
  } catch (error) {
    next(error);
  }
});

// ==================== CONFLICT SCREENING & ANALYTICS ====================

/*
 * @route   POST /api/v1/conflicts/screen
 * @desc    Screen for potential conflicts
 * @access  Private (Requires conflict:screen permission)
 * @body    {Array} partyNames - Names to screen against
 * @body    {Array} involvedUsers - User IDs to screen against
 * @body    {String} matterType - Type of matter
 * @returns {Array} Potential conflict matches
 */
router.post('/screen', auth.authorize('conflict', 'screen'), async (req, res, next) => {
  try {
    const { tenantId } = req.tenantContext;
    const { partyNames, involvedUsers, matterType } = req.body;

    if ((!partyNames?.length) && (!involvedUsers?.length)) {
      return res.status(400).json({
        success: false,
        error: 'At least one screening criteria required (partyNames or involvedUsers)',
      });
    }

    const screeningData = { partyNames, involvedUsers };
    const matches = await Conflict.screenForConflicts(tenantId, screeningData);

    // Filter by matter type if provided
    let filteredMatches = matches;
    if (matterType) {
      filteredMatches = matches.filter(
        (conflict) =>
          !conflict.matter?.matterType ||
          conflict.matter.matterType === matterType
      );
    }

    const message = filteredMatches.length > 0
      ? 'Potential conflicts found'
      : 'No potential conflicts detected';

    res.status(200).json({
      success: true,
      count: filteredMatches.length,
      data: filteredMatches,
      message,
    });
  } catch (error) {
    next(error);
  }
});

/*
 * @route   GET /api/v1/conflicts/stats
 * @desc    Get conflict statistics for tenant
 * @access  Private (Requires conflict:read permission)
 * @returns {Object} Conflict statistics
 */
router.get('/stats', auth.authorize('conflict', 'read'), async (req, res, next) => {
  try {
    const { tenantId } = req.tenantContext;
    const stats = await Conflict.getTenantStatistics(tenantId);

    res.status(200).json({
      success: true,
      data: stats,
      message: 'Conflict statistics retrieved successfully',
    });
  } catch (error) {
    next(error);
  }
});

/*
 * @route   GET /api/v1/conflicts/search
 * @desc    Search conflicts by various criteria
 * @access  Private (Requires conflict:read permission)
 * @query   {String} q - Search query
 * @query   {String} severity - Filter by severity
 * @query   {String} type - Filter by conflict type
 * @query   {String} status - Filter by status
 * @returns {Array} Matching conflicts
 */
router.get('/search', auth.authorize('conflict', 'read'), async (req, res, next) => {
  try {
    const { tenantId } = req.tenantContext;
    const { q, severity, type, status } = req.query;

    const query = { tenantId };

    // Text search if query provided
    if (q) {
      const searchRegex = new RegExp(q, 'i');
      query.$or = [
        { description: searchRegex },
        { 'parties.primaryParty.name': searchRegex },
        { 'parties.secondaryParty.name': searchRegex },
      ];
    }

    // Apply filters
    if (severity) query.severity = severity;
    if (type) query.conflictType = type;
    if (status) query.status = status;

    const conflicts = await Conflict.find(query)
      .sort({ 'detection.detectionDate': -1 })
      .limit(50)
      .populate('audit.createdBy', 'name email');

    const message = conflicts.length > 0 ? 'Conflicts found' : 'No conflicts match criteria';

    res.status(200).json({
      success: true,
      count: conflicts.length,
      data: conflicts,
      message,
    });
  } catch (error) {
    next(error);
  }
});

// ==================== COMPLIANCE ENDPOINTS ====================

/*
 * @route   GET /api/v1/conflicts/:id/compliance
 * @desc    Get compliance status for conflict
 * @access  Private (Requires conflict:read permission)
 * @param   {String} id - Conflict ID
 * @returns {Object} Compliance status
 */
router.get('/:id/compliance', auth.authorize('conflict', 'read'), async (req, res, next) => {
  try {
    const { tenantId } = req.tenantContext;
    const conflictId = req.params.id;

    const conflict = await Conflict.findOne({
      _id: conflictId,
      tenantId,
    }).select('compliance audit.metadata');

    if (!conflict) {
      return res.status(404).json({
        success: false,
        error: `Conflict not found with id ${conflictId}`,
      });
    }

    const complianceStatus = {
      popia: {
        compliant: conflict.popiaCompliant || false,
        consentObtained: conflict.compliance?.popia?.dataSubjectConsent?.obtained || false,
        officerNotified: conflict.compliance?.popia?.informationOfficerNotified || false,
      },
      lpc: {
        rule7_1: conflict.compliance?.lpcRules?.rule7_1 || false,
        rule7_2: conflict.compliance?.lpcRules?.rule7_2 || false,
        ethicalClearanceRequired: conflict.compliance?.lpcRules?.ethicalClearanceRequired || false,
      },
      companiesAct: {
        directorDutiesDeclared: conflict.compliance?.companiesAct?.directorDuties?.declarationFiled || false,
        boardApproval: conflict.compliance?.companiesAct?.directorDuties?.boardApproval || false,
      },
    };

    // Calculate overall compliance
    complianceStatus.overallCompliant =
      complianceStatus.popia.compliant &&
      complianceStatus.lpc.rule7_1 &&
      complianceStatus.companiesAct.directorDutiesDeclared;

    res.status(200).json({
      success: true,
      data: complianceStatus,
      message: 'Compliance status retrieved',
    });
  } catch (error) {
    next(error);
  }
});

/*
 * @route   POST /api/v1/conflicts/:id/compliance/popia-consent
 * @desc    Record POPIA consent for conflict
 * @access  Private (Requires conflict:manage permission)
 * @param   {String} id - Conflict ID
 * @body    {Object} consentData - Consent information
 * @returns {Object} Updated compliance status
 */
router.post('/:id/compliance/popia-consent', auth.authorize('conflict', 'manage'), async (req, res, next) => {
  try {
    const { tenantId } = req.tenantContext;
    const userId = req.user.id;
    const conflictId = req.params.id;
    const { consentMethod, consentRecordId } = req.body;

    const conflict = await Conflict.findOne({
      _id: conflictId,
      tenantId,
    });

    if (!conflict) {
      return res.status(404).json({
        success: false,
        error: `Conflict not found with id ${conflictId}`,
      });
    }

    // Initialize compliance object if it doesn't exist
    if (!conflict.compliance) conflict.compliance = {};
    if (!conflict.compliance.popia) conflict.compliance.popia = {};

    conflict.compliance.popia.dataSubjectConsent = {
      obtained: true,
      consentDate: new Date(),
      consentMethod: consentMethod || 'digital',
      consentRecordId: consentRecordId || `CONSENT-${conflict._id}`,
    };

    conflict.audit.updatedBy = userId;
    conflict.audit.updatedAt = new Date();

    const savedConflict = await conflict.save();

    res.status(200).json({
      success: true,
      data: savedConflict.compliance.popia,
      message: 'POPIA consent recorded successfully',
    });
  } catch (error) {
    next(error);
  }
});

// ==================== ERROR HANDLING MIDDLEWARE ====================

/*
 * Global error handler for conflict routes
 * @middleware errorHandler
 */
router.use((error, req, res, next) => {
  console.error(`Conflict API Error: ${error.message}`, {
    tenantId: req.tenantContext?.tenantId,
    userId: req.user?.id,
    endpoint: req.originalUrl,
    stack: error.stack,
  });

  // MongoDB duplicate key error
  if (error.code === 11000) {
    return res.status(409).json({
      success: false,
      error: 'Duplicate conflict detected',
      field: Object.keys(error.keyPattern)[0],
    });
  }

  // Mongoose validation error
  if (error.name === 'ValidationError') {
    return res.status(400).json({
      success: false,
      error: 'Validation failed',
      details: Object.keys(error.errors).map((key) => error.errors[key].message),
    });
  }

  // Custom application errors
  if (error.message?.includes('Invalid severity level')) {
    return res.status(400).json({
      success: false,
      error: error.message,
    });
  }

  // Default error
  res.status(error.statusCode || 500).json({
    success: false,
    error: error.message || 'Server Error',
  });
});

export default router;
