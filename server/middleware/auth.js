// middleware/auth.js

const jwt = require('jsonwebtoken');
const asyncHandler = require('express-async-handler');
const User = require('../models/userModel');
const CustomError = require('../utils/customError');

// Middleware to protect routes
exports.protect = asyncHandler(async (req, res, next) => {
    let token;

    if (
        req.headers.authorization &&
        req.headers.authorization.startsWith('Bearer')
    ) {
        token = req.headers.authorization.split(' ')[1];
    }

    if (!token) {
        console.warn('🛑 No token found in Authorization header');
        return next(new CustomError('Not authorized, token missing', 401));
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        console.log('🔍 Decoded token:', decoded);

        const user = await User.findById(decoded.id).select('-password');
        console.log('👤 Fetched user from DB:', user);

        if (!user) {
            console.warn(`❌ No user found for ID: ${decoded.id}`);
            return next(new CustomError('The user for this token no longer exists.', 401));
        }

        req.user = user;
        next();
    } catch (err) {
        console.error('🚨 JWT error:', err.message);
        return next(new CustomError('Not authorized or token failed', 401));
    }
});

// Optional role-based access
exports.authorize = (...roles) => {
    return (req, res, next) => {
        if (!roles.includes(req.user.role)) {
            return next(new CustomError(`User role '${req.user.role}' is not authorized`, 403));
        }
        next();
    };
};
