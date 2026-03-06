#!/* eslint-disable */
/* ╔═══════════════════════════════════════════════════════════════════════════╗
  ║ WILSY OS - BETA AUTH MIDDLEWARE                                           ║
  ║ Temporary bypass for beta testing - REMOVE BEFORE PRODUCTION             ║
  ╚═══════════════════════════════════════════════════════════════════════════╝ */

// BETA MODE: Allow all requests for testing
export const authMiddleware = (req, res, next) => {
  // For beta testing, attach a mock user
  req.user = {
    id: 'beta-user',
    email: 'beta@wilsyos.com',
    roles: ['admin'],
    tenantId: req.headers['x-tenant-id'] || 'default',
  };
  next();
};

export const optionalAuthMiddleware = (req, res, next) => {
  req.user = {
    id: 'beta-user',
    email: 'beta@wilsyos.com',
    roles: ['admin'],
    tenantId: req.headers['x-tenant-id'] || 'default',
  };
  next();
};

export const requireRoles = (allowedRoles) => (req, res, next) => {
  next();
};

export const requirePermissions = (requiredPermissions) => (req, res, next) => {
  next();
};

export const requireMFA = (req, res, next) => {
  next();
};

export const refreshToken = (req, res) => {
  res.json({
    accessToken: 'beta-token',
    refreshToken: 'beta-refresh',
    tokenType: 'Bearer',
    expiresIn: 3600,
  });
};

export const logout = (req, res) => {
  res.json({
    message: 'Logged out successfully',
    timestamp: new Date().toISOString(),
  });
};

export const authServiceInstance = {
  generateTokens: () => ({
    accessToken: 'beta-token',
    refreshToken: 'beta-refresh',
  }),
};

export default authMiddleware;
