const User = require('../models/userModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');
const { logAuditEvent } = require('../utils/auditLogger');
const sendEmail = require('../utils/sendMail');
const jwt = require('jsonwebtoken');

// In-memory failed login tracker (or use Redis for production)
const failedLoginAttempts = {};

const generateToken = (id) => {
    return jwt.sign({ id }, process.env.JWT_SECRET, {
        expiresIn: '30d',
    });
};

const sendTokenResponse = (user, statusCode, res) => {
    const token = generateToken(user._id);

    const cookieOptions = {
        expires: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
    };

    res.status(statusCode)
        .cookie('token', token, cookieOptions)
        .json({
            success: true,
            token,
            data: {
                id: user._id,
                name: user.name,
                email: user.email,
                role: user.role,
            },
        });
};

// --- Register ---
exports.register = async (req, res, next) => {
    try {
        const { name, email, password, role } = req.body;

        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return next(new CustomError('An account with this email already exists.', 400));
        }

        const user = await User.create({ name, email, password, role });

        logger.info(`New user registered: ${user.email}`);
        logAuditEvent(`✅ Registered new user: ${email} | IP: ${req.ip}`);

        sendTokenResponse(user, 201, res);
    } catch (error) {
        logger.error(`Registration error: ${error.message}`);
        next(error);
    }
};

// --- Login ---
exports.login = async (req, res, next) => {
    try {
        const { email, password } = req.body;

        if (!email || !password) {
            return next(new CustomError('Please provide an email and password.', 400));
        }

        const user = await User.findOne({ email }).select('+password');

        if (!user || !(await user.matchPassword(password))) {
            logAuditEvent(`❌ Failed login for ${email} | IP: ${req.ip}`);

            // Track failed attempts
            failedLoginAttempts[email] = (failedLoginAttempts[email] || 0) + 1;

            // If >= 3 failed attempts, alert admin
            if (failedLoginAttempts[email] >= 3) {
                logger.warn(`🚨 Multiple failed logins for ${email}`);
                await sendEmail({
                    to: process.env.ALERT_EMAIL,
                    subject: `🚨 Security Alert: Failed Login Attempts`,
                    text: `There have been ${failedLoginAttempts[email]} failed login attempts for ${email} from IP ${req.ip}`,
                });
                // Reset to avoid spamming
                failedLoginAttempts[email] = 0;
            }

            return next(new CustomError('Invalid email or password.', 401));
        }

        // Successful login — reset tracker
        failedLoginAttempts[email] = 0;

        logger.info(`User logged in: ${user.email}`);
        logAuditEvent(`✅ Successful login: ${email} | IP: ${req.ip}`);

        sendTokenResponse(user, 200, res);
    } catch (error) {
        logger.error(`Login error: ${error.message}`);
        next(error);
    }
};

// --- Get Me ---
exports.getMe = async (req, res, next) => {
    try {
        const user = await User.findById(req.user.id);

        if (!user) {
            return next(new CustomError('User not found.', 404));
        }

        res.status(200).json({
            success: true,
            data: {
                id: user._id,
                name: user.name,
                email: user.email,
                role: user.role,
            }
        });
    } catch (error) {
        logger.error(`GetMe error: ${error.message}`);
        next(error);
    }
};
