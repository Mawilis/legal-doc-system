const jwt = require('jsonwebtoken');
const User = require('../models/userModel');
const CustomError = require('../utils/customError');

// Protect routes by checking JWT token
const protect = async (req, res, next) => {
    console.log('Inside protect middleware');
    let token;

    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
        try {
            token = req.headers.authorization.split(' ')[1];
            const decoded = jwt.verify(token, process.env.JWT_SECRET);
            req.user = await User.findById(decoded.id).select('-password');

            if (!req.user) {
                return next(new CustomError('User not found', 404));
            }

            next();
        } catch (error) {
            console.error('Not authorized, token failed', error);
            return next(new CustomError('Not authorized, token failed', 401));
        }
    } else {
        return next(new CustomError('Not authorized, no token', 401));
    }
};

// Authorize specific roles
const authorize = (...roles) => {
    return (req, res, next) => {
        if (!roles.includes(req.user.role)) {
            return next(new CustomError('User role not authorized', 403));
        }
        next();
    };
};

module.exports = {
    protect,
    authorize,
};
