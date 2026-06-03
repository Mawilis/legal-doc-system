/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - INTEGRITY SHIELD MIDDLEWARE [V1.0.0-SINGULARITY]                                                                            ║
 * ║ [REQUEST VALIDATION | SECURITY HEADER ENFORCEMENT | INSTITUTIONAL DEFENSE]                                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0-SINGULARITY | PRODUCTION READY | BILLION DOLLAR SPEC                                                                    ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | REVENUE-GRADE ARCHITECTURE                                                       ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/middleware/integrityShield.js                                             ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 👥 COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                 ║
 * ║ • Wilson Khanyezi (CEO/Lead Architect) - Mandated zero-fracture request integrity for Wilsy OS. [2026-05-02]                           ║
 * ║ • AI Engineering (Gemini) - CREATED: Implemented institutional header enforcement and payload integrity checks.                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ 🛠️ FUNCTIONAL LOGIC:                                                                                                                   ║
 * ║ 1. Security Header Injection: Hardens the response against common strike vectors (Sniffing, Framing, XSS).                             ║
 * ║ 2. Payload Validation: Ensures POST/PUT/PATCH bodies are structured as valid objects, preventing malformed strikes.                    ║
 * ║ 3. Zero-Trust Enforcement: Acts as the primary filter before request-sealing or JWT verification.                                      ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

/**
 * @function integrityShield
 * @description Validates the structural integrity of inbound requests and injects mandatory security headers.
 * @param {Object} req - Express Request object.
 * @param {Object} res - Express Response object.
 * @param {Function} next - Next middleware function.
 */
export const integrityShield = (req, res, next) => {

  // 🛡️ INSTITUTIONAL SECURITY HEADERS
  // Prevents the browser from interpreting files as a different MIME type (e.g., executing CSS as JS).
  res.setHeader('X-Content-Type-Options', 'nosniff');

  // Prevents the interface from being embedded in <iframe> or <frame> tags to stop Clickjacking.
  res.setHeader('X-Frame-Options', 'DENY');

  // Instructs the browser to block the page if a Cross-Site Scripting (XSS) attack is detected.
  res.setHeader('X-XSS-Protection', '1; mode=block');

  /**
   * 🧪 STRIKE VALIDATION: Body Integrity Check
   * For state-changing methods (POST, PUT, PATCH), we mandate that the body must be a valid object.
   * This prevents primitive-type injection or malformed JSON from reaching the controllers.
   */
  const stateChangingMethods = ['POST', 'PUT', 'PATCH'];

  if (stateChangingMethods.includes(req.method) && req.body) {
    if (typeof req.body !== 'object' || Array.isArray(req.body)) {
      return res.status(400).json({
        success: false,
        message: 'INTEGRITY_BREACH: Inbound strike payload must be a valid object.'
      });
    }
  }

  // Finality: The request has passed integrity validation. Proceed to next gate.
  next();
};

export default integrityShield;
