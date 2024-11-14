// ~/legal-doc-system/server/controllers/authController.js

const catchAsync = require('../utils/catchAsync');
const User = require('../models/userModel'); // Import User model
const jwt = require('jsonwebtoken'); // Import JWT for token handling
const crypto = require('crypto'); // Crypto for generating secure tokens
const sendEmail = require('../utils/sendEmail'); // Utility function for sending emails
const logger = require('../utils/logger'); // Import logger
const { CustomError } = require('../utils/customError'); // Custom error handling class

/**
 * Helper function to generate a JWT for a user
 * @param {Object} user - The user object to create the token for
 * @returns {string} JWT token
 */
const signToken = (user) => {
    console.log('Generating JWT for user:', user._id);
    return jwt.sign(
        { id: user._id, role: user.role },
        process.env.JWT_SECRET,
        { expiresIn: process.env.JWT_EXPIRES_IN || '1h' }
    );
};

/**
 * Helper function to generate a refresh token for a user
 * @param {Object} user - The user object to create the refresh token for
 * @returns {string} JWT refresh token
 */
const signRefreshToken = (user) => {
    console.log('Generating refresh token for user:', user._id);
    return jwt.sign(
        { id: user._id },
        process.env.JWT_REFRESH_SECRET,
        { expiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d' }
    );
};

/**
 * Register a new user
 */
exports.register = catchAsync(async (req, res, next) => {
    const { name, email, password } = req.body;

    // Ensure required fields are provided
    if (!name || !email || !password) {
        console.log('Registration failed: Missing required fields');
        return next(new CustomError('Please provide name, email, and password', 400));
    }

    // Ensure email is unique
    const existingUser = await User.findOne({ email });
    if (existingUser) {
        console.log('Attempt to register with existing email:', email);
        return next(new CustomError('Email is already registered', 400));
    }

    // Create a new user and save to the database
    const user = new User({ name, email, password });
    await user.save();
    console.log('New user created:', { userId: user._id, email: user.email });

    // Generate a JWT and Refresh token for the user
    const token = signToken(user);
    const refreshToken = signRefreshToken(user);

    console.log('User registered successfully:', { email, userId: user._id });
    res.status(201).json({
        token,
        refreshToken,
        user: { id: user._id, name: user.name, email: user.email }
    });
});

/**
 * Login an existing user
 */
exports.login = catchAsync(async (req, res, next) => {
    const { email, password } = req.body;

    // Ensure required fields are provided
    if (!email || !password) {
        console.log('Login failed: Missing email or password');
        return next(new CustomError('Please provide email and password', 400));
    }

    // Validate user credentials
    const user = await User.findOne({ email }).select('+password');
    if (!user || !(await user.comparePassword(password))) {
        console.log('Invalid login attempt:', { email });
        return next(new CustomError('Invalid email or password', 401));
    }

    // Generate a JWT and Refresh token for the user
    const token = signToken(user);
    const refreshToken = signRefreshToken(user);

    console.log('User logged in successfully:', { email, userId: user._id });
    res.status(200).json({
        token,
        refreshToken,
        user: { id: user._id, name: user.name, email: user.email }
    });
});

/**
 * Middleware to protect routes using JWT authentication
 */
exports.protect = catchAsync(async (req, res, next) => {
    let token;

    // Get token from Authorization header
    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
        token = req.headers.authorization.split(' ')[1];
    }

    if (!token) {
        console.log('Unauthorized access attempt - no token provided');
        return next(new CustomError('Not authenticated', 401));
    }

    try {
        // Verify token
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        console.log('Decoded token:', decoded);

        // Find user by ID
        const user = await User.findById(decoded.id);
        if (!user) {
            console.log('User not found for provided token:', { userId: decoded.id });
            return next(new CustomError('User no longer exists', 401));
        }

        req.user = user;
        console.log('User authenticated successfully:', { userId: user._id });
        next();
    } catch (err) {
        console.log('Error verifying token:', err);
        return next(new CustomError('Invalid or expired token', 401));
    }
});

/**
 * Middleware to restrict access to admin users
 */
exports.restrictToAdmin = (req, res, next) => {
    if (req.user.role !== 'admin') {
        console.log('Unauthorized admin access attempt by user:', { userId: req.user._id });
        return next(new CustomError('Access denied: Admin only', 403));
    }
    console.log('Admin access granted:', { userId: req.user._id });
    next();
};

/**
 * Handle forgot password
 */
exports.forgotPassword = catchAsync(async (req, res, next) => {
    const { email } = req.body;

    if (!email) {
        console.log('Forgot password request missing email');
        return next(new CustomError('Please provide an email', 400));
    }

    const user = await User.findOne({ email });
    if (!user) {
        console.log('Password reset requested for non-existing user:', { email });
        return next(new CustomError('User not found', 404));
    }

    // Create a reset token
    const resetToken = user.createPasswordResetToken();
    await user.save({ validateBeforeSave: false });
    console.log('Password reset token created for user:', { userId: user._id });

    // Send reset email
    const resetUrl = `${req.protocol}://${req.get('host')}/api/auth/reset-password/${resetToken}`;
    const message = `Forgot your password? Click here to reset it: ${resetUrl}. If you didn't request this, please ignore this email.`;

    await sendEmail({
        email: user.email,
        subject: 'Password Reset Request',
        message,
    });

    console.log('Password reset email sent to:', { email });
    res.status(200).json({ message: 'Password reset token sent to email' });
});

/**
 * Handle password reset
 */
exports.resetPassword = catchAsync(async (req, res, next) => {
    const resetToken = req.params.token;
    const { password } = req.body;

    if (!password) {
        console.log('Password reset attempt missing new password');
        return next(new CustomError('Please provide a new password', 400));
    }

    const hashedToken = crypto.createHash('sha256').update(resetToken).digest('hex');

    // Find user by the hashed reset token
    const user = await User.findOne({
        passwordResetToken: hashedToken,
        passwordResetExpires: { $gt: Date.now() },
    });

    if (!user) {
        console.log('Invalid or expired password reset token');
        return next(new CustomError('Token is invalid or has expired', 400));
    }

    // Update password and remove reset token
    user.password = password;
    user.passwordResetToken = undefined;
    user.passwordResetExpires = undefined;
    await user.save();

    // Generate a new JWT token for the user
    const token = signToken(user);
    console.log('Password reset successfully for user:', { userId: user._id });
    res.status(200).json({
        token,
        user: { id: user._id, name: user.name, email: user.email }
    });
});

/**
 * Handle refresh token generation
 */
exports.refreshToken = catchAsync(async (req, res, next) => {
    const { refreshToken } = req.body;

    if (!refreshToken) {
        console.log('No refresh token provided for token refresh request');
        return next(new CustomError('No refresh token provided', 400));
    }

    try {
        // Verify refresh token
        const decoded = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET);
        const user = await User.findById(decoded.id);
        if (!user) {
            console.log('User not found for provided refresh token');
            return next(new CustomError('User not found', 404));
        }

        // Generate a new access token
        const newToken = signToken(user);
        console.log('New access token generated for user:', { userId: user._id });
        res.status(200).json({ token: newToken });
    } catch (err) {
        console.log('Error refreshing token:', err);
        return next(new CustomError('Invalid refresh token', 400));
    }
});
