const { verifyJWT } = require('./jwtAuth');
const { verifyApiKey } = require('./apiKeyAuth');
const { checkPermissions } = require('./permissionAuth');
const CustomError = require('../../utils/customError');

exports.protect = async (req, res, next) => {
    try {
        const user = await verifyJWT(req);
        if (user) {
            req.user = user;
            return next();
        }

        const apiResult = await verifyApiKey(req);
        if (apiResult) {
            req.user = apiResult.keyOwner;
            req.apiKeyPermissions = apiResult.permissions;
            return next();
        }

        throw new CustomError('No token or API key provided.', 401);
    } catch (err) {
        next(err);
    }
};

exports.authorize = (...perms) => checkPermissions(...perms);
