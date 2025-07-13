// server/models/userModel.js

const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const crypto = require('crypto'); // Built-in Node.js module

const userSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, 'Please provide a name.'],
        trim: true,
    },
    email: {
        type: String,
        required: [true, 'Please provide an email.'],
        unique: true,
        lowercase: true, // Always store emails in lowercase for consistency
        trim: true,
        match: [
            /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,
            'Please provide a valid email address.',
        ],
    },
    role: {
        type: String,
        enum: ['user', 'admin', 'deputy'], // Restrict roles to these values
        default: 'user',
    },
    password: {
        type: String,
        required: [true, 'Please provide a password.'],
        minlength: [6, 'Password must be at least 6 characters long.'],
        select: false, // Critically important: Do not return the password in queries by default
    },
    passwordResetToken: String,
    passwordResetExpire: Date,
}, {
    timestamps: true, // Automatically add createdAt and updatedAt
});

// --- Mongoose Middleware (Hook) ---
// This function runs automatically BEFORE a document is saved to the database.
userSchema.pre('save', async function (next) {
    // We only want to run this function if the password was actually modified.
    // This prevents the password from being re-hashed every time a user updates their email or name.
    if (!this.isModified('password')) {
        return next();
    }

    // Hash the password with a "cost factor" of 12. Higher is more secure but slower.
    const salt = await bcrypt.genSalt(12);
    this.password = await bcrypt.hash(this.password, salt);

    // For password resets, we don't want to re-validate the password field when saving.
    // So we clear the confirm password field if it exists.
    if (this.passwordConfirm) {
        this.passwordConfirm = undefined;
    }

    next();
});

// --- Instance Methods ---
// These are helper functions that will be available on every user document.

// Method to compare the password entered by the user with the hashed password in the database.
userSchema.methods.matchPassword = async function (enteredPassword) {
    // `bcrypt.compare` securely handles the comparison of the plain text password
    // with the stored hash.
    return await bcrypt.compare(enteredPassword, this.password);
};

// Method to generate and hash a password reset token for the user.
userSchema.methods.getResetPasswordToken = function () {
    // 1. Generate a random, secure token.
    const resetToken = crypto.randomBytes(20).toString('hex');

    // 2. Hash the token for secure storage in the database.
    this.passwordResetToken = crypto
        .createHash('sha256')
        .update(resetToken)
        .digest('hex');

    // 3. Set an expiration time for the token (e.g., 10 minutes from now).
    this.passwordResetExpire = Date.now() + 10 * 60 * 1000;

    // 4. Return the UN-hashed token. This is what we send to the user's email.
    return resetToken;
};

const User = mongoose.model('User', userSchema);

module.exports = User;
