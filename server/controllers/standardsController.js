/*
 * File: server/controllers/standardsController.js
 * STATUS: PRODUCTION-READY
 * PURPOSE: Compliance Gateway. Validates legal documents against Court Rules & Jurisdictional Standards.
 * AUTHOR: Wilsy Core Team
 * SECURITY: Internal Service Secret Authentication. Tenant-Scoping.
 */

'use strict';

const axios = require('axios');
const { emitAudit } = require('../middleware/auditMiddleware');

// Configuration
const STANDARDS_SERVICE_URL = process.env.STANDARDS_SERVICE_URL || 'http://127.0.0.1:6100';
const SERVICE_SECRET = process.env.SERVICE_SECRET || 'wilsy_internal_secret';

/**
 * @desc    Validate Document against Court Rules
 * @route   POST /api/standards/validate
 * @access  Lawyer, Admin
 */
exports.validateDocument = async (req, res, next) => {
    try {
        const { documentType, content, jurisdiction } = req.body;

        // 1. Proxy request to Standards Microservice
        const response = await axios.post(`${STANDARDS_SERVICE_URL}/validate`, {
            tenantId: req.user.tenantId,
            documentType,
            content,
            jurisdiction: jurisdiction || 'HIGH_COURT_SA'
        }, {
            headers: { 'x-service-secret': SERVICE_SECRET },
            timeout: 5000
        });

        // 2. Audit the Compliance Check
        await emitAudit(req, {
            resource: 'compliance_engine',
            action: 'VALIDATE_STANDARDS',
            severity: response.data.isValid ? 'INFO' : 'WARN',
            summary: `Document validation performed for ${documentType}`,
            metadata: {
                isValid: response.data.isValid,
                errorCount: response.data.errors?.length || 0
            }
        });

        res.status(200).json({
            status: 'success',
            data: response.data
        });

    } catch (error) {
        if (error.response) {
            // Handle validation failures (400) or service errors (500)
            return res.status(error.response.status).json(error.response.data);
        }

        console.error('❌ [Standards Gateway] Connection Failed:', error.message);
        res.status(503).json({
            status: 'error',
            message: 'Compliance/Standards Service is currently offline.'
        });
    }
};

/**
 * @desc    Fetch Active Legal Rules & Templates
 * @route   GET /api/standards/rules
 * @access  Authenticated User
 */
exports.getRules = async (req, res, next) => {
    try {
        const { category } = req.query;

        const response = await axios.get(`${STANDARDS_SERVICE_URL}/rules`, {
            params: { category },
            headers: { 'x-service-secret': SERVICE_SECRET },
            timeout: 3000
        });

        res.status(200).json({
            status: 'success',
            data: response.data
        });

    } catch (error) {
        res.status(503).json({
            status: 'error',
            message: 'Unable to fetch Court Rules at this time.'
        });
    }
};

/**
 * @desc    Check FICA/KYC Compliance Requirements
 * @route   GET /api/standards/fica-requirements
 * @access  Admin, Compliance Officer
 */
exports.getFicaRequirements = async (req, res, next) => {
    try {
        const { entityType } = req.query; // 'INDIVIDUAL' vs 'COMPANY'

        const response = await axios.get(`${STANDARDS_SERVICE_URL}/requirements/fica`, {
            params: { entityType },
            headers: { 'x-service-secret': SERVICE_SECRET }
        });

        res.status(200).json({
            status: 'success',
            data: response.data
        });
    } catch (error) {
        next(error);
    }
};