// server/controllers/settingsController.js

const User = require('../models/userModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

/**
 * @desc    Update details for the currently logged-in user
 * @route   PUT /api/settings/updatedetails
 * @access  Private
 */
exports.updateDetails = async (req, res, next) => {
    try {
        // We only allow updating a limited set of fields.
        // We explicitly exclude role and password changes from this endpoint.
        const fieldsToUpdate = {
            name: req.body.name,
            email: req.body.email,
        };

        // Find the user by the ID from the token (`req.user.id` is set by `protect` middleware)
        // and update their details.
        const updatedUser = await User.findByIdAndUpdate(req.user.id, fieldsToUpdate, {
            new: true, // Return the updated document
            runValidators: true, // Ensure the new email is a valid format
        }).select('-password'); // Exclude password from the response

        logger.info(`User details updated for: ${updatedUser.email}`);

        res.status(200).json({
            success: true,
            data: updatedUser,
        });
    } catch (error) {
        logger.error(`Error updating user details: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Update password for the currently logged-in user
 * @route   PUT /api/settings/updatepassword
 * @access  Private
 */
exports.updatePassword = async (req, res, next) => {
    try {
        const { currentPassword, newPassword } = req.body;

        // 1. Find the user and explicitly include their password for comparison.
        const user = await User.findById(req.user.id).select('+password');

        // 2. Check if the provided current password is correct.
        const isMatch = await user.matchPassword(currentPassword);
        if (!isMatch) {
            return next(new CustomError('Incorrect current password.', 401));
        }

        // 3. Set the new password.
        user.password = newPassword;

        // 4. Save the user. The `pre-save` hook in the User model will automatically hash the new password.
        await user.save();

        logger.info(`Password updated successfully for: ${user.email}`);

        // It's good practice to not send back any data, just a success confirmation.
        res.status(200).json({
            success: true,
            message: 'Password updated successfully.',
        });

    } catch (error) {
        logger.error(`Error updating user password: ${error.message}`);
        next(error);
    }
};
