const express = require('express');
const winston = require('winston');
const cors = require('cors');
const app = express();

// --- LOGGER ---
const logger = winston.createLogger({ 
    transports: [new winston.transports.Console({ format: winston.format.simple() })] 
});

app.use(express.json());
app.use(cors());

// --- THE BRAIN: COURT RULES ---
// In a billion-dollar system, these rules are dynamic, not hardcoded in the frontend.
const RULES = {
    'High Court': {
        required: ['title', 'caseNumber', 'plaintiff', 'serviceAddress'],
        regex: {
            caseNumber: /^\d{4}\/\d{4}$/ // Expects format like 2023/1234
        }
    },
    'Magistrate Court': {
        required: ['caseNumber', 'court'],
        regex: {}
    }
};

// --- ENDPOINT: VALIDATE INSTRUCTION ---
app.post('/validate', (req, res) => {
    const { courtType, payload } = req.body;
    logger.info(`🔍 [Standards] Validating for: ${courtType || 'General'}`);

    const ruleSet = RULES[courtType] || RULES['High Court']; // Default to High Court
    const missing = [];

    // 1. Check Required Fields
    ruleSet.required.forEach(field => {
        if (!payload[field]) missing.push(field);
    });

    if (missing.length > 0) {
        logger.warn(`❌ Validation Failed: Missing ${missing.join(', ')}`);
        return res.status(400).json({ valid: false, reason: `Missing fields: ${missing.join(', ')}` });
    }

    // 2. Check Patterns (e.g., Case Number format)
    if (ruleSet.regex.caseNumber && payload.caseNumber) {
        if (!ruleSet.regex.caseNumber.test(payload.caseNumber)) {
             logger.warn(`❌ Validation Failed: Invalid Case Number Format`);
             return res.status(400).json({ valid: false, reason: "Case Number must be format YYYY/NNNN" });
        }
    }

    logger.info('✅ Validation Passed');
    res.json({ valid: true, timestamp: new Date() });
});

// --- HEALTH CHECK ---
app.get('/health', (req, res) => res.json({ status: 'Standards Engine Online' }));

const PORT = 6100;
app.listen(PORT, () => logger.info(`🧠 [Standards Service] Listening on Port ${PORT}`));
