/**
 * @file /Users/wilsonkhanyezi/legal-doc-system/server/lib/storage.js
 * @module Storage
 * @description S3-compatible multi-tenant storage adapter with envelope encryption
 * @description Implements per-tenant data isolation with data residency compliance
 * 
 * @requires aws-sdk (AWS SDK v3)
 * @requires crypto for envelope encryption
 * @requires lib/kms for key wrapping
 * @requires dotenv for environment variables
 * 
 * @compliance POPIA §19 - Security measures for personal information
 * @compliance ECT Act §15 - Integrity and authenticity of data messages
 * @compliance Companies Act 2008 §24 - Records retention
 * @compliance GDPR Art.32 - Security of processing
 * @compliance SA Data Residency Laws - Protection of Personal Information Act
 * 
 * @security Envelope encryption with per-tenant keys
 * @security Data residency enforcement with compliance tagging
 * @security Multi-tenant isolation with fail-closed authorization
 * 
 * @multitenant Per-tenant encryption keys and storage prefixes
 * @multitenant Tenant quotas and rate limiting
 * 
 * @author Wilson Khanyezi <wilsy.wk@gmail.com>
 * @copyright Wilsy OS™ - All Rights Reserved
 */

const { S3Client, PutObjectCommand, GetObjectCommand, DeleteObjectCommand,
    HeadObjectCommand, ListObjectsV2Command, CopyObjectCommand,
    CreateMultipartUploadCommand, UploadPartCommand, CompleteMultipartUploadCommand,
    AbortMultipartUploadCommand } = require('@aws-sdk/client-s3');
const { getSignedUrl } = require('@aws-sdk/s3-request-presigner');
const crypto = require('crypto');
const kms = require('./kms');
const path = require('path');
const stream = require('stream');

// Load environment variables
require('dotenv').config();

// Environment variable validation
const REQUIRED_ENV_VARS = [
    'S3_ENDPOINT',
    'S3_REGION',
    'S3_ACCESS_KEY_ID',
    'S3_SECRET_ACCESS_KEY',
    'S3_BUCKET_PREFIX'
];

for (const envVar of REQUIRED_ENV_VARS) {
    if (!process.env[envVar]) {
        throw new Error(`Storage initialization failed: Missing ${envVar} environment variable`);
    }
}

/**
 * @class Storage
 * @description S3-compatible storage adapter with multi-tenant envelope encryption
 */
class Storage {
    /**
     * @constructor
     * @description Initialize storage client with multi-tenant configuration
     * @param {Object} options - Storage configuration options
     */
    constructor(options = {}) {
        this.options = {
            endpoint: process.env.S3_ENDPOINT,
            region: process.env.S3_REGION || 'af-south-1',
            credentials: {
                accessKeyId: process.env.S3_ACCESS_KEY_ID,
                secretAccessKey: process.env.S3_SECRET_ACCESS_KEY
            },
            forcePathStyle: process.env.S3_FORCE_PATH_STYLE === 'true',
            bucketPrefix: process.env.S3_BUCKET_PREFIX || 'wilsy-',
            defaultBucket: process.env.S3_DEFAULT_BUCKET || 'wilsy-legal-documents',
            encryptionAlgorithm: 'aes-256-gcm',
            keyWrappingAlgorithm: 'RSA-OAEP-256',
            maxFileSize: parseInt(process.env.S3_MAX_FILE_SIZE) || 100 * 1024 * 1024, // 100MB default
            defaultExpiry: parseInt(process.env.S3_SIGNED_URL_EXPIRY) || 3600, // 1 hour
            ...options
        };

        // Initialize S3 client
        this.s3Client = new S3Client({
            endpoint: this.options.endpoint,
            region: this.options.region,
            credentials: this.options.credentials,
            forcePathStyle: this.options.forcePathStyle,
            // Security configuration
            requestHandler: {
                // Timeout configuration for legal documents
                requestTimeout: 30000,
                socketTimeout: 30000
            }
        });

        // Tenant-specific bucket cache
        this.tenantBuckets = new Map();

        // Initialize KMS for key wrapping
        this.kms = kms;

        console.log(`Storage initialized with endpoint: ${this.options.endpoint}, region: ${this.options.region}`);
    }

    /**
     * @method getTenantBucket
     * @description Get or create bucket name for tenant with compliance validation
     * @param {string} tenantId - Tenant identifier
     * @param {string} dataResidency - Data residency region
     * @returns {string} Bucket name for tenant
     * @private
     */
    _getTenantBucket(tenantId, dataResidency = 'ZA') {
        const cacheKey = `${tenantId}:${dataResidency}`;

        if (this.tenantBuckets.has(cacheKey)) {
            return this.tenantBuckets.get(cacheKey);
        }

        // Validate tenant ID format
        if (!tenantId || typeof tenantId !== 'string') {
            throw new Error('Invalid tenant ID provided');
        }

        // Map data residency to region-specific bucket naming
        const regionPrefix = this._getRegionPrefix(dataResidency);

        // Generate bucket name with tenant isolation
        const bucketName = `${this.options.bucketPrefix}${regionPrefix}${tenantId.replace(/[^a-z0-9-]/gi, '-').toLowerCase()}`;

        // Cache the bucket name
        this.tenantBuckets.set(cacheKey, bucketName);

        return bucketName;
    }

    /**
     * @method _getRegionPrefix
     * @description Get region prefix for data residency compliance
     * @param {string} dataResidency - Data residency code
     * @returns {string} Region prefix
     * @private
     */
    _getRegionPrefix(dataResidency) {
        const regionMap = {
            'ZA': 'za-',    // South Africa - POPIA compliance
            'EU': 'eu-',    // European Union - GDPR compliance
            'US': 'us-',    // United States
            'AU': 'au-',    // Australia
            'CA': 'ca-',    // Canada
            'UK': 'uk-',    // United Kingdom
            'DEFAULT': 'global-'
        };

        return regionMap[dataResidency] || regionMap.DEFAULT;
    }

    /**
     * @method _generateDataEncryptionKey
     * @description Generate a random data encryption key (DEK) for envelope encryption
     * @returns {Object} DEK with key material and metadata
     * @private
     */
    _generateDataEncryptionKey() {
        const dek = crypto.randomBytes(32); // 256-bit key for AES-256
        const iv = crypto.randomBytes(12);  // 96-bit IV for GCM

        return {
            key: dek,
            iv: iv,
            algorithm: this.options.encryptionAlgorithm,
            keyId: `dek-${Date.now()}-${crypto.randomBytes(8).toString('hex')}`
        };
    }

    /**
     * @method _encryptData
     * @description Encrypt data using envelope encryption pattern
     * @param {Buffer} data - Data to encrypt
     * @param {Object} dek - Data encryption key
     * @returns {Object} Encrypted data with metadata
     * @private
     */
    _encryptData(data, dek) {
        const cipher = crypto.createCipheriv(dek.algorithm, dek.key, dek.iv);

        const encrypted = Buffer.concat([
            cipher.update(data),
            cipher.final()
        ]);

        const authTag = cipher.getAuthTag();

        return {
            encryptedData: encrypted,
            iv: dek.iv,
            authTag: authTag,
            algorithm: dek.algorithm,
            keyId: dek.keyId
        };
    }

    /**
     * @method _decryptData
     * @description Decrypt data using envelope encryption
     * @param {Buffer} encryptedData - Encrypted data
     * @param {Buffer} iv - Initialization vector
     * @param {Buffer} authTag - Authentication tag
     * @param {Buffer} dek - Data encryption key
     * @returns {Buffer} Decrypted data
     * @private
     */
    _decryptData(encryptedData, iv, authTag, dek) {
        const decipher = crypto.createDecipheriv(this.options.encryptionAlgorithm, dek, iv);
        decipher.setAuthTag(authTag);

        return Buffer.concat([
            decipher.update(encryptedData),
            decipher.final()
        ]);
    }

    /**
     * @method _validateFileSize
     * @description Validate file size against tenant quotas and system limits
     * @param {Buffer} data - File data
     * @param {string} tenantId - Tenant identifier
     * @throws {Error} If file size exceeds limits
     * @private
     */
    _validateFileSize(data, tenantId) {
        const fileSize = data.length;

        // Check against system maximum
        if (fileSize > this.options.maxFileSize) {
            throw new Error(`File size ${fileSize} exceeds maximum allowed size of ${this.options.maxFileSize} bytes`);
        }

        // TODO: Check against tenant storage quota
        // This would integrate with a tenant quota service

        return true;
    }

    /**
     * @method _generateStorageKey
     * @description Generate storage key with tenant isolation and versioning
     * @param {string} tenantId - Tenant identifier
     * @param {string} fileId - File identifier
     * @param {string} version - File version
     * @param {Object} metadata - File metadata
     * @returns {string} Storage key
     * @private
     */
    _generateStorageKey(tenantId, fileId, version = 'v1', metadata = {}) {
        // Validate inputs
        if (!tenantId || !fileId) {
            throw new Error('Tenant ID and File ID are required');
        }

        // Sanitize fileId to prevent path traversal
        const sanitizedFileId = fileId.replace(/\.\./g, '').replace(/\//g, '-');

        // Generate timestamp for versioning
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

        // Construct storage key with tenant isolation
        const storageKey = `${tenantId}/${sanitizedFileId}/${version}/${timestamp}`;

        return storageKey;
    }

    /**
     * @method upload
     * @description Upload file with envelope encryption and compliance tagging
     * @param {string} tenantId - Tenant identifier
     * @param {string} fileId - File identifier
     * @param {Buffer} data - File data
     * @param {Object} metadata - File metadata including compliance tags
     * @returns {Promise<Object>} Upload result with encryption metadata
     */
    async upload(tenantId, fileId, data, metadata = {}) {
        try {
            // Fail closed: Validate tenant context
            if (!tenantId) {
                throw new Error('Tenant ID is required for storage operations');
            }

            // Validate file size
            this._validateFileSize(data, tenantId);

            // Generate data encryption key
            const dek = this._generateDataEncryptionKey();

            // Encrypt data
            const encrypted = this._encryptData(data, dek);

            // Wrap DEK with tenant's KEK using KMS
            const wrappedKey = await this.kms.wrapKey(
                tenantId,
                dek.key,
                this.options.keyWrappingAlgorithm
            );

            // Get data residency from metadata or default to SA
            const dataResidency = metadata.dataResidencyCompliance || 'ZA';

            // Get tenant bucket
            const bucketName = this._getTenantBucket(tenantId, dataResidency);

            // Generate storage key
            const storageKey = this._generateStorageKey(tenantId, fileId, metadata.version, metadata);

            // Prepare S3 metadata with compliance tags
            const s3Metadata = {
                'x-amz-meta-tenant-id': tenantId,
                'x-amz-meta-file-id': fileId,
                'x-amz-meta-encryption-algorithm': encrypted.algorithm,
                'x-amz-meta-encryption-key-id': encrypted.keyId,
                'x-amz-meta-data-residency': dataResidency,
                'x-amz-meta-compliance-popia': 'true',
                'x-amz-meta-compliance-ect': 'true',
                'x-amz-meta-retention-policy': metadata.retentionPolicy || 'STANDARD_5_YEARS',
                'x-amz-meta-created-by': metadata.createdBy || 'system',
                'x-amz-meta-original-filename': metadata.originalFilename || fileId,
                'x-amz-meta-content-type': metadata.contentType || 'application/octet-stream',
                'x-amz-meta-sha256-hash': crypto.createHash('sha256').update(data).digest('hex'),
                'x-amz-meta-upload-timestamp': new Date().toISOString()
            };

            // Prepare encryption metadata for storage
            const encryptionMetadata = {
                wrappedKey: wrappedKey.toString('base64'),
                iv: encrypted.iv.toString('base64'),
                authTag: encrypted.authTag.toString('base64'),
                keyId: encrypted.keyId,
                algorithm: encrypted.algorithm,
                keyWrappingAlgorithm: this.options.keyWrappingAlgorithm
            };

            // Store encryption metadata as separate metadata
            s3Metadata['x-amz-meta-encryption-metadata'] = JSON.stringify(encryptionMetadata);

            // Prepare upload parameters
            const uploadParams = {
                Bucket: bucketName,
                Key: storageKey,
                Body: encrypted.encryptedData,
                Metadata: s3Metadata,
                ContentType: metadata.contentType || 'application/octet-stream',
                ContentLength: encrypted.encryptedData.length,
                // Server-side encryption (if supported by S3 provider)
                ServerSideEncryption: 'AES256',
                // Storage class based on retention policy
                StorageClass: this._getStorageClass(metadata.retentionPolicy),
                // Legal hold if required
                LegalHold: metadata.legalHold ? { Status: 'ON' } : undefined,
                // Retention configuration
                ObjectLockMode: metadata.retentionMode || 'COMPLIANCE',
                ObjectLockRetainUntilDate: metadata.retainUntilDate ? new Date(metadata.retainUntilDate) : undefined
            };

            // Upload to S3
            const command = new PutObjectCommand(uploadParams);
            const result = await this.s3Client.send(command);

            // Construct response with storage metadata
            const storageResult = {
                success: true,
                fileId: fileId,
                storageKey: storageKey,
                bucket: bucketName,
                encryptedSize: encrypted.encryptedData.length,
                originalSize: data.length,
                encryptionMetadata: encryptionMetadata,
                compliance: {
                    dataResidency: dataResidency,
                    popiaCompliant: true,
                    ectCompliant: true,
                    retentionPolicy: metadata.retentionPolicy || 'STANDARD_5_YEARS'
                },
                s3Metadata: {
                    etag: result.ETag,
                    versionId: result.VersionId,
                    serverSideEncryption: result.ServerSideEncryption
                },
                uploadedAt: new Date().toISOString()
            };

            return storageResult;

        } catch (error) {
            console.error(`Storage upload failed for tenant ${tenantId}, file ${fileId}:`, error);
            throw new Error(`Upload failed: ${error.message}`);
        }
    }

    /**
     * @method download
     * @description Download file with envelope decryption
     * @param {string} tenantId - Tenant identifier
     * @param {string} storageKey - Storage key or file identifier
     * @returns {Promise<Object>} Download result with decrypted data
     */
    async download(tenantId, storageKey) {
        try {
            // Fail closed: Validate tenant context
            if (!tenantId) {
                throw new Error('Tenant ID is required for storage operations');
            }

            // Extract bucket name from storage key or use default
            const bucketName = this._extractBucketFromStorageKey(storageKey) ||
                this._getTenantBucket(tenantId, 'ZA');

            // Get object metadata first
            const headCommand = new HeadObjectCommand({
                Bucket: bucketName,
                Key: storageKey
            });

            const headResult = await this.s3Client.send(headCommand);

            // Verify tenant isolation
            const objectTenantId = headResult.Metadata?.['x-amz-meta-tenant-id'];
            if (objectTenantId !== tenantId) {
                throw new Error('Tenant isolation violation: Access denied');
            }

            // Check legal hold
            if (headResult.ObjectLockLegalHoldStatus === 'ON') {
                console.warn(`File ${storageKey} is under legal hold for tenant ${tenantId}`);
            }

            // Get encrypted data
            const getCommand = new GetObjectCommand({
                Bucket: bucketName,
                Key: storageKey
            });

            const s3Object = await this.s3Client.send(getCommand);

            // Read stream into buffer
            const chunks = [];
            for await (const chunk of s3Object.Body) {
                chunks.push(chunk);
            }
            const encryptedData = Buffer.concat(chunks);

            // Parse encryption metadata
            const encryptionMetadata = JSON.parse(
                headResult.Metadata?.['x-amz-meta-encryption-metadata'] || '{}'
            );

            if (!encryptionMetadata.wrappedKey || !encryptionMetadata.iv || !encryptionMetadata.authTag) {
                throw new Error('Invalid encryption metadata: Missing required fields');
            }

            // Unwrap DEK using tenant's KEK
            const wrappedKey = Buffer.from(encryptionMetadata.wrappedKey, 'base64');
            const dek = await this.kms.unwrapKey(
                tenantId,
                wrappedKey,
                encryptionMetadata.keyWrappingAlgorithm
            );

            // Decrypt data
            const iv = Buffer.from(encryptionMetadata.iv, 'base64');
            const authTag = Buffer.from(encryptionMetadata.authTag, 'base64');

            const decryptedData = this._decryptData(encryptedData, iv, authTag, dek);

            // Verify SHA-256 hash if available
            const expectedHash = headResult.Metadata?.['x-amz-meta-sha256-hash'];
            if (expectedHash) {
                const actualHash = crypto.createHash('sha256').update(decryptedData).digest('hex');
                if (actualHash !== expectedHash) {
                    throw new Error('Data integrity check failed: Hash mismatch');
                }
            }

            // Construct response
            const downloadResult = {
                success: true,
                data: decryptedData,
                metadata: {
                    contentType: s3Object.ContentType,
                    contentLength: decryptedData.length,
                    originalSize: headResult.ContentLength,
                    lastModified: s3Object.LastModified,
                    etag: s3Object.ETag,
                    storageClass: s3Object.StorageClass,
                    compliance: {
                        dataResidency: headResult.Metadata?.['x-amz-meta-data-residency'],
                        retentionPolicy: headResult.Metadata?.['x-amz-meta-retention-policy'],
                        legalHold: headResult.ObjectLockLegalHoldStatus === 'ON'
                    },
                    userMetadata: headResult.Metadata
                }
            };

            return downloadResult;

        } catch (error) {
            console.error(`Storage download failed for tenant ${tenantId}, key ${storageKey}:`, error);
            throw new Error(`Download failed: ${error.message}`);
        }
    }

    /**
     * @method delete
     * @description Delete file with compliance validation
     * @param {string} tenantId - Tenant identifier
     * @param {string} storageKey - Storage key
     * @param {boolean} force - Force delete even with legal hold (admin only)
     * @returns {Promise<Object>} Delete result
     */
    async delete(tenantId, storageKey, force = false) {
        try {
            // Fail closed: Validate tenant context
            if (!tenantId) {
                throw new Error('Tenant ID is required for storage operations');
            }

            // Extract bucket name
            const bucketName = this._extractBucketFromStorageKey(storageKey) ||
                this._getTenantBucket(tenantId, 'ZA');

            // Check if file exists and get metadata
            const headCommand = new HeadObjectCommand({
                Bucket: bucketName,
                Key: storageKey
            });

            const headResult = await this.s3Client.send(headCommand);

            // Verify tenant isolation
            const objectTenantId = headResult.Metadata?.['x-amz-meta-tenant-id'];
            if (objectTenantId !== tenantId) {
                throw new Error('Tenant isolation violation: Access denied');
            }

            // Check legal hold
            if (headResult.ObjectLockLegalHoldStatus === 'ON' && !force) {
                throw new Error('Cannot delete file under legal hold. Use force=true with proper authorization.');
            }

            // Check retention policy
            const retentionPolicy = headResult.Metadata?.['x-amz-meta-retention-policy'];
            const retentionEnd = headResult.ObjectLockRetainUntilDate;

            if (retentionEnd && new Date() < retentionEnd && !force) {
                throw new Error(`Cannot delete file before retention period ends: ${retentionEnd}`);
            }

            // Delete the object
            const deleteCommand = new DeleteObjectCommand({
                Bucket: bucketName,
                Key: storageKey
            });

            const result = await this.s3Client.send(deleteCommand);

            // Log deletion for audit trail
            console.log(`File deleted: ${storageKey} for tenant ${tenantId}`);

            return {
                success: true,
                deletedKey: storageKey,
                bucket: bucketName,
                tenantId: tenantId,
                deletedAt: new Date().toISOString(),
                compliance: {
                    legalHoldRespected: headResult.ObjectLockLegalHoldStatus === 'ON' && !force,
                    retentionPolicy: retentionPolicy,
                    retentionEnd: retentionEnd
                }
            };

        } catch (error) {
            // Handle 404 Not Found gracefully
            if (error.name === 'NotFound' || error.code === 'NoSuchKey') {
                return {
                    success: false,
                    error: 'File not found',
                    deletedKey: storageKey,
                    tenantId: tenantId
                };
            }

            console.error(`Storage delete failed for tenant ${tenantId}, key ${storageKey}:`, error);
            throw new Error(`Delete failed: ${error.message}`);
        }
    }

    /**
     * @method list
     * @description List files for tenant with pagination and filtering
     * @param {string} tenantId - Tenant identifier
     * @param {Object} options - List options
     * @returns {Promise<Object>} List result with pagination
     */
    async list(tenantId, options = {}) {
        try {
            // Fail closed: Validate tenant context
            if (!tenantId) {
                throw new Error('Tenant ID is required for storage operations');
            }

            const {
                prefix = '',
                delimiter = '/',
                maxKeys = 100,
                continuationToken,
                dataResidency = 'ZA'
            } = options;

            // Get tenant bucket
            const bucketName = this._getTenantBucket(tenantId, dataResidency);

            // List objects
            const listCommand = new ListObjectsV2Command({
                Bucket: bucketName,
                Prefix: `${tenantId}/${prefix}`,
                Delimiter: delimiter,
                MaxKeys: maxKeys,
                ContinuationToken: continuationToken
            });

            const result = await this.s3Client.send(listCommand);

            // Process results
            const files = [];
            const prefixes = [];

            if (result.Contents) {
                for (const item of result.Contents) {
                    // Skip the directory marker
                    if (item.Key.endsWith('/')) continue;

                    files.push({
                        key: item.Key,
                        size: item.Size,
                        lastModified: item.LastModified,
                        etag: item.ETag,
                        storageClass: item.StorageClass,
                        tenantId: tenantId
                    });
                }
            }

            if (result.CommonPrefixes) {
                for (const prefixObj of result.CommonPrefixes) {
                    prefixes.push(prefixObj.Prefix);
                }
            }

            return {
                success: true,
                files: files,
                prefixes: prefixes,
                pagination: {
                    isTruncated: result.IsTruncated,
                    continuationToken: result.NextContinuationToken,
                    keyCount: result.KeyCount,
                    maxKeys: maxKeys
                },
                bucket: bucketName,
                tenantId: tenantId
            };

        } catch (error) {
            console.error(`Storage list failed for tenant ${tenantId}:`, error);
            throw new Error(`List failed: ${error.message}`);
        }
    }

    /**
     * @method generateSignedUrl
     * @description Generate pre-signed URL for secure file access
     * @param {string} tenantId - Tenant identifier
     * @param {string} storageKey - Storage key
     * @param {string} operation - Operation (getObject, putObject)
     * @param {Object} options - URL options
     * @returns {Promise<string>} Signed URL
     */
    async generateSignedUrl(tenantId, storageKey, operation = 'getObject', options = {}) {
        try {
            // Fail closed: Validate tenant context
            if (!tenantId) {
                throw new Error('Tenant ID is required for storage operations');
            }

            const {
                expiresIn = this.options.defaultExpiry,
                responseContentDisposition,
                responseContentType,
                dataResidency = 'ZA'
            } = options;

            // Validate operation
            const validOperations = ['getObject', 'putObject', 'deleteObject'];
            if (!validOperations.includes(operation)) {
                throw new Error(`Invalid operation: ${operation}. Must be one of: ${validOperations.join(', ')}`);
            }

            // Get tenant bucket
            const bucketName = this._extractBucketFromStorageKey(storageKey) ||
                this._getTenantBucket(tenantId, dataResidency);

            // Create command based on operation
            let command;
            switch (operation) {
                case 'getObject':
                    command = new GetObjectCommand({
                        Bucket: bucketName,
                        Key: storageKey,
                        ResponseContentDisposition: responseContentDisposition,
                        ResponseContentType: responseContentType
                    });
                    break;

                case 'putObject':
                    command = new PutObjectCommand({
                        Bucket: bucketName,
                        Key: storageKey
                    });
                    break;

                case 'deleteObject':
                    command = new DeleteObjectCommand({
                        Bucket: bucketName,
                        Key: storageKey
                    });
                    break;

                default:
                    throw new Error(`Unsupported operation: ${operation}`);
            }

            // Generate signed URL
            const signedUrl = await getSignedUrl(this.s3Client, command, {
                expiresIn: expiresIn
            });

            return signedUrl;

        } catch (error) {
            console.error(`Generate signed URL failed for tenant ${tenantId}, key ${storageKey}:`, error);
            throw new Error(`Generate signed URL failed: ${error.message}`);
        }
    }

    /**
     * @method getMetadata
     * @description Get file metadata without downloading content
     * @param {string} tenantId - Tenant identifier
     * @param {string} storageKey - Storage key
     * @returns {Promise<Object>} File metadata
     */
    async getMetadata(tenantId, storageKey) {
        try {
            // Fail closed: Validate tenant context
            if (!tenantId) {
                throw new Error('Tenant ID is required for storage operations');
            }

            // Extract bucket name
            const bucketName = this._extractBucketFromStorageKey(storageKey) ||
                this._getTenantBucket(tenantId, 'ZA');

            // Head object to get metadata
            const headCommand = new HeadObjectCommand({
                Bucket: bucketName,
                Key: storageKey
            });

            const result = await this.s3Client.send(headCommand);

            // Verify tenant isolation
            const objectTenantId = result.Metadata?.['x-amz-meta-tenant-id'];
            if (objectTenantId !== tenantId) {
                throw new Error('Tenant isolation violation: Access denied');
            }

            // Parse encryption metadata
            let encryptionMetadata = {};
            try {
                encryptionMetadata = JSON.parse(
                    result.Metadata?.['x-amz-meta-encryption-metadata'] || '{}'
                );
            } catch (e) {
                console.warn('Failed to parse encryption metadata:', e);
            }

            // Construct response
            const metadata = {
                success: true,
                key: storageKey,
                bucket: bucketName,
                tenantId: tenantId,
                size: result.ContentLength,
                contentType: result.ContentType,
                lastModified: result.LastModified,
                etag: result.ETag,
                storageClass: result.StorageClass,
                serverSideEncryption: result.ServerSideEncryption,
                legalHold: result.ObjectLockLegalHoldStatus === 'ON',
                retentionMode: result.ObjectLockMode,
                retainUntilDate: result.ObjectLockRetainUntilDate,
                compliance: {
                    dataResidency: result.Metadata?.['x-amz-meta-data-residency'],
                    popiaCompliant: result.Metadata?.['x-amz-meta-compliance-popia'] === 'true',
                    ectCompliant: result.Metadata?.['x-amz-meta-compliance-ect'] === 'true',
                    retentionPolicy: result.Metadata?.['x-amz-meta-retention-policy']
                },
                encryption: {
                    algorithm: encryptionMetadata.algorithm,
                    keyId: encryptionMetadata.keyId,
                    keyWrappingAlgorithm: encryptionMetadata.keyWrappingAlgorithm
                },
                userMetadata: result.Metadata
            };

            return metadata;

        } catch (error) {
            // Handle 404 Not Found
            if (error.name === 'NotFound' || error.code === 'NoSuchKey') {
                throw new Error('File not found');
            }

            console.error(`Get metadata failed for tenant ${tenantId}, key ${storageKey}:`, error);
            throw new Error(`Get metadata failed: ${error.message}`);
        }
    }

    /**
     * @method _extractBucketFromStorageKey
     * @description Extract bucket name from storage key if it contains bucket info
     * @param {string} storageKey - Storage key
     * @returns {string|null} Bucket name or null
     * @private
     */
    _extractBucketFromStorageKey(storageKey) {
        // Check if storage key contains bucket prefix
        if (storageKey.includes('://')) {
            const urlParts = storageKey.split('/');
            if (urlParts.length > 2) {
                // Format: s3://bucket-name/key
                return urlParts[2];
            }
        }

        return null;
    }

    /**
     * @method _getStorageClass
     * @description Get appropriate storage class based on retention policy
     * @param {string} retentionPolicy - Retention policy
     * @returns {string} Storage class
     * @private
     */
    _getStorageClass(retentionPolicy) {
        const storageClassMap = {
            'STANDARD_5_YEARS': 'STANDARD',
            'EXTENDED_10_YEARS': 'STANDARD_IA', // Infrequent Access
            'PERMANENT': 'GLACIER', // Archive storage
            'PAIA_SPECIAL': 'STANDARD',
            'DEFAULT': 'STANDARD'
        };

        return storageClassMap[retentionPolicy] || storageClassMap.DEFAULT;
    }

    /**
     * @method getTenantStorageUsage
     * @description Get storage usage statistics for tenant
     * @param {string} tenantId - Tenant identifier
     * @param {string} dataResidency - Data residency region
     * @returns {Promise<Object>} Storage usage statistics
     */
    async getTenantStorageUsage(tenantId, dataResidency = 'ZA') {
        try {
            // Fail closed: Validate tenant context
            if (!tenantId) {
                throw new Error('Tenant ID is required for storage operations');
            }

            const bucketName = this._getTenantBucket(tenantId, dataResidency);

            let totalSize = 0;
            let fileCount = 0;
            let continuationToken = null;

            do {
                const listCommand = new ListObjectsV2Command({
                    Bucket: bucketName,
                    Prefix: `${tenantId}/`,
                    ContinuationToken: continuationToken
                });

                const result = await this.s3Client.send(listCommand);

                if (result.Contents) {
                    for (const item of result.Contents) {
                        if (!item.Key.endsWith('/')) { // Skip directory markers
                            totalSize += item.Size;
                            fileCount++;
                        }
                    }
                }

                continuationToken = result.NextContinuationToken;

            } while (continuationToken);

            return {
                success: true,
                tenantId: tenantId,
                bucket: bucketName,
                dataResidency: dataResidency,
                statistics: {
                    totalSize: totalSize,
                    fileCount: fileCount,
                    averageFileSize: fileCount > 0 ? totalSize / fileCount : 0,
                    measuredAt: new Date().toISOString()
                }
            };

        } catch (error) {
            // Handle bucket not found (no storage used yet)
            if (error.name === 'NoSuchBucket') {
                return {
                    success: true,
                    tenantId: tenantId,
                    bucket: null,
                    dataResidency: dataResidency,
                    statistics: {
                        totalSize: 0,
                        fileCount: 0,
                        averageFileSize: 0,
                        measuredAt: new Date().toISOString()
                    }
                };
            }

            console.error(`Get storage usage failed for tenant ${tenantId}:`, error);
            throw new Error(`Get storage usage failed: ${error.message}`);
        }
    }

    /**
     * @method copy
     * @description Copy file within or between buckets with compliance preservation
     * @param {string} sourceTenantId - Source tenant identifier
     * @param {string} sourceKey - Source storage key
     * @param {string} destTenantId - Destination tenant identifier
     * @param {string} destKey - Destination storage key
     * @param {Object} options - Copy options
     * @returns {Promise<Object>} Copy result
     */
    async copy(sourceTenantId, sourceKey, destTenantId, destKey, options = {}) {
        try {
            // Fail closed: Validate tenant context
            if (!sourceTenantId || !destTenantId) {
                throw new Error('Source and destination tenant IDs are required');
            }

            const {
                sourceDataResidency = 'ZA',
                destDataResidency = 'ZA',
                preserveMetadata = true,
                newRetentionPolicy
            } = options;

            // Get source and destination buckets
            const sourceBucket = this._getTenantBucket(sourceTenantId, sourceDataResidency);
            const destBucket = this._getTenantBucket(destTenantId, destDataResidency);

            // Get source metadata
            const sourceMetadata = await this.getMetadata(sourceTenantId, sourceKey);

            // Check legal hold on source
            if (sourceMetadata.legalHold) {
                throw new Error('Cannot copy file under legal hold');
            }

            // Prepare copy parameters
            const copySource = `${sourceBucket}/${sourceKey}`;

            const copyParams = {
                Bucket: destBucket,
                CopySource: copySource,
                Key: destKey,
                MetadataDirective: preserveMetadata ? 'COPY' : 'REPLACE'
            };

            // Update metadata if needed
            if (!preserveMetadata || newRetentionPolicy) {
                const metadata = {
                    ...sourceMetadata.userMetadata,
                    'x-amz-meta-tenant-id': destTenantId,
                    'x-amz-meta-copied-from': copySource,
                    'x-amz-meta-copied-at': new Date().toISOString()
                };

                if (newRetentionPolicy) {
                    metadata['x-amz-meta-retention-policy'] = newRetentionPolicy;
                }

                copyParams.Metadata = metadata;
                copyParams.MetadataDirective = 'REPLACE';
            }

            // Copy the object
            const copyCommand = new CopyObjectCommand(copyParams);
            const result = await this.s3Client.send(copyCommand);

            return {
                success: true,
                source: {
                    tenantId: sourceTenantId,
                    key: sourceKey,
                    bucket: sourceBucket
                },
                destination: {
                    tenantId: destTenantId,
                    key: destKey,
                    bucket: destBucket
                },
                copyResult: {
                    etag: result.CopyObjectResult?.ETag,
                    lastModified: result.CopyObjectResult?.LastModified
                },
                copiedAt: new Date().toISOString()
            };

        } catch (error) {
            console.error(`Copy failed from ${sourceTenantId}:${sourceKey} to ${destTenantId}:${destKey}:`, error);
            throw new Error(`Copy failed: ${error.message}`);
        }
    }
}

// =============================================================================
// EXPORT
// =============================================================================

module.exports = Storage;

// =============================================================================
// MIGRATION NOTES
// =============================================================================
/**
 * @migration v1.0.0
 * - Initial S3-compatible storage adapter with envelope encryption
 * - Multi-tenant isolation with per-tenant buckets/prefixes
 * - Data residency compliance with region-specific storage
 * - POPIA/ECT/Companies Act compliance tagging
 *
 * @backward-compatibility
 * - New storage system doesn't affect existing file systems
 * - Existing files need migration to new envelope encryption format
 * - Migration script required for legacy storage
 *
 * @next-steps
 * 1. Set up S3-compatible storage (MinIO, AWS S3, etc.)
 * 2. Configure environment variables for storage endpoint
 * 3. Set up KMS (Vault Transit) for key wrapping
 * 4. Create migration script for existing files
 * 5. Implement tenant quota management service
 */

// Wilsy Touching Lives.
// Chief Architect: Wilson Khanyezi — wilsy.wk@gmail.com | +27 69 046 5710