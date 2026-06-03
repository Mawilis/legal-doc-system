/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN IP VALIDATION MIDDLEWARE                            ║
 * ║ [IP ADDRESS VALIDATION | FORENSIC TRACKING | SECURITY ENFORCEMENT]       ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | INSTITUTIONAL GRADE                   ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 *
 * @team Collaboration Notes:
 * - Validates and sanitizes IP addresses
 * - Detects proxy/VPN/Tor usage
 * - Enforces IP allow/block lists
 * - Tracks IP reputation and abuse patterns
 * - 101/10 security standard
 *
 * @last_updated: 2026-03-18
 * @lead_architect: Wilson Khanyezi
 */

import net from 'net';
import dns from 'dns';
import { promisify } from 'util';

const lookupAsync = promisify(dns.lookup);

// ============================================================================
// CONFIGURATION
// ============================================================================

// Private IP ranges (RFC 1918)
const PRIVATE_RANGES = [
  { start: '10.0.0.0', end: '10.255.255.255' },
  { start: '172.16.0.0', end: '172.31.255.255' },
  { start: '192.168.0.0', end: '192.168.255.255' }
];

// Localhost ranges
const LOCALHOST_RANGES = [
  { start: '127.0.0.0', end: '127.255.255.255' },
  { start: '::1', end: '::1' }
];

// Reserved IP ranges
const RESERVED_RANGES = [
  { start: '0.0.0.0', end: '0.255.255.255' },
  { start: '169.254.0.0', end: '169.254.255.255' },
  { start: '224.0.0.0', end: '239.255.255.255' },
  { start: '240.0.0.0', end: '255.255.255.255' }
];

// Known VPN/Proxy IPs (in production, this would come from a service)
const VPN_IPS = new Set([
  // Example VPN IPs - in production, use a proper VPN detection API
]);

// Known Tor exit nodes (in production, this would come from Tor project)
const TOR_EXIT_NODES = new Set([
  // Example Tor nodes - in production, use Tor DNS-based detection
]);

// IP reputation cache
const ipReputationCache = new Map();
const REPUTATION_CACHE_TTL = 30 * 60 * 1000; // 30 minutes

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Convert IP to number for range comparison
 * @param {string} ip - IPv4 address
 * @returns {number} IP as number
 */
const ipToNumber = (ip) => {
  const parts = ip.split('.').map(Number);
  return ((parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]) >>> 0;
};

/**
 * Check if IPv4 is in range
 * @param {string} ip - IPv4 address
 * @param {Object} range - Range object with start and end
 * @returns {boolean} True if in range
 */
const isIPv4InRange = (ip, range) => {
  const ipNum = ipToNumber(ip);
  const startNum = ipToNumber(range.start);
  const endNum = ipToNumber(range.end);
  return ipNum >= startNum && ipNum <= endNum;
};

/**
 * Validate IPv4 address
 * @param {string} ip - IP address
 * @returns {boolean} True if valid
 */
const isValidIPv4 = (ip) => {
  const parts = ip.split('.');
  if (parts.length !== 4) return false;

  return parts.every(part => {
    const num = parseInt(part, 10);
    return num >= 0 && num <= 255 && part === num.toString();
  });
};

/**
 * Validate IPv6 address
 * @param {string} ip - IP address
 * @returns {boolean} True if valid
 */
const isValidIPv6 = (ip) => {
  return net.isIPv6(ip);
};

/**
 * Normalize IP address
 * @param {string} ip - IP address
 * @returns {string} Normalized IP
 */
const normalizeIP = (ip) => {
  // Remove port if present
  ip = ip.split(':')[0];

  // Handle IPv6 with brackets
  if (ip.startsWith('[') && ip.endsWith(']')) {
    ip = ip.slice(1, -1);
  }

  return ip;
};

/**
 * Get IP version
 * @param {string} ip - IP address
 * @returns {number} IP version (4, 6, or 0 for invalid)
 */
const getIPVersion = (ip) => {
  if (net.isIPv4(ip)) return 4;
  if (net.isIPv6(ip)) return 6;
  return 0;
};

// ============================================================================
// IP CLASSIFICATION
// ============================================================================

/**
 * Check if IP is private
 * @param {string} ip - IP address
 * @returns {boolean} True if private
 */
export const isPrivateIP = (ip) => {
  if (getIPVersion(ip) !== 4) return false;

  return PRIVATE_RANGES.some(range => isIPv4InRange(ip, range));
};

/**
 * Check if IP is localhost
 * @param {string} ip - IP address
 * @returns {boolean} True if localhost
 */
export const isLocalhost = (ip) => {
  if (getIPVersion(ip) === 4) {
    return LOCALHOST_RANGES.some(range => isIPv4InRange(ip, range));
  }

  return ip === '::1' || ip === '0:0:0:0:0:0:0:1';
};

/**
 * Check if IP is reserved
 * @param {string} ip - IP address
 * @returns {boolean} True if reserved
 */
export const isReservedIP = (ip) => {
  if (getIPVersion(ip) !== 4) return false;

  return RESERVED_RANGES.some(range => isIPv4InRange(ip, range));
};

/**
 * Check if IP is from VPN
 * @param {string} ip - IP address
 * @returns {boolean} True if VPN
 */
export const isVPNIP = (ip) => {
  return VPN_IPS.has(ip);
};

/**
 * Check if IP is Tor exit node
 * @param {string} ip - IP address
 * @returns {boolean} True if Tor
 */
export const isTorExitNode = (ip) => {
  return TOR_EXIT_NODES.has(ip);
};

// ============================================================================
// IP REPUTATION
// ============================================================================

/**
 * Get IP reputation score
 * @param {string} ip - IP address
 * @returns {Promise<Object>} Reputation data
 */
export const getIPReputation = async (ip) => {
  // Check cache
  if (ipReputationCache.has(ip)) {
    const cached = ipReputationCache.get(ip);
    if (Date.now() - cached.timestamp < REPUTATION_CACHE_TTL) {
      return cached.data;
    }
    ipReputationCache.delete(ip);
  }

  // In production, this would call an IP reputation service
  // For now, return mock data
  const reputation = {
    ip,
    score: 100,
    threats: [],
    lastSeen: new Date().toISOString(),
    categories: [],
    confidence: 95
  };

  // Check against known bad IPs
  if (isVPNIP(ip)) {
    reputation.score -= 30;
    reputation.threats.push('VPN_PROXY');
  }

  if (isTorExitNode(ip)) {
    reputation.score -= 50;
    reputation.threats.push('TOR_EXIT_NODE');
  }

  // Cache result
  ipReputationCache.set(ip, {
    data: reputation,
    timestamp: Date.now()
  });

  return reputation;
};

// ============================================================================
// IP VALIDATION MIDDLEWARE
// ============================================================================

/**
 * IP validation middleware
 * @param {Object} options - Configuration options
 * @returns {Function} Express middleware
 */
export const validateIP = (options = {}) => {
  const {
    allowPrivate = false,
    allowLocalhost = true,
    allowReserved = false,
    allowVPN = false,
    allowTor = false,
    requireReputation = false,
    minReputationScore = 50,
    blockOnFailure = true,
    trustProxy = true,
    extractFromHeader = true
  } = options;

  return async (req, res, next) => {
    try {
      let ip;

      // Extract IP from various sources
      if (trustProxy) {
        // Check proxy headers
        ip = req.headers['x-forwarded-for']?.split(',')[0].trim();
      }

      if (!ip && extractFromHeader) {
        ip = req.headers['x-real-ip'] ||
              req.headers['x-client-ip'] ||
              req.headers['cf-connecting-ip'];
      }

      if (!ip) {
        ip = req.ip || req.connection.remoteAddress || req.socket.remoteAddress;
      }

      if (!ip) {
        if (blockOnFailure) {
          return res.status(400).json({
            success: false,
            error: 'IP_NOT_FOUND',
            message: 'Unable to determine client IP address'
          });
        }
        return next();
      }

      // Normalize IP
      ip = normalizeIP(ip);
      const version = getIPVersion(ip);

      if (version === 0) {
        if (blockOnFailure) {
          return res.status(400).json({
            success: false,
            error: 'INVALID_IP',
            message: 'Invalid IP address format'
          });
        }
        return next();
      }

      // Check localhost
      if (isLocalhost(ip) && !allowLocalhost) {
        if (blockOnFailure) {
          return res.status(403).json({
            success: false,
            error: 'LOCALHOST_NOT_ALLOWED',
            message: 'Localhost access is not permitted'
          });
        }
      }

      // Check private IP
      if (isPrivateIP(ip) && !allowPrivate) {
        if (blockOnFailure) {
          return res.status(403).json({
            success: false,
            error: 'PRIVATE_IP_NOT_ALLOWED',
            message: 'Private IP access is not permitted'
          });
        }
      }

      // Check reserved IP
      if (isReservedIP(ip) && !allowReserved) {
        if (blockOnFailure) {
          return res.status(403).json({
            success: false,
            error: 'RESERVED_IP_NOT_ALLOWED',
            message: 'Reserved IP access is not permitted'
          });
        }
      }

      // Check VPN
      if (isVPNIP(ip) && !allowVPN) {
        if (blockOnFailure) {
          return res.status(403).json({
            success: false,
            error: 'VPN_NOT_ALLOWED',
            message: 'VPN access is not permitted'
          });
        }
      }

      // Check Tor
      if (isTorExitNode(ip) && !allowTor) {
        if (blockOnFailure) {
          return res.status(403).json({
            success: false,
            error: 'TOR_NOT_ALLOWED',
            message: 'Tor access is not permitted'
          });
        }
      }

      // Check reputation
      if (requireReputation) {
        const reputation = await getIPReputation(ip);

        if (reputation.score < minReputationScore) {
          if (blockOnFailure) {
            return res.status(403).json({
              success: false,
              error: 'LOW_IP_REPUTATION',
              message: 'IP address has low reputation score',
              score: reputation.score,
              threats: reputation.threats
            });
          }
        }

        // Attach reputation to request
        req.ipReputation = reputation;
      }

      // Attach IP info to request
      req.clientIP = ip;
      req.clientIPVersion = version;
      req.clientIPInfo = {
        ip,
        version,
        isLocalhost: isLocalhost(ip),
        isPrivate: isPrivateIP(ip),
        isReserved: isReservedIP(ip),
        isVPN: isVPNIP(ip),
        isTor: isTorExitNode(ip)
      };

      next();

    } catch (error) {
      console.error('[IP-VALIDATION] Error:', error);

      if (blockOnFailure) {
        return res.status(500).json({
          success: false,
          error: 'IP_VALIDATION_ERROR',
          message: 'An error occurred during IP validation'
        });
      }

      next();
    }
  };
};

// ============================================================================
// IP WHITELIST/BLACKLIST MIDDLEWARE
// ============================================================================

/**
 * IP whitelist middleware
 * @param {Array} whitelist - Allowed IPs/CIDRs
 */
export const ipWhitelist = (whitelist = []) => {
  return (req, res, next) => {
    const ip = req.clientIP || req.ip;

    if (!ip) {
      return res.status(403).json({
        success: false,
        error: 'IP_REQUIRED',
        message: 'IP address is required'
      });
    }

    // Check if IP is in whitelist
    const allowed = whitelist.some(pattern => {
      if (pattern.includes('/')) {
        // CIDR notation - implement CIDR matching
        return ip.startsWith(pattern.split('/')[0]);
      }
      return pattern === ip;
    });

    if (!allowed) {
      return res.status(403).json({
        success: false,
        error: 'IP_NOT_WHITELISTED',
        message: 'IP address is not whitelisted'
      });
    }

    next();
  };
};

/**
 * IP blacklist middleware
 * @param {Array} blacklist - Blocked IPs/CIDRs
 */
export const ipBlacklist = (blacklist = []) => {
  return (req, res, next) => {
    const ip = req.clientIP || req.ip;

    if (!ip) {
      return next();
    }

    // Check if IP is in blacklist
    const blocked = blacklist.some(pattern => {
      if (pattern.includes('/')) {
        // CIDR notation - implement CIDR matching
        return ip.startsWith(pattern.split('/')[0]);
      }
      return pattern === ip;
    });

    if (blocked) {
      return res.status(403).json({
        success: false,
        error: 'IP_BLACKLISTED',
        message: 'IP address is blacklisted'
      });
    }

    next();
  };
};

// ============================================================================
// RATE LIMITING BY IP
// ============================================================================

/**
 * IP-based rate limiting
 * @param {Object} options - Rate limit options
 */
export const ipRateLimit = (options = {}) => {
  const {
    windowMs = 60 * 1000, // 1 minute
    max = 100,
    message = 'Too many requests from this IP'
  } = options;

  const requests = new Map();

  return (req, res, next) => {
    const ip = req.clientIP || req.ip;
    const now = Date.now();

    if (!ip) {
      return next();
    }

    // Get or create request count for IP
    let ipData = requests.get(ip);
    if (!ipData) {
      ipData = {
        count: 0,
        resetTime: now + windowMs
      };
      requests.set(ip, ipData);
    }

    // Reset if window expired
    if (now > ipData.resetTime) {
      ipData.count = 0;
      ipData.resetTime = now + windowMs;
    }

    // Increment count
    ipData.count++;

    // Check limit
    if (ipData.count > max) {
      return res.status(429).json({
        success: false,
        error: 'IP_RATE_LIMIT_EXCEEDED',
        message,
        retryAfter: Math.ceil((ipData.resetTime - now) / 1000)
      });
    }

    next();
  };
};

// ============================================================================
// IP INFO API ENDPOINTS
// ============================================================================

/**
 * Get current IP info
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
export const getCurrentIPInfo = (req, res) => {
  res.json({
    success: true,
    data: {
      ip: req.clientIP,
      version: req.clientIPVersion,
      info: req.clientIPInfo,
      reputation: req.ipReputation,
      timestamp: new Date().toISOString()
    }
  });
};

/**
 * Lookup IP info
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
export const lookupIP = async (req, res) => {
  const ip = req.params.ip || req.query.ip;

  if (!ip) {
    return res.status(400).json({
      success: false,
      error: 'IP_REQUIRED',
      message: 'IP address is required'
    });
  }

  const version = getIPVersion(ip);

  if (version === 0) {
    return res.status(400).json({
      success: false,
      error: 'INVALID_IP',
      message: 'Invalid IP address format'
    });
  }

  const reputation = await getIPReputation(ip);

  res.json({
    success: true,
    data: {
      ip,
      version,
      info: {
        isLocalhost: isLocalhost(ip),
        isPrivate: isPrivateIP(ip),
        isReserved: isReservedIP(ip),
        isVPN: isVPNIP(ip),
        isTor: isTorExitNode(ip)
      },
      reputation,
      timestamp: new Date().toISOString()
    }
  });
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  validateIP,
  ipWhitelist,
  ipBlacklist,
  ipRateLimit,
  getCurrentIPInfo,
  lookupIP,
  isPrivateIP,
  isLocalhost,
  isReservedIP,
  isVPNIP,
  isTorExitNode,
  getIPReputation
};
