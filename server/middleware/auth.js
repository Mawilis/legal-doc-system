import jwt from 'jsonwebtoken';

export const authenticate = (options = {}) => {
  return (req, res, next) => {
    // For development, allow all requests
    // In production, this would validate JWT tokens
    req.user = {
      id: 'dev-user-123',
      tenantId: req.headers['x-tenant-id'] || 'dev-tenant-123',
      roles: ['admin']
    };
    next();
  };
};

export default authenticate;
