/*
 * File: server/middleware/ipMetadata.js
 * STATUS: PRODUCTION-READY | FORENSIC INTELLIGENCE GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Extracts, normalizes, and enriches client IP data. This provides the 
 * "Geographic Fingerprint" for every request.
 *
 * KEY FEATURES FOR FUTURE ENGINEERS:
 * 1. Proxy-Awareness: Correctly identifies the real client IP behind Load Balancers.
 * 2. Privacy Compliance: Hashes IPs to comply with POPIA/GDPR for long-term logs.
 * 3. Geolocation: Adds Country/City context (requires geoip-lite or similar).
 * 4. Anomaly Context: Flags private vs public IPs for security risk scoring.
 * -----------------------------------------------------------------------------
 */

'use strict';

const geoip = require('geoip-lite');
const crypto = require('crypto');

/**
 * PRIVACY UTILITY:
 * Hashes the IP to allow uniqueness tracking without storing PII.
 */
const hashIp = (ip) => {
    if (!ip || ip === 'unknown') return 'unknown';
    // Use a system secret to salt the hash for higher security
    const salt = process.env.IP_HASH_SALT || 'wilsy-default-salt';
    return crypto.createHash('sha256').update(ip + salt).digest('hex').substring(0, 16);
};

/**
 * PROXY DETECTOR:
 * Identifies if the request is coming from a local or private network.
 */
const isPrivateIp = (ip) => {
    return /^(127\.|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[0-1])\.)/.test(ip);
};

const ipMetadata = (req, res, next) => {
    try {
        // 1. EXTRACT REAL CLIENT IP
        // Behind Nginx/AWS, the real IP is the first element in X-Forwarded-For
        const forwardedFor = req.headers['x-forwarded-for'];
        const clientIp = forwardedFor
            ? forwardedFor.split(',')[0].trim()
            : (req.socket.remoteAddress || 'unknown');

        // 2. INITIALIZE SECURITY CONTEXT
        req.security = req.security || {};

        // 3. ENRICH IP METADATA
        const metadata = {
            address: clientIp,
            hash: hashIp(clientIp),
            isPrivate: isPrivateIp(clientIp),
            timestamp: new Date().toISOString()
        };

        // 4. GEOLOCATION ENRICHMENT
        // We skip lookup for private/local IPs to save CPU
        if (!metadata.isPrivate && clientIp !== 'unknown') {
            const geo = geoip.lookup(clientIp);
            if (geo) {
                metadata.geo = {
                    country: geo.country,
                    region: geo.region,
                    city: geo.city,
                    timezone: geo.timezone,
                    coordinates: geo.ll // [lat, lng]
                };
            }
        }

        // 5. ATTACH TO REQUEST
        req.ipMetadata = metadata;

        // 6. FORENSIC HOOK
        // If the IP is from a high-risk country or blacklisted range, 
        // this is where you would flag req.security.isHighRisk = true.

        next();
    } catch (err) {
        // Fail open: IP metadata is for enrichment, don't crash the request.
        console.error('IP_METADATA_MIDDLEWARE_ERR:', err);
        next();
    }
};

module.exports = { ipMetadata };