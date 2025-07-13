const Role = require('../../models/roleModel');
const CustomError = require('../../utils/customError');
const logger = require('../../utils/logger');

exports.checkPermissions = (...requiredPermissions) => {
    return async (req, res, next) => {
        if (req.apiKeyPermissions) {
            const hasPerm = requiredPermissions.every(p => req.apiKeyPermissions.includes(p));
            if (hasPerm) return next();
            return next(new CustomError('API Key lacks required permissions.', 403));
        }

        const userRole = await Role.findOne({ name: req.user.role });
        if (!userRole) {
            logger.warn(`User role '${req.user.role}' not found`);
            return next(new CustomError('Role not found.', 403));
        }

        const hasPerm = requiredPermissions.every(p => userRole.permissions.includes(p));
        if (hasPerm) return next();
        logger.warn(`User ${req.user.email} lacks permissions: [${requiredPermissions.join(', ')}]`);
        return next(new CustomError('Insufficient permissions.', 403));
    };
};
