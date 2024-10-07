const User = require('../models/userModel');
const CustomError = require('../utils/customError');

// Get All Users (Admin-only)
exports.getAllUsers = async (req, res, next) => {
    try {
        const users = await User.find();
        res.status(200).json(users);
    } catch (error) {
        next(new CustomError('Unable to fetch users', 500));
    }
};

// Get User by ID
exports.getUserById = async (req, res, next) => {
    try {
        const user = await User.findById(req.params.userId);
        if (!user) {
            return next(new CustomError('User not found', 404));
        }
        res.status(200).json(user);
    } catch (error) {
        next(new CustomError('Error fetching user', 500));
    }
};

// Create New User (Admin-only)
exports.createUser = async (req, res, next) => {
    try {
        const { name, email, password, role } = req.body;
        const user = new User({ name, email, password, role });
        await user.save();

        // Emit real-time event for new user creation
        req.io.emit('user-created', user);

        res.status(201).json(user);
    } catch (error) {
        next(new CustomError('Error creating user', 400));
    }
};

// Update User (Admin-only)
exports.updateUser = async (req, res, next) => {
    try {
        const user = await User.findByIdAndUpdate(req.params.userId, req.body, { new: true });
        if (!user) {
            return next(new CustomError('User not found', 404));
        }

        // Emit real-time event for user update
        req.io.emit('user-updated', user);

        res.status(200).json(user);
    } catch (error) {
        next(new CustomError('Error updating user', 400));
    }
};

// Delete User (Admin-only)
exports.deleteUser = async (req, res, next) => {
    try {
        const user = await User.findByIdAndDelete(req.params.userId);
        if (!user) {
            return next(new CustomError('User not found', 404));
        }

        // Emit real-time event for user deletion
        req.io.emit('user-deleted', user);

        res.status(200).json({ message: 'User deleted successfully' });
    } catch (error) {
        next(new CustomError('Error deleting user', 400));
    }
};

// Get Current User Profile
exports.getProfile = async (req, res, next) => {
    try {
        const user = await User.findById(req.user.id);
        if (!user) {
            return next(new CustomError('User not found', 404));
        }
        res.status(200).json(user);
    } catch (error) {
        next(new CustomError('Error fetching profile', 500));
    }
};

// Update Current User Profile
exports.updateProfile = async (req, res, next) => {
    try {
        const user = await User.findByIdAndUpdate(req.user.id, req.body, { new: true });
        if (!user) {
            return next(new CustomError('User not found', 404));
        }
        res.status(200).json(user);
    } catch (error) {
        next(new CustomError('Error updating profile', 500));
    }
};
