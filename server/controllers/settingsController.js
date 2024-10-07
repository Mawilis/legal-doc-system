const User = require('../models/userModel');
const CustomError = require('../utils/customError');

// Get User Settings
exports.getSettings = async (req, res, next) => {
    try {
        const user = await User.findById(req.user.id);
        res.status(200).json(user.settings);
    } catch (error) {
        next(new CustomError('Error fetching settings', 500));
    }
};

// Update User Settings
exports.updateSettings = async (req, res, next) => {
    try {
        const updatedUser = await User.findByIdAndUpdate(req.user.id, { settings: req.body }, { new: true });
        res.status(200).json(updatedUser.settings);
    } catch (error) {
        next(new CustomError('Error updating settings', 500));
    }
};
