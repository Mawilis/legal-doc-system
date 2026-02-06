/**
 * =============================================================================
 * WILSY OS - SOVEREIGN CASE CONTROLLER
 * =============================================================================
 */
const Case = require('../models/Case');

exports.createCase = async (req, res) => {
    try {
        // Enforce Multi-Tenancy from the user's JWT (simulated here)
        const tenantId = req.user.tenantId; 
        
        const newCase = new Case({
            ...req.body,
            tenantId: tenantId,
            createdBy: req.user.id
        });

        await newCase.save();
        res.status(201).json({ success: true, data: newCase });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
};

exports.getTenantCases = async (req, res) => {
    try {
        // Only fetch cases belonging to this user's firm
        const cases = await Case.find({ tenantId: req.user.tenantId });
        res.status(200).json({ success: true, count: cases.length, data: cases });
    } catch (error) {
        res.status(500).json({ success: false, error: 'Quantum Retrieval Error' });
    }
};
