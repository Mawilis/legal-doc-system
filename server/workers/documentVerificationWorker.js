'use strict';
const { EventEmitter } = require('events');
const crypto = require('crypto');
const logger = require('../utils/logger');

class DocumentVerificationWorker extends EventEmitter {
    constructor() {
        super();
        this.queue = [];
        this.processing = new Set();
        this.results = new Map();
        this.maxConcurrent = 3;
        this.retryDelay = 5000;
        this.maxRetries = 3;
        this.workerInterval = null;
        this.isShuttingDown = false;
        
        this._startWorker();
    }

    /**
     * Queue document for scanning
     */
    async queueForScanning(documentId, tenantId) {
        const job = {
            id: `scan_${documentId}_${Date.now()}`,
            documentId,
            tenantId,
            type: 'VIRUS_SCAN',
            status: 'QUEUED',
            attempts: 0,
            maxAttempts: this.maxRetries,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };

        this.queue.push(job);
        logger.info('Document queued for scanning', { documentId, tenantId, jobId: job.id });
        
        this.emit('queued', job);
        return job;
    }

    /**
     * Queue document for OCR
     */
    async queueForOCR(documentId, tenantId, options = {}) {
        const job = {
            id: `ocr_${documentId}_${Date.now()}`,
            documentId,
            tenantId,
            type: 'OCR',
            options,
            status: 'QUEUED',
            attempts: 0,
            maxAttempts: this.maxRetries,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };

        this.queue.push(job);
        logger.info('Document queued for OCR', { documentId, tenantId, jobId: job.id });
        
        this.emit('queued', job);
        return job;
    }

    /**
     * Queue document for fraud detection
     */
    async queueForFraudCheck(documentId, tenantId) {
        const job = {
            id: `fraud_${documentId}_${Date.now()}`,
            documentId,
            tenantId,
            type: 'FRAUD_CHECK',
            status: 'QUEUED',
            attempts: 0,
            maxAttempts: this.maxRetries,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };

        this.queue.push(job);
        logger.info('Document queued for fraud check', { documentId, tenantId, jobId: job.id });
        
        this.emit('queued', job);
        return job;
    }

    /**
     * Get job status
     */
    getJobStatus(jobId) {
        for (const job of this.processing) {
            if (job.id === jobId) {
                return { ...job, status: 'PROCESSING' };
            }
        }

        const queued = this.queue.find(j => j.id === jobId);
        if (queued) {
            return queued;
        }

        const result = this.results.get(jobId);
        if (result) {
            return result;
        }

        return null;
    }

    /**
     * Shutdown worker
     */
    shutdown() {
        this.isShuttingDown = true;
        if (this.workerInterval) {
            clearInterval(this.workerInterval);
            this.workerInterval = null;
        }
        this.queue = [];
        this.processing.clear();
        this.results.clear();
        this.removeAllListeners();
    }

    /**
     * Start worker
     */
    _startWorker() {
        if (this.workerInterval) return;
        
        this.workerInterval = setInterval(() => {
            if (this.isShuttingDown) return;
            this._processQueue();
        }, 1000);

        // Allow Node to exit if this is the only thing running
        this.workerInterval.unref();
    }

    /**
     * Process queue
     */
    async _processQueue() {
        if (this.processing.size >= this.maxConcurrent || this.queue.length === 0) {
            return;
        }

        const available = this.maxConcurrent - this.processing.size;
        const toProcess = this.queue.splice(0, available);

        for (const job of toProcess) {
            this.processing.add(job);
            this._processJob(job).catch(error => {
                logger.error('Job processing failed', { jobId: job.id, error: error.message });
            });
        }
    }

    /**
     * Process individual job
     */
    async _processJob(job) {
        if (this.isShuttingDown) return;
        
        job.status = 'PROCESSING';
        job.startedAt = new Date().toISOString();
        
        logger.info('Processing job', { jobId: job.id, type: job.type });

        try {
            let result;

            switch (job.type) {
                case 'VIRUS_SCAN':
                    result = await this._performVirusScan(job);
                    break;
                case 'OCR':
                    result = await this._performOCR(job);
                    break;
                case 'FRAUD_CHECK':
                    result = await this._performFraudCheck(job);
                    break;
                default:
                    throw new Error(`Unknown job type: ${job.type}`);
            }

            job.status = 'COMPLETED';
            job.completedAt = new Date().toISOString();
            job.result = result;

            this.results.set(job.id, { ...job });

            this.emit('completed', job);

            logger.info('Job completed', { 
                jobId: job.id, 
                type: job.type,
                duration: new Date(job.completedAt) - new Date(job.startedAt)
            });

        } catch (error) {
            job.attempts++;
            job.lastError = error.message;

            if (job.attempts < job.maxAttempts && !this.isShuttingDown) {
                job.status = 'RETRY';
                job.retryAt = new Date(Date.now() + this.retryDelay).toISOString();
                
                setTimeout(() => {
                    if (!this.isShuttingDown) {
                        this.processing.delete(job);
                        this.queue.push(job);
                    }
                }, this.retryDelay);

                logger.warn('Job will be retried', { 
                    jobId: job.id, 
                    attempt: job.attempts,
                    error: error.message 
                });
            } else {
                job.status = 'FAILED';
                job.failedAt = new Date().toISOString();
                
                this.results.set(job.id, { ...job });

                this.emit('failed', job);

                logger.error('Job failed permanently', { 
                    jobId: job.id, 
                    attempts: job.attempts,
                    error: error.message 
                });
            }
        } finally {
            this.processing.delete(job);
        }
    }

    /**
     * Perform virus scan
     */
    async _performVirusScan(job) {
        await this._sleep(2000);
        return { scanned: true, clean: true, threats: [] };
    }

    /**
     * Perform OCR
     */
    async _performOCR(job) {
        await this._sleep(3000);
        return { text: 'OCR text', confidence: 0.95 };
    }

    /**
     * Perform fraud check
     */
    async _performFraudCheck(job) {
        await this._sleep(1500);
        return { risk: 'LOW', score: 0.1, flags: [] };
    }

    /**
     * Sleep utility
     */
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

module.exports = new DocumentVerificationWorker();
