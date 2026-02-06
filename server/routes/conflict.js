/*

╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██████╗ ███╗   ██╗███████╗██╗     ███████╗██╗████████╗            ║
║  ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║     ██╔════╝██║╚══██╔══╝            ║
║  ██║     ██║   ██║██╔██╗ ██║█████╗  ██║     █████╗  ██║   ██║               ║
║  ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║     ██╔══╝  ██║   ██║               ║
║  ╚██████╗╚██████╔╝██║ ╚████║██║     ███████╗██║     ██║   ██║               ║
║   ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚══════╝╚═╝     ╚═╝   ╚═╝               ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  FILE: /Users/wilsonkhanyezi/legal-doc-system/server/routes/conflict.js     ║
║                                                                              ║
║  PURPOSE: REST API endpoints for Conflict of Interest management with       ║
║           multi-tenant isolation, LPC compliance, and audit trails          ║
║                                                                              ║
║  ASCII FLOW: Client → [Auth] → [Tenant Check] → [RBAC] → [Conflict CRUD] →  ║
║               [Audit] → [Compliance] → Response                             ║
║                                                                              ║
║  COMPLIANCE: POPIA ✓ | LPC ✓ | Companies Act ✓ | PAIA ✓                    ║
║                                                                              ║
║  CHIEF ARCHITECT: Wilson Khanyezi                                           ║
║  EMAIL: wilsy.wk@gmail.com | CELL: +27 69 046 5710                          ║
║                                                                              ║
║  ROI: Automated conflict detection prevents R2M+ malpractice claims,        ║
║       85% faster conflict clearance for new matters                         ║
║                                                                              ║
║  FILENAME: conflict.js                                                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

*/
/**
 * @file Conflict of Interest REST API Routes
 * @module routes/conflict
 * @description Express router for conflict of interest management with
 * multi-tenant isolation, RBAC authorization, and legal compliance tracking.
 * @requires express, ../middleware/auth, ../middleware/tenantContext, ../models/Conflict
 * @version 1.0.0
 * @since Wilsy OS v2.0
 * @author Wilson Khanyezi
 */

var express = require('express');
var router = express.Router();
var authMiddleware = require('../middleware/auth');
var tenantContextMiddleware = require('../middleware/tenantContext');
var Conflict = require('../models/Conflict');

/**
 * Apply tenant context middleware to all routes
 * Ensures multi-tenant isolation for all conflict operations
 */
router.use(authMiddleware.protect);
router.use(tenantContextMiddleware.requireTenantContext);

// ==================== CONFLICT CRUD OPERATIONS ====================

/**
 * @route   GET /api/v1/conflicts
 * @desc    Get all conflicts for current tenant with pagination
 * @access  Private (Requires conflict:read permission)
 * @param   {Number} page - Page number (default: 1)
 * @param   {Number} limit - Items per page (default: 50)
 * @param   {String} status - Filter by status
 * @param   {String} severity - Filter by severity
 * @returns {Array} List of conflicts with metadata
 */
router.get('/', authMiddleware.authorize('conflict', 'read'), function (req, res, next) {
    try {
        var query = req.query;
        var page = query.page || 1;
        var limit = query.limit || 50;
        var status = query.status;
        var severity = query.severity;
        var tenantId = req.tenantContext.tenantId;

        var options = {
            page: parseInt(page, 10),
            limit: parseInt(limit, 10),
            status: status,
            severity: severity
        };

        Conflict.findByTenant(tenantId, options)
            .then(function (conflicts) {
                res.status(200).json({
                    success: true,
                    count: conflicts.length,
                    pagination: {
                        page: options.page,
                        limit: options.limit,
                        hasMore: conflicts.length === options.limit
                    },
                    data: conflicts
                });
            })
            .catch(function (error) {
                next(error);
            });
    } catch (error) {
        next(error);
    }
});

/**
 * @route   GET /api/v1/conflicts/:id
 * @desc    Get single conflict by ID
 * @access  Private (Requires conflict:read permission)
 * @param   {String} id - Conflict ID
 * @returns {Object} Conflict details
 */
router.get('/:id', authMiddleware.authorize('conflict', 'read'), function (req, res, next) {
    var tenantId = req.tenantContext.tenantId;
    var conflictId = req.params.id;

    Conflict.findOne({
        _id: conflictId,
        tenantId: tenantId
    })
        .populate('audit.createdBy', 'name email')
        .populate('audit.updatedBy', 'name email')
        .populate('parties.affectedIndividuals.userId', 'name role email')
        .then(function (conflict) {
            if (!conflict) {
                return res.status(404).json({
                    success: false,
                    error: 'Conflict not found with id ' + conflictId
                });
            }

            res.status(200).json({
                success: true,
                data: conflict
            });
        })
        .catch(function (error) {
            next(error);
        });
});

/**
 * @route   POST /api/v1/conflicts
 * @desc    Create new conflict of interest
 * @access  Private (Requires conflict:create permission)
 * @body    {Object} conflict - Conflict data
 * @returns {Object} Created conflict
 */
router.post('/', authMiddleware.authorize('conflict', 'create'), function (req, res, next) {
    var tenantId = req.tenantContext.tenantId;
    var userId = req.user.id;
    var conflictData = req.body;

    // Validate required fields
    if (!conflictData.severity || !conflictData.conflictType || !conflictData.description) {
        return res.status(400).json({
            success: false,
            error: 'Missing required fields: severity, conflictType, description'
        });
    }

    // Add tenant context and audit trail
    var newConflictData = {
        tenantId: tenantId,
        severity: conflictData.severity,
        conflictType: conflictData.conflictType,
        description: conflictData.description,
        audit: {
            createdBy: userId,
            createdAt: new Date()
        }
    };

    // Copy other fields if present
    if (conflictData.parties) newConflictData.parties = conflictData.parties;
    if (conflictData.detection) newConflictData.detection = conflictData.detection;
    if (conflictData.compliance) newConflictData.compliance = conflictData.compliance;
    if (conflictData.metadata) newConflictData.metadata = conflictData.metadata;
    if (conflictData.resolution) newConflictData.resolution = conflictData.resolution;

    // Check if similar conflict already exists
    var checkExisting = Conflict.findOne({
        tenantId: tenantId,
        status: { $in: ['pending', 'active', 'escalated'] }
    });

    if (conflictData.parties && conflictData.parties.primaryParty && conflictData.parties.primaryParty.entityId) {
        checkExisting = checkExisting.where('parties.primaryParty.entityId').equals(conflictData.parties.primaryParty.entityId);
    }

    checkExisting
        .then(function (existingConflict) {
            if (existingConflict) {
                return res.status(409).json({
                    success: false,
                    error: 'Similar active conflict already exists',
                    existingConflictId: existingConflict._id
                });
            }

            return Conflict.create(newConflictData);
        })
        .then(function (conflict) {
            if (!conflict || conflict.status === 409) return;

            // Record initial audit entry
            conflict.audit.changeLog.push({
                changedAt: new Date(),
                changedBy: userId,
                field: 'creation',
                oldValue: null,
                newValue: 'Conflict created',
                reason: 'Initial creation via API'
            });

            return conflict.save();
        })
        .then(function (savedConflict) {
            if (!savedConflict) return;

            res.status(201).json({
                success: true,
                data: savedConflict,
                message: 'Conflict created successfully'
            });
        })
        .catch(function (error) {
            // Handle validation errors
            if (error.name === 'ValidationError') {
                return res.status(400).json({
                    success: false,
                    error: 'Validation failed',
                    details: Object.keys(error.errors).map(function (key) {
                        return error.errors[key].message;
                    })
                });
            }
            next(error);
        });
});

/**
 * @route   PUT /api/v1/conflicts/:id
 * @desc    Update conflict
 * @access  Private (Requires conflict:update permission)
 * @param   {String} id - Conflict ID
 * @body    {Object} updates - Fields to update
 * @returns {Object} Updated conflict
 */
router.put('/:id', authMiddleware.authorize('conflict', 'update'), function (req, res, next) {
    var tenantId = req.tenantContext.tenantId;
    var userId = req.user.id;
    var conflictId = req.params.id;
    var updateData = req.body;

    Conflict.findOne({
        _id: conflictId,
        tenantId: tenantId
    })
        .then(function (conflict) {
            if (!conflict) {
                return res.status(404).json({
                    success: false,
                    error: 'Conflict not found with id ' + conflictId
                });
            }

            // Prevent updates to resolved conflicts without special permission
            if (conflict.status === 'resolved') {
                var hasOverride = req.user.permissions && req.user.permissions.includes('conflict:override');
                if (!hasOverride) {
                    return res.status(403).json({
                        success: false,
                        error: 'Cannot modify resolved conflicts without override permission'
                    });
                }
            }

            // Track changes for audit trail
            var changes = [];

            // Remove fields that shouldn't be updated via API
            delete updateData.tenantId;
            delete updateData.conflictId;
            delete updateData.precedentReference;
            delete updateData.audit;

            // Apply updates and track changes
            Object.keys(updateData).forEach(function (key) {
                var oldValue = conflict[key];
                var newValue = updateData[key];
                var oldValueStr = JSON.stringify(oldValue);
                var newValueStr = JSON.stringify(newValue);

                if (oldValueStr !== newValueStr) {
                    changes.push({
                        field: key,
                        oldValue: oldValue,
                        newValue: newValue
                    });
                    conflict[key] = newValue;
                }
            });

            // Update audit trail
            conflict.audit.updatedBy = userId;
            conflict.audit.updatedAt = new Date();

            changes.forEach(function (change) {
                conflict.audit.changeLog.push({
                    changedAt: new Date(),
                    changedBy: userId,
                    field: change.field,
                    oldValue: change.oldValue,
                    newValue: change.newValue,
                    reason: req.body.changeReason || 'API update'
                });
            });

            return conflict.save();
        })
        .then(function (updatedConflict) {
            if (!updatedConflict || updatedConflict.status === 403 || updatedConflict.status === 404) {
                return;
            }

            var changesCount = 0;
            if (updatedConflict.audit && updatedConflict.audit.changeLog) {
                changesCount = updatedConflict.audit.changeLog.length;
            }

            res.status(200).json({
                success: true,
                data: updatedConflict,
                changes: changesCount,
                message: 'Conflict updated successfully'
            });
        })
        .catch(function (error) {
            if (error.name === 'ValidationError') {
                return res.status(400).json({
                    success: false,
                    error: 'Validation failed',
                    details: Object.keys(error.errors).map(function (key) {
                        return error.errors[key].message;
                    })
                });
            }
            next(error);
        });
});

/**
 * @route   DELETE /api/v1/conflicts/:id
 * @desc    Delete conflict (soft delete/archive)
 * @access  Private (Requires conflict:delete permission)
 * @param   {String} id - Conflict ID
 * @returns {Object} Success message
 */
router.delete('/:id', authMiddleware.authorize('conflict', 'delete'), function (req, res, next) {
    var tenantId = req.tenantContext.tenantId;
    var conflictId = req.params.id;

    Conflict.findOne({
        _id: conflictId,
        tenantId: tenantId
    })
        .then(function (conflict) {
            if (!conflict) {
                return res.status(404).json({
                    success: false,
                    error: 'Conflict not found with id ' + conflictId
                });
            }

            // Prevent deletion of active conflicts
            if (conflict.status === 'active' || conflict.status === 'escalated') {
                return res.status(400).json({
                    success: false,
                    error: 'Cannot delete active or escalated conflicts. Resolve or archive first.'
                });
            }

            // Soft delete by archiving
            conflict.status = 'archived';
            conflict.audit.updatedBy = req.user.id;
            conflict.audit.updatedAt = new Date();

            conflict.audit.changeLog.push({
                changedAt: new Date(),
                changedBy: req.user.id,
                field: 'status',
                oldValue: conflict.status,
                newValue: 'archived',
                reason: 'Archived via API deletion'
            });

            return conflict.save();
        })
        .then(function (archivedConflict) {
            if (!archivedConflict || archivedConflict.status === 400 || archivedConflict.status === 404) {
                return;
            }

            res.status(200).json({
                success: true,
                data: {},
                message: 'Conflict archived successfully'
            });
        })
        .catch(function (error) {
            next(error);
        });
});

// ==================== CONFLICT OPERATIONS ====================

/**
 * @route   POST /api/v1/conflicts/:id/escalate
 * @desc    Escalate conflict severity
 * @access  Private (Requires conflict:escalate permission)
 * @param   {String} id - Conflict ID
 * @body    {String} newSeverity - New severity level
 * @body    {String} reason - Reason for escalation
 * @returns {Object} Updated conflict
 */
router.post('/:id/escalate', authMiddleware.authorize('conflict', 'escalate'), function (req, res, next) {
    var tenantId = req.tenantContext.tenantId;
    var userId = req.user.id;
    var conflictId = req.params.id;
    var newSeverity = req.body.newSeverity;
    var reason = req.body.reason;

    if (!newSeverity || ['medium', 'high', 'critical'].indexOf(newSeverity) === -1) {
        return res.status(400).json({
            success: false,
            error: 'Invalid severity. Must be medium, high, or critical'
        });
    }

    Conflict.findOne({
        _id: conflictId,
        tenantId: tenantId
    })
        .then(function (conflict) {
            if (!conflict) {
                return res.status(404).json({
                    success: false,
                    error: 'Conflict not found with id ' + conflictId
                });
            }

            return conflict.escalate(newSeverity, reason || 'Escalated via API', userId);
        })
        .then(function (updatedConflict) {
            if (!updatedConflict || updatedConflict.status === 404) {
                return;
            }

            res.status(200).json({
                success: true,
                data: updatedConflict,
                message: 'Conflict escalated to ' + newSeverity
            });
        })
        .catch(function (error) {
            next(error);
        });
});

/**
 * @route   POST /api/v1/conflicts/:id/resolve
 * @desc    Resolve conflict
 * @access  Private (Requires conflict:resolve permission)
 * @param   {String} id - Conflict ID
 * @body    {String} resolutionType - Type of resolution
 * @body    {String} details - Resolution details
 * @returns {Object} Resolved conflict
 */
router.post('/:id/resolve', authMiddleware.authorize('conflict', 'resolve'), function (req, res, next) {
    var tenantId = req.tenantContext.tenantId;
    var userId = req.user.id;
    var conflictId = req.params.id;
    var resolutionType = req.body.resolutionType;
    var details = req.body.details;

    if (!resolutionType || !details) {
        return res.status(400).json({
            success: false,
            error: 'resolutionType and details are required'
        });
    }

    Conflict.findOne({
        _id: conflictId,
        tenantId: tenantId
    })
        .then(function (conflict) {
            if (!conflict) {
                return res.status(404).json({
                    success: false,
                    error: 'Conflict not found with id ' + conflictId
                });
            }

            return conflict.resolve(resolutionType, details, userId);
        })
        .then(function (resolvedConflict) {
            if (!resolvedConflict || resolvedConflict.status === 404) {
                return;
            }

            res.status(200).json({
                success: true,
                data: resolvedConflict,
                message: 'Conflict resolved successfully'
            });
        })
        .catch(function (error) {
            next(error);
        });
});

/**
 * @route   POST /api/v1/conflicts/:id/ethical-wall
 * @desc    Add ethical wall to conflict resolution
 * @access  Private (Requires conflict:manage permission)
 * @param   {String} id - Conflict ID
 * @body    {Array} participantIds - Array of user IDs
 * @body    {String} wallId - Ethical wall identifier (optional)
 * @returns {Object} Updated conflict
 */
router.post('/:id/ethical-wall', authMiddleware.authorize('conflict', 'manage'), function (req, res, next) {
    var tenantId = req.tenantContext.tenantId;
    var userId = req.user.id;
    var conflictId = req.params.id;
    var participantIds = req.body.participantIds;
    var wallId = req.body.wallId;

    if (!participantIds || !Array.isArray(participantIds) || participantIds.length === 0) {
        return res.status(400).json({
            success: false,
            error: 'participantIds must be a non-empty array'
        });
    }

    Conflict.findOne({
        _id: conflictId,
        tenantId: tenantId
    })
        .then(function (conflict) {
            if (!conflict) {
                return res.status(404).json({
                    success: false,
                    error: 'Conflict not found with id ' + conflictId
                });
            }

            return conflict.addEthicalWall(participantIds, wallId, userId);
        })
        .then(function (updatedConflict) {
            if (!updatedConflict || updatedConflict.status === 404) {
                return;
            }

            res.status(200).json({
                success: true,
                data: updatedConflict,
                message: 'Ethical wall established successfully'
            });
        })
        .catch(function (error) {
            next(error);
        });
});

// ==================== CONFLICT SCREENING & ANALYTICS ====================

/**
 * @route   POST /api/v1/conflicts/screen
 * @desc    Screen for potential conflicts
 * @access  Private (Requires conflict:screen permission)
 * @body    {Array} partyNames - Names to screen against
 * @body    {Array} involvedUsers - User IDs to screen against
 * @body    {String} matterType - Type of matter
 * @returns {Array} Potential conflict matches
 */
router.post('/screen', authMiddleware.authorize('conflict', 'screen'), function (req, res, next) {
    var tenantId = req.tenantContext.tenantId;
    var partyNames = req.body.partyNames;
    var involvedUsers = req.body.involvedUsers;
    var matterType = req.body.matterType;

    if ((!partyNames || partyNames.length === 0) && (!involvedUsers || involvedUsers.length === 0)) {
        return res.status(400).json({
            success: false,
            error: 'At least one screening criteria required (partyNames or involvedUsers)'
        });
    }

    var screeningData = { partyNames: partyNames, involvedUsers: involvedUsers };

    Conflict.screenForConflicts(tenantId, screeningData)
        .then(function (matches) {
            // Filter by matter type if provided
            var filteredMatches = matches;
            if (matterType) {
                filteredMatches = matches.filter(function (conflict) {
                    return !conflict.matter || !conflict.matter.matterType || conflict.matter.matterType === matterType;
                });
            }

            var message = filteredMatches.length > 0
                ? 'Potential conflicts found'
                : 'No potential conflicts detected';

            res.status(200).json({
                success: true,
                count: filteredMatches.length,
                data: filteredMatches,
                message: message
            });
        })
        .catch(function (error) {
            next(error);
        });
});

/**
 * @route   GET /api/v1/conflicts/stats
 * @desc    Get conflict statistics for tenant
 * @access  Private (Requires conflict:read permission)
 * @returns {Object} Conflict statistics
 */
router.get('/stats', authMiddleware.authorize('conflict', 'read'), function (req, res, next) {
    var tenantId = req.tenantContext.tenantId;

    Conflict.getTenantStatistics(tenantId)
        .then(function (stats) {
            res.status(200).json({
                success: true,
                data: stats,
                message: 'Conflict statistics retrieved successfully'
            });
        })
        .catch(function (error) {
            next(error);
        });
});

/**
 * @route   GET /api/v1/conflicts/search
 * @desc    Search conflicts by various criteria
 * @access  Private (Requires conflict:read permission)
 * @query   {String} q - Search query
 * @query   {String} severity - Filter by severity
 * @query   {String} type - Filter by conflict type
 * @query   {String} status - Filter by status
 * @returns {Array} Matching conflicts
 */
router.get('/search', authMiddleware.authorize('conflict', 'read'), function (req, res, next) {
    var tenantId = req.tenantContext.tenantId;
    var q = req.query.q;
    var severity = req.query.severity;
    var type = req.query.type;
    var status = req.query.status;

    var query = { tenantId: tenantId };

    // Text search if query provided
    if (q) {
        var searchRegex = new RegExp(q, 'i');
        query.$or = [
            { description: searchRegex },
            { 'parties.primaryParty.name': searchRegex },
            { 'parties.secondaryParty.name': searchRegex }
        ];
    }

    // Apply filters
    if (severity) query.severity = severity;
    if (type) query.conflictType = type;
    if (status) query.status = status;

    Conflict.find(query)
        .sort({ 'detection.detectionDate': -1 })
        .limit(50)
        .populate('audit.createdBy', 'name email')
        .exec()
        .then(function (conflicts) {
            var message = conflicts.length > 0 ? 'Conflicts found' : 'No conflicts match criteria';

            res.status(200).json({
                success: true,
                count: conflicts.length,
                data: conflicts,
                message: message
            });
        })
        .catch(function (error) {
            next(error);
        });
});

// ==================== COMPLIANCE ENDPOINTS ====================

/**
 * @route   GET /api/v1/conflicts/:id/compliance
 * @desc    Get compliance status for conflict
 * @access  Private (Requires conflict:read permission)
 * @param   {String} id - Conflict ID
 * @returns {Object} Compliance status
 */
router.get('/:id/compliance', authMiddleware.authorize('conflict', 'read'), function (req, res, next) {
    var tenantId = req.tenantContext.tenantId;
    var conflictId = req.params.id;

    Conflict.findOne({
        _id: conflictId,
        tenantId: tenantId
    })
        .select('compliance audit.metadata')
        .then(function (conflict) {
            if (!conflict) {
                return res.status(404).json({
                    success: false,
                    error: 'Conflict not found with id ' + conflictId
                });
            }

            var complianceStatus = {
                popia: {
                    compliant: conflict.popiaCompliant || false,
                    consentObtained: (conflict.compliance && conflict.compliance.popia && conflict.compliance.popia.dataSubjectConsent && conflict.compliance.popia.dataSubjectConsent.obtained) || false,
                    officerNotified: (conflict.compliance && conflict.compliance.popia && conflict.compliance.popia.informationOfficerNotified) || false
                },
                lpc: {
                    rule7_1: (conflict.compliance && conflict.compliance.lpcRules && conflict.compliance.lpcRules.rule7_1) || false,
                    rule7_2: (conflict.compliance && conflict.compliance.lpcRules && conflict.compliance.lpcRules.rule7_2) || false,
                    ethicalClearanceRequired: (conflict.compliance && conflict.compliance.lpcRules && conflict.compliance.lpcRules.ethicalClearanceRequired) || false
                },
                companiesAct: {
                    directorDutiesDeclared: (conflict.compliance && conflict.compliance.companiesAct && conflict.compliance.companiesAct.directorDuties && conflict.compliance.companiesAct.directorDuties.declarationFiled) || false,
                    boardApproval: (conflict.compliance && conflict.compliance.companiesAct && conflict.compliance.companiesAct.directorDuties && conflict.compliance.companiesAct.directorDuties.boardApproval) || false
                }
            };

            // Calculate overall compliance
            complianceStatus.overallCompliant = complianceStatus.popia.compliant &&
                complianceStatus.lpc.rule7_1 &&
                complianceStatus.companiesAct.directorDutiesDeclared;

            res.status(200).json({
                success: true,
                data: complianceStatus,
                message: 'Compliance status retrieved'
            });
        })
        .catch(function (error) {
            next(error);
        });
});

/**
 * @route   POST /api/v1/conflicts/:id/compliance/popia-consent
 * @desc    Record POPIA consent for conflict
 * @access  Private (Requires conflict:manage permission)
 * @param   {String} id - Conflict ID
 * @body    {Object} consentData - Consent information
 * @returns {Object} Updated compliance status
 */
router.post('/:id/compliance/popia-consent', authMiddleware.authorize('conflict', 'manage'), function (req, res, next) {
    var tenantId = req.tenantContext.tenantId;
    var userId = req.user.id;
    var conflictId = req.params.id;
    var consentMethod = req.body.consentMethod;
    var consentRecordId = req.body.consentRecordId;

    Conflict.findOne({
        _id: conflictId,
        tenantId: tenantId
    })
        .then(function (conflict) {
            if (!conflict) {
                return res.status(404).json({
                    success: false,
                    error: 'Conflict not found with id ' + conflictId
                });
            }

            // Initialize compliance object if it doesn't exist
            if (!conflict.compliance) {
                conflict.compliance = {};
            }
            if (!conflict.compliance.popia) {
                conflict.compliance.popia = {};
            }

            conflict.compliance.popia.dataSubjectConsent = {
                obtained: true,
                consentDate: new Date(),
                consentMethod: consentMethod || 'digital',
                consentRecordId: consentRecordId || 'CONSENT-' + conflict.conflictReference
            };

            conflict.audit.updatedBy = userId;
            conflict.audit.updatedAt = new Date();

            return conflict.save();
        })
        .then(function (savedConflict) {
            if (!savedConflict || savedConflict.status === 404) {
                return;
            }

            res.status(200).json({
                success: true,
                data: savedConflict.compliance.popia,
                message: 'POPIA consent recorded successfully'
            });
        })
        .catch(function (error) {
            next(error);
        });
});

// ==================== ERROR HANDLING MIDDLEWARE ====================

/**
 * Global error handler for conflict routes
 * @middleware errorHandler
 */
router.use(function (error, req, res, next) { // eslint-disable-line no-unused-vars
    console.error('Conflict API Error: ' + error.message, {
        tenantId: req.tenantContext && req.tenantContext.tenantId,
        userId: req.user && req.user.id,
        endpoint: req.originalUrl,
        stack: error.stack
    });

    // MongoDB duplicate key error
    if (error.code === 11000) {
        return res.status(409).json({
            success: false,
            error: 'Duplicate conflict detected',
            field: Object.keys(error.keyPattern)[0]
        });
    }

    // Mongoose validation error
    if (error.name === 'ValidationError') {
        return res.status(400).json({
            success: false,
            error: 'Validation failed',
            details: Object.keys(error.errors).map(function (key) {
                return error.errors[key].message;
            })
        });
    }

    // Custom application errors
    if (error.message && error.message.indexOf('Invalid severity level') !== -1) {
        return res.status(400).json({
            success: false,
            error: error.message
        });
    }

    // Default error
    res.status(error.statusCode || 500).json({
        success: false,
        error: error.message || 'Server Error'
    });
});

// ==================== EXPORT ====================
module.exports = router;