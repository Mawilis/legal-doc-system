// ~/server/models/locationModel.js

const mongoose = require('mongoose');

/**
 * @file This file defines the Mongoose schema for storing real-time location data.
 * It is optimized for high-performance geospatial queries using a 2dsphere index.
 */

/**
 * Defines the Mongoose schema for a location entry.
 */
const locationSchema = new mongoose.Schema({
    // A required reference to the user being tracked.
    // Indexing this field is crucial for quickly finding the location history of a specific user.
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User', // This should match the name of your User model
        required: true,
        index: true,
    },
    // The location is stored in the official GeoJSON Point format.
    // This is the standard and most powerful way to store geospatial data in MongoDB.
    location: {
        type: {
            type: String,
            enum: ['Point'], // 'location.type' must be 'Point'
            required: true,
        },
        coordinates: {
            type: [Number], // Array of numbers for [longitude, latitude]
            required: true,
        },
    },
}, {
    // Mongoose's built-in timestamp option automatically adds and manages
    // `createdAt` and `updatedAt` fields, which is more robust than manual handling.
    timestamps: true
});

// --- Geospatial Index ---
// This `2dsphere` index is the key to enabling high-performance geospatial queries,
// such as finding all users within a certain radius or polygon.
locationSchema.index({ location: '2dsphere' });

// Compile the schema into a Mongoose model.
const Location = mongoose.model('Location', locationSchema);

module.exports = Location;
