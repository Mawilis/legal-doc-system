// server/controllers/passwordController.js

const crypto = require('crypto');
const User = require('../models/userModel');
const CustomError = require('../utils/customError');
const sendEmail = require('../utils/sendMail'); // We will assume this utility exists
const logger = require('../utils/logger');

/**
 * @desc    Forgot Password - Generate token and send to user's email
 * @route   POST /api/password/forgotpassword
 * @access  Public
 */
exports.forgotPassword = async (req, res, next) => {
    try {
        // 1. Get user by their email
        const user = await User.findOne({ email: req.body.email });

        if (!user) {
            // For security, we don't reveal if the user exists or not.
            // We send a success message either way, but only send an email if the user is found.
            logger.warn(`Password reset attempt for non-existent email: ${req.body.email}`);
            return res.status(200).json({
                success: true,
                data: 'If a user with that email exists, a password reset link has been sent.',
            });
        }

        // 2. Generate the reset token using the method on our user model
        const resetToken = user.getResetPasswordToken();

        // 3. Save the user document with the new reset token fields
        await user.save({ validateBeforeSave: false }); // Disable validation to save without a password change

        // 4. Create the reset URL that will be sent in the email
        // In a real app, this would point to your frontend's reset password page.
        const resetUrl = `${req.protocol}://${req.get('host')}/resetpassword/${resetToken}`;

        const message = `You are receiving this email because you (or someone else) has requested the reset of a password. Please make a PUT request to: \n\n ${resetUrl}`;

        // 5. Send the email
        try {
            await sendEmail({
                email: user.email,
                subject: 'Password Reset Token',
                message,
            });

            logger.info(`Password reset email sent to: ${user.email}`);
            res.status(200).json({ success: true, data: 'Email sent' });
        } catch (err) {
            logger.error(`Email could not be sent: ${err.message}`);
            // If the email fails to send, we must clear the reset token fields from the database
            // to prevent a user from being stuck in a state where they can't request another token.
            user.passwordResetToken = undefined;
            user.passwordResetExpire = undefined;
            await user.save({ validateBeforeSave: false });

            return next(new CustomError('Email could not be sent', 500));
        }
    } catch (error) {
        next(error);
    }
};

/**
 * @desc    Reset user's password
 * @route   PUT /api/password/resetpassword/:resettoken
 * @access  Public
 */
exports.resetPassword = async (req, res, next) => {
    try {
        // 1. Get the unhashed token from the URL parameter
        const resetToken = req.params.resettoken;

        // 2. Hash the token so we can compare it to the one stored in the database
        const hashedToken = crypto
            .createHash('sha256')
            .update(resetToken)
            .digest('hex');

        // 3. Find the user by the hashed token and check if the token has not expired
        const user = await User.findOne({
            passwordResetToken: hashedToken,
            passwordResetExpire: { $gt: Date.now() }, // Check that the expiry date is greater than now
        });

        if (!user) {
            return next(new CustomError('Invalid or expired token.', 400));
        }

        // 4. If the token is valid, set the new password
        user.password = req.body.password;

        // 5. Clear the reset token fields, as they have now been used
        user.passwordResetToken = undefined;
        user.passwordResetExpire = undefined;

        // 6. Save the user. The 'pre-save' middleware will automatically hash the new password.
        await user.save();

        // Note: We don't log the user in here. They must log in again with their new password.
        logger.info(`Password successfully reset for user: ${user.email}`);

        res.status(200).json({
            success: true,
            data: 'Password reset successfully.',
        });
    } catch (error) {
        next(error);
    }
};
