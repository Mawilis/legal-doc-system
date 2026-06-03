/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN GEOGRAPHIC BLOCKING MIDDLEWARE                      ║
 * ║ [IP GEOLOCATION | REGIONAL RESTRICTIONS | COMPLIANCE ENFORCEMENT]        ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | INSTITUTIONAL GRADE                   ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 *
 * @team Collaboration Notes:
 * - Enforces geographic access restrictions based on IP location
 * - Supports allowlists and blocklists by country/region
 * - Integrates with MaxMind GeoIP2 database
 * - Compliance with POPIA, GDPR, and other regional regulations
 * - 101/10 security standard
 *
 * @last_updated: 2026-03-18
 * @lead_architect: Wilson Khanyezi
 */

import geoip from 'geoip-lite';
import crypto from 'crypto';

// ============================================================================
// CONFIGURATION
// ============================================================================

// Country codes (ISO 3166-1 alpha-2)
const ALLOWED_COUNTRIES = process.env.ALLOWED_COUNTRIES
  ? process.env.ALLOWED_COUNTRIES.split(',')
  : []; // Empty means allow all

const BLOCKED_COUNTRIES = process.env.BLOCKED_COUNTRIES
  ? process.env.BLOCKED_COUNTRIES.split(',')
  : [];

// Special regions (e.g., EU for GDPR)
const REGIONS = {
  EU: ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'],
  EEA: ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'IS', 'LI', 'NO'],
  NA: ['US', 'CA', 'MX'],
  SA: ['ZA', 'BW', 'LS', 'SZ', 'NA', 'ZW'],
  AF: ['DZ', 'AO', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CV', 'CF', 'TD', 'KM', 'CD', 'CG', 'CI', 'DJ', 'EG', 'GQ', 'ER', 'ET', 'GA', 'GM', 'GH', 'GN', 'GW', 'KE', 'LS', 'LR', 'LY', 'MG', 'MW', 'ML', 'MR', 'MU', 'MA', 'MZ', 'NA', 'NE', 'NG', 'RW', 'ST', 'SN', 'SC', 'SL', 'SO', 'ZA', 'SS', 'SD', 'SZ', 'TZ', 'TG', 'TN', 'UG', 'ZM', 'ZW']
};

// Cache for geoip lookups
const geoCache = new Map();
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get country code from IP address
 * @param {string} ip - IP address
 * @returns {Object} Geolocation data
 */
const getGeoData = (ip) => {
  // Check cache
  if (geoCache.has(ip)) {
    const cached = geoCache.get(ip);
    if (Date.now() - cached.timestamp < CACHE_TTL) {
      return cached.data;
    }
    geoCache.delete(ip);
  }

  // Lookup geo data
  const geo = geoip.lookup(ip);

  // Cache result
  if (geo) {
    geoCache.set(ip, {
      data: geo,
      timestamp: Date.now()
    });
  }

  return geo;
};

/**
 * Check if country is in a region
 * @param {string} countryCode - ISO country code
 * @param {string} region - Region name
 * @returns {boolean} True if in region
 */
const isInRegion = (countryCode, region) => {
  const regionCountries = REGIONS[region];
  return regionCountries ? regionCountries.includes(countryCode) : false;
};

/**
 * Check if IP is from allowed country
 * @param {string} countryCode - ISO country code
 * @returns {boolean} True if allowed
 */
const isCountryAllowed = (countryCode) => {
  if (!countryCode) return false;

  // If allowlist is empty, allow all (except blocked)
  if (ALLOWED_COUNTRIES.length === 0) {
    return !BLOCKED_COUNTRIES.includes(countryCode);
  }

  return ALLOWED_COUNTRIES.includes(countryCode);
};

/**
 * Check if IP is from blocked country
 * @param {string} countryCode - ISO country code
 * @returns {boolean} True if blocked
 */
const isCountryBlocked = (countryCode) => {
  if (!countryCode) return false;
  return BLOCKED_COUNTRIES.includes(countryCode);
};

/**
 * Log geo-blocking event for forensic audit
 * @param {Object} req - Express request object
 * @param {Object} geo - Geo data
 * @param {string} reason - Block reason
 */
const logGeoBlock = (req, geo, reason) => {
  const logEntry = {
    timestamp: new Date().toISOString(),
    ip: req.ip,
    path: req.path,
    method: req.method,
    country: geo?.country || 'unknown',
    region: geo?.region || 'unknown',
    city: geo?.city || 'unknown',
    reason,
    userAgent: req.headers['user-agent'],
    userId: req.user?._id || 'unauthenticated'
  };

  console.warn('[GEO-BLOCK] Access blocked:', logEntry);

  // In production, this would be sent to a security monitoring system
};

// ============================================================================
// GEO-BLOCKING MIDDLEWARE
// ============================================================================

/**
 * Geographic blocking middleware
 * @param {Object} options - Configuration options
 * @returns {Function} Express middleware
 */
export const geoBlock = (options = {}) => {
  const {
    enabled = true,
    blockOnFailure = true,
    allowLocalhost = true,
    logBlocked = true,
    exemptPaths = ['/health', '/api/test', '/public'],
    exemptRoles = ['admin', 'superadmin']
  } = options;

  return (req, res, next) => {
    // Skip if disabled
    if (!enabled) {
      return next();
    }

    // Allow exempt paths
    if (exemptPaths.some(path => req.path.startsWith(path))) {
      return next();
    }

    // Allow localhost if configured
    const ip = req.ip || req.connection.remoteAddress;
    if (allowLocalhost && (ip === '127.0.0.1' || ip === '::1' || ip === 'localhost')) {
      return next();
    }

    // Allow exempt roles for authenticated users
    if (req.user && req.user.role && exemptRoles.includes(req.user.role)) {
      return next();
    }

    try {
      // Get geo data
      const geo = getGeoData(ip);

      // If no geo data and we block on failure
      if (!geo && blockOnFailure) {
        if (logBlocked) {
          logGeoBlock(req, null, 'GEO_LOOKUP_FAILED');
        }

        return res.status(403).json({
          success: false,
          error: 'ACCESS_DENIED',
          message: 'Unable to determine your location. Access denied.'
        });
      }

      // If no geo data and we don't block on failure, allow
      if (!geo) {
        return next();
      }

      // Check if country is blocked
      if (isCountryBlocked(geo.country)) {
        if (logBlocked) {
          logGeoBlock(req, geo, 'COUNTRY_BLOCKED');
        }

        return res.status(403).json({
          success: false,
          error: 'ACCESS_DENIED',
          message: 'Access from your region is not permitted.'
        });
      }

      // Check if country is allowed
      if (!isCountryAllowed(geo.country)) {
        if (logBlocked) {
          logGeoBlock(req, geo, 'COUNTRY_NOT_ALLOWED');
        }

        return res.status(403).json({
          success: false,
          error: 'ACCESS_DENIED',
          message: 'Access from your region is not permitted.'
        });
      }

      // Attach geo data to request
      req.geo = {
        country: geo.country,
        region: geo.region,
        city: geo.city,
        ll: geo.ll,
        metro: geo.metro,
        area: geo.area,
        eu: isInRegion(geo.country, 'EU')
      };

      next();

    } catch (error) {
      console.error('[GEO-BLOCK] Error:', error);

      if (blockOnFailure) {
        return res.status(500).json({
          success: false,
          error: 'GEO_BLOCKING_ERROR',
          message: 'An error occurred while checking geographic access.'
        });
      }

      next();
    }
  };
};

// ============================================================================
// GDPR COMPLIANCE MIDDLEWARE
// ============================================================================

/**
 * GDPR compliance middleware
 * Enforces EU data protection rules for EU residents
 */
export const gdprCompliance = (options = {}) => {
  const {
    requireConsent = true,
    dataMinimization = true,
    logViolations = true
  } = options;

  return (req, res, next) => {
    // Check if user is from EU
    const isEU = req.geo?.eu || false;

    if (!isEU) {
      return next();
    }

    // Check GDPR consent
    if (requireConsent) {
      const consent = req.headers['x-gdpr-consent'] || req.cookies?.gdprConsent;

      if (!consent || consent !== 'granted') {
        if (logViolations) {
          console.warn('[GDPR] Missing consent from EU user:', {
            ip: req.ip,
            path: req.path,
            timestamp: new Date().toISOString()
          });
        }

        return res.status(403).json({
          success: false,
          error: 'GDPR_CONSENT_REQUIRED',
          message: 'GDPR consent is required for users in the European Union.'
        });
      }
    }

    // Data minimization - remove unnecessary data
    if (dataMinimization && req.body) {
      const sensitiveFields = ['ip', 'userAgent', 'fingerprint', 'location'];

      const minimizeData = (obj) => {
        if (!obj || typeof obj !== 'object') return;

        Object.keys(obj).forEach(key => {
          if (sensitiveFields.includes(key.toLowerCase())) {
            delete obj[key];
          } else if (typeof obj[key] === 'object') {
            minimizeData(obj[key]);
          }
        });
      };

      minimizeData(req.body);
    }

    // Attach GDPR flag to request
    req.gdpr = {
      applicable: true,
      consent: true,
      dataMinimized: dataMinimization
    };

    next();
  };
};

// ============================================================================
// POPIA COMPLIANCE MIDDLEWARE
// ============================================================================

/**
 * POPIA compliance middleware
 * Enforces South African data protection rules
 */
export const popiaCompliance = (options = {}) => {
  const {
    requireConsent = true,
    dataMinimization = true,
    logViolations = true
  } = options;

  return (req, res, next) => {
    // Check if user is from South Africa
    const isZA = req.geo?.country === 'ZA';

    if (!isZA) {
      return next();
    }

    // Check POPIA consent
    if (requireConsent) {
      const consent = req.headers['x-popia-consent'] || req.cookies?.popiaConsent;

      if (!consent || consent !== 'granted') {
        if (logViolations) {
          console.warn('[POPIA] Missing consent from SA user:', {
            ip: req.ip,
            path: req.path,
            timestamp: new Date().toISOString()
          });
        }

        return res.status(403).json({
          success: false,
          error: 'POPIA_CONSENT_REQUIRED',
          message: 'POPIA consent is required for users in South Africa.'
        });
      }
    }

    // Data minimization for SA users
    if (dataMinimization && req.body) {
      const sensitiveFields = ['idNumber', 'passport', 'bankAccount', 'creditCard'];

      const minimizeData = (obj) => {
        if (!obj || typeof obj !== 'object') return;

        Object.keys(obj).forEach(key => {
          if (sensitiveFields.includes(key.toLowerCase())) {
            delete obj[key];
          } else if (typeof obj[key] === 'object') {
            minimizeData(obj[key]);
          }
        });
      };

      minimizeData(req.body);
    }

    // Attach POPIA flag to request
    req.popia = {
      applicable: true,
      consent: true,
      dataMinimized: dataMinimization
    };

    next();
  };
};

// ============================================================================
// GEO-IP API ENDPOINTS
// ============================================================================

/**
 * Get current location info (with user consent)
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
export const getCurrentLocation = (req, res) => {
  if (!req.geo) {
    return res.status(404).json({
      success: false,
      error: 'LOCATION_NOT_FOUND',
      message: 'Unable to determine your location'
    });
  }

  // Return limited info for privacy
  res.json({
    success: true,
    data: {
      country: req.geo.country,
      region: req.geo.region,
      city: req.geo.city,
      eu: req.geo.eu,
      timestamp: new Date().toISOString()
    }
  });
};

/**
 * Check if location is allowed
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
export const checkLocation = (req, res) => {
  const ip = req.query.ip || req.ip;
  const geo = getGeoData(ip);

  if (!geo) {
    return res.json({
      success: true,
      data: {
        allowed: false,
        reason: 'LOCATION_UNKNOWN',
        message: 'Unable to determine location'
      }
    });
  }

  const allowed = isCountryAllowed(geo.country);
  const blocked = isCountryBlocked(geo.country);

  res.json({
    success: true,
    data: {
      allowed: allowed && !blocked,
      country: geo.country,
      region: geo.region,
      city: geo.city,
      reason: blocked ? 'COUNTRY_BLOCKED' : (allowed ? 'ALLOWED' : 'COUNTRY_NOT_ALLOWED')
    }
  });
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  geoBlock,
  gdprCompliance,
  popiaCompliance,
  getCurrentLocation,
  checkLocation,
  getGeoData,
  isInRegion,
  REGIONS
};
