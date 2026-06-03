/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DYNAMIC JURISDICTION ROUTES [V1.0.0-OMEGA]                                                                                  ║
 * ║ [RUNTIME JURISDICTION LOADING | TENANT-TO-COUNTRY RESOLUTION | PAN-AFRICAN DISCOVERY]                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/routes/jurisdictionRoutes.js                                              ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import express from 'express';
import JurisdictionRegistry from '../models/JurisdictionRegistry.js';
import { requireSovereignAuth, enforceMilitaryWhitelist } from '../middleware/auth.middleware.js';

const router = express.Router();

/**
 * @route   GET /api/jurisdictions
 * @desc    Returns all active jurisdictions (country codes, names, primary statutes)
 * @access  Protected — requires valid JWT
 */
router.get('/', requireSovereignAuth, async (req, res) => {
  try {
    const jurisdictions = await JurisdictionRegistry.getActiveCountries();
    res.status(200).json({ success: true, data: jurisdictions, total: jurisdictions.length });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

/**
 * @route   GET /api/jurisdictions/:countryCode
 * @desc    Returns the full jurisdiction profile for a specific country
 * @access  Protected — requires valid JWT
 */
router.get('/:countryCode', requireSovereignAuth, async (req, res) => {
  try {
    const jurisdiction = await JurisdictionRegistry.findOne({
      countryCode: req.params.countryCode.toUpperCase(),
      isActive: true
    }).lean();

    if (!jurisdiction) {
      return res.status(404).json({
        success: false,
        message: `Jurisdiction '${req.params.countryCode.toUpperCase()}' not found in the registry.`
      });
    }

    res.status(200).json({ success: true, data: jurisdiction });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

/**
 * @route   GET /api/jurisdictions/region/:bloc
 * @desc    Returns all jurisdictions within a regional bloc (e.g., 'EAC', 'ECOWAS', 'SADC')
 * @access  Protected — requires valid JWT
 */
router.get('/region/:bloc', requireSovereignAuth, async (req, res) => {
  try {
    const jurisdictions = await JurisdictionRegistry.find({
      regionalBloc: req.params.bloc.toUpperCase(),
      isActive: true
    }).select('countryCode countryName primaryStatute').lean();

    res.status(200).json({ success: true, data: jurisdictions, total: jurisdictions.length });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

/**
 * @route   GET /api/jurisdictions/resolve/:tenantId
 * @desc    Resolves which jurisdiction a tenant belongs to
 * @access  Protected — requires valid JWT
 */
router.get('/resolve/:tenantId', requireSovereignAuth, async (req, res) => {
  try {
    // In production, this queries the tenant profile for their registered country
    // For now, we use a header-based resolution or tenant configuration
    const tenantCountry = req.headers['x-tenant-country'] || 'TZ';
    const jurisdiction = await JurisdictionRegistry.findOne({
      countryCode: tenantCountry.toUpperCase(),
      isActive: true
    }).lean();

    if (!jurisdiction) {
      return res.status(404).json({ success: false, message: 'Jurisdiction not configured for this tenant.' });
    }

    res.status(200).json({ success: true, data: jurisdiction });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

export default router;
