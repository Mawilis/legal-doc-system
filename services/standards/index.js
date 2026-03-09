/**
 * File: services/standards/index.js
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | Legal Compliance & Validation Engine
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - DYNAMIC RULES: Fetches validation logic from MongoDB.
 * - COMPLIANCE: Ensures documents meet specific Court Rules (High Court vs Magistrate).
 * - STANDARDIZATION: Enforces data formats (Case Numbers, ID Numbers) before processing.
 * -----------------------------------------------------------------------------
 */

'use strict';

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const winston = require('winston');

// --- CONFIGURATION ---
const PORT = process.env.STANDARDS_PORT || 6100;
const MONGO_URI = process.env.MONGO_URI || process.env.MONGODB_URI   POST /validate
 * @desc    Validate a document payload against active court rules
 */
app.post('/validate', async (req, res) => {
    const { courtType, payload } = req.body;
    logger.info(`🔍 [Standards] Validating for: ${courtType || 'Unknown Context'}`);

    try {
        // 1. Fetch Dynamic Rule
        let ruleSet = await Rule.findOne({ courtType });
        if (!ruleSet) {
            // Fallback to strict High Court rules if specific court not found
            ruleSet = await Rule.findOne({ courtType: 'High Court' });
        }

        const missing = [];
        const invalidFormats = [];

        // 2. Check Required Fields
        if (ruleSet && ruleSet.requiredFields) {
            ruleSet.requiredFields.forEach(field => {
                if (!payload[field]) missing.push(field);
            });
        }

        // 3. Check Regex Patterns
        if (ruleSet && ruleSet.regexPatterns) {
            for (const [field, patternStr] of ruleSet.regexPatterns) {
                if (payload[field]) {
                    const regex = new RegExp(patternStr);
                    if (!regex.test(payload[field])) {
                        invalidFormats.push(`${field} (Expected format: ${patternStr})`);
                    }
                }
            }
        }

        // 4. Decision
        if (missing.length > 0 || invalidFormats.length > 0) {
            logger.warn(`❌ Validation Failed: Missing [${missing}], Invalid [${invalidFormats}]`);
            return res.status(400).json({
                valid: false,
                errors: { missing, invalidFormats },
                ruleApplied: ruleSet.courtType
            });
        }

        logger.info('✅ Validation Passed');
        res.json({ valid: true, timestamp: new Date(), ruleApplied: ruleSet.courtType });

    } catch (err) {
        logger.error('Validation Error:', err);
        res.status(500).json({ error: 'Validation Engine Failed' });
    }
});

/**
 * @route   GET /rules
 * @desc    Fetch all active rules (for Frontend forms)
 */
app.get('/rules', async (req, res) => {
    const rules = await Rule.find();
    res.json(rules);
});

// --- ACTIVATION ---
app.listen(PORT, '0.0.0.0', () => {
    logger.info(`🧠 [Standards Service] Compliance Engine Online on Port ${PORT}`);
});


