// ~/legal-doc-system/server/models/userModel.js

const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const validator = require('validator');
const logger = require('../utils/logger');

// Enum for user roles
const roles = ['user', 'admin', 'attorney', 'sheriff'];

const userSchema = new mongoose.Schema(
    {
        name: {
            type: String,
            required: [true, 'Name is required'],
            trim: true,
            minlength: [2, 'Name must be at least 2 characters'],
        },
        email: {
            type: String,
            required: [true, 'Email is required'],
            unique: true,
            lowercase: true,
            trim: true,
            validate: [validator.isEmail, 'Please provide a valid email address'],
        },
        password: {
            type: String,
            required: [true, 'Password is required'],
            minlength: [8, 'Password must be at least 8 characters'],
            select: false,
            validate: {
                validator: function (value) {
                    return validator.isStrongPassword(value, {
                        minLength: 8,
                        minLowercase: 1,
                        minUppercase: 1,
                        minNumbers: 1,
                        minSymbols: 1,
                    });
                },
                message:
                    'Password must contain at least 8 characters, including an uppercase letter, a number, and a special character.',
            },
        },
        role: {
            type: String,
            enum: roles,
            default: 'user',
        },
        passwordResetToken: String,
        passwordResetExpires: Date,
    },
    {
        timestamps: true,
    }
);

// Pre-save middleware to hash passwords
userSchema.pre('save', async function (next) {
    // Only hash the password if it has been modified
    if (!this.isModified('password')) return next();

    try {
        // Generate a salt and hash the password
        const salt = await bcrypt.genSalt(12);
        this.password = await bcrypt.hash(this.password, salt);
        next();
    } catch (err) {
        logger.error('Error hashing password:', err);
        return next(err);
    }
});

// Method to compare passwords during login
userSchema.methods.comparePassword = async function (enteredPassword) {
    return await bcrypt.compare(enteredPassword, this.password);
};

// Method to create a password reset token
userSchema.methods.createPasswordResetToken = function () {
    const resetToken = crypto.randomBytes(32).toString('hex');
    this.passwordResetToken = crypto.createHash('sha256').update(resetToken).digest('hex');
    this.passwordResetExpires = Date.now() + 10 * 60 * 1000; // Token valid for 10 minutes

    return resetToken;
};

// Exclude sensitive fields when converting to JSON
userSchema.methods.toJSON = function () {
    const obj = this.toObject();
    delete obj.password;
    delete obj.passwordResetToken;
    delete obj.passwordResetExpires;
    return obj;
};

// Export user model
const User = mongoose.model('User', userSchema);
module.exports = User;
