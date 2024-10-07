const User = require('../models/userModel');
const crypto = require('crypto');
const CustomError = require('../utils/customError');
const sendEmail = require('../utils/sendEmail');

// Request Password Reset Token
exports.requestPasswordReset = async (req, res, next) => {
    try {
        const user = await User.findOne({ email: req.body.email });
        if (!user) return next(new CustomError('No user found with that email', 404));

        const resetToken = user.getResetPasswordToken();
        await user.save({ validateBeforeSave: false });

        const resetUrl = `${req.protocol}://${req.get('host')}/api/password/reset/${resetToken}`;
        const message = `Reset your password by clicking on the following link: ${resetUrl}`;

        try {
            await sendEmail({ email: user.email, subject: 'Password Reset Token', message });
            res.status(200).json({ message: 'Reset token sent to email' });
        } catch (error) {
            user.resetPasswordToken = undefined;
            user.resetPasswordExpire = undefined;
            await user.save({ validateBeforeSave: false });
            next(new CustomError('Error sending email', 500));
        }
    } catch (error) {
        next(new CustomError('Error requesting password reset', 500));
    }
};

// Reset Password
exports.resetPassword = async (req, res, next) => {
    const resetToken = crypto.createHash('sha256').update(req.params.token).digest('hex');

    try {
        const user = await User.findOne({
            resetPasswordToken: resetToken,
            resetPasswordExpire: { $gt: Date.now() },
        });

        if (!user) {
            return next(new CustomError('Invalid or expired token', 400));
        }

        user.password = req.body.password;
        user.resetPasswordToken = undefined;
        user.resetPasswordExpire = undefined;
        await user.save();

        res.status(200).json({ message: 'Password updated successfully' });
    } catch (error) {
        next(new CustomError('Error resetting password', 500));
    }
};
