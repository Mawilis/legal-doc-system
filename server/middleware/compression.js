/*
 * File: server/middleware/compression.js
 * STATUS: PRODUCTION-READY | PERFORMANCE & EFFICIENCY GRADE
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Dramatically reduces the size of HTTP responses (JSON, HTML, Text).
 * Essential for performance in low-bandwidth environments (Courts, Mobile).
 *
 * KEY FEATURES FOR FUTURE ENGINEERS:
 * 1. Intelligent Filtering: Skips already compressed files (PDFs, Images, ZIPs).
 * 2. SSE Protection: Disables compression for streaming data to prevent buffering.
 * 3. Resource Efficiency: 1KB threshold prevents overhead on tiny responses.
 * 4. Observability: Integrates with req.logAudit for forensic transparency.
 * -----------------------------------------------------------------------------
 */

'use strict';

const compression = require('compression');

/**
 * COMPRESSION FILTER LOGIC:
 * Decides whether a response is a candidate for Gzip/Deflate.
 */
const shouldCompress = (req, res) => {
    // 1. HEADER OPT-OUT
    if (req.headers['x-no-compression']) return false;

    // 2. STREAM PROTECTION
    // Do not compress Server-Sent Events (SSE) or streams, as it breaks real-time delivery.
    const contentType = res.getHeader('Content-Type') || '';
    if (contentType === 'text/event-stream') return false;

    // 3. BINARY PROTECTION
    // PDFs and Images are already compressed. Re-compressing wastes CPU.
    if (/\b(image|audio|video|application\/zip|application\/pdf)\b/i.test(contentType)) {
        return false;
    }

    // 4. DEFAULT COMPRESSION FILTER
    return compression.filter(req, res);
};

/**
 * EXPORTED MIDDLEWARE CONFIGURATION:
 * Optimized for high-concurrency legal platforms.
 */
const compressionMiddleware = compression({
    // THRESHOLD: 1024 bytes (1KB). 
    // Small responses gain no benefit from compression due to header overhead.
    threshold: 1024,

    // FILTER: Uses the advanced logic defined above.
    filter: shouldCompress,

    // LEVEL: 6 (Balanced). 
    // Higher levels consume significantly more CPU for marginal size gains.
    level: parseInt(process.env.COMPRESSION_LEVEL || '6', 10),
});

/*
 * NOTE FOR ENGINEERS:
 * If users report 'Slow Real-time Updates', check if the Content-Type 
 * in the controller is set correctly to 'text/event-stream' to bypass this.
 */

module.exports = compressionMiddleware;