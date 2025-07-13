const jwt = require('jsonwebtoken');
const asyncHandler = require('express-async-handler');
const User = require('../models/userModel');
const CustomError = require('../utils/customError');

exports.protect = asyncHandler(async (req, res, next) => {
    let token;

    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
        token = req.headers.authorization.split(' ')[1];
    }

    if (!token) {
        return next(new CustomError('No token provided', 401));
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        const user = await User.findById(decoded.id);

        if (!user) {
            console.warn(`❌ No user found for ID: ${decoded.id}`);
            return next(new CustomError('The user for this token no longer exists.', 401));
        }

        req.user = user;
        next();
    } catch (err) {
        console.error('❌ Auth error:', err.message);
        return next(new CustomError('Not authorized or token failed', 401));
    }
});

exports.authorize = (...roles) => {
    return (req, res, next) => {
        if (!roles.includes(req.user.role)) {
            return next(new CustomError(`User role ${req.user.role} not authorized to access this route`, 403));
        }
        next();
    };
};
