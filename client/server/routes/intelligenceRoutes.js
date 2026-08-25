/**
 * Epitome: Express Router Configuration for Intelligence and Repository Censuses.
 * Collaboration Comments: 
 *   - Architect: Wilsy OS Core Engineering (Wilson Khanyezi)
 *   - Tier: Billion-Dollar Production Grade (v8.0.0-Omega)
 *   - Biblical Worth Billions Reference: "And the Lord answered me: 'Write the vision; make it plain on tablets, so he may run who reads it.'" — Habakkuk 2:2
 */

const express = require('express');
const router = express.Router();
const { getRepositoryCensus } = require('../controllers/intelligenceController');

/**
 * @route   GET /api/v1/intelligence/repository-census
 * @desc    Fetch live repository census and Merkle audit state for Panel 6
 * @access  Private / Executive Sovereign Control Room
 */
router.get('/repository-census', getRepositoryCensus);

module.exports = router;
