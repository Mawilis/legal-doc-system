const User = require('../models/userModel');
const CustomError = require('../utils/customError');

// Create a new user (Admin-Only)
exports.createUser = async (req, res, next) => {
    try {
        const { name, email, password, role } = req.body;
        const user = new User({ name, email, password, role });
        await user.save();
        req.io.emit('user-created', user);  // Real-time update

        res.status(201).json(user);
    } catch (err) {
        next(new CustomError('Failed to create user', 500));
    }
};

// Get all users (Admin-Only)
exports.getAllUsers = async (req, res, next) => {
    try {
        const users = await User.find({});
        res.status(200).json(users);
    } catch (err) {
        next(new CustomError('Failed to fetch users', 500));
    }
};

// Get user by ID
exports.getUserById = async (req, res, next) => {
    try {
        const user = await User.findById(req.params.userId);
        if (!user) return next(new CustomError('User not found', 404));
        res.status(200).json(user);
    } catch (err) {
        next(err);
    }
};

// Update user (Admin-Only)
exports.updateUser = async (req, res, next) => {
    try {
        const user = await User.findByIdAndUpdate(req.params.userId, req.body, { new: true });
        if (!user) return next(new CustomError('User not found', 404));

        req.io.emit('user-updated', user);  // Real-time update
        res.status(200).json(user);
    } catch (err) {
        next(err);
    }
};

// Delete user (Admin-Only)
exports.deleteUser = async (req, res, next) => {
    try {
        const user = await User.findByIdAndDelete(req.params.userId);
        if (!user) return next(new CustomError('User not found', 404));

        req.io.emit('user-deleted', user);  // Real-time update
        res.status(200).json({ message: 'User deleted' });
    } catch (err) {
        next(err);
    }
};
