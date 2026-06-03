/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN RATE LIMITER MIDDLEWARE [V2.1.2-OMEGA-FINALITY]                                                                   ║
 * ║ [REQUEST THROTTLING | DDOS PROTECTION | SOVEREIGN WHITELISTING | BIBLICAL WORTH]                                                       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.1.2-OMEGA | PRODUCTION READY | BILLION DOLLAR SPEC                                                                          ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY | BOARDROOM READY                                        ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/rateLimiter.js                                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated zero-latency whitelisting for local telemetry development. [2026-05-15]              ║
 * ║ • AI Engineering (Gemini) - RECTIFIED: Implemented IPv6 normalization to resolve 429 lockout on local Mac loopback. [2026-05-15]        ║
 * ║ • AI Engineering (Gemini) - FORTIFIED: Injected immunity for Telemetry Pulse and Discovery routes. [2026-05-15]                         ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

/**
 * 🛡️ SOVEREIGN RATE LIMITER FACTORY
 */
export const rateLimiter = (options = {}) => {
  const {
    windowMs = 60 * 1000,
    max = 5000,
    message = 'SOVEREIGN_THRESHOLD_REACHED: Request density exceeds institutional limits.'
  } = options;

  const store = new Map();
  const whitelist = ['127.0.0.1', '::1', '::ffff:127.0.0.1', 'localhost', 'GLOBAL_ROOT', 'WILSY_ROOT', 'WILSY_GLOBAL_ROOT'];

  // Clean up old entries periodically
  setInterval(() => {
    const now = Date.now();
    for (const [key, data] of store.entries()) {
      if (now - data.resetTime > windowMs) store.delete(key);
    }
  }, windowMs);

  return (req, res, next) => {
    // 🛡️ RECTIFIED: Absolute immunity for critical system discovery and telemetry
    if (req.url.includes('/telemetry/pulse') || req.url.includes('/auth/discover')) {
      return next();
    }

    const rawIp = req.ip || req.connection.remoteAddress || '0.0.0.0';
    const cleanIp = rawIp.replace(/^.*:/, '');
    const tenantId = req.headers['x-tenant-id'];
    const now = Date.now();

    // 🛡️ SOVEREIGN BYPASS
    if (whitelist.includes(rawIp) || whitelist.includes(cleanIp) || (tenantId && whitelist.includes(tenantId))) {
      return next();
    }

    let rateData = store.get(cleanIp);
    if (!rateData) {
      rateData = { count: 0, resetTime: now + windowMs };
      store.set(cleanIp, rateData);
    }

    if (now > rateData.resetTime) {
      rateData.count = 0;
      rateData.resetTime = now + windowMs;
    }

    rateData.count++;

    res.setHeader('X-RateLimit-Limit', max);
    res.setHeader('X-RateLimit-Remaining', Math.max(0, max - rateData.count));
    res.setHeader('X-RateLimit-Reset', Math.ceil(rateData.resetTime / 1000));

    if (rateData.count > max) {
      console.warn(`[THROTTLE] 🛡️ Shield engaged for ${cleanIp}: ${rateData.count}/${max}`);
      return res.status(429).json({ success: false, error: 'RATE_LIMIT_EXCEEDED', message });
    }

    next();
  };
};

export default rateLimiter;
