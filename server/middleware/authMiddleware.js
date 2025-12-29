// File: server/middleware/authMiddleware.js
// -----------------------------------------------------------------------------
// COLLABORATION NOTES:
// - Verifies JWT access tokens for protected Gateway routes.
// - Must use SAME JWT_SECRET as Auth Service.
// - Attaches decoded user context to req.user; forwards tenantId to headers.
// -----------------------------------------------------------------------------

'use strict';

const jwt = require('jsonwebtoken');
const JWT_SECRET = process.env.JWT_SECRET || 'your_billion_dollar_secret_key';

exports.protect = async (req, res, next) => {
  let token;

  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    token = req.headers.authorization.split(' ')[1];
    try {
      const decoded = jwt.verify(token, JWT_SECRET);
      req.user = decoded;
      if (decoded.tenantId) {
        req.headers['x-tenant-id'] = decoded.tenantId;
      }
      return next();
    } catch (error) {
      console.error('🔴 [AuthMiddleware] Token Verification Failed:', error.message);
      return res.status(401).json({ message: 'Not authorized, token failed' });
    }
  }

  console.warn('⚠️ [AuthMiddleware] No token provided for protected route');
  return res.status(401).json({ message: 'Not authorized, no token' });
};
