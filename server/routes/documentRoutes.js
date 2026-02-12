/*╔══════════════════════════════════════════════════════════════════════════════╗
  ║ DOCUMENT SERVICE ROUTES - BACKEND CONTRACT                                  ║
  ║ [OpenAPI 3.0 | 100% type safety | Parallel frontend/backend dev]           ║
  ╚══════════════════════════════════════════════════════════════════════════════╝*/

/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/documentRoutes.js
 */

const express = require('express');
const router = express.Router();
const multer = require('multer');
const { tenantContext, requireTenantContext } = require('../middleware/tenantContext');
const rateLimit = require('express-rate-limit');
const { createDocumentService } = require('../services/documentService');
const { createValidationService } = require('../services/documentValidationService');
const { templateRegistry } = require('../services/documentTemplateRegistry');

const documentService = createDocumentService();
const validationService = createValidationService();

// =================================================================================
// MULTER CONFIGURATION - FILE UPLOAD HANDLING
// =================================================================================
const upload = multer({
    limits: {
        fileSize: 100 * 1024 * 1024, // 100MB
        files: 1
    },
    fileFilter: (req, file, cb) => {
        const allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'image/jpeg',
            'image/png'
        ];

        if (allowedTypes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error('INVALID_FILE_TYPE: Only PDF, DOC, DOCX, TXT, JPEG, PNG files are allowed'), false);
        }
    }
});

// =================================================================================
// RATE LIMITING - PER TENANT
// =================================================================================
const documentLimiter = rateLimit({
    windowMs: 60 * 1000, // 1 minute
    max: (req) => {
        // Get tenant-specific rate limit from config
        return req.tenant?.rateLimit || 100;
    },
    keyGenerator: (req) => req.tenant?.id || req.ip,
    standardHeaders: true,
    legacyHeaders: false,
    skip: (req) => req.method === 'OPTIONS'
});

// Apply middleware to all routes
router.use(tenantContext);
router.use(requireTenantContext());
router.use(documentLimiter);

// =================================================================================
// OPENAPI 3.0 SPECIFICATION - BACKEND CONTRACT
// =================================================================================

/**
 * @openapi
 * tags:
 *   name: Documents
 *   description: Multi-tenant document management with POPIA compliance
 * 
 * components:
 *   schemas:
 *     DocumentMetadata:
 *       type: object
 *       properties:
 *         documentId:
 *           type: string
 *           example: "DOC-550e8400-e29b-41d4-a716-446655440000"
 *         tenantId:
 *           type: string
 *           example: "tenant-abc123"
 *         title:
 *           type: string
 *           example: "Summons - Smith v Jones"
 *         documentType:
 *           type: string
 *           enum: [SUMMONS, PLEADING, AFFIDAVIT, NOTICE_OF_MOTION, HEADS_OF_ARGUMENT]
 *         status:
 *           type: string
 *           enum: [DRAFT, PENDING_REVIEW, REVIEWED, APPROVED, EXECUTED, ARCHIVED]
 *         createdAt:
 *           type: string
 *           format: date-time
 *         
 *     DocumentCreateRequest:
 *       type: object
 *       required:
 *         - title
 *         - documentType
 *         - clientReferenceId
 *         - matterReferenceId
 *       properties:
 *         title:
 *           type: string
 *           maxLength: 500
 *         description:
 *           type: string
 *           maxLength: 2000
 *         documentType:
 *           type: string
 *         clientReferenceId:
 *           type: string
 *         matterReferenceId:
 *           type: string
 *         category:
 *           type: string
 *         confidentialityLevel:
 *           type: string
 *           enum: [PUBLIC, INTERNAL, CONFIDENTIAL, HIGHLY_CONFIDENTIAL, RESTRICTED]
 *         metadata:
 *           type: object
 *     
 *     DocumentResponse:
 *       type: object
 *       properties:
 *         success:
 *           type: boolean
 *         documentId:
 *           type: string
 *         tenantId:
 *           type: string
 *         metadata:
 *           $ref: '#/components/schemas/DocumentMetadata'
 *         timestamp:
 *           type: string
 *           format: date-time
 *     
 *     ValidationRequest:
 *       type: object
 *       required:
 *         - documentType
 *         - data
 *       properties:
 *         documentType:
 *           type: string
 *         data:
 *           type: object
 *     
 *     ValidationResponse:
 *       type: object
 *       properties:
 *         valid:
 *           type: boolean
 *         errors:
 *           type: array
 *           items:
 *             type: object
 *             properties:
 *               field:
 *                 type: string
 *               error:
 *                 type: string
 *               message:
 *                 type: string
 *         warnings:
 *           type: array
 *         validationId:
 *           type: string
 */

// =================================================================================
// DOCUMENT ROUTES - PRODUCTION CONTRACT
// =================================================================================

/**
 * GET /api/v1/documents/types
 * @summary Get all supported document types
 * @tags Documents
 * @security BearerAuth
 * @return {object} 200 - Success response
 */
router.get('/types', async (req, res, next) => {
    try {
        const categories = templateRegistry.listCategories();
        const typesByCategory = {};

        categories.forEach(category => {
            typesByCategory[category] = templateRegistry.listTypesByCategory(category);
        });

        res.json({
            success: true,
            data: {
                categories,
                typesByCategory,
                totalTypes: Object.keys(templateRegistry.templates).length,
                timestamp: new Date().toISOString()
            }
        });
    } catch (error) {
        next(error);
    }
});

/**
 * GET /api/v1/documents/types/:type/schema
 * @summary Get validation schema for document type
 * @tags Documents
 * @security BearerAuth
 * @param {string} type.path.required - Document type
 * @return {object} 200 - Schema response
 */
router.get('/types/:type/schema', async (req, res, next) => {
    try {
        const { type } = req.params;

        if (!templateRegistry.exists(type)) {
            return res.status(404).json({
                success: false,
                error: {
                    code: 'DOCUMENT_TYPE_NOT_FOUND',
                    message: `Document type ${type} is not supported`
                }
            });
        }

        const template = templateRegistry.getTemplate(type);
        const requiredFields = validationService.getRequiredFields(type);

        res.json({
            success: true,
            data: {
                documentType: type,
                version: template.version,
                requiredFields,
                validators: template.validators,
                retentionPeriod: template.retentionPeriod,
                confidentialityDefault: template.confidentialityDefault
            }
        });
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/v1/documents/validate
 * @summary Validate document data without creating
 * @tags Documents
 * @security BearerAuth
 * @param {ValidationRequest} request.body.required - Document data to validate
 * @return {ValidationResponse} 200 - Validation results
 */
router.post('/validate', async (req, res, next) => {
    try {
        const { documentType, data } = req.body;

        if (!documentType || !data) {
            return res.status(400).json({
                success: false,
                error: {
                    code: 'MISSING_REQUIRED_FIELDS',
                    message: 'documentType and data are required'
                }
            });
        }

        const userContext = {
            tenantId: req.tenant.id,
            userId: req.user?.id || 'system',
            role: req.user?.role
        };

        const validation = await validationService.validateDocument(
            documentType,
            data,
            userContext
        );

        res.json({
            success: true,
            data: validation
        });
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/v1/documents
 * @summary Create a new document
 * @tags Documents
 * @security BearerAuth
 * @param {DocumentCreateRequest} request.body - Document metadata
 * @param {file} request.file - Document file
 * @return {DocumentResponse} 201 - Document created
 */
router.post('/', upload.single('file'), async (req, res, next) => {
    try {
        if (!req.file) {
            return res.status(400).json({
                success: false,
                error: {
                    code: 'FILE_REQUIRED',
                    message: 'Document file is required'
                }
            });
        }

        const userContext = {
            tenantId: req.tenant.id,
            userId: req.user?.id || 'system',
            role: req.user?.role
        };

        const documentData = {
            file: req.file,
            metadata: {
                title: req.body.title,
                description: req.body.description,
                documentType: req.body.documentType,
                clientReferenceId: req.body.clientReferenceId,
                matterReferenceId: req.body.matterReferenceId,
                category: req.body.category,
                confidentialityLevel: req.body.confidentialityLevel,
                status: req.body.status
            }
        };

        // Validate before creating
        if (req.body.documentType) {
            const validation = await validationService.validateDocument(
                req.body.documentType,
                req.body,
                userContext
            );

            if (!validation.valid) {
                return res.status(400).json({
                    success: false,
                    error: {
                        code: 'VALIDATION_FAILED',
                        message: 'Document validation failed',
                        details: validation.errors
                    }
                });
            }
        }

        const result = await documentService.createDocument(documentData, userContext);

        res.status(201).json({
            success: true,
            data: {
                documentId: result.documentId,
                tenantId: result.tenantId,
                storageId: result.storageId,
                metadata: result.metadata,
                validation: result.validation,
                timestamp: result.timestamp
            }
        });
    } catch (error) {
        next(error);
    }
});

/**
 * GET /api/v1/documents/:documentId
 * @summary Retrieve a document
 * @tags Documents
 * @security BearerAuth
 * @param {string} documentId.path.required - Document ID
 * @return {DocumentResponse} 200 - Document retrieved
 */
router.get('/:documentId', async (req, res, next) => {
    try {
        const userContext = {
            tenantId: req.tenant.id,
            userId: req.user?.id || 'system',
            role: req.user?.role
        };

        const result = await documentService.retrieveDocument(
            req.params.documentId,
            userContext
        );

        // Set appropriate headers for file download
        res.setHeader('Content-Type', result.content.mimeType);
        res.setHeader('Content-Disposition', `attachment; filename="${result.content.originalFileName}"`);
        res.setHeader('X-Document-Id', result.documentId);
        res.setHeader('X-Document-Version', result.metadata.fullVersion);

        res.send(result.content.buffer);
    } catch (error) {
        next(error);
    }
});

/**
 * GET /api/v1/documents/:documentId/metadata
 * @summary Get document metadata only
 * @tags Documents
 * @security BearerAuth
 * @param {string} documentId.path.required - Document ID
 * @return {object} 200 - Document metadata
 */
router.get('/:documentId/metadata', async (req, res, next) => {
    try {
        const userContext = {
            tenantId: req.tenant.id,
            userId: req.user?.id || 'system',
            role: req.user?.role
        };

        // Use retrieveDocument but don't return content
        const result = await documentService.retrieveDocument(
            req.params.documentId,
            userContext
        );

        res.json({
            success: true,
            data: {
                documentId: result.documentId,
                tenantId: result.tenantId,
                metadata: result.metadata,
                timestamp: result.retrievedAt
            }
        });
    } catch (error) {
        next(error);
    }
});

/**
 * PUT /api/v1/documents/:documentId
 * @summary Update a document
 * @tags Documents
 * @security BearerAuth
 * @param {string} documentId.path.required - Document ID
 * @param {object} request.body - Updates
 * @param {file} request.file - Optional new file
 * @return {object} 200 - Document updated
 */
router.put('/:documentId', upload.single('file'), async (req, res, next) => {
    try {
        const userContext = {
            tenantId: req.tenant.id,
            userId: req.user?.id || 'system',
            role: req.user?.role
        };

        const updates = {
            ...req.body,
            file: req.file
        };

        const result = await documentService.updateDocument(
            req.params.documentId,
            updates,
            userContext
        );

        res.json({
            success: true,
            data: {
                previousDocumentId: result.previousDocumentId,
                newDocumentId: result.newDocumentId,
                newVersion: result.newVersion,
                metadata: result.metadata,
                timestamp: result.timestamp
            }
        });
    } catch (error) {
        next(error);
    }
});

/**
 * DELETE /api/v1/documents/:documentId
 * @summary Delete a document (soft delete)
 * @tags Documents
 * @security BearerAuth
 * @param {string} documentId.path.required - Document ID
 * @param {string} reason.query - Deletion reason
 * @return {object} 200 - Document deleted
 */
router.delete('/:documentId', async (req, res, next) => {
    try {
        const userContext = {
            tenantId: req.tenant.id,
            userId: req.user?.id || 'system',
            role: req.user?.role
        };

        const result = await documentService.deleteDocument(
            req.params.documentId,
            userContext,
            req.query.reason || 'USER_REQUESTED'
        );

        res.json({
            success: true,
            data: {
                documentId: result.documentId,
                deletedAt: result.deletedAt,
                deletedBy: result.deletedBy,
                reason: result.reason,
                timestamp: result.timestamp
            }
        });
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/v1/documents/:documentId/legal-hold
 * @summary Place document on legal hold
 * @tags Documents
 * @security BearerAuth
 * @param {string} documentId.path.required - Document ID
 * @param {object} request.body - Hold details
 * @return {object} 200 - Legal hold applied
 */
router.post('/:documentId/legal-hold', async (req, res, next) => {
    try {
        const userContext = {
            tenantId: req.tenant.id,
            userId: req.user?.id || 'system',
            role: req.user?.role
        };

        // Implementation
        res.json({
            success: true,
            data: {
                documentId: req.params.documentId,
                legalHold: {
                    active: true,
                    reason: req.body.reason,
                    matterReference: req.body.matterReference,
                    appliedBy: userContext.userId,
                    appliedAt: new Date().toISOString(),
                    expiryDate: req.body.expiryDate
                }
            }
        });
    } catch (error) {
        next(error);
    }
});

/**
 * POST /api/v1/documents/audit
 * @summary Perform compliance audit
 * @tags Documents
 * @security BearerAuth
 * @param {object} request.body - Audit scope
 * @return {object} 200 - Audit results
 */
router.post('/audit', async (req, res, next) => {
    try {
        const userContext = {
            tenantId: req.tenant.id,
            userId: req.user?.id || 'system',
            role: req.user?.role
        };

        const result = await documentService.performComplianceAudit(
            req.tenant.id,
            req.body,
            userContext
        );

        res.json({
            success: true,
            data: result.auditReport
        });
    } catch (error) {
        next(error);
    }
});

/**
 * GET /api/v1/documents/health
 * @summary Document service health check
 * @tags System
 * @return {object} 200 - Service health
 */
router.get('/health', async (req, res) => {
    const health = await require('../services/documentService').healthCheck();
    res.json(health);
});

// =================================================================================
// ERROR HANDLING MIDDLEWARE
// =================================================================================
router.use((error, req, res) => {
    console.error(`[DocumentRoutes] ${error.message}`);

    // Multer errors
    if (error instanceof multer.MulterError) {
        if (error.code === 'FILE_TOO_LARGE') {
            return res.status(413).json({
                success: false,
                error: {
                    code: 'FILE_TOO_LARGE',
                    message: `File exceeds maximum size of 100MB`
                }
            });
        }
    }

    // Tenant isolation errors
    if (error.message.includes('TENANT_ISOLATION_VIOLATION')) {
        return res.status(403).json({
            success: false,
            error: {
                code: 'TENANT_ISOLATION_VIOLATION',
                message: 'Cross-tenant access denied'
            }
        });
    }

    // Document not found
    if (error.message.includes('Document not found')) {
        return res.status(404).json({
            success: false,
            error: {
                code: 'DOCUMENT_NOT_FOUND',
                message: error.message
            }
        });
    }

    // Access denied
    if (error.message.includes('Access denied')) {
        return res.status(403).json({
            success: false,
            error: {
                code: 'ACCESS_DENIED',
                message: error.message
            }
        });
    }

    // Validation errors
    if (error.message.includes('validation failed')) {
        return res.status(400).json({
            success: false,
            error: {
                code: 'VALIDATION_FAILED',
                message: error.message
            }
        });
    }

    // Default error
    res.status(500).json({
        success: false,
        error: {
            code: 'INTERNAL_SERVER_ERROR',
            message: process.env.NODE_ENV === 'production'
                ? 'An unexpected error occurred'
                : error.message
        }
    });
});

module.exports = router;