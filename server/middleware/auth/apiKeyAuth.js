const crypto = require('crypto');
const ApiKey = require('../../models/apiKeyModel');
const User = require('../../models/userModel');
const CustomError = require('../../utils/customError');

exports.verifyApiKey = async (req) => {
    if (req.headers['x-api-key']) {
        const apiKey = req.headers['x-api-key'];
        const keyHash = crypto.createHash('sha256').update(apiKey).digest('hex');
        const storedKey = await ApiKey.findOne({ keyHash });
        if (!storedKey) throw new CustomError('Invalid API Key.', 401);
        if (storedKey.expiresAt && storedKey.expiresAt < new Date()) {
            throw new CustomError('API Key has expired.', 401);
        }
        const keyOwner = await User.findById(storedKey.user).select('-password');
        if (!keyOwner) throw new CustomError('API Key user no longer exists.', 401);
        storedKey.lastUsed = new Date();
        storedKey.save();
        return { keyOwner, permissions: storedKey.permissions };
    }
    return null;
};
