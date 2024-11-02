const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const validator = require('validator');
const logger = require('../utils/logger'); // Centralized logger (using Winston)

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
            match: [
                /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/,
                'Please provide a valid email address',
            ],
        },
        password: {
            type: String,
            required: [true, 'Password is required'],
            minlength: [8, 'Password must be at least 8 characters'],
            select: false, // Password should not be returned by default
            validate: {
                validator: function (value) {
                    return (
                        validator.isStrongPassword(value, {
                            minLength: 8,
                            minLowercase: 1,
                            minUppercase: 1,
                            minNumbers: 1,
                            minSymbols: 1,
                        })
                    );
                },
                message: 'Password must contain at least 8 characters, including an uppercase letter, a number, and a special character.',
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

// Custom pre-save hook for handling unique validation on email
userSchema.pre('save', async function (next) {
    if (!this.isModified('email')) return next();

    try {
        const existingUser = await mongoose.models.User.findOne({ email: this.email });
        if (existingUser) {
            return next(new Error('The email address is already taken.'));
        }
        next();
    } catch (err) {
        logger.error('Error during unique validation:', err);
        next(err);
    }
});

// Password hashing middleware before saving to the database
userSchema.pre('save', async function (next) {
    if (!this.isModified('password')) return next();

    try {
        const salt = await bcrypt.genSalt(12);
        this.password = await bcrypt.hash(this.password, salt);
        next();
    } catch (err) {
        logger.error('Error hashing password:', err);
        return next(new Error('Error hashing password'));
    }
});

// Method to compare passwords for authentication
userSchema.methods.comparePassword = async function (enteredPassword) {
    return await bcrypt.compare(enteredPassword, this.password);
};

// Method to update password and ensure it is hashed
userSchema.methods.updatePassword = async function (newPassword) {
    const salt = await bcrypt.genSalt(12);
    this.password = await bcrypt.hash(newPassword, salt);
    await this.save();
};

// Method to create a password reset token
userSchema.methods.createPasswordResetToken = function () {
    const resetToken = crypto.randomBytes(32).toString('hex');
    this.passwordResetToken = crypto.createHash('sha256').update(resetToken).digest('hex');
    this.passwordResetExpires = Date.now() + 10 * 60 * 1000; // Token valid for 10 minutes

    return resetToken;
};

// Transform user object to JSON (excluding sensitive fields)
userSchema.methods.toJSON = function () {
    const user = this.toObject();
    delete user.password;
    delete user.passwordResetToken;
    delete user.passwordResetExpires;
    return user;
};

// Static method to validate a role before updating
userSchema.statics.validateRole = function (role) {
    if (!roles.includes(role)) {
        throw new Error('Invalid role');
    }
};

// Export user model
const User = mongoose.model('User', userSchema);
module.exports = User;
