/* eslint-disable */
import * as validation from '../utils/validationUtils.js';

/**
 * Wilsy OS Global Validation Middleware
 * Enforces POPIA compliance and data integrity at the edge.
 */
export const validateLegalPayload = (req, res, next) => {
    // 1. Data Integrity Check (SA-Specific)
    const { idNumber, companyReg, citation } = req.body;

    if (idNumber && !validation.validateSAID(idNumber)) {
        return res.status(400).json({
            success: false,
            error: 'VALIDATION_FAILED',
            details: 'The South African ID number provided is mathematically invalid (Luhn failure).'
        });
    }

    if (companyReg && !validation.validateCIPC(companyReg)) {
        return res.status(400).json({
            success: false,
            error: 'VALIDATION_FAILED',
            details: 'Company registration must follow the CIPC format: YYYY/NNNNNN/NN.'
        });
    }

    // 2. POPIA Compliance Check
    // We scan the entire body for PII patterns
    const piiFound = validation.detectPII(JSON.stringify(req.body));

    if (piiFound.length > 0) {
        // Tag the request for the Audit Logger
        req.piiMetadata = {
            detected: piiFound,
            timestamp: new Date().toISOString()
        };

        // Inform the client/frontend that the data is being treated as PII
        res.setHeader('X-Wilsy-Compliance', 'PII_ENCRYPTED');
    }

    next();
};