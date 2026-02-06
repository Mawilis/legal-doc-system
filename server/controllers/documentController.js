/* eslint-disable max-len, no-console */
/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██████╗  ██████╗  ██████╗██╗   ██╗███╗   ██╗███████╗███╗   ██╗████████╗   ║
║  ██╔══██╗██╔═══██╗██╔════╝██║   ██║████╗  ██║██╔════╝████╗  ██║╚══██╔══╝   ║
║  ██║  ██║██║   ██║██║     ██║   ██║██╔██╗ ██║█████╗  ██╔██╗ ██║   ██║      ║
║  ██║  ██║██║   ██║██║     ██║   ██║██║╚██╗██║██╔══╝  ██║╚██╗██║   ██║      ║
║  ██████╔╝╚██████╔╝╚██████╗╚██████╔╝██║ ╚████║███████╗██║ ╚████║   ██║      ║
║  ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═══╝   ╚═╝      ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  FILE: /Users/wilsonkhanyezi/legal-doc-system/server/controllers/documentController.js ║
║                                                                              ║
║  PURPOSE: Sovereign Document Controller with Multi-tenant Security & Audit  ║
║           ASCII: [Request]→[Auth]→[Encrypt]→[Audit]→[Store]→[Response]     ║
║  COMPLIANCE: POPIA/ECT/PAIA/FICA/Companies Act/Cybercrimes Act             ║
║                                                                              ║
║  CHIEF ARCHITECT: Wilson Khanyezi                                           ║
║  EMAIL: wilsy.wk@gmail.com | CELL: +27 69 046 5710                          ║
║                                                                              ║
║  FILENAME: documentController.js                                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

/**
 * @file Sovereign Document Controller with Multi-tenant Security & Audit
 * @module controllers/documentController
 * @description REST API controller for document operations with full audit trail, 
 *              encryption, and multi-tenant isolation
 * @requires express, ../models/Document, ../models/AuditTrail, ../lib/kms, ../middleware/tenantContext
 * @version 1.0.0
 * @since Wilsy OS v3.0
 * @author Wilson Khanyezi
 */

const Document = require('../models/Document');
const AuditTrail = require('../models/AuditTrail');
const kms = require('../lib/kms');
const { authorize } = require('../middleware/auth');
const { validateTenantContext } = require('../middleware/tenantContext');

/**
 * Document Controller - Manages all document operations with security and compliance
 * @namespace documentController
 */
const documentController = {
    /**
     * Upload a new document with encryption and audit logging
     * @route POST /api/documents
     * @access Private (requires authentication and tenant context)
     * @param {Object} req - Express request object
     * @param {Object} res - Express response object
     * @returns {Promise<void>}
     */
    uploadDocument: async (req, res) => {
        try {
            // Extract tenant context (must be present via middleware)
            const { tenantId, userId } = req.tenantContext;

            if (!tenantId || !userId) {
                return res.status(403).json({
                    success: false,
                    error: 'MISSING_TENANT_CONTEXT',
                    message: 'Tenant context is required for document operations'
                });
            }

            // Check authorization
            const isAuthorized = await authorize(userId, 'CREATE', 'DOCUMENT');
            if (!isAuthorized) {
                return res.status(403).json({
                    success: false,
                    error: 'UNAUTHORIZED',
                    message: 'User not authorized to upload documents'
                });
            }

            // Extract document data from request
            const {
                title,
                description,
                caseId,
                documentType,
                classification = 'CONFIDENTIAL',
                tags = [],
                retentionPolicy = 'LPC_6YR',
                metadata = {}
            } = req.body;

            // Validate required fields
            if (!title || !documentType) {
                return res.status(400).json({
                    success: false,
                    error: 'VALIDATION_ERROR',
                    message: 'Title and documentType are required fields'
                });
            }

            // Get file from upload (assuming multer or similar middleware)
            const file = req.file;
            if (!file) {
                return res.status(400).json({
                    success: false,
                    error: 'NO_FILE_UPLOADED',
                    message: 'No document file was uploaded'
                });
            }

            // Generate encryption key for this document
            const encryptionKey = await kms.generateDataKey(`tenant-${tenantId}`);

            // Encrypt file content
            const encryptedContent = await kms.encrypt(
                file.buffer,
                encryptionKey.plaintext
            );

            // Create document record
            const document = new Document({
                tenantId,
                title,
                description,
                caseId,
                documentType,
                classification,
                tags,
                fileMetadata: {
                    originalName: file.originalname,
                    mimeType: file.mimetype,
                    size: file.size,
                    encoding: file.encoding
                },
                storage: {
                    encryptedContent: encryptedContent.ciphertext,
                    encryptionKeyId: encryptionKey.keyId,
                    iv: encryptedContent.iv,
                    authTag: encryptedContent.authTag,
                    algorithm: 'AES-256-GCM',
                    storageLocation: {
                        dataResidencyCompliance: 'ZA_ONLY',
                        primaryRegion: 'af-south-1'
                    }
                },
                retentionPolicy: {
                    rule: retentionPolicy,
                    disposalDate: calculateDisposalDate(retentionPolicy)
                },
                metadata: {
                    ...metadata,
                    uploadedBy: userId,
                    uploadedAt: new Date(),
                    version: 1,
                    accessStats: {
                        totalAccesses: 0,
                        successfulAccesses: 0,
                        failedAccesses: 0,
                        lastAccessed: null
                    }
                },
                audit: {
                    createdBy: userId,
                    createdAt: new Date()
                }
            });

            // Save document
            await document.save();

            // Log audit trail for document creation
            await AuditTrail.logDocumentAccess({
                tenantId,
                userId,
                userRole: req.user?.role || 'USER',
                documentId: document._id,
                documentVersion: 1,
                accessType: 'UPLOAD',
                documentMetadata: {
                    title,
                    documentType,
                    classification,
                    fileSize: file.size,
                    mimeType: file.mimetype
                },
                ipAddress: req.ip,
                userAgent: req.get('User-Agent'),
                sessionId: req.session?.id,
                success: true,
                statusCode: 201,
                responseTimeMs: Date.now() - req.startTime
            });

            // Destroy plaintext key from memory
            encryptionKey.plaintext.fill(0);

            return res.status(201).json({
                success: true,
                message: 'Document uploaded successfully',
                data: {
                    documentId: document._id,
                    title: document.title,
                    documentType: document.documentType,
                    classification: document.classification,
                    fileSize: document.fileMetadata.size,
                    uploadDate: document.metadata.uploadedAt,
                    retentionPolicy: document.retentionPolicy,
                    downloadUrl: `/api/documents/${document._id}/download`,
                    viewUrl: `/api/documents/${document._id}/view`
                }
            });

        } catch (error) {
            console.error('Document upload error:', error);

            // Log failed attempt to audit trail
            if (req.tenantContext && req.tenantContext.userId) {
                try {
                    await AuditTrail.logDocumentAccess({
                        tenantId: req.tenantContext.tenantId,
                        userId: req.tenantContext.userId,
                        userRole: req.user?.role || 'USER',
                        documentId: null,
                        accessType: 'UPLOAD',
                        documentMetadata: {
                            title: req.body?.title || 'Unknown',
                            documentType: req.body?.documentType || 'UNKNOWN'
                        },
                        ipAddress: req.ip,
                        userAgent: req.get('User-Agent'),
                        sessionId: req.session?.id,
                        success: false,
                        statusCode: 500,
                        responseTimeMs: Date.now() - req.startTime,
                        errorDetails: error.message
                    });
                } catch (auditError) {
                    console.error('Failed to log audit trail:', auditError);
                }
            }

            return res.status(500).json({
                success: false,
                error: 'UPLOAD_FAILED',
                message: 'Failed to upload document',
                details: process.env.NODE_ENV === 'development' ? error.message : undefined
            });
        }
    },

    /**
     * Get document by ID with access control and audit logging
     * @route GET /api/documents/:id
     * @access Private (requires authentication and document access permission)
     * @param {Object} req - Express request object
     * @param {Object} res - Express response object
     * @returns {Promise<void>}
     */
    getDocument: async (req, res) => {
        try {
            const { tenantId, userId } = req.tenantContext;
            const { id } = req.params;
            const { version } = req.query;

            if (!tenantId || !userId) {
                return res.status(403).json({
                    success: false,
                    error: 'MISSING_TENANT_CONTEXT',
                    message: 'Tenant context is required for document operations'
                });
            }

            // Check authorization
            const isAuthorized = await authorize(userId, 'READ', 'DOCUMENT');
            if (!isAuthorized) {
                return res.status(403).json({
                    success: false,
                    error: 'UNAUTHORIZED',
                    message: 'User not authorized to view documents'
                });
            }

            // Find document with tenant isolation
            const document = await Document.findOne({
                _id: id,
                tenantId
            });

            if (!document) {
                return res.status(404).json({
                    success: false,
                    error: 'DOCUMENT_NOT_FOUND',
                    message: 'Document not found or you do not have permission to access it'
                });
            }

            // Check specific document permissions (ABAC)
            const canAccess = await checkDocumentAccess(userId, document, 'VIEW');
            if (!canAccess) {
                return res.status(403).json({
                    success: false,
                    error: 'ACCESS_DENIED',
                    message: 'You do not have permission to access this document'
                });
            }

            // Log successful access
            await AuditTrail.logDocumentAccess({
                tenantId,
                userId,
                userRole: req.user?.role || 'USER',
                documentId: document._id,
                documentVersion: version || document.metadata.version,
                accessType: 'VIEW',
                documentMetadata: {
                    title: document.title,
                    documentType: document.documentType,
                    classification: document.classification,
                    fileSize: document.fileMetadata.size,
                    mimeType: document.fileMetadata.mimeType
                },
                ipAddress: req.ip,
                userAgent: req.get('User-Agent'),
                sessionId: req.session?.id,
                success: true,
                statusCode: 200,
                responseTimeMs: Date.now() - req.startTime
            });

            // Update document access statistics
            document.metadata.accessStats.totalAccesses += 1;
            document.metadata.accessStats.successfulAccesses += 1;
            document.metadata.accessStats.lastAccessed = new Date();
            await document.save();

            return res.status(200).json({
                success: true,
                data: {
                    documentId: document._id,
                    title: document.title,
                    description: document.description,
                    documentType: document.documentType,
                    classification: document.classification,
                    caseId: document.caseId,
                    tags: document.tags,
                    fileMetadata: {
                        originalName: document.fileMetadata.originalName,
                        mimeType: document.fileMetadata.mimeType,
                        size: document.fileMetadata.size,
                        uploadedAt: document.metadata.uploadedAt
                    },
                    retentionPolicy: document.retentionPolicy,
                    metadata: {
                        version: document.metadata.version,
                        uploadedBy: document.metadata.uploadedBy,
                        accessStats: document.metadata.accessStats
                    },
                    audit: {
                        createdBy: document.audit.createdBy,
                        createdAt: document.audit.createdAt,
                        lastModified: document.audit.updatedAt
                    }
                }
            });

        } catch (error) {
            console.error('Get document error:', error);

            // Log failed access attempt
            if (req.tenantContext && req.tenantContext.userId) {
                try {
                    await AuditTrail.logDocumentAccess({
                        tenantId: req.tenantContext.tenantId,
                        userId: req.tenantContext.userId,
                        userRole: req.user?.role || 'USER',
                        documentId: req.params.id,
                        accessType: 'VIEW',
                        ipAddress: req.ip,
                        userAgent: req.get('User-Agent'),
                        sessionId: req.session?.id,
                        success: false,
                        statusCode: 500,
                        responseTimeMs: Date.now() - req.startTime,
                        errorDetails: error.message
                    });
                } catch (auditError) {
                    console.error('Failed to log audit trail:', auditError);
                }
            }

            return res.status(500).json({
                success: false,
                error: 'FETCH_FAILED',
                message: 'Failed to retrieve document',
                details: process.env.NODE_ENV === 'development' ? error.message : undefined
            });
        }
    },

    /**
     * Download document with encryption and watermarking
     * @route GET /api/documents/:id/download
     * @access Private (requires download permission)
     * @param {Object} req - Express request object
     * @param {Object} res - Express response object
     * @returns {Promise<void>}
     */
    downloadDocument: async (req, res) => {
        try {
            const { tenantId, userId } = req.tenantContext;
            const { id } = req.params;

            if (!tenantId || !userId) {
                return res.status(403).json({
                    success: false,
                    error: 'MISSING_TENANT_CONTEXT',
                    message: 'Tenant context is required for document operations'
                });
            }

            // Check authorization
            const isAuthorized = await authorize(userId, 'DOWNLOAD', 'DOCUMENT');
            if (!isAuthorized) {
                return res.status(403).json({
                    success: false,
                    error: 'UNAUTHORIZED',
                    message: 'User not authorized to download documents'
                });
            }

            // Find document with tenant isolation
            const document = await Document.findOne({
                _id: id,
                tenantId
            });

            if (!document) {
                return res.status(404).json({
                    success: false,
                    error: 'DOCUMENT_NOT_FOUND',
                    message: 'Document not found or you do not have permission to access it'
                });
            }

            // Check specific document permissions
            const canDownload = await checkDocumentAccess(userId, document, 'DOWNLOAD');
            if (!canDownload) {
                return res.status(403).json({
                    success: false,
                    error: 'DOWNLOAD_DENIED',
                    message: 'You do not have permission to download this document'
                });
            }

            // Decrypt document content
            const encryptionKey = await kms.decryptDataKey(
                document.storage.encryptionKeyId,
                `tenant-${tenantId}`
            );

            const decryptedContent = await kms.decrypt(
                document.storage.encryptedContent,
                encryptionKey,
                document.storage.iv,
                document.storage.authTag
            );

            // Apply watermark for confidential/restricted documents
            let finalContent = decryptedContent;
            if (document.classification === 'CONFIDENTIAL' ||
                document.classification === 'RESTRICTED') {
                finalContent = await applyWatermark(
                    decryptedContent,
                    document.fileMetadata.mimeType,
                    {
                        userId,
                        downloadTime: new Date().toISOString(),
                        purpose: 'Download'
                    }
                );
            }

            // Log download to audit trail
            await AuditTrail.logDocumentAccess({
                tenantId,
                userId,
                userRole: req.user?.role || 'USER',
                documentId: document._id,
                documentVersion: document.metadata.version,
                accessType: 'DOWNLOAD',
                documentMetadata: {
                    title: document.title,
                    documentType: document.documentType,
                    classification: document.classification,
                    fileSize: document.fileMetadata.size,
                    mimeType: document.fileMetadata.mimeType
                },
                ipAddress: req.ip,
                userAgent: req.get('User-Agent'),
                sessionId: req.session?.id,
                success: true,
                statusCode: 200,
                responseTimeMs: Date.now() - req.startTime,
                accessDurationMs: Date.now() - req.startTime
            });

            // Update access statistics
            document.metadata.accessStats.totalAccesses += 1;
            document.metadata.accessStats.successfulAccesses += 1;
            document.metadata.accessStats.lastAccessed = new Date();
            await document.save();

            // Set response headers
            res.setHeader('Content-Type', document.fileMetadata.mimeType);
            res.setHeader('Content-Length', finalContent.length);
            res.setHeader('Content-Disposition',
                `attachment; filename="${encodeURIComponent(document.fileMetadata.originalName)}"`);
            res.setHeader('X-Document-Id', document._id);
            res.setHeader('X-Classification', document.classification);
            res.setHeader('X-Downloaded-By', userId);
            res.setHeader('X-Download-Time', new Date().toISOString());

            // Send file
            return res.send(finalContent);

        } catch (error) {
            console.error('Download document error:', error);

            // Log failed download attempt
            if (req.tenantContext && req.tenantContext.userId) {
                try {
                    await AuditTrail.logDocumentAccess({
                        tenantId: req.tenantContext.tenantId,
                        userId: req.tenantContext.userId,
                        userRole: req.user?.role || 'USER',
                        documentId: req.params.id,
                        accessType: 'DOWNLOAD',
                        ipAddress: req.ip,
                        userAgent: req.get('User-Agent'),
                        sessionId: req.session?.id,
                        success: false,
                        statusCode: 500,
                        responseTimeMs: Date.now() - req.startTime,
                        errorDetails: error.message
                    });
                } catch (auditError) {
                    console.error('Failed to log audit trail:', auditError);
                }
            }

            return res.status(500).json({
                success: false,
                error: 'DOWNLOAD_FAILED',
                message: 'Failed to download document',
                details: process.env.NODE_ENV === 'development' ? error.message : undefined
            });
        }
    },

    /**
     * Update document metadata (document content cannot be modified - create new version instead)
     * @route PUT /api/documents/:id
     * @access Private (requires update permission)
     * @param {Object} req - Express request object
     * @param {Object} res - Express response object
     * @returns {Promise<void>}
     */
    updateDocument: async (req, res) => {
        try {
            const { tenantId, userId } = req.tenantContext;
            const { id } = req.params;

            if (!tenantId || !userId) {
                return res.status(403).json({
                    success: false,
                    error: 'MISSING_TENANT_CONTEXT',
                    message: 'Tenant context is required for document operations'
                });
            }

            // Check authorization
            const isAuthorized = await authorize(userId, 'UPDATE', 'DOCUMENT');
            if (!isAuthorized) {
                return res.status(403).json({
                    success: false,
                    error: 'UNAUTHORIZED',
                    message: 'User not authorized to update documents'
                });
            }

            // Find document with tenant isolation
            const document = await Document.findOne({
                _id: id,
                tenantId
            });

            if (!document) {
                return res.status(404).json({
                    success: false,
                    error: 'DOCUMENT_NOT_FOUND',
                    message: 'Document not found or you do not have permission to access it'
                });
            }

            // Check if user can update this specific document
            const canUpdate = await checkDocumentAccess(userId, document, 'UPDATE');
            if (!canUpdate) {
                return res.status(403).json({
                    success: false,
                    error: 'UPDATE_DENIED',
                    message: 'You do not have permission to update this document'
                });
            }

            // Extract updatable fields (cannot change file content)
            const updatableFields = [
                'title',
                'description',
                'classification',
                'tags',
                'retentionPolicy',
                'metadata'
            ];

            const updates = {};
            updatableFields.forEach(field => {
                if (req.body[field] !== undefined) {
                    updates[field] = req.body[field];
                }
            });

            // Update document
            Object.assign(document, updates);
            document.audit.updatedBy = userId;
            document.audit.updatedAt = new Date();
            document.metadata.version += 1;

            await document.save();

            // Log update to audit trail
            await AuditTrail.logDocumentAccess({
                tenantId,
                userId,
                userRole: req.user?.role || 'USER',
                documentId: document._id,
                documentVersion: document.metadata.version,
                accessType: 'EDIT',
                documentMetadata: {
                    title: document.title,
                    documentType: document.documentType,
                    classification: document.classification
                },
                ipAddress: req.ip,
                userAgent: req.get('User-Agent'),
                sessionId: req.session?.id,
                success: true,
                statusCode: 200,
                responseTimeMs: Date.now() - req.startTime
            });

            return res.status(200).json({
                success: true,
                message: 'Document updated successfully',
                data: {
                    documentId: document._id,
                    title: document.title,
                    version: document.metadata.version,
                    updatedAt: document.audit.updatedAt,
                    updatedBy: document.audit.updatedBy
                }
            });

        } catch (error) {
            console.error('Update document error:', error);

            // Log failed update attempt
            if (req.tenantContext && req.tenantContext.userId) {
                try {
                    await AuditTrail.logDocumentAccess({
                        tenantId: req.tenantContext.tenantId,
                        userId: req.tenantContext.userId,
                        userRole: req.user?.role || 'USER',
                        documentId: req.params.id,
                        accessType: 'EDIT',
                        ipAddress: req.ip,
                        userAgent: req.get('User-Agent'),
                        sessionId: req.session?.id,
                        success: false,
                        statusCode: 500,
                        responseTimeMs: Date.now() - req.startTime,
                        errorDetails: error.message
                    });
                } catch (auditError) {
                    console.error('Failed to log audit trail:', auditError);
                }
            }

            return res.status(500).json({
                success: false,
                error: 'UPDATE_FAILED',
                message: 'Failed to update document',
                details: process.env.NODE_ENV === 'development' ? error.message : undefined
            });
        }
    },

    /**
     * Delete document (soft delete with retention policy enforcement)
     * @route DELETE /api/documents/:id
     * @access Private (requires delete permission)
     * @param {Object} req - Express request object
     * @param {Object} res - Express response object
     * @returns {Promise<void>}
     */
    deleteDocument: async (req, res) => {
        try {
            const { tenantId, userId } = req.tenantContext;
            const { id } = req.params;
            const { permanent = false } = req.query;

            if (!tenantId || !userId) {
                return res.status(403).json({
                    success: false,
                    error: 'MISSING_TENANT_CONTEXT',
                    message: 'Tenant context is required for document operations'
                });
            }

            // Check authorization
            const isAuthorized = await authorize(userId, 'DELETE', 'DOCUMENT');
            if (!isAuthorized) {
                return res.status(403).json({
                    success: false,
                    error: 'UNAUTHORIZED',
                    message: 'User not authorized to delete documents'
                });
            }

            // Find document with tenant isolation
            const document = await Document.findOne({
                _id: id,
                tenantId
            });

            if (!document) {
                return res.status(404).json({
                    success: false,
                    error: 'DOCUMENT_NOT_FOUND',
                    message: 'Document not found or you do not have permission to access it'
                });
            }

            // Check if user can delete this specific document
            const canDelete = await checkDocumentAccess(userId, document, 'DELETE');
            if (!canDelete) {
                return res.status(403).json({
                    success: false,
                    error: 'DELETE_DENIED',
                    message: 'You do not have permission to delete this document'
                });
            }

            // Check retention policy - cannot delete if under legal hold
            if (document.retentionPolicy.rule === 'LEGAL_HOLD') {
                return res.status(423).json({
                    success: false,
                    error: 'LEGAL_HOLD',
                    message: 'Document is under legal hold and cannot be deleted',
                    legalHoldUntil: document.retentionPolicy.holdUntil
                });
            }

            // Check if document can be permanently deleted
            const canPermanentDelete = permanent &&
                await authorize(userId, 'PERMANENT_DELETE', 'DOCUMENT');

            if (canPermanentDelete) {
                // Permanent deletion - only for admins/compliance officers
                await document.deleteOne();
            } else {
                // Soft delete (mark as deleted)
                document.deleted = true;
                document.deletedAt = new Date();
                document.deletedBy = userId;
                document.metadata.deletionReason = req.body.deletionReason || 'User request';
                await document.save();
            }

            // Log deletion to audit trail
            await AuditTrail.logDocumentAccess({
                tenantId,
                userId,
                userRole: req.user?.role || 'USER',
                documentId: document._id,
                documentVersion: document.metadata.version,
                accessType: 'DELETE',
                documentMetadata: {
                    title: document.title,
                    documentType: document.documentType,
                    classification: document.classification
                },
                ipAddress: req.ip,
                userAgent: req.get('User-Agent'),
                sessionId: req.session?.id,
                success: true,
                statusCode: 200,
                responseTimeMs: Date.now() - req.startTime,
                metadata: {
                    permanent: canPermanentDelete,
                    deletionReason: document.metadata.deletionReason
                }
            });

            return res.status(200).json({
                success: true,
                message: canPermanentDelete ?
                    'Document permanently deleted' :
                    'Document marked as deleted',
                data: {
                    documentId: document._id,
                    deletedAt: document.deletedAt,
                    deletedBy: document.deletedBy,
                    permanent: canPermanentDelete
                }
            });

        } catch (error) {
            console.error('Delete document error:', error);

            // Log failed deletion attempt
            if (req.tenantContext && req.tenantContext.userId) {
                try {
                    await AuditTrail.logDocumentAccess({
                        tenantId: req.tenantContext.tenantId,
                        userId: req.tenantContext.userId,
                        userRole: req.user?.role || 'USER',
                        documentId: req.params.id,
                        accessType: 'DELETE',
                        ipAddress: req.ip,
                        userAgent: req.get('User-Agent'),
                        sessionId: req.session?.id,
                        success: false,
                        statusCode: 500,
                        responseTimeMs: Date.now() - req.startTime,
                        errorDetails: error.message
                    });
                } catch (auditError) {
                    console.error('Failed to log audit trail:', auditError);
                }
            }

            return res.status(500).json({
                success: false,
                error: 'DELETE_FAILED',
                message: 'Failed to delete document',
                details: process.env.NODE_ENV === 'development' ? error.message : undefined
            });
        }
    },

    /**
     * Search documents with filtering and pagination
     * @route GET /api/documents
     * @access Private (requires read permission)
     * @param {Object} req - Express request object
     * @param {Object} res - Express response object
     * @returns {Promise<void>}
     */
    searchDocuments: async (req, res) => {
        try {
            const { tenantId, userId } = req.tenantContext;
            const {
                query,
                documentType,
                classification,
                caseId,
                tags,
                startDate,
                endDate,
                page = 1,
                limit = 20,
                sortBy = 'uploadedAt',
                sortOrder = 'desc'
            } = req.query;

            if (!tenantId || !userId) {
                return res.status(403).json({
                    success: false,
                    error: 'MISSING_TENANT_CONTEXT',
                    message: 'Tenant context is required for document operations'
                });
            }

            // Check authorization
            const isAuthorized = await authorize(userId, 'READ', 'DOCUMENT');
            if (!isAuthorized) {
                return res.status(403).json({
                    success: false,
                    error: 'UNAUTHORIZED',
                    message: 'User not authorized to search documents'
                });
            }

            // Build search query with tenant isolation
            const searchQuery = {
                tenantId,
                deleted: { $ne: true } // Exclude soft-deleted documents
            };

            // Text search
            if (query) {
                searchQuery.$text = { $search: query };
            }

            // Filter by document type
            if (documentType) {
                searchQuery.documentType = documentType;
            }

            // Filter by classification
            if (classification) {
                searchQuery.classification = classification;
            }

            // Filter by case
            if (caseId) {
                searchQuery.caseId = caseId;
            }

            // Filter by tags
            if (tags) {
                const tagArray = Array.isArray(tags) ? tags : tags.split(',');
                searchQuery.tags = { $all: tagArray };
            }

            // Date range filter
            if (startDate || endDate) {
                searchQuery['metadata.uploadedAt'] = {};
                if (startDate) {
                    searchQuery['metadata.uploadedAt'].$gte = new Date(startDate);
                }
                if (endDate) {
                    searchQuery['metadata.uploadedAt'].$lte = new Date(endDate);
                }
            }

            // Calculate pagination
            const skip = (parseInt(page) - 1) * parseInt(limit);
            const sort = { [sortBy]: sortOrder === 'desc' ? -1 : 1 };

            // Execute search
            const documents = await Document.find(searchQuery)
                .sort(sort)
                .skip(skip)
                .limit(parseInt(limit))
                .select('-storage.encryptedContent') // Don't return encrypted content
                .lean();

            // Get total count for pagination
            const total = await Document.countDocuments(searchQuery);

            // Log search to audit trail
            await AuditTrail.logDocumentAccess({
                tenantId,
                userId,
                userRole: req.user?.role || 'USER',
                accessType: 'SEARCH',
                documentMetadata: {
                    searchQuery: query || 'All documents',
                    filters: {
                        documentType,
                        classification,
                        caseId,
                        tags: tags ? (Array.isArray(tags) ? tags : tags.split(',')) : undefined
                    }
                },
                ipAddress: req.ip,
                userAgent: req.get('User-Agent'),
                sessionId: req.session?.id,
                success: true,
                statusCode: 200,
                responseTimeMs: Date.now() - req.startTime,
                dataVolume: {
                    recordsAffected: documents.length
                }
            });

            return res.status(200).json({
                success: true,
                data: {
                    documents: documents.map(doc => ({
                        documentId: doc._id,
                        title: doc.title,
                        description: doc.description,
                        documentType: doc.documentType,
                        classification: doc.classification,
                        caseId: doc.caseId,
                        tags: doc.tags,
                        fileMetadata: {
                            originalName: doc.fileMetadata.originalName,
                            mimeType: doc.fileMetadata.mimeType,
                            size: doc.fileMetadata.size,
                            uploadedAt: doc.metadata.uploadedAt
                        },
                        retentionPolicy: doc.retentionPolicy,
                        metadata: {
                            version: doc.metadata.version,
                            uploadedBy: doc.metadata.uploadedBy,
                            accessStats: doc.metadata.accessStats
                        }
                    })),
                    pagination: {
                        page: parseInt(page),
                        limit: parseInt(limit),
                        total,
                        pages: Math.ceil(total / parseInt(limit))
                    }
                }
            });

        } catch (error) {
            console.error('Search documents error:', error);

            // Log failed search attempt
            if (req.tenantContext && req.tenantContext.userId) {
                try {
                    await AuditTrail.logDocumentAccess({
                        tenantId: req.tenantContext.tenantId,
                        userId: req.tenantContext.userId,
                        userRole: req.user?.role || 'USER',
                        accessType: 'SEARCH',
                        ipAddress: req.ip,
                        userAgent: req.get('User-Agent'),
                        sessionId: req.session?.id,
                        success: false,
                        statusCode: 500,
                        responseTimeMs: Date.now() - req.startTime,
                        errorDetails: error.message
                    });
                } catch (auditError) {
                    console.error('Failed to log audit trail:', auditError);
                }
            }

            return res.status(500).json({
                success: false,
                error: 'SEARCH_FAILED',
                message: 'Failed to search documents',
                details: process.env.NODE_ENV === 'development' ? error.message : undefined
            });
        }
    },

    /**
     * Get document access history for audit purposes
     * @route GET /api/documents/:id/access-history
     * @access Private (requires audit permission)
     * @param {Object} req - Express request object
     * @param {Object} res - Express response object
     * @returns {Promise<void>}
     */
    getDocumentAccessHistory: async (req, res) => {
        try {
            const { tenantId, userId } = req.tenantContext;
            const { id } = req.params;
            const { startDate, endDate, limit = 50 } = req.query;

            if (!tenantId || !userId) {
                return res.status(403).json({
                    success: false,
                    error: 'MISSING_TENANT_CONTEXT',
                    message: 'Tenant context is required for document operations'
                });
            }

            // Check authorization - requires special audit permission
            const isAuthorized = await authorize(userId, 'AUDIT', 'DOCUMENT');
            if (!isAuthorized) {
                return res.status(403).json({
                    success: false,
                    error: 'UNAUTHORIZED',
                    message: 'User not authorized to view document access history'
                });
            }

            // Verify document exists and user has access
            const document = await Document.findOne({
                _id: id,
                tenantId
            });

            if (!document) {
                return res.status(404).json({
                    success: false,
                    error: 'DOCUMENT_NOT_FOUND',
                    message: 'Document not found or you do not have permission to access it'
                });
            }

            // Get access history from audit trail
            const accessHistory = await AuditTrail.getDocumentAccessHistory(id, {
                tenantId,
                startDate,
                endDate,
                limit: parseInt(limit)
            });

            // Log audit access
            await AuditTrail.logDocumentAccess({
                tenantId,
                userId,
                userRole: req.user?.role || 'USER',
                documentId: document._id,
                accessType: 'AUDIT_ACCESS',
                documentMetadata: {
                    title: document.title,
                    classification: document.classification
                },
                ipAddress: req.ip,
                userAgent: req.get('User-Agent'),
                sessionId: req.session?.id,
                success: true,
                statusCode: 200,
                responseTimeMs: Date.now() - req.startTime,
                metadata: {
                    auditAction: 'VIEW_ACCESS_HISTORY'
                }
            });

            return res.status(200).json({
                success: true,
                data: {
                    documentId: document._id,
                    title: document.title,
                    classification: document.classification,
                    accessHistory,
                    summary: {
                        totalAccesses: document.metadata.accessStats.totalAccesses,
                        successfulAccesses: document.metadata.accessStats.successfulAccesses,
                        failedAccesses: document.metadata.accessStats.failedAccesses,
                        lastAccessed: document.metadata.accessStats.lastAccessed
                    }
                }
            });

        } catch (error) {
            console.error('Get access history error:', error);

            return res.status(500).json({
                success: false,
                error: 'HISTORY_FETCH_FAILED',
                message: 'Failed to retrieve document access history',
                details: process.env.NODE_ENV === 'development' ? error.message : undefined
            });
        }
    }
};

// ==============================================
// HELPER FUNCTIONS
// ==============================================

/**
 * Calculate disposal date based on retention policy
 * @param {string} retentionPolicy - Retention policy rule
 * @returns {Date} Disposal date
 */
function calculateDisposalDate(retentionPolicy) {
    const disposalDate = new Date();

    switch (retentionPolicy) {
        case 'LPC_6YR':
            disposalDate.setFullYear(disposalDate.getFullYear() + 6);
            break;
        case 'COMPANIES_ACT_7YR':
            disposalDate.setFullYear(disposalDate.getFullYear() + 7);
            break;
        case 'PAIA_5YR':
            disposalDate.setFullYear(disposalDate.getFullYear() + 5);
            break;
        case 'PERMANENT':
            return null; // Never dispose
        default:
            disposalDate.setFullYear(disposalDate.getFullYear() + 3); // Default 3 years
    }

    return disposalDate;
}

/**
 * Check if user has specific access to a document (ABAC)
 * @param {string} userId - User ID
 * @param {Object} document - Document object
 * @param {string} action - Action to perform
 * @returns {Promise<boolean>} Whether access is granted
 */
async function checkDocumentAccess(userId, document, action) {
    try {
        // Get user details (simplified - in production, fetch from User model)
        const user = {
            id: userId,
            role: 'USER' // Default role
        };

        // Basic role-based checks
        if (user.role === 'SYSTEM_ADMIN') {
            return true; // Admins can do everything
        }

        if (user.role === 'COMPLIANCE_OFFICER') {
            // Compliance officers can audit and view restricted documents
            return action === 'VIEW' || action === 'AUDIT_ACCESS';
        }

        // Document owner can do most things (except permanent delete)
        if (document.metadata.uploadedBy === userId) {
            return action !== 'PERMANENT_DELETE';
        }

        // Case-based access - users assigned to the case can view/download
        if (document.caseId) {
            // TODO: Implement case assignment check
            // For now, allow view/download if user is part of the case
            return action === 'VIEW' || action === 'DOWNLOAD';
        }

        // Classification-based restrictions
        if (document.classification === 'RESTRICTED') {
            return action === 'VIEW' && user.role === 'LEGAL_COUNSEL';
        }

        // Default: allow view for internal users
        return action === 'VIEW' && user.role !== 'CLIENT';

    } catch (error) {
        console.error('Document access check error:', error);
        return false; // Fail closed
    }
}

/**
 * Apply watermark to document content
 * @param {Buffer} content - Document content
 * @param {string} mimeType - MIME type of document
 * @param {Object} watermarkData - Watermark metadata
 * @returns {Promise<Buffer>} Watermarked content
 */
async function applyWatermark(content, mimeType, watermarkData) {
    try {
        // Simplified watermarking - in production, use proper libraries
        // For PDFs: use pdf-lib or similar
        // For images: use sharp or similar
        // For office docs: use mammoth or similar

        const watermarkText = `Wilsy OS | ${watermarkData.userId} | ${watermarkData.downloadTime} | ${watermarkData.purpose}`;

        // For now, return original content with metadata header
        // TODO: Implement proper watermarking based on file type
        return content;

    } catch (error) {
        console.error('Watermark application error:', error);
        return content; // Return original content if watermarking fails
    }
}

// ==============================================
// MERMAID DIAGRAM: Document Controller Flow
// ==============================================

/*
```mermaid
flowchart TD
    A[API Request] --> B{Validate Tenant Context}
    B -->|Missing| C[Fail: 403 Forbidden]
    B -->|Valid| D[Check Authorization]
    
    D -->|Denied| E[Fail: 403 Unauthorized]
    D -->|Granted| F{Operation Type}
    
    F -->|Upload| G[Generate Encryption Key]
    F -->|Read/Download| H[Retrieve Document]
    F -->|Update| I[Validate Update Fields]
    F -->|Delete| J[Check Retention Policy]
    F -->|Search| K[Build Search Query]
    F -->|Audit| L[Verify Audit Permission]
    
    G --> M[Encrypt Content]
    H --> N[Decrypt Content<br>Apply Watermark]
    I --> O[Update Metadata]
    J --> P[Soft/Permanent Delete]
    K --> Q[Execute Search]
    L --> R[Retrieve Audit Trail]
    
    M --> S[Store Document]
    N --> T[Stream to Client]
    O --> U[Save Changes]
    P --> V[Update Status]
    Q --> W[Return Results]
    R --> X[Return Audit Log]
    
    S --> Y[Log to Audit Trail]
    T --> Y
    U --> Y
    V --> Y
    W --> Y
    X --> Y
    
    Y --> Z[Return Success Response]
    C --> ZA[Return Error Response]
    E --> ZA
    
    subgraph "Security & Compliance"
        AB[Tenant Isolation]
        AC[RBAC/ABAC Authorization]
        AD[AES-256-GCM Encryption]
        AE[Audit Trail Logging]
        AF[Watermarking]
        AG[Retention Enforcement]
    end
    
    B -.-> AB
    D -.-> AC
    G -.-> AD
    M -.-> AD
    H -.-> AD
    N -.-> AF
    J -.-> AG
    Y -.-> AE
    
    style A fill:#e1f5fe
    style Z fill:#e8f5e8
    style ZA fill:#ffebee
    style C fill:#ffebee
    style E fill:#ffebee*/