// server/models/deputyModel.js

const mongoose = require('mongoose');

const deputySchema = new mongoose.Schema(
    {
        // --- Core Relationship ---
        // This creates a direct, one-to-one link to the User model.
        // Each deputy profile MUST be associated with one user account.
        user: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User',
            required: true,
            unique: true, // Ensures one user cannot have multiple deputy profiles.
        },

        // --- Deputy-Specific Information ---
        badgeNumber: {
            type: String,
            required: [true, 'A badge number is required.'],
            unique: true,
            trim: true,
        },
        serviceRegion: {
            type: String,
            required: [true, 'A service region is required.'],
            trim: true,
        },
        fieldContactNumber: {
            type: String,
            trim: true,
        },

        // --- Performance Metrics (optional but useful) ---
        // These could be updated periodically by a background job or controller logic.
        totalServicesCompleted: {
            type: Number,
            default: 0,
        },
        averageTimeToServe: {
            type: Number, // Stored in hours or days
            default: 0,
        },
    },
    {
        timestamps: true,
    }
);

const Deputy = mongoose.model('Deputy', deputySchema);

module.exports = Deputy;
